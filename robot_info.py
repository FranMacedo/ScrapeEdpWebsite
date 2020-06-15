from robot_edp_online import *
from my_functions import find_between_r
from run_robot import df_db, create_download_log
import os
from glob import glob

# cml_cils = df_db.loc[df_db.gestao=='CML','cil'].tolist()
# # print(cml_cpes)

# files_db = glob(os.path.join(r"Z:\DATABASE\ENERGIA\DATAFILES", '*/**'))
# cils_db = [find_between_r(c, '\\', '') for c in files_db]

# cml_cils_db = [c for c in cils_db if int(c) in cml_cils]
# cml_files_db = [f for f in files_db if find_between_r(f, '\\', '') in cml_cils_db]
# print(cml_files_db)
# print(len(cml_files_db))
# cils_months = {}
# for cil_path in cml_files_db:
#     cils_months[find_between_r(cil_path, '\\', '')] = os.listdir(cil_path)

# print(cils_months)


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

    return cpes


def info_cpe(cpe, driver, wait, f_logs, wait_short, all_cpes_data, tt):

    cpe_data = {}
    lista_button(driver)
    success_search = search_cpe(driver, cpe, wait, f_logs)

    if not success_search:
        lista_button(driver)
        success_search = search_cpe(driver, cpe, wait, f_logs)

    wait_loading_state(driver, 100)

    try:
        rows_begin = wait.until(ec.presence_of_all_elements_located((By.LINK_TEXT, cpe)))
    except TimeoutException:
        print_text_both("-No results found. Trying next CPE...", f_logs)
        return all_cpes_data

    print_text_both("-{} list result(s) found for that CPE".format(len(rows_begin)), f_logs)
    for row in rows_begin:
        # row = rows_begin[0]
        index_row = rows_begin.index(row)
        print_text_both(f"--Trying row {index_row + 1}", f_logs)

        wait_loading_state(driver, 100)

        is_lista = lista_button(driver)
        if is_lista:
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
    return all_cpes_data


def write_data(data):
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
    report_path = os.path.join(logs_dir, 'cpe_info_' + today + '.csv')
    df.to_csv(report_path)


def get_info(gestao=None, cils_or_cpes=None, get_new=False, only_active=False):
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)

    f_logs = f"{logs_dir}/logs_{year}_{month}_{day}.txt"
    print_text_both(
        f"***RECOLHA DE INFORMAÇÃO***\n\n\n**DIA {day}-{month}-{now.year} ÀS {now.hour}H{now.minute}min**", f_logs)
    if get_new and cils_or_cpes:
        print_text_both('impossivel adequirir informação nova sobre cpes expecíficos. Tente uma gestão!', f_logs)
        return

    if not get_new:
        cpes = get_cpes(gestao, cils_or_cpes, f_logs)
        if not cpes:
            print_text_both("done", f_logs)
            return
        print_text_both(f'\n\nA tentar reunir informação para os cpes: {space_l(cpes)}......', f_logs)
        diff_gestao = df_db.loc[df_db.cpe.isin(cpes), 'gestao'].unique()
    else:
        cpes = []
        if gestao:
            diff_gestao = [gestao.upper()]
        else:
            print_text_both('Impossível reunir informação nova se não fornecer uma gestão...', f_logs)
            return

    all_cpes_data = {}

    for gestao_i in diff_gestao:
        usernames = df_db.loc[df_db.gestao == gestao_i.upper(), 'user'].unique()
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
            wait_loading_state(driver, 100)
            # driver.close()
            # driver.quit()
            # return
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
            if only_active:
                print_text_both(f"\n\n-------TURNING ON ACTIVO-------\n\n", f_logs)
                wait.until(ec.element_to_be_clickable((By.ID, "edp-dropdown-state"))).click()
                wait.until(ec.presence_of_element_located((By.ID, "checkbox_Inativo"))).click()
                wait.until(ec.element_to_be_clickable((By.ID, "btn-filter"))).click()
                wait_loading_state(driver, 100)

            if get_new:

                if only_active:
                    print_text_both(
                        f"\n\n------------------ GOING FOR ALL CPES THAT ARE ACTIVE----------------------\n\n", f_logs)
                else:
                    print_text_both(
                        f"\n\n------------------ GOING FOR ALL CPES ----------------------\n\n", f_logs)

                cpes_user = []
                pg = 1

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
                            print_text_both(f'trying page {pg}..', f_logs)
                            next_page.click()
                            wait_loading_state(driver, 100)
                        else:
                            break
                    except:
                        break
                # temporary save cpes gathered, in case of some sort of failure
                df_cpes_user = pd.DataFrame(cpes_user)
                cpes_user_path = os.path.join(logs_dir, 'cpes_' + str_to_path(username) + '.csv')
                df_cpes_user.to_csv(cpes_user_path)
                print_text_both(f"\n------>ALL CPES GATHERED: {len(cpes_user)} cpes\n", f_logs)

            cpes_fail = []

            print_text_both(f"\n\n------------------ GOING FOR INFO OF EACH CPE ----------------------\n\n", f_logs)
            cpes_user
            total_nr = len(cpes_user)
            for cpe_tt in cpes_user[:4]:
                cpe = cpe_tt['cpe']
                cpe_nr = cpes_user.index(cpe_tt)+1
                print_text_both('\n\n||' + '-'*cpe_nr + f'{round((cpe_nr/total_nr)*100, 1)}% ' +
                                ' '*(total_nr-cpe_nr) + f'({cpe_nr}/{total_nr})', f_logs)
                print_text_both(f"Trying cpe {cpe}", f_logs)

                try:
                    all_cpes_data = info_cpe(cpe, driver, wait, f_logs, wait_short, all_cpes_data, cpe_tt['tt'])
                    # all_cpes_data['tt'] = cpe_tt['tt']
                except:
                    print_text_both(f"-!!Something went wrong with {cpe}. Trying again later....", f_logs)
                    cpes_fail.append(cpe_tt)

                print_text_both(f"SUCCESS!", f_logs)

            if cpes_fail:
                driver.close()
                driver.quit()
                driver, action, wait, wait_long, wait_short = connect_driver()

                cpes_fail_again = []
                print_text_both(f"Trying failed cpes: \n\n{space_l(cpes_fail)}", f_logs)

                for cpe_tt in cpes_fail:
                    cpe = cpe_tt['cpe']
                    print_text_both(f"Trying cpe {cpe}: number {cpes_fail.index(cpe_tt)+1}", f_logs)
                    try:
                        all_cpes_data = info_cpe(cpe, driver, wait, f_logs, wait_short, all_cpes_data, cpe_tt['tt'])
                    except:
                        print_text_both(f"Something went wrong with {cpe}. Quit trying!", f_logs)
                        cpes_fail_again.append(cpe_tt)

                df_cpes_fail = pd.DataFrame(cpes_fail_again)
                cpes_fail_path = os.path.join(logs_dir, 'cpes_FAIL_' + str_to_path(username) + '.csv')
                df_cpes_fail.to_csv(cpes_fail_path)
            try:
                driver.close()
                driver.quit()
            except:
                pass
    write_data(all_cpes_data)
    try:
        driver.close()
        driver.quit()
    except:
        pass
    return
