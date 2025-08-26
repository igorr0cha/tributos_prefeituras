import logging
import time
import utils.selenium_utils as u
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# CONFIGURAÇÕES DO CHROME
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-webgl")
# -----------------------------

# MAPEAMENTO os Locators (majoritamente, XPaths)
FORMULARIO_LOCATORS = {
    # Seção: Dados do Imóvel
    "imovel_cadastro": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[2]/input',
    "imovel_cep": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[3]/input',
    "imovel_logradouro": '//*[@id="txtEnderecoImovel"]',
    "imovel_numero": '//*[@id="txtNumeroImovel"]',
    "imovel_complemento": '//*[@id="txtComplImovel"]',
    "imovel_uf_select": '//*[@id="txtUFImovel"]',
    "imovel_municipio_select": '//*[@id="txtMunicipioImovel"]',

    # Seção: Comprador
    "comprador_cpf_cnpj": '//*[@id="fdsComprador"]/div[1]/div[1]/input',
    "comprador_nome": '//*[@id="fdsComprador"]/div[1]/div[2]/div/div/input',
    "comprador_adicionar_btn": '//*[@id="fdsComprador"]/div[2]/button', 

    # Seção: Vendedor
    "vendedor_cpf_cnpj": '//*[@id="fdsVendedor"]/div[1]/div[1]/input',
    "vendedor_nome": '//*[@id="fdsVendedor"]/div[1]/div[2]/div/div/input',
    "vendedor_adicionar_btn": '//*[@id="fdsVendedor"]/div[2]/button', 

    # Seção: Dados da Transação
    "transacao_valor_total": '//*[@id="pnlTela1"]/div/fieldset[4]/div/div[1]/input',
    "transacao_tipo_financiamento_select": '//*[@id="txtTipoFinanciamento"]', # tem ID
    "transacao_totalidade_sim_radio": '//*[@id="lblTransmissaoTotalidade"]', 
    "transacao_totalidade_nao_radio": '//*[@id="lblTransmissaoTotalidade"]', 
    "transacao_tipo_instrumento_particular_radio": '//*[@id="divTipoInstrumento"]/span[1]/label', 
    "transacao_tipo_instrumento_escritura_radio": '//*[@id="divTipoInstrumento"]/span[2]/label', 
    "transacao_cartorio_select": '//*[@id="DdlCartorioRegistroImovel"]', # tem ID
    "transacao_matricula": '//*[@id="txtMatricula"]'
}

def preencher_dados_imovel(driver, dados: dict):
    logging.info("Preenchendo dados do imóvel...")

    u.fill_input(FORMULARIO_LOCATORS["imovel_cadastro"], dados.get("cadastro_imovel"), driver)
    u.fill_input(FORMULARIO_LOCATORS["imovel_cep"], dados.get("cep"), driver)


def preencher_pessoas(driver, tipo_pessoa: str, pessoas: list):
    logging.info(f"Preenchendo dados para: Comprador:")

    

def preencher_dados_transacao(driver, dados: dict):
    logging.info("Preenchendo dados da transação...")
    u.fill_input(FORMULARIO_LOCATORS["transacao_valor_total"], dados.get("valor_total"), driver)

    # Exemplo para campo de seleção (dropdown)
    u.get_select_option_by_text(FORMULARIO_LOCATORS["transacao_tipo_financiamento_select"], dados.get("tipo_financiamento"), driver)

    # Exemplo para botões de rádio
    if dados.get("transmite_totalidade"):
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_sim_radio"], driver)
    else:
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_nao_radio"], driver)
    
    # Adicione a lógica para os outros campos de rádio e seleção aqui...
    u.fill_input(FORMULARIO_LOCATORS["transacao_matricula"], dados.get("matricula"), driver)


def sao_paulo_bot():
    logging.info("Iniciando o bot de São Paulo...")
    driver = None
    try:
        # --- ESTRUTURA DE DADOS COMPLETA (EXEMPLO) ---
        # No futuro, estes dados virão do seu sistema interno.
        dados_completos_itbi = {
            "imovel": {
                "cadastro_imovel": "123.456.789-0",
                "cep": "01001-000",
                "uf": "SP",
                "municipio": "São Paulo"
            },
            "compradores": [
                {"cpf_cnpj": "111.111.111-11", "nome": "Comprador Um da Silva"}
            ],
            "vendedores": [
                {"cpf_cnpj": "222.222.222-22", "nome": "Vendedor Dois de Souza"}
            ],
            "transacao": {
                "valor_total": "500000,00",
                "tipo_financiamento": "Sistema Financeiro da Habitação (SFH)",
                "transmite_totalidade": True, # True para Sim, False para Não
                "tipo_instrumento": "ESCRITURA_PUBLICA",
                "cartorio_registro": "1º Oficial de Registro de Imóveis",
                "matricula": "98765"
            }
        }

        driver = u.getDriver("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")

        logging.info("Aceitando cookies...")
        u.cookie_accept(driver, "CLASS_NAME", "cc__button__autorizacao--all")
        
        # --- ORQUESTRAÇÃO DO PREENCHIMENTO ---
        preencher_dados_imovel(driver, dados_completos_itbi["imovel"])
        preencher_pessoas(driver, "comprador", dados_completos_itbi["compradores"])
        preencher_pessoas(driver, "vendedor", dados_completos_itbi["vendedores"])
        preencher_dados_transacao(driver, dados_completos_itbi["transacao"])
        # ------------------------------------

        logging.info("Formulário preenchido. Pausa para verificação.")
        time.sleep(15) # Tempo aumentado para visualização completa

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")
    finally:
        if driver:
            logging.info("Fechando o navegador.")
            driver.quit()
