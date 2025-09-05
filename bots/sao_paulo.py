# Arquivo: bots/sao_paulo.py

import logging
import time
import utils.selenium_utils as u

import random

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

    "transacao_tipo_financiamento_select": '//*[@id="cboTpFinan"]', 
    "transacao_valor_financiamento": '//*[@id="txt_valor_financiado"]',
    "aviso_financiamento": '/html/body/div[3]/div',
    "botao_aviso_financiamento": "//button[contains(@class, 'swal2-confirm')]", # class

    "transacao_proporcao_transmitida_input": '//*[@id="divTotalidade"]/input', # input que so aparece se marcado como NÃO
    "transacao_totalidade_sim_radio": '//*[@id="lblTransmissaoTotalidade"]', # label do "SIM"
    "transacao_totalidade_nao_radio": '//*[@id="rdlTotalidadeNao"]', # label do "NÃO"

    "transacao_tipo_instrumento_particular_radio": '//*[@id="divTipoInstrumento"]/span[1]/label',
    "transacao_tipo_instrumento_escritura_radio": '//*[@id="divTipoInstrumento"]/span[2]/label',

    # Campos que aparecem após selecionar o tipo de instrumento
    "transacao_data_input": "//input[@id='date']", # Mais robusto e específico
    "transacao_cartorio_notas_input": "//input[@id='txtCartorioNotas']",
    "transacao_uf_cartorio_select": "//select[@id='TxtUfCartorioNotas']",
    "transacao_municipio_cartorio_input": "//input[@id='txtMunicipioCartorioNotas']",

    "transacao_cartorio_select": '//*[@id="DdlCartorioRegistroImovel"]',
    "transacao_matricula": '//*[@id="txtMatricula"]',

    "botao_avancar": '//*[@id="pnlTela1"]/div/div[5]/button[2]',
    "botao_aviso_financiamento_fechar": '/html/body/div[3]/div/div[1]/button' ,

    # página PÓS AVANÇAR:
    "botao_calcular_imposto": '//*[@id="secao-para-impressao-confirmacao"]/div[5]/button[2]',
    "botao_emitir_guia_tributos": '',
} 
# ------------------------------------
 
