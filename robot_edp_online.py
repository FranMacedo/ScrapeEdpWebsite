from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
from my_functions import *
import time
import datetime
import pandas as pd
import ctypes
import pandas.io.formats.excel
import shutil
# from django.conf import settings
# download_dir = os.path.join(settings.STATICFILES_DIRS[0], 'assets/downloads')
curent_dir = os.getcwd()
download_dir = os.path.join(curent_dir, 'downloads')
logs_dir = os.path.join(download_dir, 'logs')
downloads_path = os.path.join(download_dir, 'files')

# if dirs don't exist yet
if not os.isdir(download_dir):
    os.mkdir(download_dir)

if not os.isdir(logs_dir):
    os.mkdir(logs_dir)

if not os.isdir(downloads_path):
    os.mkdir(downloads_path)
    
destination_path = "Z:\\DATABASE\\ENERGIA\\DATAFILES"


def connect_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")

    prefs = {"download.default_directory": downloads_path}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome("chromedriver/chromedriver.exe", options=chrome_options)
    driver.get("https://online.edpdistribuicao.pt/pt/Pages/Home.aspx")  # Inicio do website pretendido no webdriver
    action = ActionChains(driver)

    global wait
    global wait_long

    wait = WebDriverWait(driver, 30)
    wait_long = WebDriverWait(driver, 100)

    return driver, action, wait, wait_long


def print_text_both(texto, file_name):
    print(texto)
    # today = datetime.date.today()
    # file_name = f"{logs_dir}\\registo_{today}.txt"
    try:
        registo = open(file_name, 'a')
        texto_escrever = ['\n'] + [texto]

    except FileNotFoundError:
        registo = open(file_name, "w+")
        texto_escrever = texto

    registo.writelines(texto_escrever)
    registo.close()


def empty_download_dir():
  files = os.listdir(downloads_path)
  for f in files:
    os.remove(os.path.join(downloads_path, f))


def scroll_to_element(driver, element):
    desired_y = (element.size['height'] / 2) + element.location['y']
    window_h = driver.execute_script('return window.innerHeight')
    window_y = driver.execute_script('return window.pageYOffset')
    current_y = (window_h / 2) + window_y
    scroll_y_by = desired_y - current_y

    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
    return


def wait_loading_state(driver, time):
    WebDriverWait(driver, time).until(
        ec.invisibility_of_element_located((By.CSS_SELECTOR, "div[class='backdrop full-screen']")))
    return


def search_cpe(driver, cpe, wait, f_logs):
    success_search = True
    wait_loading_state(driver, 100)

    try:
        search_text_box = wait.until(ec.presence_of_element_located((By.ID, "srch-term")))
        scroll_to_element(driver, search_text_box)
        search_text_box.clear()
        search_text_box.send_keys(str(cpe))
    except TimeoutException:
        print_text_both("Search Box not available or took too long o load...", f_logs)

        success_search = False

    try:
        wait_loading_state(driver, 100)
    except TimeoutException:
        print_text_both("Took too long to load...", f_logs)

        success_search = False

    try:
        search_button = wait.until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="btn-srch-term"]')))
        search_button.click()
    except TimeoutException:
        print_text_both("Took too long to find search button...", f_logs)

        success_search = False

    return success_search


def check_exists_by_css_selector(webdriver, css_selector):
    time.sleep(3)
    try:
        webdriver.find_element_by_css_selector(css_selector)
    except NoSuchElementException:
        return False
    return True


