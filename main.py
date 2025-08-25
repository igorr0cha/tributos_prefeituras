# main.py
import logging
import os
import sys
import threading

from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.interface_logs import Ui_MainWindow
from utils.qt_logging_handler import QtLogHandler
from bots.sao_paulo import sao_paulo_bot

# --- Configuração do Logging ---
if not os.path.exists("logs"):
    os.makedirs("logs")

# Formato do Log
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler para o arquivo
file_handler = logging.FileHandler('logs/automation.log', mode='a')
file_handler.setFormatter(log_formatter)

# Handler para a interface (Customizado)
qt_handler = QtLogHandler()
qt_handler.setFormatter(log_formatter)

# Configuração do logger principal
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,
        qt_handler
    ]
)

def run_automation():
    """Função que executa os bots."""
    logging.info("Iniciando a automação...")
    try:
        # Lote de processamento (coloque aqui quais bots serão executados)
        sao_paulo_bot()
        logging.info("Automação concluída com sucesso.")
    except Exception as e:
        logging.error(f"A automação foi encerrada devido a um erro: {e}")

def main():
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Conecta o sinal do handler ao método que atualiza a interface
    qt_handler.log_signal.connect(ui.append_log)

    # Inicia a automação em uma thread separada
    automation_thread = threading.Thread(target=run_automation)
    automation_thread.start()

    MainWindow.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()