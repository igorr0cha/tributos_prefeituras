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


def sao_paulo_bot():

    logging.info("Iniciando o bot de São Paulo...")
    driver = None  # Defina antes do try

    try:
        logging.info("Operação do bot em andamento...")

        driver = u.getDriver("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

        logging.info("Aceitando cookies...")

        u.cookie_accept(driver,"CLASS_NAME","cc__button__autorizacao--all")

        logging.info("scrollando ate input de cadastro")
        u.scroll_to_element("//*[@id='pnlTela1']/div/fieldset[1]/div/div[2]/input", driver)
        
        xpath_cadastro = "//input[@aria-labelledby='lblCadastroImovel']"
        driver.find_element(By.XPATH, xpath_cadastro).click()

        u.fill_input(driver.find_element(By.XPATH, xpath_cadastro), "Texto de exemplo 123", driver)
        time.sleep(10)

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")

    finally:
        # Garante que o driver seja fechado mesmo se ocorrer um erro
        if driver:
            driver.quit()


            