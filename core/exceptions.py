# Erros customizados (Ex: GuiaNaoEncontradaError)

import logging

class GuiaNaoEncontradaError(Exception):
    pass

try:
    # ...código que pode não encontrar a guia...
    raise GuiaNaoEncontradaError("Guia não encontrada no sistema")
except GuiaNaoEncontradaError as e:
    logging.error(str(e))

class GuiaJaExisteError(Exception):
    pass
