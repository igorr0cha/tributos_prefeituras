# Arquivo: bots/sao_paulo.py

import logging
import time
import utils.selenium_utils as u
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys # Importa a classe Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select # lida com dropdowns


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

    "transacao_tipo_financiamento_select": '//*[@id="cboTpFinan"]', # TODO: VERIFICAR ESSE CAMINHO
    "transacao_valor_financiamento": '//*[@id="txt_valor_financiado"]',

    "aviso_financiamento": '/html/body/div[3]/div',
    "botao_aviso_financiamento": "//button[contains(@class, 'swal2-confirm')]", # class

    "transacao_totalidade_sim_radio": '//*[@id="lblTransmissaoTotalidade"]', # label do "SIM"
    "transacao_totalidade_nao_radio": '//*[@id="rdlTotalidadeNao"]', # label do "NÃO"

    "transacao_tipo_instrumento_particular_radio": '//*[@id="divTipoInstrumento"]/span[1]/label',
    "transacao_tipo_instrumento_escritura_radio": '//*[@id="divTipoInstrumento"]/span[2]/label',

    "transacao_cartorio_select": '//*[@id="DdlCartorioRegistroImovel"]',
    "transacao_matricula": '//*[@id="txtMatricula"]'
} 
# ------------------------------------
# Funções secundárias da perfeitura de SAO PAULO

def sp_cookie_accept(driver):
    try:
        wait = WebDriverWait(driver, 25)
        
        seletor_do_host = "prodamsp-componente-consentimento"
        
        host = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_do_host)))

        shadow_root = host.shadow_root

        seletor_do_botao = "input[value='Autorizo o uso de todos os cookies e estou de acordo com a política de privacidade.']"
        botao_cookies = shadow_root.find_element(By.CSS_SELECTOR, seletor_do_botao)
        time.sleep(2)

        try:
            driver.execute_script("arguments[0].click();", botao_cookies)
        except Exception as e:
            botao_cookies.click()

        logging.info("Botão dentro do Shadow DOM foi clicado com sucesso!")

    except Exception as e:
        logging.error(f"Não foi possível encontrar ou clicar no elemento dentro do Shadow DOM.")
        logging.error(f"Erro: {e}")

def preencher_dados_imovel(driver, dados: dict):
    logging.info("Preenchendo cadastro do imóvel para auto-completar...")
    
    valor = dados.get("cadastro_imovel")
    if not valor:
        logging.error("Cadastro do imóvel não informado!")
        raise Exception("Cadastro do imóvel não informado!")

    # Passo 1: Focar e preencher o campo
    campo_cadastro = u.scroll_to_element(FORMULARIO_LOCATORS["imovel_cadastro"], driver)
    campo_cadastro.clear()
    campo_cadastro.send_keys(str(valor))
    
    # Passo 2: Simular o "blur" (perder o foco), que é um gatilho comum
    #driver.execute_script("arguments[0].blur();", campo_cadastro)
    #time.sleep(1) # Pequena pausa para o JS reagir

    # Passo 3: Enviar a tecla TAB para mover para o próximo campo, um gatilho ainda mais robusto
    campo_cadastro.send_keys(Keys.TAB)
    logging.info(f"Valor '{valor}' inserido e TAB pressionado para acionar o preenchimento.")
    
    # Passo 4: Esperar explicitamente pelo preenchimento de um dos campos
    try: 
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[3]/input'))
        )
        logging.info("Preenchimento automático detectado.")
    except Exception:
        logging.warning("O campo CEP não foi preenchido automaticamente após 15 segundos.")
        raise Exception("Falha no preenchimento automático do CEP.")


    # Passo 5: Verificar se o preenchimento automático funcionou
    campos_a_verificar = {
        "cep": '//*[@id="pnlTela1"]/div/fieldset[1]/div/div[3]/input',
        "logradouro": '//*[@id="txtEnderecoImovel"]',
    }
    for nome, xpath in campos_a_verificar.items():
        elemento = u.get_element(xpath, driver)
        valor_do_campo = elemento.get_attribute("value")
        if not valor_do_campo:
            logging.warning(f"Atenção: O campo '{nome}' não foi preenchido automaticamente.")
            raise Exception(f"Falha no preenchimento automático para o campo '{nome}'.")
    
    logging.info("Campos de endereço preenchidos automaticamente com sucesso.")