# --- MAPEAMENTO DE CARTÓRIOS DE REGISTRO ---
# Mapeia o nome completo do cartório para o valor numérico usado no <select> do site.
CARTORIO_REGISTRO_MAP = {
    "1º Cartório de Registro de Imóvel": "1",
    "2º Cartório de Registro de Imóvel": "2",
    "3º Cartório de Registro de Imóvel": "3",
    "4º Cartório de Registro de Imóvel": "4",
    "5º Cartório de Registro de Imóvel": "5",
    "6º Cartório de Registro de Imóvel": "6",
    "7º Cartório de Registro de Imóvel": "7",
    "8º Cartório de Registro de Imóvel": "8",
    "9º Cartório de Registro de Imóvel": "9",
    "10º Cartório de Registro de Imóvel": "10",
    "11º Cartório de Registro de Imóvel": "11",
    "12º Cartório de Registro de Imóvel": "12",
    "13º Cartório de Registro de Imóvel": "13",
    "14º Cartório de Registro de Imóvel": "14",
    "15º Cartório de Registro de Imóvel": "15",
    "16º Cartório de Registro de Imóvel": "16",
    "17º Cartório de Registro de Imóvel": "17",
    "18º Cartório de Registro de Imóvel": "18",
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

        logging.info("Botão de 'aceitar cookies' foi clicado com sucesso!")

    except Exception as e:
        logging.info(f"Não encontrado botão de 'aceitar cookies'")

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
            time.sleep(1) # Pausa para o novo campo aparecer

        # Localiza o campo e limpa antes de preencher
        seletor_cpf_cnpj = FORMULARIO_LOCATORS[f"{tipo_pessoa}_cpf_cnpj"]
        campo_cpf_cnpj = u.scroll_to_element(seletor_cpf_cnpj, driver)
        campo_cpf_cnpj.clear()
        
        cpf_cnpj_valor = pessoa.get("cpf_cnpj")
        if not cpf_cnpj_valor:
            logging.warning(f"CPF/CNPJ não fornecido para {tipo_pessoa} {i+1}. Pulando.")
            continue

        # Limpa o valor para contar apenas os dígitos
        digitos_apenas = ''.join(filter(str.isdigit, cpf_cnpj_valor))
        
        # --- LÓGICA CONDICIONAL DE PREENCHIMENTO ---
        if len(digitos_apenas) == 14 or len(digitos_apenas) == 11:
            # É um CPF/CNPJ: digita lentamente, como um humano
            logging.info(f"Detectado CPF/CNPJ. Digitanto '{cpf_cnpj_valor}' lentamente.")
            for caractere in cpf_cnpj_valor:
                campo_cpf_cnpj.send_keys(caractere)
                # Pausa aleatória entre 50 e 150 milissegundos
                time.sleep(random.uniform(0.05, 0.15))
            # Pressiona TAB para acionar o preenchimento automático do nome
            campo_cpf_cnpj.send_keys(Keys.TAB)

        #time.sleep(1) # Pausa para a requisição do nome ser concluída

        # Verifica se o nome foi preenchido automaticamente
        nome_xpath = f'//*[@id="fdsComprador"]/div[1]/div[2]/div/div/input' if tipo_pessoa == "comprador" else f'//*[@id="fdsVendedor"]/div[1]/div[2]/div/div/input'
        
        try:
            # Espera explícita para o nome ser preenchido
            campo_nome = WebDriverWait(driver, 5).until(
                lambda d: d.find_element(By.XPATH, nome_xpath)
            )
            nome_valor = campo_nome.get_attribute("value")

            if nome_valor:
                logging.info(f"Nome preenchido automaticamente para {tipo_pessoa} {i+1}: {nome_valor}")
            else:
                # Se o valor ainda estiver vazio, preenche manualmente
                logging.info(f"Nome não preenchido automaticamente para {tipo_pessoa} {i+1}. Inserindo manualmente.")
                nome_manual = pessoa.get("nome") or "NOME_NAO_ENCONTRADO"
                campo_nome.send_keys(nome_manual)
        except TimeoutException:
            logging.error(f"O campo de nome para {tipo_pessoa} {i+1} não foi encontrado.")
            raise


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
            sp_close_aviso_financiamento(FORMULARIO_LOCATORS["botao_aviso_financiamento"],driver)

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
        # Se transmite_totalidade for False, usamos o script para selecionar "NÃO"
        logging.info("Selecionando 'NÃO' para a transmissão da totalidade via script Vue.")
        try:
            radio_button_id = 'rdlTotalidadeNao'
            script = f"""
                const radioId = arguments[0];
                const radioElement = document.getElementById(radioId);
                if (!radioElement) {{
                    return {{ success: false, message: 'Elemento radio #' + radioId + ' não encontrado.' }};
                }}
                let el = radioElement;
                let vueComponent = null;
                while (el.parentElement) {{
                    el = el.parentElement;
                    if (el.__vue__) {{
                        if (typeof el.__vue__.mostrarTotalidade === 'function') {{
                            vueComponent = el.__vue__;
                            break;
                        }}
                    }}
                }}
                if (!vueComponent) {{
                    return {{ success: false, message: 'Instância Vue com o método mostrarTotalidade não foi encontrada.' }};
                }}
                
                // Clica no label para garantir a mudança visual
                document.querySelector('label[for="' + radioId + '"]').click();
                
                // Atualiza o estado e chama o método
                vueComponent.transmissaoTotalidade = 'Não';
                vueComponent.mostrarTotalidade();
                
                return {{ success: true, message: 'Estado da totalidade modificado com sucesso.' }};
            """
            resultado = driver.execute_script(script, radio_button_id)

            if not resultado or not resultado.get('success'):
                raise Exception(f"Falha ao manipular Vue para totalidade: {resultado.get('message', 'Erro desconhecido')}")
            
            logging.info(f"Script Vue para totalidade executado: {resultado.get('message')}")
            
            # Esperar explicitamente que o campo "PROPORÇÃO TRANSMITIDA" se torne visível
            wait = WebDriverWait(driver, 10)
            seletor_proporcao = FORMULARIO_LOCATORS["transacao_proporcao_transmitida_input"]
            wait.until(EC.visibility_of_element_located((By.XPATH, seletor_proporcao)))
            logging.info("Campo 'Proporção Transmitida' está visível.")

            proporcao_valor = dados.get("proporcao_transmitida")
            if not proporcao_valor:
                raise ValueError("A transmissão da totalidade é 'NÃO', mas o valor para 'proporcao_transmitida' não foi fornecido.")

            u.fill_input(seletor_proporcao, proporcao_valor, driver)
            logging.info(f"Proporção transmitida de '{proporcao_valor}%' preenchida.")

        except TimeoutException:
            raise Exception("Falha crítica: O campo de proporção não apareceu após a seleção.")
        except Exception as e:
            raise Exception(f"Erro ao preencher a proporção transmitida: {e}")



    # Tipo de instrumento -----------------------------

    logging.info("Preenchendo o tipo de instrumento.")
    tipo_instrumento = dados.get("tipo_instrumento")
    if tipo_instrumento == "ESCRITURA_PUBLICA":
        valor_vue = "Publico"
        radio_id = "rad_publico"
    elif tipo_instrumento == "INSTRUMENTO_PARTICULAR":
        valor_vue = "Particular"
        radio_id = "rad_particular"
    else:
        raise ValueError(f"Tipo de instrumento '{tipo_instrumento}' é inválido.")

    try:
        script = f"""
            const radioId = arguments[0];
            const instrumentValue = arguments[1];
            const radioElement = document.getElementById(radioId);
            if (!radioElement) return {{ success: false, message: 'Elemento radio #' + radioId + ' não encontrado.' }};
            
            let el = radioElement;
            let vueComponent = null;
            while (el.parentElement) {{
                el = el.parentElement;
                if (el.__vue__) {{
                    if (typeof el.__vue__.mostrarDataTransacao === 'function' && typeof el.__vue__.mostrarCartorioNotas === 'function') {{
                        vueComponent = el.__vue__;
                        break;
                    }}
                }}
            }}
            if (!vueComponent) return {{ success: false, message: 'Instância Vue com os métodos necessários não foi encontrada.' }};

            document.querySelector('label[for="' + radioId + '"]').click();
            vueComponent.tipoInstrumento = instrumentValue;
            vueComponent.mostrarDataTransacao();
            vueComponent.mostrarCartorioNotas();
            
            return {{ success: true, message: 'Estado do tipo de instrumento modificado.' }};
        """
        resultado = driver.execute_script(script, radio_id, valor_vue)
        if not resultado or not resultado.get('success'):
            raise Exception(f"Falha ao manipular Vue para tipo de instrumento: {resultado.get('message', 'Erro desconhecido')}")
        
        logging.info(f"Script Vue para tipo de instrumento executado: {resultado.get('message')}")

        # Aguardar e preencher os campos que aparecem
        wait = WebDriverWait(driver, 10)
        logging.info("Aguardando campos de data e cartório se tornarem visíveis...")

        # O campo de data sempre aparece, então esperamos por ele e o preenchemos
        wait.until(EC.visibility_of_element_located((By.XPATH, FORMULARIO_LOCATORS["transacao_data_input"])))
        u.fill_input(FORMULARIO_LOCATORS["transacao_data_input"], dados.get("data_registro"), driver)
        logging.info("Campo 'Data da Transação' preenchido.")

        # Os campos de cartório só aparecem para 'Escritura Pública'
        if tipo_instrumento == "ESCRITURA_PUBLICA":
            wait.until(EC.visibility_of_element_located((By.XPATH, FORMULARIO_LOCATORS["transacao_cartorio_notas_input"])))
            
            u.fill_input(FORMULARIO_LOCATORS["transacao_cartorio_notas_input"], dados.get("cartorio_notas"), driver)
            u.get_select_option_by_text(FORMULARIO_LOCATORS["transacao_uf_cartorio_select"], dados.get("uf_cartorio"), driver)
            u.fill_input(FORMULARIO_LOCATORS["transacao_municipio_cartorio_input"], dados.get("municipio_cartorio"), driver)
            logging.info("Campos de cartório de notas preenchidos.")
        
        logging.info("Campos dinâmicos de 'Tipo de Instrumento' preenchidos com sucesso.")

    except Exception as e:
        # Adiciona exc_info=True para logar o traceback completo do erro
        logging.error(f"Erro ao selecionar o tipo de instrumento: {e}", exc_info=True)
        raise

    # CARTÓRIO DE REGISTRO E MATRÍCULA -----------------------------

    logging.info("Preenchendo cartório de registro e matrícula.")
    
    try:
        # Pega o nome do cartório dos dados de entrada
        cartorio_texto = dados.get("cartorio_registro")
        if not cartorio_texto:
            raise ValueError("O nome do 'cartorio_registro' não foi fornecido.")

        # Usa o mapa para encontrar o valor numérico correspondente
        cartorio_valor_numerico = CARTORIO_REGISTRO_MAP.get(cartorio_texto)
        
        # Verifica se o cartório foi encontrado no mapa
        if not cartorio_valor_numerico:
            raise ValueError(f"Cartório de registro inválido ou não mapeado: '{cartorio_texto}'")

        # Encontra o elemento dropdown
        seletor_cartorio = FORMULARIO_LOCATORS["transacao_cartorio_select"]
        elemento_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, seletor_cartorio))
        )
        
        # Usa a classe Select para escolher a opção pelo VALOR numérico obtido do mapa
        select = Select(elemento_select)
        select.select_by_value(cartorio_valor_numerico)

        logging.info(f"Cartório de registro '{cartorio_texto}' (valor: {cartorio_valor_numerico}) selecionado com sucesso.")

    except Exception as e:
        logging.error(f"Não foi possível selecionar o cartório de registro: {e}", exc_info=True)
        raise

    # Preenche a matrícula (continua igual)
    u.fill_input(FORMULARIO_LOCATORS["transacao_matricula"], dados.get("matricula"), driver)

    # Clica para avançar
    driver.find_elements(By.XPATH, FORMULARIO_LOCATORS['botao_avancar'])[0].click()

    #  Clicando para calcular imposto na próxima página
    u.wait_for_page_load(driver)
    u.scroll_to_element(FORMULARIO_LOCATORS["botao_calcular_imposto"], driver).click()
    logging.info("Dados da transação preenchidos e avançado para a próxima etapa.")

    time.sleep(1000) #TODO: REMOVER ESSA PAUSA

    # Emitindo guia de tributos:
    u.scroll_to_element(FORMULARIO_LOCATORS['botao_emitir_guia_tributos'], driver).click()


