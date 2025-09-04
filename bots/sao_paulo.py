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

    "transacao_proporcao_transmitida_input": '//*[@id="divTotalidade"]/input', # input que so aparece se marcado como NÃO
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


# Arquivo: bots/sao_paulo.py

# (Mantenha todos os seus imports e o resto do código como está)

def preencher_dados_transacao(driver, dados: dict):
    
    logging.info("Preenchendo dados da transação...")

    # valor total da transação -----------------------------
    u.fill_input(FORMULARIO_LOCATORS["transacao_valor_total"], dados.get("valor_total"), driver)

    # Verifica se a transação é financiada -----------------------------
    if dados.get("financiado"):
        try:    
            logging.info("Transação financiada. Modificando estado do componente Vue via JavaScript.")

            tipo_financiamento_texto = dados.get("tipo_financiamento")
            if not tipo_financiamento_texto:
                raise ValueError("O 'tipo_financiamento' não foi fornecido nos dados.")

        
            ## Passo 1: Encontrar o valor correto da <option>

            seletor_dropdown = FORMULARIO_LOCATORS["transacao_tipo_financiamento_select"]

            u.scroll_to_element(seletor_dropdown, driver)

            wait = WebDriverWait(driver, 15)
            dropdown = wait.until(EC.presence_of_element_located((By.XPATH, seletor_dropdown)))
            option_xpath = f".//option[normalize-space(text())='{tipo_financiamento_texto}']"
            valor_da_opcao = dropdown.find_element(By.XPATH, option_xpath).get_attribute("value")
            logging.info(f"Opção de financiamento encontrada: Texto='{tipo_financiamento_texto}', Valor='{valor_da_opcao}'.")

            ## Passo 2: Script que encontra a instância Vue e manipular seu estado

            id_do_dropdown = "cboTpFinan"
            
            script = f"""
                // Argumentos passados do Selenium para o script
                const dropdownId = arguments[0];
                const optionValue = arguments[1];

                // 1. Pega o elemento do DOM
                const dropdownElement = document.getElementById(dropdownId);
                if (!dropdownElement) {{
                    return {{ success: false, message: 'Elemento dropdown #' + dropdownId + ' não encontrado.' }};
                }}

                // 2. Encontra a instância Vue correta subindo na árvore DOM
                // A lógica (métodos e dados) está no componente pai do dropdown.
                let el = dropdownElement;
                let vueComponent = null;
                while (el.parentElement) {{
                    el = el.parentElement;
                    if (el.__vue__) {{
                        // Verificamos se este componente Vue tem o método que precisamos
                        if (typeof el.__vue__.atualizaDescricaoTipoFinanciamento === 'function') {{
                            vueComponent = el.__vue__;
                            break;
                        }}
                    }}
                }}

                if (!vueComponent) {{
                    return {{ success: false, message: 'Instância Vue com o método necessário não foi encontrada.' }};
                }}

                // 3. ATUALIZA O ESTADO DIRETAMENTE (A parte mais importante)
                // Isso atualiza a variável 'tipoFinanciamento' no 'data' do componente
                vueComponent.tipoFinanciamento = optionValue;

                // 4. CHAMA O MÉTODO DIRETAMENTE
                // Isso executa a função que muda 'exibeValorFinanciado' para true
                vueComponent.atualizaDescricaoTipoFinanciamento(dropdownElement);

                return {{ success: true, message: 'Estado do componente Vue modificado com sucesso.' }};
            """
            
            # Executa o script e passa os argumentos necessários
            resultado = driver.execute_script(script, id_do_dropdown, valor_da_opcao)
            
            if not resultado or not resultado.get('success'):
                error_message = resultado.get('message', 'Erro desconhecido ao executar script Vue.')
                raise Exception(f"Falha ao manipular o componente Vue: {error_message}")
            
            logging.info(f"Script Vue executado: {resultado.get('message')}")


            # Passo 3: Lidar com o popup de aviso
            sp_close_aviso_financiamento(driver)


            # Passo 4: Esperar o campo 'Valor Financiado' se tornar visível
            logging.info("Aguardando o campo 'Valor Financiado' se tornar visível...")
            seletor_valor_financiado = FORMULARIO_LOCATORS["transacao_valor_financiamento"]
            wait.until(
                EC.visibility_of_element_located((By.XPATH, seletor_valor_financiado))
            )
            logging.info("Campo 'Valor Financiado' está visível.")


            # Passo 5: Preencher o valor financiado
            valor_a_preencher = dados.get("valor_financiamento")
            u.fill_input(seletor_valor_financiado, valor_a_preencher, driver)
            logging.info(f"Valor financiado '{valor_a_preencher}' preenchido.")


        except TimeoutException:
            logging.error("O campo 'Valor Financiado' não ficou visível após a manipulação do componente Vue.")
            raise Exception("Falha crítica: O campo de valor financiado não apareceu.")
        except Exception as e:
            logging.error(f"Falha ao preencher os dados do financiamento: {e}")
            raise


    # Totalidade: -----------------------------

    logging.info("Preenchendo informações sobre a totalidade do imóvel.")

    if dados.get("transmite_totalidade"):
        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_sim_radio"], driver)
        logging.info("Selecionado 'SIM' para a transmissão da totalidade do imóvel.")
    else: 
        # Se transmite_totalidade for False, clicamos em "NÃO"

        # TODO: VERIFICAR E AJUSTAR ERRO DEBUGANDO

        u.click_button(FORMULARIO_LOCATORS["transacao_totalidade_nao_radio"], driver)
        logging.info("Selecionado 'NÃO' para a transmissão da totalidade. Aguardando campo de proporção.")

        try:
            # Esperar explicitamente que o campo "PROPORÇÃO TRANSMITIDA" se torne visível
            wait = WebDriverWait(driver, 10)
            seletor_proporcao = FORMULARIO_LOCATORS["transacao_proporcao_transmitida_input"]
            
            wait.until(
                EC.visibility_of_element_located((By.XPATH, seletor_proporcao))
            )
            logging.info("Campo 'Proporção Transmitida' está visível.")

            # Verificar se o dado da proporção foi fornecido
            proporcao_valor = dados.get("proporcao_transmitida")
            if not proporcao_valor:
                raise ValueError("A transmissão da totalidade é 'NÃO', mas o valor para 'proporcao_transmitida' não foi fornecido.")

            # Preencher o campo
            u.fill_input(seletor_proporcao, proporcao_valor, driver)
            logging.info(f"Proporção transmitida de '{proporcao_valor}%' preenchida.")

        except TimeoutException:
            logging.error("O campo 'Proporção Transmitida' não ficou visível após clicar em 'NÃO'.")
            raise Exception("Falha crítica: O campo de proporção não apareceu.")
        except Exception as e:
            logging.error(f"Erro ao preencher a proporção transmitida: {e}")
            raise


    # Tipo de escritura -----------------------------
    if dados.get("tipo_instrumento") == "ESCRITURA_PUBLICA":
        u.click_button(FORMULARIO_LOCATORS["transacao_tipo_instrumento_escritura_radio"], driver)
    else:
        u.click_button(FORMULARIO_LOCATORS["transacao_tipo_instrumento_particular_radio"], driver)

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
                "transmite_totalidade": False, # True para Sim, False para Não
                "proporcao_transmitida": "50,00", # VALOR EM PORCENTAGEM
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