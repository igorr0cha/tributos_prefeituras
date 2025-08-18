# Um "contrato" (classe base) que todo bot deve seguir

class BaseBot:
    def process_message(self, message: str) -> str:
        raise NotImplementedError("O método 'process_message' deve ser implementado.")

    def send_message(self, message: str) -> None:
        raise NotImplementedError("O método 'send_message' deve ser implementado.")