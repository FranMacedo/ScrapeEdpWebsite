from .robot_edp_online import robot, logs_dir
from .my_functions import connect_db, find_between_r
from datetime import datetime as dt
import pandas as pd
import os
from glob import glob
import sys

try:
    df_db = connect_db('energia', False)
    print(df_db)
except Exception as e:
    print(
        f"Ocurreu um erro a tentar ligar à rede...:{e}\n\nTente Novamente mais tarde, depois de a ligação estar estabelecida.")
    sys.exit()


def str_to_dt(d):
    if isinstance(d, str):
        return pd.to_datetime(d)
    return d


def create_download_log(report):
    print(report)
    all_dates_txt = []
    cat = []
    cils = []
    for k, v in report.items():
        cils.append(k)
        for k2, v2 in v.items():
            cat.append(k2)
            all_dates_txt.append(v2)

    all_dates_txt = [item for sublist in all_dates_txt for item in sublist]
    all_dates_txt = list(set(all_dates_txt))
    cat = list(set(cat))
    cils = list(set(cils))

    df = pd.DataFrame(columns=all_dates_txt, index=cils)

    for date in all_dates_txt:
        for cil in cils:
            for k2, v2 in report[cil].items():
                if date in v2:
                    df.loc[cil, date] = k2

    today = dt.today().strftime('%Y-%m-%d %Hh_%Mm')
    report_path = os.path.join(logs_dir, 'download_' + today + '.csv')
    df.to_csv(report_path)
    return

# robot(df_db.loc[df_db.cil==3874085].iloc[0], ['202003', '202004', '202005'], {}, True)


def robot_inst(cil_or_cpe, date_list=None, date_begin=dt(2013, 1, 1), date_end=dt.now().date(),
               replace=True, report={}, destination_path="Z:\\DATABASE\\ENERGIA\\DATAFILES"):
    if isinstance(cil_or_cpe, str):
        if 'PT' in cil_or_cpe:
            inst = df_db.loc[df_db.cpe == cil_or_cpe].iloc[0]
        else:
            inst = df_db.loc[df_db.cil == int(cil_or_cpe)].iloc[0]
    else:
        inst = df_db.loc[df_db.cil == int(cil_or_cpe)].iloc[0]

    if date_list:
        if isinstance(date_list, str):
            ym = [str_to_dt(date_list).strftime('%Y%m')]
        else:
            ym = [str_to_dt(d).strftime('%Y%m') for d in date_list]

    else:
        date_begin = str_to_dt(date_begin)
        date_end = str_to_dt(date_end)

        ym = pd.date_range(start=date_begin, end=date_end,
                           freq='MS').strftime('%Y%m').tolist()

    ym.sort()
    print(f"\nTrying: {ym}")
    try:
        return True, robot(inst, ym, replace, destination_path)
    except Exception as e:
        print(f'\n\nsomething went wrong: {e}\n\n')
        return False, [inst['cil'], ym]


def multi_robot(cils_or_cpes=None, gestao=None, date_list=None, date_begin=dt(2013, 1, 1),
                date_end=dt.now().date(), replace=True, destination_path="Z:\\DATABASE\\ENERGIA\\DATAFILES"):

    if gestao:
        df_gestao = df_db.loc[df_db.gestao == gestao, :]
        df_gestao = df_gestao.loc[df_gestao.abastecimento != "BTN", :]
        cils_or_cpes = df_gestao.cil.tolist()

    print(cils_or_cpes)
    print(len(cils_or_cpes))
    report = {}
    missing_cils = []
    for cil in cils_or_cpes:
        result, r = robot_inst(cil_or_cpe=cil, date_list=date_list,
                               date_begin=date_begin, date_end=date_end, replace=replace, report=report,
                               destination_path=destination_path)
        if result:
            report[cil] = r
        else:
            missing_cils.append(r[0])

    for cil in missing_cils:
        result, r = robot_inst(cil_or_cpe=cil, date_list=date_list,
                               date_begin=date_begin, date_end=date_end, replace=replace, report=report,
                               destination_path=destination_path)
        if result:
            report[cil] = r
        else:
            report[cil] = {'new file added': [],
                           'download fail': r[1],
                           'file replaced': [],
                           'file extended': []
                           }

    create_download_log(report)
