import logging
import time
import pkgutil
import importlib
import bots

import utils.selenium_utils as u

def _load_bot_functions():
    """
    Função interna que descobre e carrega dinamicamente todas as funções de bot.
    Isso escaneia a pasta 'bots' e registra qualquer bot que siga a convenção.
    """
    bots_registry = {}
    logging.info("Carregando bots disponíveis...")
    for finder, modname, ispkg in pkgutil.iter_modules(bots.__path__, bots.__name__ + '.'):
        if not ispkg: 
            try:
                module = importlib.import_module(modname)
                bot_name = modname.split('.')[-1]
                function_name = f"{bot_name}_bot"

                if hasattr(module, function_name):
                    bot_function = getattr(module, function_name)
                    bots_registry[bot_name] = bot_function
                    logging.info(f"Bot '{bot_name}' descoberto e carregado.")
                else:
                    logging.warning(f"Módulo '{modname}' encontrado, mas a função principal '{function_name}' não foi encontrada dentro dele.")
            except Exception as e:
                logging.error(f"Falha ao carregar o módulo do bot: '{modname}'. Erro: {e}")
    return bots_registry

AVAILABLE_BOTS = _load_bot_functions()

def run_automation(bot_name):
    """
    Orquestra a execução de um bot específico, selecionando-o da lista de bots
    carregados dinamicamente.
    """
    logging.info(f"Orquestrador iniciando a execução do bot: '{bot_name}'")
    driver = None

    try:
        bot_to_run = AVAILABLE_BOTS.get(bot_name)

        if bot_to_run:
            logging.info("Criando o driver do navegador...")
            driver = u.getDriver(url="about:blank")

            logging.info(f"Executando a função principal do bot '{bot_name}'...")
            bot_to_run(driver)
            logging.info(f"Bot '{bot_name}' finalizado com sucesso.")
        else:
            logging.error(f"Bot '{bot_name}' não reconhecido pelo orquestrador.")
            logging.info(f"Bots disponíveis: {list(AVAILABLE_BOTS.keys())}")
            raise ValueError(f"Bot '{bot_name}' não foi encontrado ou não segue a convenção de nomenclatura.")

    except Exception as e:
        logging.critical(f"Uma falha crítica ocorreu durante a execução do bot '{bot_name}': {e}")
    
    finally:
        if driver:
            logging.info("Orquestrador finalizando o driver do navegador.")
            u.quit_driver(driver)