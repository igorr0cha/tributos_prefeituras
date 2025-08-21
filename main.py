# Ponto de entrada: Inicia a automação

import logging
import os

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
    
    

    logging.info("Automação concluída com sucesso.")

if __name__ == "__main__":
    main()
# end main