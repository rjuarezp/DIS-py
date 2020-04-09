#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:07:12 2020

@author: manjaro
"""
import os
import sql_functions

def sort_table(window, data, by_column, table_key, ascending):
    ascending = not ascending
    data.sort_values(by=[by_column], ascending=ascending, inplace=True)
    content = data.values.tolist()
    window.FindElement(table_key).Update(content)
    
def open_documents(data_path, list_documents, list_doc_types, dbname):
    for i, document in enumerate(list_documents):
        year = 2000 + int(document.split('_')[2][0:2])
        doc_type_name = sql_functions.get_cross('doc_types', 'template', 'name', list_doc_types[i], dbname)[0][0]
        doc_name = os.path.join(data_path, doc_type_name, str(year), document)
        print(doc_name)
    