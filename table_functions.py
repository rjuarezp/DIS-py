#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:07:12 2020

@author: manjaro
"""

def sort_table(window, data, by_column, table_key, ascending):
    ascending = not ascending
    data.sort_values(by=[by_column], ascending=ascending, inplace=True)
    content = data.values.tolist()
    window.FindElement(table_key).Update(content)
    