from .robot_edp_online import *
from .run_robot import df_db, create_download_log
import os
from glob import glob
from .auto_email import send_auto_email
import time
import math


def str_to_path(text):
    if isinstance(text, str):
        chars = "@/\\`*{}[]()>#+-.!$"
        for c in chars:
            text = text.replace(c, "_")
    return text


def space_l(l):
    return" ".join(list(map(str, l)))


def get_cpes(gestao, cils_or_cpes, f_logs):
    cpes_fail = []
    if not cils_or_cpes and not gestao:
        print_text_both('please select one "gestao" (gestao=*string*) or a number of cpes/cils (cpes_or_cils=*list*)', f_logs)
        return None
    if gestao:
        cpes = df_db.loc[df_db.gestao == gestao.upper(), 'cpe'].tolist()
        if not cpes:
            print_text_both(f'A gestão selecionada --{gestao}-- não é válida... tente novamente.', f_logs)

            return None
    else:

        if isinstance(cils_or_cpes, str):
            cils_or_cpes = [cils_or_cpes]

        cpes = []

        for c in cils_or_cpes:
            if isinstance(c, str) and 'PT' in c:
                cpes.append(c)
            else:
                try:
                    c = int(c)
                    cpe = df_db.loc[df_db.cil == c, 'cpe'].values[0]
                    cpes.append(cpe)
                except:
                    cpes_fail.append(c)
                    continue
        if not cpes:
            print_text_both(
                f'::ERRO!:: Os cpes/cils selecionados não são válidos... tente novamente:\n:::: -->CPES/CILS inválidos: {space_l(cils_or_cpes)}', f_logs)
            return None

    if cpes_fail:
        print_text_both(f'::ERRO!:: SÓ nos cils/cpes: {space_l(cpes_fail)}. \n:::: -->Serão ignorados.', f_logs)

    cpes = list(set(cpes))
    return cpes


def info_cpe(cpe, driver, wait, f_logs, wait_short, all_cpes_data, tt):

    cpe_data = {}
    lista_button(driver)
    try:
        success_search = search_cpe(driver, cpe, wait, f_logs)
        if not success_search:
            lista_button(driver)
            success_search = search_cpe(driver, cpe, wait, f_logs)
    except InvalidElementStateException:
        print_text_both("-Not possible to search. trying to click in this page", f_logs)

    wait_loading_state(driver, 100)

    try:
        rows_begin = wait.until(ec.presence_of_all_elements_located((By.LINK_TEXT, cpe)))
    except TimeoutException:
        print_text_both("-No results found. Trying next CPE...", f_logs)
        return False, all_cpes_data

    print_text_both("-{} list result(s) found for that CPE".format(len(rows_begin)), f_logs)
    for row in rows_begin:
        # row = rows_begin[0]
        index_row = rows_begin.index(row)
        print_text_both(f"--Trying row {index_row + 1}", f_logs)

        wait_loading_state(driver, 100)

        is_lista = lista_button(driver)

        if is_lista:
            try:
                success_search = search_cpe(driver, cpe, wait, f_logs)
                if not success_search:
                    print_text_both("--nao é possivel procurar", f_logs)
                    continue
            except InvalidElementStateException:
                print_text_both("-Not possible to search. trying to click for this row in this page", f_logs)
        try:
            rows = wait.until(ec.presence_of_all_elements_located((By.LINK_TEXT, cpe)))
            row = rows[index_row]

        except (TimeoutException, IndexError):
            print_text_both("--No results found for this CPE. Trying next CPE...", f_logs)
            continue

        wait_loading_state(driver, 100)
        try:
            scroll_to_element(driver, row)

        except StaleElementReferenceException:
            lista_button(driver)
            success_search = search_cpe(driver, cpe, wait, f_logs)
            if not success_search:
                print_text_both("--nao é possivel procurar", f_logs)
                continue
            try:
                rows = wait.until(ec.presence_of_all_elements_located((By.LINK_TEXT, cpe)))
                row = rows[index_row]
            except (TimeoutException, IndexError):
                print_text_both("--No results found for this CPE. Trying next CPE...", f_logs)
                continue

        row.click()
        wait_loading_state(driver, 100)
        # all_info = driver.find_elements_by_class_name( "card-subtitle")
        all_info = wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, "card-subtitle")))
        row_name = f"row {index_row + 1}"
        cpe_data[row_name] = {}
        for a in all_info:
            try:
                name = a.text
                name_info = driver.execute_script("""return arguments[0].nextElementSibling""", a).text
                cpe_data[row_name][name] = name_info
            except:
                continue

        try:
            consumos_tab = wait_short.until(ec.element_to_be_clickable((By.LINK_TEXT, "Consumos")))
            cpe_data[row_name]['consumos'] = True
        except TimeoutException:
            print_text_both("---!!Consumos tab not found...", f_logs)
            cpe_data[row_name]['consumos'] = False
        cpe_data[row_name]['abastecimento'] = tt
        wait_loading_state(driver, 100)
        all_cpes_data[cpe] = cpe_data
        back_button = wait.until(ec.element_to_be_clickable((By.ID, "btn-go-back")))
        back_button.click()
        wait_loading_state(driver, 150)
    return True, all_cpes_data


