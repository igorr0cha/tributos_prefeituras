import logging

import utils.selenium_utils as u


def sao_paulo_bot():
    logging.info("Iniciando o bot de São Paulo...")
    
    try:
        # Simulação de operação do bot'
        logging.info("Operação do bot em andamento...")

        u.find_chrome_path()
        u.find_chromedriver_path()
        navegador = u.getDriver("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")

    logging.info("Bot de São Paulo concluído com sucesso.")
