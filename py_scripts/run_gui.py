'''
        CREATES SIMPLE GUI, FOR USER TO QUERY INTERNAL REDE (Z:/) TO GET INFO REGARDING CILS AND DATAFILES AVAILABLE
'''

import time
import PySimpleGUI as sg
from func.run_robot import df_db, multi_robot
from datetime import datetime as dt


def turn_to_bool(s):
    s = str(s)
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']


choices = list(set(df_db.gestao.tolist()))
choices = ['ALL'] + choices

choices = [str(c).strip() for c in choices]
layout = [
    [sg.Text('Please enter your preferences:')],
    [sg.Text('Gestão', size=(10, 1)), sg.Combo(choices, key='GESTAO', default_value='None', enable_events=True)],
    [sg.Text('CPEs', size=(10, 1)), sg.Listbox(values=('aaa', 'bbb', 'ccc'),
                                               size=(60, 3), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
    [sg.Text('CPEs ou CILs', size=(10, 1)), sg.InputText(key='CILS-OR-CPES', size=(60, 3))],

    [sg.In(key='DATE-BEGIN', enable_events=True, visible=False), sg.CalendarButton('Start Date...', target='DATE-BEGIN', pad=None,
                                                                                   button_color=('red', 'white'), key='DATE-BEGIN-BTN', format=('%Y-%m')), sg.In(key='DATE-END', enable_events=True, visible=False), sg.CalendarButton('End Date...', target='DATE-END', pad=None,
                                                                                                                                                                                                                                       button_color=('red', 'white'), key='DATE-END-BTN', format=('%Y-%m'))],
    # [sg.Text('With details (gestão, tt and files)?', size=(30, 1)),
    # sg.Radio('Yes', "DETAIL", key="DETAIL-TRUE", default=True, enable_events=True),
    # sg.Radio('No', "DETAIL", key="DETAIL-FALSE", enable_events=True)],

    #    [sg.Text('Format to pandas df?', size=(30, 1)),
    # sg.Radio('Yes', "FORMAT", key="FORMAT-TRUE", default=True, enable_events=True),
    # sg.Radio('No', "FORMAT", key="FORMAT-FALSE", enable_events=True)],

    #   [sg.Text('Write to excel?', size=(30, 1)),
    # sg.Radio('Yes', "EXCEL", key="EXCEL-TRUE", default=True, enable_events=True),
    # sg.Radio('No', "EXCEL", key="EXCEL-FALSE", enable_events=True)],


    [sg.Button('Ok'), sg.Cancel()]
]

window = sg.Window('Get Info from Rede Z:/', layout)
while True:                  # the event loop
    event, values = window.read()
    print(event)
    print(values)
    # if event in ["DETAIL-TRUE", "DETAIL-FALSE"]:
    # 	with_detail = turn_to_bool(event.split('-')[1])

    # 	if not with_detail:
    # 		window['FORMAT-TRUE'].update(value=False)
    # 		window['FORMAT-FALSE'].update(value=True)
    # 		window['EXCEL-TRUE'].update(value=False)
    # 		window['EXCEL-FALSE'].update(value=True)

    # elif event in ["FORMAT-TRUE", "FORMAT-FALSE", "EXCEL-TRUE", "EXCEL-FALSE"]:
    # 	with_format = turn_to_bool(event.split('-')[1])

    # 	if with_format:
    # 		window['DETAIL-TRUE'].update(value=True)
    # 		window['DETAIL-FALSE'].update(value=False)

    if event == 'DATE-BEGIN':
        window['DATE-BEGIN-BTN'].update(values['DATE-BEGIN'])
    elif event == 'DATE-END':
        window['DATE-END-BTN'].update(values['DATE-END'])
    elif event == 'Ok':
        print(values)
        if values['GESTAO'] == 'None':
            gestao = None
        else:
            gestao = values['GESTAO']
        if values['CILS-OR-CPES']:
            cils_or_cpes = list(values['CILS-OR-CPES'].split(','))
        else:
            cils_or_cpes = None

        if values['DATE-BEGIN']:
            date_begin = values['DATE-BEGIN']
        else:
            date_begin = dt(2012, 1, 1)

        if values['DATE-END']:
            date_end = values['DATE-END']
        else:
            date_end = dt.now().date()

        multi_robot(cils_or_cpes=cils_or_cpes, gestao=gestao, date_list=None,
                    date_begin=date_begin, date_end=date_end, replace=True)
        break
    elif event in (None, 'Exit', 'Cancel'):
        break
    else:
        print(values)
time.sleep(5)
window.close()
