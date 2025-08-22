# main.py
import logging
import os
from core.orchestrator import run_automation # <-- MUDANÇA: Importamos o orquestrador

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
    
    try:
        #Lote de procesamento (COLOCAR AQUI QUAIS BOTS SERÃO EXECUTADOS)
        run_automation("sao_paulo")

        logging.info("Automação concluída com sucesso.")

    except Exception as e:
        logging.error(f"A automação foi encerrada devido a um erro: {e}")

if __name__ == "__main__":
    main()