def preencher_pessoas(driver, tipo_pessoa: str, pessoas: list):
    for i, pessoa in enumerate(pessoas):
        logging.info(f"Preenchendo dados para {tipo_pessoa} {i+1}:")
        if i > 0:
            u.click_button(FORMULARIO_LOCATORS[f"{tipo_pessoa}_adicionar_btn"], driver)
            # time.sleep(2) # TODO: VERIFICAR TEMPO

        campo_cpf_cnpj = u.scroll_to_element(FORMULARIO_LOCATORS[f"{tipo_pessoa}_cpf_cnpj"], driver)
        campo_cpf_cnpj.clear()
        cpf_cnpj_valor = pessoa.get("cpf_cnpj")
        u.fill_input(FORMULARIO_LOCATORS[f"{tipo_pessoa}_cpf_cnpj"], cpf_cnpj_valor, driver)
        # time.sleep(1)  # TODO: VERIFICAR TEMPO

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
    
    # Valor total da transação
    u.fill_input(FORMULARIO_LOCATORS["transacao_valor_total"], dados.get("valor_total"), driver)

    # Navega para o campo de tipo de financiamento
    u.scroll_to_element(FORMULARIO_LOCATORS["transacao_tipo_financiamento_select"], driver)

    # Verifica se é financiado:
    if dados.get("financiado"):
        try:    
            logging.info("Transação é financiada. Preenchendo detalhes do financiamento...")

            tipo_financiamento_desejado = dados.get("tipo_financiamento")
            if not tipo_financiamento_desejado:
                raise ValueError("O 'tipo_financiamento' não foi fornecido nos dados.")
            
            # 1. Clica no dropdown para abrir as opções
            xpath_dropdown = FORMULARIO_LOCATORS["transacao_tipo_financiamento_select"]
            u.click_button(xpath_dropdown, driver)
            time.sleep(1)

            # 2. Seleciona a opção usando a classe Select (forma correta e robusta)
            try:
                # Encontra o elemento <select>
                dropdown_element = u.get_element(FORMULARIO_LOCATORS["transacao_tipo_financiamento_select"], driver)
                
                # Cria um objeto Select
                select_object = Select(dropdown_element)
                
                # Seleciona a opção pelo texto visível, o que dispara os eventos JS
                select_object.select_by_visible_text(tipo_financiamento_desejado)
                
                logging.info(f"Opção '{tipo_financiamento_desejado}' selecionada com sucesso.")

            except Exception as e:
                logging.error(f"Não foi possível selecionar a opção '{tipo_financiamento_desejado}'. Erro: {e}")
                raise Exception(f"Opção de financiamento '{tipo_financiamento_desejado}' não encontrada ou não selecionável.")

            # Lida com o popup de aviso que pode aparecer
            sp_close_aviso_financiamento(driver)

            # 3. Aguarda o campo de valor financiado aparecer
            logging.info("Aguardando o campo de valor financiado aparecer...")

            valor_financiado_xpath = FORMULARIO_LOCATORS["transacao_valor_financiamento"]
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, valor_financiado_xpath))
            )
            
            # 4. Preenche o campo de valor financiado
            valor_a_preencher = dados.get("valor_financiamento")
            u.fill_input(valor_financiado_xpath, valor_a_preencher, driver)
            logging.info("Valor do financiamento preenchido com sucesso.")

        except Exception as e:
            logging.error(f"Falha ao preencher os dados do financiamento: {e}")
            raise # Interrompe o bot se esta etapa crítica falhar



    # Totalidade do imóvel
    if dados.get("transmite_totalidade"):
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_sim_radio"], driver)   
    else:
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_nao_radio"], driver)

    # Tipo de instrumento
    if dados.get("tipo_instrumento") == "ESCRITURA_PUBLICA":
        u.click_button(FORMULARIO_LOCATORS["transacao_tipo_instrumento_escritura_radio"], driver)
    else: # Assume "INSTRUMENTO_PARTICULAR" como padrão
        u.click_button(FORMULARIO_LOCATORS["transacao_tipo_instrumento_particular_radio"], driver)

    # Lógica para matrícula/transcrição do cartório de registro
    u.get_select_option_by_text(FORMULARIO_LOCATORS["transacao_cartorio_select"], dados.get("cartorio_registro"), driver)
    u.fill_input(FORMULARIO_LOCATORS["transacao_matricula"], dados.get("matricula"), driver)

