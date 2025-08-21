# Ponto de entrada: Inicia a automação

import logging
import os
import utils as u

from bots.sao_paulo import sao_paulo_bot

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/automation.log',
    filemode='a'
)

def main():
    logging.info("Iniciando a automação...")
    
    # TESTANDO COM SÃO PAULO
    sao_paulo_bot()
    

    logging.info("Automação concluída com sucesso.")

if __name__ == "__main__":
    main()
