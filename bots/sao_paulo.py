import logging
import utils.selenium_utils as u
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait

def sao_paulo_bot():
    logging.info("Iniciando o bot de São Paulo...")

    try:
        logging.info("Operação do bot em andamento...")
        driver = u.getDriver("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

        logging.info("Aceitando cookies...")
        
        # u.cookie_accept(driver,"CLASS_NAME","cc__button__autorizacao--all")

        time.sleep(10)        
    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")

    logging.info("Bot de São Paulo concluído com sucesso.")