def list_button(driver):
    action = ActionChains(driver)

    # FM - Acrescentei esta função, visto que a EDP criou um novo popup ("cartão") que surge as vezes
    # Esta função verifica se existe e click no botão certo
    try:
        if check_exists_by_css_selector(driver, '#card-n-0'):

            if check_exists_by_css_selector(driver, '#btn_list'):

                list_button_1 = WebDriverWait(driver, 100).until(ec.element_to_be_clickable((By.ID, "btn_list")))

                try:
                    action.move_to_element(list_button_1).click().perform()

                except TimeoutException:
                    time.sleep(5)
                    action.move_to_element(list_button_1).click().perform()

            elif check_exists_by_css_selector(driver, '#btn-see-all'):

                list_button_2 = WebDriverWait(driver, 100).until(ec.element_to_be_clickable((By.ID, "btn-see-all")))

                try:
                    action.move_to_element(list_button_2).click().perform()
                except TimeoutException:
                    time.sleep(5)
                    action.move_to_element(list_button_2).click().perform()
                return
        else:
            return
    except TimeoutException:
        time.sleep(10)
        if check_exists_by_css_selector(driver, '#card-n-0'):

            if check_exists_by_css_selector(driver, '#btn_list'):

                list_button_1 = WebDriverWait(driver, 100).until(ec.element_to_be_clickable((By.ID, "btn_list")))

                action.move_to_element(list_button_1).click().perform()

            elif check_exists_by_css_selector(driver, '#btn-see-all'):

                list_button_2 = WebDriverWait(driver, 100).until(ec.element_to_be_clickable((By.ID, "btn-see-all")))

                action.move_to_element(list_button_2).click().perform()

                return
        else:
            return

    return


def lista_button(driver):
    try:
        lista = driver.find_element_by_id('btn_list')
            # wait.until(ec.presence_of_element_located((By.ID, "btn_list")))
        lista.click()
    except NoSuchElementException:
        try:
            lista = driver.find_element_by_css_selector('#btn-see-all')

            # lista = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#btn-see-all")))
            lista.click()
        except NoSuchElementException:
            pass
    return


def test_book(filename):
    if 'tmp' in filename or 'crdownload' in filename:
        return False
    else:
        return True


def download_click(driver, downloads_path, f_logs):
    wait_loading_state(driver, 100)
    
    download_button = wait.until(
        ec.element_to_be_clickable((By.ID, "btn-export-to-excel")))
    len_dir_before = len(get_files_from_rede(downloads_path, f_logs))
    files_before = get_files_from_rede(downloads_path, f_logs)

    download_button.click()
    wait_loading_state(driver, 150)
    # time.sleep(10)

    time_to_wait = 10
    time_counter = 0

    len_dir_after = len(get_files_from_rede(downloads_path, f_logs))

    while not len_dir_after > len_dir_before:
        time.sleep(1)
        len_dir_after = len(get_files_from_rede(downloads_path, f_logs))
        time_counter += 1
        if time_counter > time_to_wait: break

    if len_dir_after > len_dir_before:
        files_new = get_files_from_rede(downloads_path, f_logs)
        new_file = [f for f in files_new if f not in files_before][0]
        is_excel = test_book(downloads_path + '\\' + new_file)

        while not is_excel:
            time.sleep(1)

            files_new = get_files_from_rede(downloads_path, f_logs)
            new_file = [f for f in files_new if f not in files_before][0]
            is_excel = test_book(downloads_path + '\\' + new_file)

            time_counter += 1
            if time_counter > time_to_wait: break

        files_new = get_files_from_rede(downloads_path, f_logs)
        new_file = [f for f in files_new if f not in files_before][0]
        is_excel = test_book(downloads_path + '\\' + new_file)

        if is_excel:
            print_text_both("   Success", f_logs)

            return True

        else:
            print_text_both("    Didn't download file. Trying again...", f_logs)
            os.remove(downloads_path + '/' + new_file)
            return False