def write_data(data, email_address):
    idx = [[], []]
    for c, v in data.items():
        for r, v2 in v.items():
            idx[0].append(c)
            idx[1].append(r)
    idx_t = list(zip(*idx))
    index = pd.MultiIndex.from_tuples(idx_t, names=['cpe', 'rows'])
    df = pd.DataFrame(index=index)
    for c in list(set(idx[0])):
        for r in list(set(idx[1])):
            try:
                c_r = data[c][r]
                for k, v in c_r.items():
                    df.loc[(c, r), k] = v
            except KeyError:
                continue
    print(df)
    today = datetime.datetime.now().strftime('%Y-%m-%d %Hh_%Mm')
    today_short = datetime.datetime.now().strftime('%Y-%m-%d')

    report_path = os.path.join(logs_dir, 'cpe_info_' + today + '.xlsx')

    df.to_excel(report_path)
    if len(df) > 30:
        df = df.iloc[:30, :]
        txt_e = '(apenas as 30 primeiras linhas)'
    else:
        txt_e = ''
    time.sleep(5)
    send_auto_email(
        receiver_email=email_address,
        title='Informações Disponiveis',
        text=f'Informação disponiveis no site da EDP reunidas com sucesso na data <b>{today}</b>{txt_e}:',
        df=df,
        conditions={'True': 'success-back', 'Ativo': 'success-back', 'row 1': 'warning-back'},
        file_path=report_path
    )

    # send_auto_email('franciscomacedo@lisboaenova.org',
    #                 f'Informações Disponiveis',
    #                 f'Informação disponiveis no site da EDP reunidas com sucesso na data\
    #                 <b>{today}</b>:', df)
    return


def login_edp(driver, wait, username, password_word):
    wait_loading_state(driver, 100)
    tipo_entidade = wait.until(ec.element_to_be_clickable((By.LINK_TEXT, "Empresarial")))
    tipo_entidade.click()
    user = wait.until(ec.presence_of_element_located((By.ID, "email")))
    user.clear()
    user.send_keys(username)
    password = wait.until(ec.presence_of_element_located((By.ID, "pwd")))
    password.clear()
    password.send_keys(password_word)

    login_button = wait.until(ec.element_to_be_clickable((By.XPATH, "//div[@class = 'card-body p-4 p-sm-5']//form"
                                                          "//div//button")))
    login_button.click()
    wait_loading_state(driver, 100)

    lista_button(driver)
    wait_loading_state(driver, 100)
    return


def print_loading_bar(i, all_i, f_logs):
    i = i+1
    item_pct = round((i/all_i)*100, 1)
    item_pct_int = int(item_pct)
    print_text_both('\n\n||' + '-'*item_pct_int + f'{item_pct}% ' +
                    ' '*(100-item_pct_int) + f'({i}/{all_i})', f_logs)


def reopen_driver(driver, username, password_word):
    try:
        driver.close()
        driver.quit()
    except:
        pass

    driver, action, wait, wait_long, wait_short = connect_driver()
    try:
        login_edp(driver, wait, username, password_word)
    except:
        time.sleep(5)
        driver, action, wait, wait_long, wait_short = connect_driver()
        login_edp(driver, wait, username, password_word)

    return driver, action, wait, wait_long, wait_short


