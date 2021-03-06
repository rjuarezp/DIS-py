import PySimpleGUI as sg
import os
import pandas as pd
import clipboard

import sql_functions
import gui_functions

sg.theme('LightGreen')

cfg_left = {'size': (20,1)}

cfg_right = {'size': (50,1)}

# Create Database
data_path = os.getcwd()
docs_path = os.path.join(data_path, 'documents')
db_name = os.path.join(data_path, 'data.sqlite3')

if not os.path.isfile(db_name):
    sql_functions.create_db(db_name)
else:
    pass

authors_list = sql_functions.get_values('authors', 'name', db_name)
doc_types_list = sql_functions.get_values('doc_types','name', db_name)
user_id = os.getlogin().lower()
default_author = sql_functions.get_authorname(db_name,user_id)[0][0]

menu_def = [['&Configuration', ['Change config file', 'Admin Database']],
            ['&About', ['License', 'DIS-Py']]
           ]
    
layout = [
        [sg.Menu(menu_def, tearoff=True, key='-MENU-')],
        [sg.Text('Author', **cfg_left), sg.Combo(authors_list, default_value=default_author, key='-AUTHOR-',**cfg_right)],
        [sg.Text('Title', **cfg_left), sg.InputText(key='-TITLE-', **cfg_right)],
        [sg.Text('Document type', **cfg_left), sg.Combo(doc_types_list, key='-DOC_TYPE-', **cfg_right)],
        [sg.Text('New document name', **cfg_left), sg.Text(size=(30,1), key='-DOC_NAME-'), sg.Button('Copy to clipboard')],
        [sg.Output(size=(75,5), key='-OUTPUT-')],
        [sg.Button('Search'), sg.Button('Save new data'), sg.Button('Quit')]
        ]

window = sg.Window('DIS-Python - User: {}'.format(user_id), layout)

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
        data['created_at'] = pd.to_datetime(data.created_at)
        data['created_at'] = data['created_at'].dt.strftime('%d.%m.%Y %H:%M:%S')
        con.close()
        data = data[data['title'].str.contains(values['-TITLE-'])]
        data = data[data['author'].str.contains(values['-AUTHOR-'])]
        data = data[data['doc_type'].str.contains(values['-DOC_TYPE-'])]
        data.reset_index(drop=True, inplace=True)
        if data.shape[0] < 1:
            print('No data found')
        else:
            gui_functions.display_searchresults(data, docs_path, db_name)
    elif event == 'Copy to clipboard':
        clipboard.copy(window['-DOC_NAME-'].DisplayText)
    elif event == 'Change config file':
        gui_functions.config_file()

window.close()