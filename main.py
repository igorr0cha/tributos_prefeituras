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