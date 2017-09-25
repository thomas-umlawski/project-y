#!/usr/bin/env python

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json



class AbstractScraper:
    def __init__(self, root_url):
        self.root_url = root_url
        self.companies_list = []
        
    def get_companies_list(self):
        """Returns the list of unique company names found"""
        return self.companies_list
    
    def update_companies_list(self, company_names):
        """Updates the object's list of unique company names"""
        cur_names = self.companies_list
        cur_names.extend(company_names)
        self.companies_list = list(set(cur_names))



class WebDBScraper(AbstractScraper):
    def __init__(self, *args, **kwargs):
        super(WebDBScraper, self).__init__(*args, **kwargs)
    
    def _construct_query(self, search_args):
        search_query = ''
        for key in search_args.keys():
            search_query += key + '=' + search_args[key] + '&'
        url = self.root_url + search_query[:-1]
        return url
    
    def search(self, search_args, find_all_args):
        """Searches company names, returns a list of company names"""
        url = self._construct_query(search_args)
        response = requests.get(url) 
        content = response.content
        soup = BeautifulSoup(content, "lxml")
        names = [line.string.strip() for line in soup.find_all(*find_all_args)]
        return names   
    



class PatentScraper(AbstractScraper):
    def __init__(self, *args, **kwargs):
        super(PatentScraper, self).__init__(*args, **kwargs)
    
    def _build_patent_individual_queries(self, comparison_op, keys, values,
                                    output_fields=None, output_options=None):
        """Constructs the queries one by one for a given value in "values",
        as patentsview's [] operator for values does not work properly"""
        patent_root_url = self.root_url 
        queries = []
        for value in values:
            json_dict = {}
            # build keys with same value each time
            keys_value = {}
            for key in keys:
                keys_value[key] = value
            json_dict[comparison_op] = keys_value
            json_str = json.dumps(json_dict)
            query = patent_root_url + json_str
                
            if output_fields is not None:
                query = query + '&f=' + json.dumps(output_fields)
            if output_options is not None:
                query = query + '&o=' + json.dumps(output_options)
            queries.append(query)
            
        return queries
    
    def _to_dataframe(self, response):
        content = response.content
        try:
            df0 = pd.read_json(content)
        except ValueError:
            return pd.DataFrame()
        json_data = [record for record in df0.patents.values]
        del df0
        df = pd.DataFrame(json_data)
        if 'assignees' in df.columns:
            df['organization'] = [assignee[0]['assignee_organization'] 
                                for assignee in df.assignees.values]
            df.drop('assignees', axis=1, inplace=True)
        return df
    
    def search(self, comparison_op, keys, values,
            output_fields=None, output_options=None):
        """Searches patents database, returns dataframe and comp. names list"""
        queries = self._build_patent_individual_queries(comparison_op, 
                            keys, values, output_fields, output_options)
        dfs = [self._to_dataframe(requests.get(query)) for query in queries]
        df = pd.concat(dfs)
        df.drop_duplicates(inplace=True)
        names = list(set(df.organization.values))
        return df, names