def trigger_only_active(driver, wait, f_logs):
    wait_loading_state(driver, 100)
    print_text_both(f"\n\n-------TURNING ON ACTIVO-------\n\n", f_logs)
    try:
        wait.until(ec.element_to_be_clickable((By.ID, "edp-dropdown-state"))).click()

        wait.until(ec.presence_of_element_located((By.ID, "checkbox_Inativo"))).click()
        wait.until(ec.element_to_be_clickable((By.ID, "btn-filter"))).click()
        wait_loading_state(driver, 100)
    except Exception as e:
        print_text_both(f"\n\n-------!!FAILED!! TURNING ON ACTIVO-------: {e}\n\n", f_logs)


def trigger_no_BTN(driver, wait, f_logs):
    wait_loading_state(driver, 100)
    print_text_both(f"\n\n-------REMOVING BTN FROM LIST-------\n\n", f_logs)
    try:
        wait.until(ec.element_to_be_clickable((By.ID, "edp-dropdown-voltage-level"))).click()
        wait.until(ec.presence_of_element_located((By.ID, "checkbox_BTN"))).click()
        all_filters = wait.until(ec.presence_of_all_elements_located((By.ID, "btn-filter")))
        tt_filter = [a for a in all_filters if 'filtrar' in a.text.lower()][0]
        tt_filter.click()
    except Exception as e:
        print_text_both(f"\n\n-------!!FAILED!! REMOVING BTN FROM LIST-------: {e}\n\n", f_logs)
    wait_loading_state(driver, 100)


