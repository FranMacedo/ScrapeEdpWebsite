'''
        CREATES SIMPLE GUI TO DOWNLOAD FILES FROM EDP, STORE THEM IN WHEREVER YOU WANT (BY DEFAULT, REDE Z:)
'''

import time
import PySimpleGUI as sg
from func.run_robot import df_db, multi_robot
from datetime import datetime as dt
import pandas as pd


def turn_to_bool(s):
    s = str(s)
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']


choices = list(set(df_db.gestao.tolist()))
choices = ['ALL'] + choices

choices = [str(c).strip() for c in choices]
layout = [
    [sg.Text('Please enter your preferences:')],

    [sg.Text('Gestão', size=(20, 1)), sg.Combo(choices, key='GESTAO', default_value='None', enable_events=True)],
    [sg.Text('OU', size=(30, 1), font='Any 15', justification='center')],

    [sg.Text('CPEs ou CILs', size=(20, 1)), sg.InputText(key='CILS-OR-CPES', size=(60, 3), enable_events=True)],
    [
        sg.Text('', size=(20, 1)),
        sg.Text('Data de Inicio', size=(20, 1), justification='center'),
        sg.Text('Data de Fim', size=(20, 1), justification='center')
    ],

    [
        sg.Text('Intervalo de Datas', size=(20, 1)),
        sg.In(key='DATE-BEGIN', enable_events=True, visible=False),
        sg.CalendarButton('2013-01', target='DATE-BEGIN', pad=None,
                          button_color=('red', 'white'), key='DATE-BEGIN-BTN', format=('%Y-%m'), size=(20, 1)),
        sg.In(key='DATE-END', enable_events=True, visible=False),
        sg.CalendarButton(dt.now().date().strftime('%Y-%m'), target='DATE-END', pad=None,
                          button_color=('red', 'white'), key='DATE-END-BTN', format=('%Y-%m'), size=(20, 1))
    ],
    [sg.Text('', size=(20, 2))],
    [sg.Text('Pasta de destino dos ficheiros\n(irá para a rede por defeito):', size=(20, 3),
             justification='center'), sg.InputText(key='DESTINATION-PATH', size=(60, 3),  justification='center')],

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
        if values['DATE-END'] and pd.to_datetime(values['DATE-END']) < pd.to_datetime(values['DATE-BEGIN']):
            sg.PopupTimed('A data de inicio não pode ser depois da data de fim!',
                          title='Erro nas datas!', auto_close_duration=3)
        else:
            window['DATE-BEGIN-BTN'].update(values['DATE-BEGIN'])
    elif event == 'DATE-END':

        print(pd.to_datetime(values['DATE-END']))
        if values['DATE-BEGIN'] and pd.to_datetime(values['DATE-END']) < pd.to_datetime(values['DATE-BEGIN']):
            sg.PopupTimed('A data de fim não pode ser antes da data de inicio!',
                          title='Erro nas datas!', auto_close_duration=3)
        else:
            window['DATE-END-BTN'].update(values['DATE-END'])

    elif event == 'GESTAO':
        window['CILS-OR-CPES'].update('')

    elif event == 'CILS-OR-CPES':
        window['GESTAO'].update(value='None')
    elif event == 'Ok':
        if values['GESTAO'] == 'None' and not values['CILS-OR-CPES']:
            sg.PopupTimed('A Gestão e os CPEs não podem estar ambos vazios!', title='ERRO!', auto_close_duration=10)
        else:
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
                date_begin = dt(2013, 1, 1)

            if values['DATE-END']:
                date_end = values['DATE-END']
            else:
                date_end = dt.now().date()
            if values['DESTINATION-PATH'] and values['DESTINATION-PATH'] != '':
                destination_path = values['DESTINATION-PATH']
            else:
                destination_path = "Z:\\DATABASE\\ENERGIA\\DATAFILES"
            print(destination_path)
            sg.PopupTimed('O download será realizado em breve...', title='Download Ready', auto_close_duration=3)
            break
    elif event in (None, 'Exit', 'Cancel'):
        break
    else:
        print(values)
# time.sleep(5)
window.close()
multi_robot(cils_or_cpes=cils_or_cpes, gestao=gestao, date_begin=date_begin,
            date_end=date_end, destination_path=destination_path)

sg.PopupTimed('Download Realizado! Verifique os ficheiros de logs para saber o resultado dos seus downloads',
              title='Download Done', auto_close_duration=3)