def multi_attempt_download_click(driver, downloads_path, f_logs):
    wait_loading_state(driver, 100)

    print_text_both("---First attempt to click download button", f_logs)

    try:
        success = download_click(driver, downloads_path, f_logs)
        if success:
            return True
    except (ElementClickInterceptedException, TimeoutException):
        print_text_both("----First attempt failed", f_logs)
        print_text_both("---Second attempt to click download button", f_logs)

    try:
        success = download_click(driver, downloads_path, f_logs)
        if success:
            return True
    except (ElementClickInterceptedException, TimeoutException):
        print_text_both("----Second attempt failed", f_logs)
        print_text_both("---Third attempt to click download button", f_logs)
    try:
        success = download_click(driver, downloads_path, f_logs)
        if success:
            return True
    except (ElementClickInterceptedException, TimeoutException):
        print_text_both("----Third attempt failed", f_logs)
        print_text_both("---Fourth attempt to click download button", f_logs)
    try:
        success = download_click(driver, downloads_path, f_logs)
        if success:
            return True
    except (ElementClickInterceptedException, TimeoutException):
        print_text_both("----Fourth attempt failed", f_logs)
        print_text_both("---Fifth attempt to click download button", f_logs)
    try:
        success = download_click(driver, downloads_path, f_logs)
        if success:
            return True
    except (ElementClickInterceptedException, TimeoutException):
        print_text_both("----Fifth attempt failed", f_logs)
        print_text_both("---Sixth attempt to click download button", f_logs)
    try:
        success = download_click(driver, downloads_path, f_logs)
        if success:
            return True
    except (ElementClickInterceptedException, TimeoutException):
        print_text_both("----Sixth attempt failed - No more attempts, skipping month", f_logs)

        return False


def select_date(driver, download_yearmons, downloads_path, f_logs):

    wait_loading_state(driver, 50)
    result = True

    years_drop_down = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "div.select-wrapper")))

    year_options =years_drop_down.find_elements_by_tag_name("option")
    year_options_values = [x.get_attribute("value") for x in year_options]

    download_years = list(set([ym[:4] for ym in download_yearmons]))

    download_years_available = [d for d in download_years if d in year_options_values]
    download_years_not_available = [d for d in download_years if d not in year_options_values]

    for a in download_years_not_available:
        print_text_both("---No data for {0} in this row.".format(a), f_logs)


    download_yearmons_avai = [ym for ym in download_yearmons if ym[:4] in download_years_available]
    downloaded_yearmons = []

    if not download_yearmons_avai:
        return False, downloaded_yearmons

    for d_ym in download_yearmons_avai:
        # d_ym = download_yearmons_avai[0]
        d_y = d_ym[:4]   # download year
        d_m = d_ym[-2:]  # download month
        i = int(d_m)          # download month integer
        m_abv = num_mes_abv(d_m)
        click_year = year_options[year_options_values.index(d_y)]
        try:
            click_year.click()
        except TimeoutException:
            print_text_both("---Took too long to load...", f_logs)

            continue

        wait_loading_state(driver, 150)
        # Este módulo serve para clicar no mês do dropdown list:


        # months_drop_down = driver.find_element_by_css_selector("div[class='w-80 mx-auto mb-3 export-month-area']")

        months_table = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "button[class='edp-btn btn-line btn-red w-100 px-1']")))
        month_sel = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[class='edp-btn btn-line btn-red w-100 px-1 selected']")))

        print_text_both("\n--Trying month {0}-{1}...".format(i, int(d_y)), f_logs)

        month_button = [m for m in months_table if m.text == m_abv]

        if not month_button:
            # então é o que está selecionado, vamos confirmar:
            if month_sel.text == m_abv:
                pass
            else:
                print_text_both("---Month {0}-{1} not available: skipping {2}...".format(i, int(d_y), month_button[0].text), f_logs)

        else:

            if not month_button[0].is_enabled():
                print_text_both("---Month {0}-{1} not available: skipping {2}...".format(i, int(d_y), month_button[0].text), f_logs)

                continue
            else:
                month_button[0].click()

        wait_loading_state(driver, 150)
        print_text_both("---Month {0}-{1} available: Downloading {2}...".format(i, int(d_y), m_abv), f_logs)


        # Este módulo lança a rotina que tenta fazer download do ficheiro de dados 6 vezes até haver sucesso:
        try:
            result = multi_attempt_download_click(driver, downloads_path, f_logs)

            try:
                wait_loading_state(driver, 150)

            except TimeoutException:
                print_text_both("---Took too long to load...", f_logs)
                continue

            if result:
                downloaded_yearmons.append(d_ym)

        except TimeoutException:
            print_text_both("---Took too long to load...skipping", f_logs)
            continue

    return result, downloaded_yearmons

