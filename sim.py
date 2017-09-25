#!/usr/bin/env python

import numpy as np
import pandas as pd
import quandl

class EquitySimulator:
    def __init__(self, SimConfig):
        self.begin_date = SimConfig.begin
        self.end_date = SimConfig.end
        self.rebal = SimConfig.rebalancing_freq
        self.initial_level = SimConfig.initial_level
        self.price_vol_src = SimConfig.price_vol_src
        if self.price_vol_src == 'quandl':
            # need to activate key
            quandl.ApiConfig.api_key = 'RhMBfJxPDnhJzZUvFzsz'
        self.price_data = None
        self.shares_data = None
        self.level = None
        
    def load_price_vol_data(self, xref):
        first_ticker = xref.Ticker.values[0]
        adj_close_df = quandl.get_table('WIKI/PRICES', ticker=first_ticker, 
            date = {'gte':self.begin_date, 'lte':self.end_date})[['date','adj_close']].copy()
        #adj_volume_df = pd.DataFrame()
        for ticker in xref.Ticker.values[1:]:
            pvdf = quandl.get_table('WIKI/PRICES', ticker=ticker,
                    date = {'gte':self.begin_date, 'lte':self.end_date})
            if len(pvdf) > 0:
                adj_close_df = pd.merge(adj_close_df, pvdf[['date','adj_close']], 
                                    on='date',how='left',suffixes=['',ticker]).copy()
        adj_close_df.rename(columns={'adj_close':first_ticker},inplace=True)
        def _remove_beginning(string, start):
            if string.startswith(start):
                return string[len(start):]
            else:
                return string
        new_cols = [_remove_beginning(string, 'adj_close') 
                        for string in adj_close_df.columns.values]
        adj_close_df.columns = new_cols
        adj_close_df.set_index('date',inplace=True)
        self.price_data = adj_close_df
    
    def run(self):
        idx = 0
        rebal = self.rebal
        tot = self.initial_level
        rebal_shares_rows = []
        while idx < len(self.price_data):
            num_instr = self.price_data.iloc[idx].count()
            shares = tot / (self.price_data.iloc[[idx]] * num_instr)
            rebal_shares_rows.append(shares)
            idx += rebal
            try:
                tot = np.nansum(self.price_data.iloc[idx].values * 
                                        shares.T.iloc[:,0].values)
            except:
                break 
        rebal_shares = pd.concat(rebal_shares_rows) 
        shares = self.price_data[['SSYS']].join(rebal_shares, lsuffix='_l',how='left')
        shares.fillna(method='pad', inplace=True)
        shares.drop('SSYS_l',axis=1,inplace=True)
        self.shares_data = shares.copy()
        
        level = self.price_data.multiply(self.shares_data).sum(axis=1)
        self.level = level.copy()