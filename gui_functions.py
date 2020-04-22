import PySimpleGUI as sg
import table_functions
import sql_functions

cfg_left = {'size': (20,1)}

cfg_right = {'size': (50,1)}

def display_searchresults(data, docs_path, dbname):
    content = data.values.tolist()
    headers_list = data.columns.tolist()
    layout2 = [
            [sg.Table(values=content,
                      headings=headers_list,
                      display_row_numbers=False,
                      auto_size_columns=True,
                      max_col_width=100,
                      justification='left',
                      num_rows=min(25, len(content)),
                      key = '-TABLE-')],
            [sg.Button('Sort by Title'), sg.Button('Sort by Doc_type'),
             sg.Button('Sort by Author'), sg.Button('Sort by Date')],
            [sg.Button('Open marked documents'),
             sg.Button('Edit data'),
             sg.Button('Quit')]
            ]
    window2 = sg.Window('DIS-Pyton - Data', layout2, grab_anywhere=False)
    ascending = False
    window2_status = True
    while window2_status:
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
        elif event2 == 'Open marked documents':
            if len(values2['-TABLE-']) == 0:
                print('Please select documents to open')
            else:
                doc_list = [data.loc[x,'doc_name'] for x in values2['-TABLE-']]
                doc_type = [data.loc[x, 'doc_type'] for x in values2['-TABLE-']]
                table_functions.open_documents(docs_path, doc_list, doc_type, dbname)    
        elif event2 == 'Edit data':
            if len(values2['-TABLE-']) != 1:
                print('Please select only one document to edit')
            else:

                curr_author = data.loc[values2['-TABLE-'][0], 'author']
                curr_title = data.loc[values2['-TABLE-'][0], 'title']
                curr_date = data.loc[values2['-TABLE-'][0], 'created_at']
                curr_docname = data.loc[values2['-TABLE-'][0], 'doc_name']
                print(curr_author, curr_title, curr_date)
                edit_document(curr_author, curr_title, curr_date, curr_docname, dbname)
                window2_status = False
                
    window2.close()

def edit_document(curr_author, curr_title, curr_date, curr_docname, dbname):
    auth_list = sql_functions.get_values('authors', 'name', dbname)
    layout3 = [
              [sg.Text('Author', **cfg_left), sg.Combo(auth_list, key='-ed_AUTHOR-', readonly=True, default_value=curr_author, **cfg_right)],
              [sg.Text('Title', **cfg_left), sg.InputText(key='-ed_title-', default_text=curr_title, **cfg_right)],
              [sg.Text('Document number', **cfg_left), sg.Text(curr_docname, key='-doc_name-', **cfg_right)],
              [sg.Text('Date', **cfg_left), sg.Text(curr_date, key='-date-', **cfg_right)],
              [sg.Output(size=(75,5), key='-ed_OUTPUT-')],
              [sg.Button('Update data & Exit'), sg.Button('Cancel')]
              ]
    
    window3 = sg.Window('DIS-Python - Edit data', layout3)
    
    while True:
        event3, values3 = window3.read(timeout=100)
        if event3 in (None, 'Cancel'):
            break
        elif event3 == 'Update data & Exit':
            # Update title
            new_title = values3['-ed_title-']
            update1 = sql_functions.update_row(dbname, 'data', 'title', new_title, 'doc_name', curr_docname)
            # Update Author, if needed
            new_author = values3['-ed_AUTHOR-']
            print(new_author)
            new_author_id = sql_functions.get_id('authors', new_author, dbname)
            print(new_author_id)
            update2 = sql_functions.update_row(dbname, 'data', 'author_id', new_author_id, 'doc_name', curr_docname)
            if update1 and update2:
                print('Update successfull!!!')
                break
            else:
                print("Update error!!!!")

    window3.close()
    
def admin_database(dbname):
    layout4 = [
              [sg.Text('Select Table', **cfg_left), sg.Combo(['authors', 'doc_types'], key='-TABLE-', **cfg_right)],
              [sg.Button('Quit')]
              ]
    
    window4 = sg.Window('DIS-Python - Edit Database', layout4)
    
    while True:
        event4, values4= window4.read(timeout=100)
        if event4 in (None, 'Quit'):
            break
    
    window4.close()
    
def config_file():
    layout5 = [
              [sg.Text('Database path', **cfg_left), sg.InputText(key='-DB_FILE-'), sg.FileBrowse(target='-DB_FILE-', file_types=(("Sqlite3", "*.sqlite3"), ("All files", "*.*"),))],
              [sg.Button('Save configuration & Quit'), sg.Button('Quit')]
              ]
    
    window5 = sg.Window('DIS-Python - Configuration', layout5)
    
    while True:
        event5, value5 = window5.read(timeout=100)
        if event5 in (None, 'Quit'):
            break
    
    window5.close()
    