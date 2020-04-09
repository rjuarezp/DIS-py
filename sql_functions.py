#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 07:46:50 2020

@author: manjaro
"""
import time as tm


def get_new_docname(data, cursor):
    query = "SELECT template FROM doc_types WHERE name='{}'".format(data)
    cursor.execute(query)
    template_name = cursor.fetchall()[0][0]
    year = tm.strftime("%y")
    query = "SELECT * FROM data WHERE doc_name LIKE '%{}%'".format(template_name+year)
    cursor.execute(query)
    n_doc = str(len(cursor.fetchall())+1)
    name = template_name + year + n_doc.zfill(3)
    return name
    
def save_new_data(title, doc_name, author_id, doc_type, connector, cursor):
    query = "INSERT INTO data(title, doc_name, author_id, doc_type) VALUES(?, ?, ?, ?)"
    values = (title, doc_name, author_id, doc_type)
    cursor.execute(query, values)
    connector.commit()

def get_values(table, column, cursor):
    query = 'SELECT DISTINCT {} FROM {} ORDER BY {}'.format(column, table, column)
    cursor.execute(query)
    data = cursor.fetchall()
    return [line[0] for line in data]

def get_id(table, pattern, cursor):
    query = "SELECT id FROM {} WHERE name='{}'".format(table,pattern)
    cursor.execute(query)
    return int(cursor.fetchall()[0][0])

def get_name(table, id, cursor):
    query = "SELECT name FROM {} WHERE id='{}'".format(table,int(id))
    cursor.execute(query)
    return int(cursor.fetchall()[0][0])

def get_all(table, cursor):
    query = "SELECT * FROM {}".format(table)
    cursor.execute(query)
    return cursor.fetchall()
