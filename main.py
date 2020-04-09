import PySimpleGUI as sg
import os
import pandas as pd
import clipboard

import sql_functions
import table_functions

sg.theme('DarkAmber')

cfg_left = {'size': (20,1)}

cfg_right = {'size': (50,1)}

# Create Database
db_name = 'data.sqlite3'

if not os.path.isfile(db_name):
    sql_functions.create_db(db_name)
else:
    pass

def display(data):
    content = data.values.tolist()
    headers_list = data.columns.tolist()
    layout2 = [
            [sg.Table(values=content,
                      headings=headers_list,
                      display_row_numbers=False,
                      num_rows=min(25, len(content)),
                      key = '-TABLE-')],
            [sg.Button('Sort by Title'), sg.Button('Sort by Doc_type'),
             sg.Button('Sort by Author'), sg.Button('Sort by Date'),
             sg.Button('Quit')]
            ]
    window2 = sg.Window('Data', layout2, grab_anywhere=False)
    ascending = False
    while True:
        event2, values2 = window2.read(timeout=100)
        if event2 in (None, 'Quit'):
            break
        elif event2 == 'Sort by Doc_type':
            ascending = not ascending
            table_functions.sort_table(window2, data, 'doc_type', '-TABLE-', ascending)
        elif event2 == 'Sort by Author':
            ascending = not ascending
            table_functions.sort_table(window2, data, 'author', '-TABLE-', ascending)
        elif event2 == 'Sort by Date':
            ascending = not ascending
            table_functions.sort_table(window2, data, 'created_at', '-TABLE-', ascending)
        elif event2 == 'Sort by Title':
            ascending = not ascending
            table_functions.sort_table(window2, data, 'title', '-TABLE-', ascending)
            
            
    window2.close()

authors_list = sql_functions.get_values('authors', 'name', db_name)
doc_types_list = sql_functions.get_values('doc_types','name', db_name)
    
layout = [
        [sg.Text('Author', **cfg_left), sg.Combo(authors_list, key='-AUTHOR-',**cfg_right)],
        [sg.Text('Title', **cfg_left), sg.InputText(key='-TITLE-', **cfg_right)],
        [sg.Text('Document type', **cfg_left), sg.Combo(doc_types_list, key='-DOC_TYPE-', **cfg_right)],
        [sg.Text('New document name', **cfg_left), sg.Text(size=(30,1), key='-DOC_NAME-'), sg.Button('Copy to clipboard')],
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
            doc_name = sql_functions.get_new_docname(values['-DOC_TYPE-'], db_name)
            window['-DOC_NAME-'].update(doc_name)
            author_id = sql_functions.get_id('authors', values['-AUTHOR-'], db_name)
            doc_type = sql_functions.get_id('doc_types', values['-DOC_TYPE-'], db_name)
            sql_functions.save_new_data(title, doc_name, author_id, doc_type, db_name)
            print('Data sucessfully saved!')

    elif event == 'Search':
        con, cursor = sql_functions.open_db(db_name)
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
        con.close()
        data = data[data['title'].str.contains(values['-TITLE-'])]
        data = data[data['author'].str.contains(values['-AUTHOR-'])]
        data = data[data['doc_type'].str.contains(values['-DOC_TYPE-'])]
        if data.shape[0] < 1:
            print('No data found')
        else:
            display(data)
    elif event == 'Copy to clipboard':
        clipboard.copy(window['-DOC_NAME-'].DisplayText)

window.close()