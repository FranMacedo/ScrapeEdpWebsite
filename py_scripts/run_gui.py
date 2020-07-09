'''
        CREATES SIMPLE GUI TO DOWNLOAD FILES FROM EDP, STORE THEM IN WHEREVER YOU WANT (BY DEFAULT, REDE Z:)
'''

import time
import PySimpleGUI as sg
from func.run_robot import df_db, multi_robot
from func.robot_info import get_info
from datetime import datetime as dt
import pandas as pd


def turn_to_bool(s):
    s = str(s)
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sim', 'ok', 'todos', 'vamos']


def validate_gestao_cpes(gestao, cils_or_cpes):
        if gestao == 'None' and not cils_or_cpes:
            sg.PopupTimed('A Gestão e os CPEs não podem estar ambos vazios!', title='ERRO!', auto_close_duration=10)
            return False
        if gestao not in df_db.gestao.tolist() and gestao != 'None':
            sg.PopupTimed('Gestão Inválida!', title='ERRO!', auto_close_duration=10)
            return False

        return True

is_download = False
is_info = False
choices = list(set(df_db.gestao.tolist()))
choices = ['ALL'] + choices

choices = [str(c).strip() for c in choices]

email_choices = ['franciscomacedo@lisboaenova.org','lisboaenovarobot@gmail.com']
tb_download = [
    [sg.Text('Downloads files from edp', size=(20, 2))],

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


    [sg.Button('Download Files', key='OK_DOWNLOAD')]
]
tab_info = [
 [sg.Text('gets info from edp', size=(20, 2))],
 [sg.Text('Gestão', size=(20, 1)), sg.Combo(choices, key='GESTAO_INFO', default_value='None', enable_events=True)],
 [sg.Text('OU', size=(30, 1), font='Any 15', justification='center')],
 [sg.Text('CPEs ou CILs', size=(20, 1)), sg.InputText(key='CILS-OR-CPES_INFO', size=(60, 3), enable_events=True)],

 [sg.Text('Find if there are new CPEs?:', size=(30, 1)),
     sg.Radio('Yes', "GETNEW", key="GETNEW-TRUE", default=True, enable_events=True),
    sg.Radio('No', "GETNEW", key="GETNEW-FALSE", enable_events=True)],

    [sg.Text('Get only active CPEs?', size=(30, 1)),
        sg.Radio('Yes', "ACTIVE", key="ACTIVE-TRUE", default=True, enable_events=True),
        sg.Radio('No', "ACTIVE", key="ACTIVE-FALSE", enable_events=True)],

    [sg.Text('Get BTN as well?', size=(30, 1)),
     sg.Radio('Yes', "BTN", key="BTN-TRUE", enable_events=True),
     sg.Radio('No', "BTN", key="BTN-FALSE", default=True, enable_events=True)],
   [sg.Text('', size=(20, 2))],
    [sg.Text('Email to send info:', size=(20, 3),
             justification='center'), sg.Combo(email_choices, key='EMAIL', size=(60, 3), default_value=email_choices[0])],

 [sg.Button('Get Info', key='OK_INFO')]
]

layout = [[sg.TabGroup([[sg.Tab('Downloads', tb_download, tooltip='Download telecontagem from EDP'), sg.Tab('Get Info', tab_info, tooltip='Gathers Info from EDP')]])],    
          [sg.Text('', size=(70, 2)), sg.Cancel(button_color=('black', 'red'))]]    


window = sg.Window('Telecontagem Manager', layout)
while True:                  # the event loop
    event, values = window.read()

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

    elif event == 'OK_DOWNLOAD':
        res = validate_gestao_cpes(values['GESTAO'], values['CILS-OR-CPES'])
        if res:
            if values['GESTAO'] == 'None':
                gestao = None
            else:
                gestao = values['GESTAO']
            if values['CILS-OR-CPES']:
                import re
                cils_or_cpes = re.split('; |, |\*|\n\t',values['CILS-OR-CPES'])
                # cils_or_cpes = list(values['CILS-OR-CPES'].split(','))
                cils_or_cpes = [c.strip(' \t,.*#\n ') for c in cils_or_cpes]
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
            is_download = True
            sg.PopupTimed('O download será realizado em breve...', title='Download Ready', auto_close_duration=3)
            break


    elif event == 'CILS-OR-CPES_INFO':
        if values['CILS-OR-CPES_INFO'] != '':
           window['GETNEW-TRUE'].update(value=False)
           window['GETNEW-FALSE'].update(value=True)
           window['GESTAO_INFO'].update(value='None')

        else:
            print('aqui!')
            window['GETNEW-TRUE'].update(value=True)
           # window['GETNEW-FALSE'].update(value=False)

    elif event == 'GETNEW-TRUE':
        if values['GETNEW-TRUE']:
            window['CILS-OR-CPES_INFO'].update('')

    elif event == 'GESTAO_INFO':
        window['CILS-OR-CPES_INFO'].update('')

    elif event == 'OK_INFO':
        res = validate_gestao_cpes(values['GESTAO_INFO'], values['CILS-OR-CPES_INFO'])

        if res:
            if values['GESTAO_INFO'] == 'None':
                    gestao = None
            else:
                gestao = values['GESTAO_INFO']
            if values['CILS-OR-CPES_INFO']:
                import re
                cils_or_cpes = re.split('; |, |\*|\n\t',values['CILS-OR-CPES_INFO'])
                # cils_or_cpes = list(values['CILS-OR-CPES_INFO'].split(','))
                cils_or_cpes = [c.strip(' \t,.*#\n ') for c in cils_or_cpes]
                print('CILS OR CPES: ', cils_or_cpes)
            else:
                cils_or_cpes = None

            is_info = True
            sg.PopupTimed('A informação será reunida em breve em breve...', title='Info Ready', auto_close_duration=3)
            break

    elif event in (None, 'Exit', 'Cancel'):
        break
    else:
        print(values)
# time.sleep(5)
window.close()
if is_download:
    multi_robot(cils_or_cpes=cils_or_cpes, gestao=gestao, date_begin=date_begin,
            date_end=date_end, destination_path=destination_path)
    sg.PopupTimed('Download Realizado! Verifique os ficheiros de logs para saber o resultado dos seus downloads',
              title='Download Done', auto_close_duration=3)

if is_info:
    res = get_info(gestao=gestao, cils_or_cpes=cils_or_cpes, get_new=values['GETNEW-TRUE'], only_active=values['ACTIVE-TRUE'], no_BTN=values['ACTIVE-FALSE'], email_address=values['EMAIL'])
    if res:
        sg.PopupTimed('Informação reunida! Verifique o seu email para consultar a Informação reunida.',
                  title='Info gathered with success', auto_close_duration=3)
    else:
        sg.PopupTimed('Ocorreu Algum erro na reunião de informação...',
                  title='Something went wrong', auto_close_duration=3)