def read_excel_edp(file, is_head=False):
    try:
        df = pd.read_excel(file, names=None, header=None)
    except PermissionError:
        time.sleep(4)
        df = pd.read_excel(file, names=None, header=None)
    df_head = df.iloc[:9, ]
    df = df.iloc[9:, ]
    df.columns = df.iloc[0, :].tolist()
    df = df.drop(df.index[0], axis=0)
    if is_head:
        return df, df_head
    else:
        return df


def organize_excel_files(inst, f_logs, ym, substituir):
  cil = inst["cil"]
  tt = inst["abastecimento"]
  cil = inst["cil"]
  tt = inst["abastecimento"]
  dwnld_files = os.listdir(downloads_path)
  dates_with_files = []
  new_files_added = []
  files_replaced = []
  files_extended = []
  
  if not dwnld_files:
    return ym, new_files_added, files_replaced, files_extended

  print_text_both(f"\n -----{cil} - ORGANIZE EXCEL FILES IN REDE", f_logs)

  for file in dwnld_files:
      # file = dwnld_files[0]
      file_path = os.path.join(downloads_path, file)
      xl_file = pd.read_excel(file_path)
      try:
          date = xl_file["Dados Globais"][9]
          split = date.split("/")
          date = split[0] + split[1]
      except KeyError:
          os.remove(file_path)
          print_text_both(f"Ficheiro {file} sem dados - removido", f_logs)
          continue

      dates_with_files.append(date)
      df = pd.read_excel(file_path, skiprows=9)
      df.columns = ["Data", "Hora", "Potência Ativa", "Potência Reativa Indutiva", "Potência Reativa Capacitiva"]

      future_file_name = f"{cil}_{date}.xlsx"
      future_file_path = os.path.join(destination_path, tt, str(cil), future_file_name)

      if not os.path.isdir(os.path.join(destination_path, tt)):
        os.mkdir(os.path.join(destination_path, test_book))
      if not os.path.isdir(os.path.join(destination_path, tt, str(cil))):
        os.mkdir(os.path.join(destination_path, tt, cil))
      if not os.path.exists(future_file_path):
        new_files_added.append(date)
        shutil.move(file_path, future_file_path)
        print(f"'{cil}_{date}.xlsx' created")
        continue
      
      df_exist, df_head = read_excel_edp(future_file_path, True)
      df_download = read_excel_edp(file_path, False)

      df_exist['data_hora'] = df_exist['Data'] + ' ' + df_exist['Hora']
      df_exist = df_exist.drop_duplicates(subset='data_hora', keep='last')

      df_download['data_hora'] = df_download['Data'] + ' ' + df_download['Hora']
      df_download = df_download.drop_duplicates(subset='data_hora', keep='last')

      dates_exist = [d for d in df_download['data_hora'].tolist() if d in df_exist['data_hora'].tolist()]
      if substituir:
          df_exist = df_exist.loc[~df_exist.data_hora.isin(dates_exist), :]
          df_new = df_exist.append(df_download)
          df_new = df_new.drop_duplicates(subset='data_hora', keep='last')
          df_new = df_new.sort_values(by='data_hora')
          files_replaced.append(date)
          print(f"'{cil}_{date}.xlsx' replaced")

      else:
          df_download = df_download.loc[~df_download.data_hora.isin(dates_exist), :]
          df_new = df_exist.append(df_download)
          df_new = df_new.drop_duplicates(subset='data_hora', keep='last')
          df_new = df_new.sort_values(by='data_hora')
          files_extended.append(date)

          print(f"'{cil}_{date}.xlsx' extended")

      df_new.drop('data_hora', axis=1, inplace=True)
      col_names = df_new.columns.tolist()
      temp_names = [1, 2, 3, 4, 5]
      df_new.columns = temp_names
      df_head.columns = temp_names
      df_col = pd.Series(col_names, index=temp_names)
      df_n = df_head.append(df_col, ignore_index=True)
      df_new = df_n.append(df_new)
      df_new.to_excel(future_file_path, index=False, header=False)

      os.remove(file_path)


  empty_dates = [d for d in ym if d not in dates_with_files]
  return empty_dates, new_files_added, files_replaced, files_extended


