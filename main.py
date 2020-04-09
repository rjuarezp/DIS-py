import PySimpleGUI as sg
import sqlite3
import os
import time as tm
import pandas as pd

sg.theme('DarkAmber')

cfg_left = {'size': (20,1)}

cfg_right = {'size': (50,1)}

# Create Database
db_name = 'data.sqlite3'
if not os.path.isfile(db_name):
    con = sqlite3.connect(db_name)
    c = con.cursor()
    query = '''CREATE TABLE IF NOT EXISTS authors(
           id integer PRIMARY KEY AUTOINCREMENT,
           name text NOT NULL
           )
            '''
    c.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS doc_types(
           id integer PRIMARY KEY AUTOINCREMENT,
           name text NOT NULL,
           template text NOT NULL
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

    doc_types = [(1, 'Folie', 'Folie_ECR_'), (2, 'Interner Brief', 'Int_Brief_ECR')]
    query = '''INSERT INTO doc_types(id, name, template) VALUES (?,?,?)
        '''
    c.executemany(query, doc_types)
    con.commit()
    authors = [(1, 'Papá'), (2, 'Mamá'), (3, 'Carlos'), (4, 'Amanda'), (5, 'Riqui')]
    c.executemany('INSERT INTO authors(id, name) VALUES (?,?)', authors)
    con.commit()
else:
    con = sqlite3.connect(db_name)
    c = con.cursor()


def get_new_docname(data):
    query = "SELECT template FROM doc_types WHERE name='{}'".format(data)
    c.execute(query)
    template_name = c.fetchall()[0][0]
    year = tm.strftime("%y")
    query = "SELECT * FROM data WHERE doc_name LIKE '%{}%'".format(template_name+year)
    c.execute(query)
    n_doc = str(len(c.fetchall())+1)
    name = template_name + year + n_doc.zfill(3)
    return name
    
def save_new_data(title, doc_name, author_id, doc_type):
    query = "INSERT INTO data(title, doc_name, author_id, doc_type) VALUES(?, ?, ?, ?)"
    values = (title, doc_name, author_id, doc_type)
    c.execute(query, values)
    con.commit()

def get_values(table, column):
    query = 'SELECT DISTINCT {} FROM {} ORDER BY {}'.format(column, table, column)
    c.execute(query)
    data = c.fetchall()
    return [line[0] for line in data]

def get_id(table, pattern):
    query = "SELECT id FROM {} WHERE name='{}'".format(table,pattern)
    c.execute(query)
    return int(c.fetchall()[0][0])

def get_name(table, id):
    query = "SELECT name FROM {} WHERE id='{}'".format(table,int(id))
    c.execute(query)
    return int(c.fetchall()[0][0])

def get_all(table):
    query = "SELECT * FROM {}".format(table)
    c.execute(query)
    return c.fetchall()

def display(data):
    content = data.values.tolist()
    headers_list = data.columns.tolist()
    layout2 = [
            [sg.Table(values=content,
                      headings=headers_list,
                      display_row_numbers=False,
                      num_rows=min(25, len(content)))],
             [sg.Button('Sort by Author'), sg.Button('Quit')]
            ]
    window2 = sg.Window('Data', layout2, grab_anywhere=False)
    while True:
        event2, values2 = window2.read(timeout=100)
        if event2 in (None, 'Quit'):
            break
        elif event2 == 'Sort by Author':
            pass
            #data.sort_values(by)
    window2.close()
    

authors_list = get_values('authors', 'name')
doc_types_list = get_values('doc_types','name')
    
layout = [
        [sg.Text('Author', **cfg_left), sg.Combo(authors_list, key='-AUTHOR-',**cfg_right)],
        [sg.Text('Title', **cfg_left), sg.InputText(key='-TITLE-', **cfg_right)],
        [sg.Text('Document type', **cfg_left), sg.Combo(doc_types_list, key='-DOC_TYPE-', **cfg_right)],
        [sg.Output(size=(70,5), key='-OUTPUT-')],
        [sg.Button('Search'), sg.Button('Save new data'), sg.Button('Quit')]
        ]

window = sg.Window('DIS-Python', layout)

while True:
    event, values = window.read(timeout=100)
    if event in (None, 'Quit'):
        break
    elif event == 'Save new data':
        window.FindElement('-OUTPUT-').Update('')
        if (values['-AUTHOR-'] not in authors_list) or (values['-DOC_TYPE-'] not in doc_types_list):
            print('Please enter a valid Author and/or Document type')
        else:
            title = values['-TITLE-']
            doc_name = get_new_docname(values['-DOC_TYPE-'])
            author_id = get_id('authors', values['-AUTHOR-'])
            doc_type = get_id('doc_types', values['-DOC_TYPE-'])
            save_new_data(title, doc_name, author_id, doc_type)
            print('Data sucessfully saved!')

    elif event == 'Search':
        window.FindElement('-OUTPUT-').Update('')
        query = '''SELECT
                         title,
                         doc_name,
                         doc_types.name as doc_type,
                         authors.name as author,
                         created_at
                   FROM
                         data
                         INNER JOIN authors on authors.id = data.author_id
                         INNER JOIN doc_types ON doc_types.id = data.doc_type;
                '''
        data = pd.read_sql_query(query, con)
        data = data[data['title'].str.contains(values['-TITLE-'])]
        data = data[data['author'].str.contains(values['-AUTHOR-'])]
        data = data[data['doc_type'].str.contains(values['-DOC_TYPE-'])]
        if data.shape[0] < 1:
            print('No data found')
        else:
            display(data)

con.close()
window.close()