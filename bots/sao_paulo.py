import logging
import utils.selenium_utils as u
from selenium.webdriver.common.by import By
import time

navegador = u.getDriver("itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

def sao_paulo_bot():
    logging.info("Iniciando o bot de São Paulo...")

    try:
        logging.info("Operação do bot em andamento...")



        navegador.find_element(By.CLASS_NAME, "cc__button__autorizacao--all").click()
        time.sleep(10)
        # u.click_button("//*[@id=\"modalPanelAtencao\"]/div[2]/div/div[2]/div/div/input[1]", navegador, timeout=10)

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")

    logging.info("Bot de São Paulo concluído com sucesso.")