def get_files_from_rede(folder, f_logs):
    try:
        files = os.listdir(folder)
    except (FileNotFoundError, PermissionError, OSError):
        time.sleep(2)
        try:
            files = os.listdir(folder)
        except (FileNotFoundError, PermissionError, OSError):
            time.sleep(5)
            try:
                files = os.listdir(folder)
            except (FileNotFoundError, PermissionError, OSError):
                time.sleep(10)
                try:
                    files = os.listdir(folder)
                except (FileNotFoundError, PermissionError, OSError):
                    time.sleep(20)
                    try:
                        files = os.listdir(folder)
                    except (FileNotFoundError, PermissionError, OSError):
                        print_text_both("Dificil de ligar à rede... espera 5 minutos", f_logs)

                        time.sleep(300)
                        try:
                            files = os.listdir(folder)
                        except (FileNotFoundError, PermissionError, OSError):
                            return None
    return files


def robot(inst, ym, substituir):
  
  downloaded_yearmons = []
  not_downloaded_yearmons = ym

  report = {'new file added': downloaded_yearmons,
            'download fail': not_downloaded_yearmons,
            'file replaced': [],
            'file extended': []
            }
                
  empty_download_dir()
  now = datetime.datetime.now()
  year = str(now.year)
  month = str(now.month).zfill(2)
  day = str(now.day).zfill(2)
  hour = str(now.hour).zfill(2)
  minute = str(now.minute).zfill(2)

  cil = inst['cil']
  cpe = inst['cpe']
  password_word = inst['password']
  username = inst['user']

  

  # cil=3874085
  # cpe = "PT0002000038740856ZG"
  # tt = 'BTE'
  # date_begin = dt(2020,4,1)
  # date_end = dt(2020,4,29)


  f_logs = f"{logs_dir}/logs_{year}_{month}_{day}.txt"
  print_text_both(f"***DOWNLOAD DE FICHEIROS***\n\n\n**DIA {day}-{month}-{now.year} ÀS {now.hour}H{now.minute}min**", f_logs)
  if not username or not password_word:
      print_text_both(f"{cil} sem credenciais para o site da EDP...", f_logs)
      return report

  driver, action, wait, wait_long = connect_driver()

  print_text_both("\nProcessing CIL: {0} | CPE: {1}".format(cil, cpe), f_logs)

  # Se for para substituir ficheiros existentes, continua. Caso contrário, reduz a lista dos ficheiros a sacar
  # Neste momento, compara só os ficheiros mensais, em vez de comparar 15 em 15 minutos. Mas como os ficheiros
  # da edp vêm de mes a mes, torna-se irrelevante.

  wait_loading_state(driver, 100)


  # Procedimento de carregar no tipo de entidade: "Empresarial"
  tipo_entidade = wait.until(ec.element_to_be_clickable((By.LINK_TEXT, "Empresarial")))
  tipo_entidade.click()

  user = wait.until(ec.presence_of_element_located((By.ID, "email")))
  user.clear()
  user.send_keys(username)
  password = wait.until(ec.presence_of_element_located((By.ID, "pwd")))
  password.clear()
  password.send_keys(password_word)

  # Carrega no botao entrar para submeter o login
  login_button = wait.until(ec.element_to_be_clickable((By.XPATH, "//div[@class = 'card-body p-4 p-sm-5']//form"
                                                                  "//div//button")))
  login_button.click()

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

      driver.close()
      return report

  print_text_both("-{} list result(s) found for that CPE".format(len(rows_begin)), f_logs)

  for row in rows_begin:
      # row = rows_begin[0]
      index_row = rows_begin.index(row)
      print_text_both(f"\n\n-Trying row {index_row + 1}", f_logs)

      wait_loading_state(driver, 100)

      lista_button(driver)
      success_search = search_cpe(driver, cpe, wait, f_logs)
      if not success_search:
          lista_button(driver)
          success_search = search_cpe(driver, cpe, wait, f_logs)
          
          if not success_search:
              print_text_both("--nao é possivel procurar", f_logs)
              driver.close()
              # report['download success'] = downloaded_yearmons
              # report['download fail'] = not_downloaded_yearmons
              return report
      try:
          rows = wait.until(ec.presence_of_all_elements_located((By.LINK_TEXT, cpe)))
          row = rows[index_row]

      except (TimeoutException, IndexError):
          print_text_both("--No results found for this CPE. Trying next CPE...", f_logs)

          # report['download success'] = downloaded_yearmons
          # report['download fail'] = not_downloaded_yearmons
          driver.close()
          return report

      wait_loading_state(driver, 100)
      try:
          scroll_to_element(driver, row)

      except StaleElementReferenceException:
          lista_button(driver)
          success_search = search_cpe(driver, cpe, wait, f_logs)
          if not success_search:
              print_text_both("--nao é possivel procurar", f_logs)
              driver.close()
              # report['download success'] = downloaded_yearmons
              # report['download fail'] = not_downloaded_yearmons
              return report

          try:
              rows = wait.until(ec.presence_of_all_elements_located((By.LINK_TEXT, cpe)))
              row = rows[index_row]
          except (TimeoutException, IndexError):
              print_text_both("--No results found for this CPE. Trying next CPE...", f_logs)

              # report['download success'] = downloaded_yearmons
              # report['download fail'] = not_downloaded_yearmons
              driver.close()
              return report

      row.click()

      wait_loading_state(driver, 100)
      try:
          consumos_tab = wait.until(ec.element_to_be_clickable((By.LINK_TEXT, "Consumos")))
      except TimeoutException:
          print_text_both("--nao é possivel procurar", f_logs)
          print_text_both("   Consumos tab not found...", f_logs)


          wait_loading_state(driver, 50)

          back_button = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#btn-go-back")))
          back_button.click()

          wait_loading_state(driver, 50)
          lista_button(driver)
          continue

      scroll_to_element(driver, consumos_tab)

      try:
          consumos_tab.click()
      except:
          driver.execute_script("arguments[0].click();", consumos_tab)

      wait_loading_state(driver, 150)

      result, downloaded_yearmons_list = select_date(driver, ym, downloads_path, f_logs)

      wait_loading_state(driver, 150)
      downloaded_yearmons = downloaded_yearmons + downloaded_yearmons_list
      not_downloaded_yearmons = [d for d in not_downloaded_yearmons if d not in downloaded_yearmons]

      back_button = wait.until(ec.element_to_be_clickable((By.ID, "btn-go-back")))
      back_button.click()
      wait_loading_state(driver, 150)

  driver.close()
  empty_dates, new_files_added, files_replaced, files_extended = organize_excel_files(inst, f_logs, ym, substituir)
  downloaded_yearmons = [d for d in downloaded_yearmons if d not in empty_dates]
  not_downloaded_yearmons = [d for d in ym if d not in downloaded_yearmons]

  report['new file added'] = new_files_added
  report['download fail'] = not_downloaded_yearmons
  report['file replaced'] = files_replaced
  report['file extended'] = files_extended

  return report
