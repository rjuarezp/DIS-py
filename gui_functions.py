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
                      justification='left',
                      num_rows=min(25, len(content)),
                      key = '-TABLE-')],
            [sg.Button('Sort by Title'), sg.Button('Sort by Doc_type'),
             sg.Button('Sort by Author'), sg.Button('Sort by Date')],
            [sg.Button('Open marked documents'),
             sg.Button('Edit data'),
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
                print(curr_author, curr_title, curr_date)
                edit_document(curr_author, curr_title, curr_date, dbname)
            
    window2.close()

def edit_document(curr_author, curr_title, curr_date, dbname):
    auth_list = sql_functions.get_values('authors', 'name', dbname)
    layout3 = [
              [sg.Text('Author', **cfg_left), sg.Combo(auth_list, key='-ed_AUTHOR-', readonly=True, default_value=curr_author, **cfg_right)],
              [sg.Text('Title', **cfg_left), sg.InputText(key='-ed_title-', default_text=curr_title, **cfg_right)],
              [sg.Button('Update data & Exit'), sg.Button('Cancel')]
              ]
    
    window3 = sg.Window('Edit data', layout3)
    
    while True:
        event3, values3 = window3.read(timeout=100)
        if event3 in (None, 'Cancel'):
            break
        elif event3 == 'Update data & Exit':
            
            pass
    window3.close()
    