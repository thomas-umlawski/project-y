#!/usr/bin/env python

import pandas as pd
import quandl

class SimConfig:
    """Simulation default configuration"""
    begin = '2010-01-01'
    end = '2017-09-25'
    price_vol_src = 'quandl'
    rebalancing_freq = 63 #days, quarterly
    initial_level = 1000
    
        
    
    