def get_info(gestao=None, cils_or_cpes=None, get_new=False, only_active=False, no_BTN=True, email_address='franciscomacedo@lisboaenova.org'):
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)

    f_logs = f"{logs_dir}/logs_{year}_{month}_{day}.txt"
    print_text_both(
        f"\n\n***RECOLHA DE INFORMAÇÃO***\n**DIA {day}-{month}-{now.year} ÀS {now.hour}H{now.minute}min**", f_logs)
    if get_new and cils_or_cpes:
        print_text_both('impossivel adequirir informação nova sobre cpes expecíficos. Tente uma gestão!', f_logs)
        return False

    if not get_new:
        cpes = get_cpes(gestao, cils_or_cpes, f_logs)

        if not cpes:
            print_text_both("done", f_logs)
            return False
        print_text_both(f'\n\nA tentar reunir informação para {len(cpes)} cpes......', f_logs)
        diff_gestao = df_db.loc[df_db.cpe.isin(cpes), 'gestao'].unique()
        diff_gestao = [g for g in diff_gestao if g is not None]
    else:
        cpes = []
        if gestao:
            diff_gestao = [gestao.upper()]
        else:
            print_text_both('Impossível reunir informação nova se não fornecer uma gestão...', f_logs)
            return False

    all_cpes_data = {}

    cpes_in_db = df_db.loc[df_db.cpe.isin(cpes)].cpe.tolist()
    cpes_NOT_in_db = [c for c in cpes if c not in cpes_in_db]
    diff_gestao_with_user = []
    for gestao_i in diff_gestao:
        # gestao_i = diff_gestao[2]
        if not gestao_i:
            continue
        usernames = df_db.loc[df_db.gestao == gestao_i, 'user'].unique()
        usernames_not_none = [u for u in usernames if u is not None]
        if not usernames_not_none:
            cpes_extra = df_db.loc[df_db.gestao == gestao_i, ].loc[df_db.cpe.isin(cpes)].cpe.tolist()
            if cpes_extra:
                cpes_NOT_in_db = cpes_NOT_in_db + cpes_extra
            continue
        else:
            diff_gestao_with_user.append(gestao_i)
    cpes_NOT_in_db = list(set(cpes_NOT_in_db))
    for gestao_i in diff_gestao_with_user:
        # gestao_i = diff_gestao_with_user[2]
        if not gestao_i:
            continue
        usernames = df_db.loc[df_db.gestao == gestao_i, 'user'].unique()
        usernames_not_none = [u for u in usernames if u is not None]

        for username in usernames_not_none:
            # username = usernames_not_none[0]
            df_user = df_db.loc[df_db.user == username, :]
            password_word = df_user.loc[:, 'password'].iloc[0]
            if not get_new:
                cpes_user = df_user.rename({'abastecimento': 'tt'}, axis=1).loc[df_user.cpe.isin(cpes)][[
                    'cpe', 'tt']].to_dict(orient='records')
                if not cpes_user:
                    print_text_both(f'username {username} sem cpes associados... a tentar o próximo username', f_logs)
                    continue
            else:
                cpes_user = []
            driver, action, wait, wait_long, wait_short = connect_driver()
            try:
                login_edp(driver, wait, username, password_word)
            except:
                time.sleep(5)
                driver, action, wait, wait_long, wait_short = connect_driver()
                login_edp(driver, wait, username, password_word)

            if only_active:
                trigger_only_active(driver, wait, f_logs)

            if no_BTN:
                trigger_no_BTN(driver, wait, f_logs)

            if get_new:

                if only_active:
                    print_text_both(
                        f"\n\n------------------ GOING FOR ALL CPES THAT ARE ACTIVE----------------------\n\n", f_logs)
                else:
                    print_text_both(
                        f"\n\n------------------ GOING FOR ALL CPES ----------------------\n\n", f_logs)

                cpes_user = []
                pg = 1
                try:
                    count_pg = wait.until(ec.presence_of_element_located((By.ID, "is-list"))).text
                    nr_pg = math.ceil(int(count_pg.split(' ')[-1])/int(count_pg.split(' ')[-3]))
                except:
                    nr_pg = None
                while True:
                    i = 0
                    wait_loading_state(driver, 100)
                    while True:
                        try:
                            possible_cpe = driver.find_element_by_id(f'btn-cpe-row-{i}').text
                            possible_tt = driver.find_element_by_id(f'voltage-row-{i}').text
                            if 'PT' in possible_cpe:
                                cpes_user.append({'cpe': possible_cpe, 'tt': possible_tt})
                        except NoSuchElementException:
                            break
                        i += 1
                    try:
                        next_page = driver.find_element_by_id('next-page')
                        if next_page.is_enabled():
                            pg += 1
                            print_text_both(f'trying page {pg}/{nr_pg if nr_pg else ""}', f_logs)
                            next_page.click()
                            wait_loading_state(driver, 100)
                        else:
                            break
                    except:
                        break

            print_text_both(f'trying to get basic info of {len(cpes_NOT_in_db)} cpes not in our db...', f_logs)
            for cpe in cpes_NOT_in_db:
                # cpe = cpes_NOT_in_db[0]

                try:
                    success_search = search_cpe(driver, cpe, wait, f_logs)
                    if not success_search:
                        lista_button(driver)
                        success_search = search_cpe(driver, cpe, wait, f_logs)
                except InvalidElementStateException:
                    print_text_both("-Not possible to search. trying to get from this page", f_logs)

                wait_loading_state(driver, 100)
                i = 0
                while True:
                    try:
                        possible_cpe = driver.find_element_by_id(f'btn-cpe-row-{i}').text
                        possible_tt = driver.find_element_by_id(f'voltage-row-{i}').text
                        if 'PT' in possible_cpe:
                            print_text_both(f'added {cpe} to info', f_logs)
                            cpes_user.append({'cpe': possible_cpe, 'tt': possible_tt})
                    except NoSuchElementException:
                        break
                    print(i)
                    i += 1
            # temporary save cpes gathered, in case of some sort of failure

            df_cpes_user = pd.DataFrame(cpes_user)
            df_cpes_user.drop_duplicates(subset='cpe', inplace=True)
            df_cpes_user.reset_index(drop=True, inplace=True)
            cpes_user_path = os.path.join(logs_dir, 'cpes_' + str_to_path(username) + '.csv')
            df_cpes_user.to_csv(cpes_user_path)
            print_text_both(f"\n------>ALL CPES GATHERED: {len(df_cpes_user)} cpes\n", f_logs)

            cpes_fail = []

            print_text_both(f"\n\n------------------ GOING FOR INFO OF EACH CPE ----------------------\n\n", f_logs)

            for i, row in df_cpes_user.iterrows():
                # cpe_tt = cpes_user[0]
                cpe = row.cpe
                tt = row.tt
                print_loading_bar(i, len(df_cpes_user), f_logs)
                print_text_both(f"Trying cpe {cpe}", f_logs)

                try:
                    res, all_cpes_data = info_cpe(cpe, driver, wait, f_logs, wait_short, all_cpes_data, tt)

                    if res:
                        print_text_both(f"SUCCESS!", f_logs)
                    else:
                        print_text_both(f"-!!Something went wrong. Trying Close and Reopen Driver...", f_logs)
                        try:
                            driver, action, wait, wait_long, wait_short = reopen_driver(driver, username, password_word)

                            if only_active:
                                trigger_only_active(driver, wait, f_logs)
                            if no_BTN:
                                trigger_no_BTN(driver, wait, f_logs)

                            res, all_cpes_data = info_cpe(cpe, driver, wait, f_logs,
                                                          wait_short, all_cpes_data, tt)
                            if res:
                                print_text_both(f"SUCCESS!", f_logs)
                            else:
                                print_text_both(
                                    f"\n\n---->>>>!!Something went wrong with {cpe}. Trying again later....\n\n", f_logs)
                                cpes_fail.append({'cpe': cpe, 'tt': tt})
                        except Exception as e:
                            print_text_both(f"-!!Something went wrong: {e}", f_logs)
                            print_text_both(
                                f"\n\n---->>>>!!Something went wrong with {cpe}. Trying again later....\n\n", f_logs)
                            cpes_fail.append({'cpe': cpe, 'tt': tt})

                except Exception as e:
                    print_text_both(f"-!!Something went wrong. Trying Close and Reopen Driver...: {e}", f_logs)
                    try:
                        driver, action, wait, wait_long, wait_short = reopen_driver(driver, username, password_word)

                        if only_active:
                            trigger_only_active(driver, wait, f_logs)
                        if no_BTN:
                            trigger_no_BTN(driver, wait, f_logs)

                        res, all_cpes_data = info_cpe(cpe, driver, wait, f_logs,
                                                      wait_short, all_cpes_data, tt)
                        if res:
                            print_text_both(f"SUCCESS!", f_logs)
                        else:
                            print_text_both(
                                f"\n\n---->>>>!!Something went wrong with {cpe}. Trying again later....\n\n", f_logs)
                            cpes_fail.append({'cpe': cpe, 'tt': tt})
                    except Exception as e:
                        print_text_both(f"-!!Something went wrong: {e}", f_logs)
                        print_text_both(
                            f"\n\n---->>>>!!Something went wrong with {cpe}. Trying again later....\n\n", f_logs)
                        cpes_fail.append({'cpe': cpe, 'tt': tt})

            if cpes_fail:
                driver, action, wait, wait_long, wait_short = reopen_driver(driver, username, password_word)
                if only_active:
                    trigger_only_active(driver, wait, f_logs)
                if no_BTN:
                    trigger_no_BTN(driver, wait, f_logs)

                cpes_fail_again = []
                print_text_both(f"Trying failed cpes: \n\n{space_l(cpes_fail)}", f_logs)

                for cpe_tt in cpes_fail:
                    cpe = cpe_tt['cpe']
                    print_text_both(f"Trying cpe {cpe}: number {cpes_fail.index(cpe_tt)+1}", f_logs)
                    try:
                        res, all_cpes_data = info_cpe(cpe, driver, wait, f_logs,
                                                      wait_short, all_cpes_data, cpe_tt['tt'])
                        if res:
                            print_text_both(f"SUCCESS!", f_logs)
                        else:
                            print_text_both(
                                f"\n\n---->>>>!!Something went wrong with {cpe}.  Quit trying!", f_logs)
                            cpes_fail_again.append(cpe_tt)
                    except Exception as e:
                        print_text_both(f"Something went wrong with {cpe}. Quit trying!: {e}", f_logs)
                        cpes_fail_again.append(cpe_tt)

                df_cpes_fail = pd.DataFrame(cpes_fail_again)
                cpes_fail_path = os.path.join(logs_dir, 'cpes_FAIL_' + str_to_path(username) + '.csv')
                df_cpes_fail.to_csv(cpes_fail_path)
            try:
                driver.close()
                driver.quit()
            except:
                pass

    write_data(all_cpes_data, email_address)
    try:
        driver.close()
        driver.quit()
    except:
        pass
    return True
