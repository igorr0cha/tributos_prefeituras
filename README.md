# 🤖 Tributos Prefeituras BOT

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green?style=for-the-badge&logo=selenium)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge)

---

## 📖 Sobre o Projeto

Este projeto é uma plataforma de automação robusta, desenvolvida para otimizar e agilizar a emissão de guias de tributos em diversas prefeituras do Brasil. Utilizando robôs (BOTs), a solução navega pelos portais municipais, preenche os dados necessários e realiza o download das guias, minimizando a intervenção manual e aumentando a eficiência dos processos fiscais.

---

## ✨ Principais Funcionalidades

- **Automação de Múltiplas Prefeituras:** Arquitetura modular que facilita a adição de novos robôs para diferentes cidades.
- **Robustez na Interação Web:** Funções utilitárias que lidam com esperas, exceções comuns e interações complexas em páginas dinâmicas.
- **Gerenciamento de Configuração:** Uso de variáveis de ambiente (`.env`) para proteger credenciais e dados sensíveis.
- **Logging Detalhado:** Registro completo das operações em arquivos de log para fácil depuração e monitoramento.
- **Tratamento de Exceções Customizado:** Classes de erro específicas para cenários de negócio, como `GuiaNaoEncontradaError`.

---

## 🏛️ Prefeituras Atendidas

A tabela abaixo detalha o status de automação para cada prefeitura.

| Status | Prefeitura | Link para o Portal | Nome do BOT | Observações |
| :--- | :--- | :--- | :--- | :--- |
| 🟠 `Em Desenvolvimento` | **São Paulo (SP)** | [Acessar Portal](https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/) | `sao_paulo.py` | - |
| 🟠 `Em Desenvolvimento` | **Goiânia (GO)** | [Acessar Portal](https://itbi.goiania.go.gov.br/sistemas/saces/asp/saces00000f0.asp?sigla=sisti) | `goiania.py` | - |
| 🟠 `Em Desenvolvimento` | **João Pessoa (PB)** | [Acessar Portal](https://receita.joaopessoa.pb.gov.br/itbi/paginas/portal/login.html) | `joao_pessoa.py` | Requer login. **Atenção:** a emissão da guia gera registro na dívida ativa. |
| ⚪ `Planejado` | *(futuras prefeituras...)* | - | - | - |

---

## 🏗️ Arquitetura do Projeto

O projeto é estruturado de forma modular para garantir escalabilidade e manutenibilidade:

```
tributos_prefeituras/
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git
├── README.md           # Documentação do projeto
├── requirements.txt    # Dependências Python do projeto
├── .env                # Arquivo para variáveis de ambiente (credenciais, etc.)
├── main.py             # Ponto de entrada da aplicação e configuração de logs
├── core/
│   ├── orchestrator.py # "Cérebro" que gerencia e seleciona o BOT a ser executado
│   └── exceptions.py   # Definição de erros customizados da aplicação
├── utils/
│   └── selenium_utils.py # Funções reutilizáveis para automação com Selenium
└── logs/
└── automation.log  # Arquivo de log com o registro das execuções
```

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem Principal:** Python
* **Automação Web:**
    * [Selenium](https://www.selenium.dev/): Para controle do navegador.
    * [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver): Versão do ChromeDriver otimizada para evitar detecção por sistemas anti-bot.
    * [Selenium-Wire](https://github.com/wkeeling/selenium-wire): Extensão que oferece funcionalidades adicionais, como a interceptação de requisições.
* **Gerenciamento de Dependências:** Pip com `requirements.txt`.

---

## 🚀 Guia de Instalação e Uso

### Pré-requisitos

- Python 3.9 ou superior
- Google Chrome instalado e atualizado
- Git

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/tributos_prefeituras.git](https://github.com/seu-usuario/tributos_prefeituras.git)
    cd tributos_prefeituras
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    - Renomeie ou crie uma cópia do arquivo `.env.example` (se houver) para `.env`.
    - Preencha o arquivo `.env` com as credenciais necessárias. Exemplo:
      ```env
      USUARIO_PORTAL_JP=seu_usuario
      SENHA_PORTAL_JP=sua_senha
      ```

### Executando a Automação

Para executar um BOT específico, utilize o ponto de entrada principal, passando a cidade como argumento (a ser implementado no `orchestrator.py`):

```bash
python main.py --cidade "joao_pessoa"

(Nota: A execução via main.py é uma sugestão de implementação para o orquestrador.)

🤝 Como Contribuir
Contribuições são muito bem-vindas! Se você deseja adicionar um novo BOT para uma prefeitura ou melhorar um existente, siga os passos:

Faça um Fork deste repositório.

Crie uma nova Branch: git checkout -b feature/nome-da-cidade.

Faça suas alterações e Commite: git commit -m 'feat: Adiciona BOT para a cidade X'.

Envie para a sua Branch: git push origin feature/nome-da-cidade.

Abra um Pull Request detalhando as mudanças.

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.