#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 07:46:50 2020

@author: manjaro
"""
import time as tm
import sqlite3

def create_db(dbname):
    con, c = open_db(dbname)    
    query = '''CREATE TABLE IF NOT EXISTS authors(
           id integer PRIMARY KEY AUTOINCREMENT,
           name text NOT NULL,
           NTuser_id text NOT NULL
           )
            '''
    c.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS doc_types(
           id integer PRIMARY KEY AUTOINCREMENT,
           name text NOT NULL,
           template text NOT NULL,
           extension text NOT NULL
           )
         '''
    c.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS data(
           id integer PRIMARY KEY AUTOINCREMENT,
           title text NOT NULL,
           doc_name text NOT NULL,
           author_id integer NOT NULL,
           doc_type integer NOT NULL,
           created_at DATE DEFAULT (datetime('now','localtime')),
           FOREIGN KEY (author_id) REFERENCES authors(id),
           FOREIGN KEY (doc_type) REFERENCES doc_types(id)
           )
         '''
    c.execute(query)
    con.commit()

    doc_types = [(1, 'Folie', 'Folie_ECR_', '.pptx'), (2, 'Interner_Brief', 'Int_Brief_ECR_', '.docx')]
    query = '''INSERT INTO doc_types(id, name, template, extension) VALUES (?,?,?,?)
        '''
    c.executemany(query, doc_types)
    con.commit()
    authors = [(1, 'Author A', 'zor3ho'), (2, 'Author B', 'jui3ho'), (3, 'Author C', 'ert3fe'), (4, 'Author D', 'ert2ho'), (5, 'Author E', 'jun2ho')]
    c.executemany('INSERT INTO authors(id, name, NTuser_id) VALUES (?,?,?)', authors)
    con.commit()
    con.close()

def open_db(dbname):
    con = sqlite3.connect(dbname)
    c = con.cursor()
    return con, c

def get_new_docname(data, dbname):
    con, cursor = open_db(dbname)
    query = "SELECT template FROM doc_types WHERE name='{}'".format(data)
    cursor.execute(query)
    template_name = cursor.fetchall()[0][0]
    year = tm.strftime("%y")
    query = "SELECT * FROM data WHERE doc_name LIKE '%{}%'".format(template_name+year)
    cursor.execute(query)
    n_doc = str(len(cursor.fetchall())+1)
    name = template_name + year + n_doc.zfill(4)
    con.close()
    return name
    
def save_new_data(title, doc_name, author_id, doc_type, dbname):
    con, cursor = open_db(dbname)
    query = "INSERT INTO data(title, doc_name, author_id, doc_type) VALUES(?, ?, ?, ?)"
    values = (title, doc_name, author_id, doc_type)
    cursor.execute(query, values)
    con.commit()
    con.close()
    

def get_values(table, column, dbname):
    con, cursor = open_db(dbname)
    query = 'SELECT DISTINCT {} FROM {} ORDER BY {}'.format(column, table, column)
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return [line[0] for line in data]

def get_id(table, pattern, dbname):
    con, cursor = open_db(dbname)
    query = "SELECT id FROM {} WHERE name='{}'".format(table,pattern)
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return int(data[0][0])

def get_name(table, id, dbname):
    con, cursor = open_db(dbname)
    query = "SELECT name FROM {} WHERE id='{}'".format(table,int(id))
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return int(data[0][0])

def get_all(table, dbname):
    con, cursor = open_db(dbname)
    query = "SELECT * FROM {}".format(table)
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return data

def get_year(dbname, doc_name):
    con, cursor = open_db(dbname)
    query = "SELECT strftime('%Y', created_at) as 'year' FROM data WHERE doc_name='{}'".format(doc_name)
    cursor.execute(query)
    data = cursor.fetchall()    
    con.close()
    return data

def get_cross(table, column, column_match, match, dbname):
    con, cursor = open_db(dbname)
    query = "SELECT {} FROM {} WHERE {}='{}'".format(column, table, column_match, match)
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return data

def get_authorname(dbname, userid):
    con, cursor = open_db(dbname)
    query = "SELECT name FROM authors WHERE NTuser_id='{}'".format(userid)
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return data

def update_row(dbname, table, update_column, value, match_column, match):
    try:
        con, cursor = open_db(dbname)
        query = "UPDATE {} SET {} = '{}' WHERE {}='{}'".format(table, update_column, value, match_column, match)
        cursor.execute(query)
        con.commit()
        con.close()
        return True
    except:
        return False
    
