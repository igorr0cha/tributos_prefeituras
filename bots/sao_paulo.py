import logging
import utils.selenium_utils as u
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ui.interface_logs import Ui_MainWindow

# DESABILITA ACELERAÇÃO POR GPU -------------
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-webgl")
# FIM --------------------------------------

def verifica_cookie(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cc__button__autorizacao--all"))
        )
        logging.info("Cookie encontrado.")
        return True
    except TimeoutException:
        logging.warning("Cookie não encontrado.")
        return False

def sao_paulo_bot():

    logging.info("Iniciando o bot de São Paulo...")
    driver = None  # Defina antes do try

    try:
        logging.info("Operação do bot em andamento...")

        driver = u.getDriver("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

        logging.info("Aceitando cookies...")

        # u.cookie_accept(driver,"CLASS_NAME","cc__button__autorizacao--all")

        time.sleep(10) 
    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")

    finally:
        # Garante que o driver seja fechado mesmo se ocorrer um erro
        if driver:
            driver.quit()