import logging
import utils.selenium_utils as u

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

servico = ChromeService(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)

def sao_paulo_bot():
    logging.info("Iniciando o bot de São Paulo...")

    try:
        logging.info("Operação do bot em andamento...")

        navegador.get("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

        u.click_button("//*[@id='modalPanelAtencao']/div[2]/div/div[2]/div/div/input[1]", navegador, timeout=10)

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")

    logging.info("Bot de São Paulo concluído com sucesso.")