def sp_close_aviso_financiamento(button_xpath,driver):
    """
    Aguarda e fecha o popup de "Informação Sobre Financiamento" se ele aparecer.
    """
    
    try:
        # Espera o botão para fechamento do popup ficar clicável por até 5 segundos.
        # O seletor é baseado na classe do botão de confirmação do SweetAlert.
        
        wait = WebDriverWait(driver, 5)
        botao_ok = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        
        logging.info("Popup de aviso de financiamento encontrado. Clicando em 'OK'.")
        botao_ok.click()
        
        # Aguarda o popup desaparecer para garantir que a ação foi concluída
        wait.until(EC.invisibility_of_element_located((By.XPATH, button_xpath)))
        logging.info("Popup de aviso fechado com sucesso.")

    except TimeoutException:
        # Se o popup não aparecer em 5 segundos, apenas continua
        logging.info("Popup de aviso de financiamento não apareceu. Continuando sem ação.")
  
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
                {"cpf_cnpj": "75517361315"} # Só precisamos do CPF
            ],
            "vendedores": [
                {"cpf_cnpj": "00360305000104"} # Só precisamos do CPF/CNPJ
            ],
            "transacao": {
                "valor_total": "1031000,00", # valor/preço TOTAL da transação
                "financiado": True, # True para Sim, False para Não
                "tipo_financiamento": "Sistema Financeiro de Habitação", # Opções válidas (SOMENTE): "Sistema Financeiro de Habitação" ou "Minha Casa Minha Vida" ou "Consórcio" ou "SFI, Carteira Hipotecária, etc", "NULL"
                "valor_financiamento": "962350,00", # valor FINANCIADO (NÃO é o VALOR TOTAL)
                "transmite_totalidade": True, # True para Sim, False para Não
                "proporcao_transmitida": None, # VALOR EM PORCENTAGEM ex: 50,00
                "tipo_instrumento": "INSTRUMENTO_PARTICULAR", # Opções válidas (SOMENTE): "ESCRITURA_PUBLICA" ou "INSTRUMENTO_PARTICULAR"

                # --- DADOS NECESSÁRIOS PARA OS NOVOS CAMPOS ---
                "data_registro": "04/09/2025",
                "cartorio_notas": None,
                "uf_cartorio": "SP",
                "municipio_cartorio": "São Paulo",
                # ----------------------------------------------
                "cartorio_registro": "15º Cartório de Registro de Imóvel",
                "matricula": "177273"
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