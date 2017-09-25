#!/usr/bin/env python

import pandas as pd
from scrapers import WebDBScraper, PatentScraper
from web_searching_params import *
from sim import EquitySimulator
from sim_config import SimConfig

# Resource for mapping
yahoo_map_path = 'C:/Users/Thomas/Desktop/yahoo_ticker_symbol.csv'

# mininum number of patents to retain in the list
min_np = 2

def scrape_web():
    ### Search 3D-Printing-Database
    web = WebDBScraper(web_root_url)
    company_names = web.search(web_search_args, web_find_all_args)
    web.update_companies_list(company_names)

    ### Search Patents
    patent = PatentScraper(patent_root_url)
    
    # First with Key Words
    df1, cn1 = patent.search(patent_comparison_op_search1,
                            patent_keys_search1,
                            patent_values_search1,
                            patent_output_fields,
                            patent_output_options)
    patent.update_companies_list(cn1)
    
    # Then, search Patents with CPC classification group ID
    df2, cn2 = patent.search(patent_comparison_op_search2,
                            patent_keys_search2,
                            patent_values_search2,
                            patent_output_fields,
                            patent_output_options)
    patent.update_companies_list(cn2)
    
    pdf = pd.concat([df1,df2]) # patent dataframe
    pdf.drop_duplicates(inplace=True)
    pdf = pdf.fillna('').copy()
    
    return web, patent, pdf

def map_companies_to_tickers(companies_list, yahoo_map_path):
    xref = pd.read_csv(yahoo_map_path, skiprows=3, index_col='Country',
                                                    encoding='latin-1')
    # keep U.S. only
    xref = xref.ix['USA'].copy()
    # modify names in companies list
    def _remove_end(string, remove):
        if string is None:
            string = ''
        for ending in remove:
            if string.endswith(ending):
                return string[:-len(ending)]
        return string
    # wrongly spelled or in caps
    companies_list.extend(['General Electric','HP'])
    companies = pd.DataFrame([_remove_end(c, to_remove) 
                                for c in companies_list],
                                columns=['Name']) 
    xref['Name'] = [_remove_end(c, to_remove) 
                                for c in xref.Name.values]
    # select companies with recognizable Name
    xref = pd.merge(xref, companies).copy()
    xref.drop_duplicates(subset=['Name'], inplace=True)
    xref = xref[xref.Exchange != 'PNK'].copy()
    return xref
              

if __name__ == "__main__":
    # scrape the web to find companies at least remotely exposed to 3d-printing
    web, patent, pdf = scrape_web()
    
    #select only those with at least min_np patents
    pdf_gb_c = pdf.groupby('organization').count()
    patent_companies = pdf_gb_c[pdf_gb_c.patent_title > min_np].index.values
    del pdf_gb_c
    
    # final list of companies: those registered in 3-printing database as
    # manufacturers, those with at least min_np patents, and traded in the U.S.
    # but not OTC
    web_companies = web.get_companies_list()
    web_companies.extend(patent_companies)
    companies_list = list(set(web_companies))
    xref = map_companies_to_tickers(companies_list, yahoo_map_path)
      
    # back-test
    sim = EquitySimulator(SimConfig)
    sim.load_price_vol_data(xref)
    sim.run()

    # show index time series
    sim.level.plot(figsize=(15,10))
    
    