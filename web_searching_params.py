#!/usr/bin/env python


### ----------------- parameters for scraping 3D Printing DB Database online
web_root_url = 'http://3dprintingdatabase.org/en/directory?'
web_search_args = {'field_address_country':'US',
               'field_services_tid':'459', # Printer manufacturers
               'title':'',
               'items_per_page':'200'}
web_find_all_args = ['span',  {'class':'field-content'}]


### -------------------------------- parameters for searching patents online
patent_root_url = 'http://www.patentsview.org/api/patents/query?q='
# Search 1 parameters: key words in title and abstract
patent_comparison_op_search1 = '_text_phrase'
patent_keys_search1 = ['patent_title', 'patent_abstract']
patent_values_search1 = ['three-dimensional printing', 
    'three-dimensional printer','three-dimension printer', 
    'additive manufacturing', 
    'laser sintering','selective laser sintering',
    'stereolitography','photopolymerization','powder bed fusion',
    '3d printer filament', 'metal 3d']
# Search 2 parameters: CPC group id corresponding to additive manufacturing
patent_comparison_op_search2 = '_eq'
patent_keys_search2 = ['cpc_group_id']
patent_values_search2 = ['B33Y']
# miscellaneous
patent_output_fields = ['patent_title','patent_abstract',
    'patent_date','assignee_organization']
patent_output_options = {'per_page':10000}

to_remove = [', Inc.',' Inc.',', Inc',' Inc',', INC.',', INC',' INC.',' INC',
            ' Ltd',', Ltd',' Ltd.',', Ltd.',', LTD.',', LTD',' LTD.',' LTD',
            ' LIMITED',' Limited',' Pty',' Co.',' Corporation','Corp.',
            ' PLC',' Company', ' Incorporated',' Development Company, L.P.',
            ' Enterprise',' Ent.',' Enterprise Company',
            ', LLC',', LLC.',' LLC',' LLC.',' Llc.',', Llc.',' Llc',', Llc',
            ' S.A.',' S.A.R.L.',', L.P.',', LP',' LP',' L.P.']