def sp_close_aviso_financiamento(driver):
    """
    Aguarda e fecha o popup de "Informação Sobre Financiamento" se ele aparecer.
    """
    try:
        # Espera o botão "OK" do popup ficar clicável por até 5 segundos.
        # O seletor é baseado na classe do botão de confirmação do SweetAlert.
        ok_button_xpath = FORMULARIO_LOCATORS["botao_aviso_financiamento"]
        
        wait = WebDriverWait(driver, 5)
        botao_ok = wait.until(EC.element_to_be_clickable((By.XPATH, ok_button_xpath)))
        
        logging.info("Popup de aviso de financiamento encontrado. Clicando em 'OK'.")
        botao_ok.click()
        
        # Aguarda o popup desaparecer para garantir que a ação foi concluída
        wait.until(EC.invisibility_of_element_located((By.XPATH, ok_button_xpath)))
        logging.info("Popup de aviso fechado com sucesso.")

    except TimeoutException:
        # Se o popup não aparecer em 5 segundos, apenas informa e continua.
        logging.info("Nenhum popup de aviso de financiamento apareceu, continuando a execução.")
    except Exception as e:
        # Captura outros erros inesperados ao tentar fechar o popup.
        logging.error(f"Erro inesperado ao tentar fechar o aviso de financiamento: {e}")



def sao_paulo_bot():
    """Função principal que orquestra a automação."""

    logging.info("Iniciando o bot de São Paulo...")
    driver = None # inicializa driver vazio para evitar inconsistências
    try:
        
        # TODO: criar função para receber dados do SGI (consultando view)

        # teste com dados HARDCODE
        dados_completos_itbi = {
            "imovel": {
                "cadastro_imovel": "07007800610" # Exemplo de cadastro real
            },
            "compradores": [
                {"cpf_cnpj": "755.173.613-15"} # Só precisamos do CPF
            ],
            "vendedores": [
                {"cpf_cnpj": "00.360.305/0010-40"} # Só precisamos do CPF/CNPJ
            ],
            "transacao": {
                "valor_total": "200000", # valor/preço TOTAL da transação
                "financiado": True, # True para Sim, False para Não
                "tipo_financiamento": "Sistema Financeiro de Habitação", # Opções válidas (SOMENTE): "Sistema Financeiro de Habitação" ou "Minha Casa Minha Vida" ou "Consórcio" ou "SFI, Carteira Hipotecária, etc", "NULL"
                "valor_financiamento": "150000", # valor FINANCIADO (NÃO é o VALOR TOTAL)
                "transmite_totalidade": True, # True para Sim, False para Não
                "tipo_instrumento": "ESCRITURA_PUBLICA", # Opções válidas (SOMENTE): "ESCRITURA_PUBLICA" ou "INSTRUMENTO_PARTICULAR"
                "cartorio_registro": "1º Oficial de Registro de Imóveis", # Opções válidas (SOMENTE): "1º Cartório de Registro de Imóvel", "2º ..." e assim por diante, até o 18º. 
                "matricula": "98765"
            }
        }

        driver = u.getDriverUndetectableLocal("https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/")
        u.wait_for_page_load(driver)

        sp_cookie_accept(driver)

        # -------- ORQUESTRAÇÃO DO PREENCHIMENTO

        # imovel
        preencher_dados_imovel(driver, dados_completos_itbi["imovel"])

        # pessoas
        preencher_pessoas(driver, "comprador", dados_completos_itbi["compradores"])
        preencher_pessoas(driver, "vendedor", dados_completos_itbi["vendedores"])

        # transacao
        preencher_dados_transacao(driver, dados_completos_itbi["transacao"])

        logging.info("Formulário preenchido. Pausa para verificação.")
        time.sleep(15)

    except Exception as e:
        logging.error(f"Erro no bot de São Paulo: {e}")
    finally:
        if driver:
            logging.info("Fechando o navegador.")
            driver.quit()