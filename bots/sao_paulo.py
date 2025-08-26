# Arquivo: bots/sao_paulo.py

import logging
import time
import utils.selenium_utils as u
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys # Importa a classe Keys

# --- CONFIGURAÇÕES DO CHROME ---
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-webgl")
# -----------------------------

# --- MAPEAMENTO DE LOCATORS ---
FORMULARIO_LOCATORS = {
    # Seção: Dados do Imóvel
    "imovel_cadastro": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[2]/input',

    # Seção: Comprador
    "comprador_cpf_cnpj": '//*[@id="fdsComprador"]/div[1]/div[1]/input',
    "comprador_adicionar_btn": '//*[@id="fdsComprador"]/div[2]/button',

    # Seção: Vendedor
    "vendedor_cpf_cnpj": '//*[@id="fdsVendedor"]/div[1]/div[1]/input',
    "vendedor_adicionar_btn": '//*[@id="fdsVendedor"]/div[2]/button',

    # Seção: Dados da Transação
    "transacao_valor_total": '//*[@id="pnlTela1"]/div/fieldset[4]/div/div[1]/input',
    "transacao_tipo_financiamento_select": '//*[@id="txtTipoFinanciamento"]',
    "transacao_totalidade_sim_radio": '//*[@id="divTransmissaoTotalidade"]/span[1]/label', # label do "SIM"
    "transacao_totalidade_nao_radio": '//*[@id="divTransmissaoTotalidade"]/span[2]/label', # label do "NÃO"
    "transacao_tipo_instrumento_particular_radio": '//*[@id="divTipoInstrumento"]/span[1]/label',
    "transacao_tipo_instrumento_escritura_radio": '//*[@id="divTipoInstrumento"]/span[2]/label',
    "transacao_cartorio_select": '//*[@id="DdlCartorioRegistroImovel"]',
    "transacao_matricula": '//*[@id="txtMatricula"]'
}
# ------------------------------------

def preencher_dados_imovel(driver, dados: dict):
    logging.info("Preenchendo cadastro do imóvel para auto-completar...")

    cadastro_imovel = u.scroll_to_element(FORMULARIO_LOCATORS["imovel_cadastro"], driver)
    cadastro_imovel.clear()

    valor = dados.get("cadastro_imovel")
    if valor:
        cadastro_imovel.send_keys(str(valor))
        logging.info("apertou o botão e deu enter")
        time.sleep(1)  # Pausa para processar e preencher valores
        cadastro_imovel.send_keys(Keys.ENTER)
        time.sleep(100)

        campos_essenciais = {
            "cep": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[3]/input',
            "logradouro": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[4]/input',
            "numero": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[5]/input'
        }

        for nome, xpath in campos_essenciais.items():
            elemento = u.scroll_to_element(xpath, driver)
            valor_atual = elemento.get_attribute("value")
            if not valor_atual:
                logging.warning(f"Atenção: O campo '{nome}' não foi preenchido automaticamente. Verifique o cadastro do imóvel.")
                raise Exception(f"Campo obrigatório '{nome}' não foi preenchido automaticamente!")

        logging.info("Campos essenciais preenchidos com sucesso: ")
    else:
        logging.error("Cadastro do imóvel não informado!")
        raise Exception("Cadastro do imóvel não informado!")


def preencher_pessoas(driver, tipo_pessoa: str, pessoas: list):
    for i, pessoa in enumerate(pessoas):
        logging.info(f"Preenchendo dados para {tipo_pessoa} {i+1}:")
        if i > 0:
            u.click_button(FORMULARIO_LOCATORS[f"{tipo_pessoa}_adicionar_btn"], driver)
            time.sleep(2)

        campo_cpf_cnpj = u.scroll_to_element(FORMULARIO_LOCATORS[f"{tipo_pessoa}_cpf_cnpj"], driver)
        campo_cpf_cnpj.clear()
        cpf_cnpj_valor = pessoa.get("cpf_cnpj")
        u.fill_input(FORMULARIO_LOCATORS[f"{tipo_pessoa}_cpf_cnpj"], cpf_cnpj_valor, driver)
        time.sleep(2)  # Aguarda preenchimento automático

        # Verifica se o nome foi preenchido automaticamente
        nome_xpath = f'//*[@id="fdsComprador"]/div[1]/div[2]/div/div/input' if tipo_pessoa == "comprador" else f'//*[@id="fdsVendedor"]/div[1]/div[2]/div/div/input'
        campo_nome = u.scroll_to_element(nome_xpath, driver)
        nome_valor = campo_nome.get_attribute("value")

        if not nome_valor:
            logging.info(f"Nome não preenchido automaticamente para {tipo_pessoa} {i+1}. Inserindo manualmente.")
            nome_manual = pessoa.get("nome") or "NOME_MANUAL"
            campo_nome.send_keys(nome_manual)
        else:
            logging.info(f"Nome preenchido automaticamente para {tipo_pessoa} {i+1}: {nome_valor}")


def preencher_dados_transacao(driver, dados: dict):
    
    logging.info("Preenchendo dados da transação...")
    u.fill_input(FORMULARIO_LOCATORS["transacao_valor_total"], dados.get("valor_total"), driver)
    u.get_select_option_by_text(FORMULARIO_LOCATORS["transacao_tipo_financiamento_select"], dados.get("tipo_financiamento"), driver)

    # Lógica para botões de rádio
    if dados.get("transmite_totalidade"):
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_sim_radio"], driver)
    else:
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_nao_radio"], driver)

    if dados.get("tipo_instrumento") == "ESCRITURA_PUBLICA":
        u.click_button(FORMULARIO_LOCATORS["transacao_tipo_instrumento_escritura_radio"], driver)
    else: # Assume "INSTRUMENTO_PARTICULAR" como padrão
        u.click_button(FORMULARIO_LOCATORS["transacao_tipo_instrumento_particular_radio"], driver)

    u.get_select_option_by_text(FORMULARIO_LOCATORS["transacao_cartorio_select"], dados.get("cartorio_registro"), driver)
    u.fill_input(FORMULARIO_LOCATORS["transacao_matricula"], dados.get("matricula"), driver)


def sao_paulo_bot():
    """Função principal que orquestra a automação."""
    logging.info("Iniciando o bot de São Paulo...")
    driver = None
    try:
        # --- ESTRUTURA DE DADOS SIMPLIFICADA ---
        dados_completos_itbi = {
            "imovel": {
                "cadastro_imovel": "07007800610" # Exemplo de cadastro real
            },
            "compradores": [
                {"cpf_cnpj": "111.111.111-11"} # Só precisamos do CPF
            ],
            "vendedores": [
                {"cpf_cnpj": "222.222.222-22"} # Só precisamos do CPF/CNPJ
            ],
            "transacao": {
                "valor_total": "500000,00",
                "tipo_financiamento": "Sistema Financeiro da Habitação (SFH)",
                "transmite_totalidade": True, # True para Sim, False para Não
                "tipo_instrumento": "ESCRITURA_PUBLICA", # "ESCRITURA_PUBLICA" ou "INSTRUMENTO_PARTICULAR"
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
        time.sleep(15)

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")
    finally:
        if driver:
            logging.info("Fechando o navegador.")
            driver.quit()