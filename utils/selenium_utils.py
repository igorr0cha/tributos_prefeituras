import os
import platform
import sys
import time
import glob
import subprocess
import time
import undetected_chromedriver as uc
import flask
import logging

import random #biblioteca para recarregar

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, JavascriptException, WebDriverException, TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def recarregar_como_humano(driver):
    """
    Recarrega a página simulando a tecla F5 para parecer mais humano.
    """
    try:
        # Encontra o corpo da página para enviar a tecla
        body = driver.find_element(By.TAG_NAME, 'body')
        
        # Pausa aleatória antes de agir
        time.sleep(random.uniform(0.5, 1.5)) 
        
        # Envia a tecla F5
        body.send_keys(Keys.F5)
        
        print("Página recarregada com a tecla F5.")
        
        # Espera o carregamento da página após o refresh
        wait_for_page_load(driver) # Usando sua função de selenium_utils.py

    except Exception as e:
        print(f"Erro ao tentar recarregar a página como humano: {e}")
        # Fallback para o método padrão se a simulação de tecla falhar
        driver.refresh()
        wait_for_page_load(driver)

def find_chrome_path():
    """
    Encontra o caminho do executável do Google Chrome de acordo com o sistema operacional.

    Returns:
        str: Caminho completo para o executável do Chrome ou None se não for encontrado
    """
    sistema = platform.system().lower()

    if sistema == "windows":
        # Obtém o diretório do usuário atual
        diretorio_usuario = os.environ.get("USERPROFILE", "")

        # Caminhos comuns para o Chrome no Windows
        caminhos_windows = [
            # Primeiro verifica no perfil do usuário atual
            os.path.join(
                diretorio_usuario,
                "AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
            ),
            os.path.join(
                diretorio_usuario,
                "AppData\\Local\\Google\\Chrome Beta\\Application\\chrome.exe",
            ),
            # Depois verifica nos diretórios padrão
            os.path.join(
                os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                "Google\\Chrome\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                "Google\\Chrome\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Google\\Chrome\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                "Google\\Chrome Beta\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                "Google\\Chrome Beta\\Application\\chrome.exe",
            ),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Google\\Chrome Beta\\Application\\chrome.exe",
            ),
        ]

        # Tenta encontrar o Chrome nos caminhos listados
        for caminho in caminhos_windows:
            if os.path.exists(caminho):
                print(f"Chrome encontrado em: {caminho}")
                return caminho

        # Tenta encontrar usando o registro do Windows
        try:
            import winreg

            # Tenta primeiro no registro do usuário atual
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon"
                )
                caminho = winreg.QueryValueEx(key, "path")[0]
                winreg.CloseKey(key)
                if os.path.exists(caminho):
                    print(f"Chrome encontrado via registro do usuário: {caminho}")
                    return caminho
            except:
                pass

            # Se não encontrar, tenta no registro do sistema
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            )
            caminho = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
            if os.path.exists(caminho):
                print(f"Chrome encontrado via registro do sistema: {caminho}")
                return caminho
        except Exception as e:
            print(f"Erro ao buscar no registro do Windows: {str(e)}")

    elif sistema == "darwin":  # macOS
        # Obtém o diretório do usuário atual
        diretorio_usuario = os.path.expanduser("~")

        caminhos_mac = [
            # Primeiro verifica no perfil do usuário atual
            os.path.join(
                diretorio_usuario,
                "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ),
            # Depois verifica nos diretórios padrão
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]

        for caminho in caminhos_mac:
            if os.path.exists(caminho):
                print(f"Chrome encontrado em: {caminho}")
                return caminho

    elif sistema == "linux":
        # Obtém o diretório do usuário atual
        diretorio_usuario = os.path.expanduser("~")

        # Tenta encontrar usando comandos do sistema
        try:
            # Tenta usar o comando 'which' para encontrar o Chrome
            resultado = subprocess.check_output(
                ["which", "google-chrome"], stderr=subprocess.STDOUT
            )
            caminho = resultado.decode().strip()
            if os.path.exists(caminho):
                print(f"Chrome encontrado via comando 'which': {caminho}")
                return caminho
        except:
            pass

        # Caminhos comuns para o Chrome no Linux
        caminhos_linux = [
            # Primeiro verifica no perfil do usuário atual
            os.path.join(diretorio_usuario, ".local/bin/google-chrome"),
            # Depois verifica nos diretórios padrão
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]

        for caminho in caminhos_linux:
            if os.path.exists(caminho):
                print(f"Chrome encontrado em: {caminho}")
                return caminho

    # Se não encontrou em nenhum lugar, retorna None
    print("Chrome não encontrado automaticamente.")
    return None

def find_chromedriver_path():
    sistema = platform.system().lower()
    arquitetura = platform.machine().lower()

    diretorio_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    diretorio_drivers = os.path.join(diretorio_projeto, "drivers")
    diretorio_pai = os.path.dirname(diretorio_projeto)

    extensao = ".exe" if sistema == "windows" else ""

    caminhos_possiveis = [
        os.path.join(os.getcwd(), f"chromedriver{extensao}"),
        os.path.join(diretorio_pai, f"chromedriver{extensao}"),
        os.path.join(diretorio_projeto, f"chromedriver{extensao}"),
    ]

    # Verifica cada um dos caminhos possíveis
    for caminho in caminhos_possiveis:
        print(f"Verificando chromedriver em: {caminho}")
        if os.path.exists(caminho):
            print(f"Chromedriver encontrado em: {caminho}")
            return caminho

    # Se não encontrou nos locais comuns, continua com os caminhos padrão
    if sistema == "linux":
        return os.path.join(diretorio_drivers, "chromedriver-linux64", "chromedriver")
    elif sistema == "darwin":  # macOS
        if "arm" in arquitetura:
            return os.path.join(
                diretorio_drivers, "chromedriver-mac-arm64", "chromedriver"
            )
        else:
            return os.path.join(
                diretorio_drivers, "chromedriver-mac-x64", "chromedriver"
            )
    elif sistema == "windows":
        # Verifica se o sistema é 32 ou 64 bits
        if sys.maxsize > 2**32:
            return os.path.join(
                diretorio_drivers, "chromedriver-win64", "chromedriver.exe"
            )
        else:
            return os.path.join(
                diretorio_drivers, "chromedriver-win32", "chromedriver.exe"
            )
    else:
        raise Exception(f"Sistema operacional não suportado: {sistema}")

def getDriverUndetectable(url: str, headless: bool = False):
    """
    Inicializa um WebDriver do Chrome INDETECTÁVEL que gerencia o driver
    automaticamente para contornar sistemas anti-bot.

    Args:
        url (str): A URL inicial para o navegador abrir.
        headless (bool): Se True, executa o navegador em modo invisível.

    Returns:
        uc.Chrome: A instância do driver do Chrome indetectável.
    """
    logging.info("Configurando o ChromeDriver no modo indetectável...")

    options = uc.ChromeOptions()
    
    # Opções para tornar a automação mais estável e parecida com um humano
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=pt-BR,pt") # Garante o idioma português
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument('--headless=new')

    # A mágica acontece aqui:
    # 1. uc.Chrome() cria um navegador "camuflado".
    # 2. ChromeDriverManager().install() baixa e fornece o caminho do driver correto.
    driver = uc.Chrome(
        options=options,
        driver_executable_path=ChromeDriverManager().install()
    )

    # Camada extra de proteção: remove a flag 'webdriver' que o Selenium cria
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()

    logging.info(f"Navegando para: {url}")
    driver.get(url)
    
    return driver

def getDriverUndetectableLocal(url: str, headless: bool = False):
    """
    Inicializa um WebDriver do Chrome INDETECTÁVEL que utiliza drivers locais
    para uma inicialização rápida, contornando sistemas anti-bot.

    Args:
        url (str): A URL inicial para o navegador abrir.
        headless (bool): Se True, executa o navegador em modo invisível.

    Returns:
        uc.Chrome: A instância do driver do Chrome indetectável.
    """
    logging.info("Configurando o ChromeDriver no modo indetectável com driver local...")

    options = uc.ChromeOptions()
    
    # Opções para tornar a automação mais estável e parecida com um humano
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=pt-BR,pt") # Garante o idioma português
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument('--headless=new')
        
    # --- Otimização ---
    # Encontra os caminhos do Chrome e do ChromeDriver localmente

    chrome_path = find_chrome_path()
    driver_path = find_chromedriver_path()

    if not driver_path or not os.path.exists(driver_path):
        logging.error("ChromeDriver não encontrado localmente. Execute o script com conexão à internet uma vez para baixá-lo.")
        raise FileNotFoundError(f"ChromeDriver não encontrado no caminho: {driver_path}")

    logging.info(f"Usando ChromeDriver local em: {driver_path}")

    driver = uc.Chrome(
        options=options,
        browser_executable_path=chrome_path,  # Aponta para a instalação do Chrome
        driver_executable_path=driver_path    # Aponta para o driver local
    )

    # Camada extra de proteção: remove a flag 'webdriver' que o Selenium cria
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()

    logging.info(f"Navegando para: {url}")
    driver.get(url)
    
    return driver

def getDriver(url, headless=False, extensions=None):
    """
    Inicializa e configura o WebDriver do Chrome usando webdriver-manager.
    """
    # --- Parte 1: Configurações Iniciais (quase a mesma) ---
    diretorio_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    print(f"Diretório de downloads: {download_dir}")

    
    print("Configurando o ChromeDriver com webdriver-manager...")
    servico = ChromeService(ChromeDriverManager().install())

    # Configuração das Opções do Chrome (igual ao seu) ---
    chrome_options = uc.ChromeOptions()
    
    # Adiciona as opções experimentais para download
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
            "plugins.always_open_pdf_externally": True,
        },
    )

    # Adiciona os argumentos comuns
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    if headless:
        chrome_options.add_argument("--headless=new")

    # Adiciona extensões (igual ao seu)
    if extensions:
        for extension in extensions:
            extension_path = os.path.join(diretorio_projeto, "extensions", extension)
            if os.path.exists(extension_path):
                chrome_options.add_argument(f"--load-extension={extension_path}")
            else:
                print(f"Extensão {extension} não encontrada em {extension_path}")

    # --- Parte 4: Inicialização do Driver (igual ao seu, mas usando o novo 'servico') ---
    seleniumwire_options = {
        "verify_ssl": True,
        "suppress_connection_errors": True,
        "ignore_http_methods": ["OPTIONS"],
    }

    driver = webdriver.Chrome(
        service=servico,  # A mágica acontece aqui!
        options=chrome_options,
        seleniumwire_options=seleniumwire_options,
    )

    driver.maximize_window()
    
    driver.execute_cdp_cmd(
        "Browser.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": download_dir,
        },
    )
    
    if url.startswith("http"):
        driver.get(url)
    else:
        driver.get(f"https://{url}")

    return driver

def getDriver_Local(url, headless=False, extensions=None):
    # Detecta o sistema operacional e arquitetura
    sistema = platform.system().lower()

    # Obtém o diretório do projeto
    diretorio_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Configura o diretório de download
    download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    print(f"Diretório de downloads: {download_dir}")

    # Determina qual pasta de driver usar com base no SO e arquitetura
    caminho_driver = find_chromedriver_path()

    if caminho_driver is None:
        raise Exception("Driver não encontrado")

    # Garante que o driver tem permissão de execução (para Linux e macOS)
    if sistema in ["linux", "darwin"]:
        os.chmod(caminho_driver, 0o755)

    # Encontra o caminho do Chrome
    chrome_path = find_chrome_path()

    # Configura as opções do Chrome
    chrome_options = uc.ChromeOptions()

    # Define o caminho do Chrome se encontrado
    
    if chrome_path:
        chrome_options.binary_location = chrome_path
    else:
        chrome_default_path = os.path.join(
            os.environ.get("USERPROFILE", ""), "AppData", "Local", "Google", "Chrome", "Application", "chrome.exe"
        )
        raise Exception(
            f"Chrome não encontrado no sistema. Verifique se o Google Chrome está instalado. Caminho: {chrome_default_path}"
        )

    # Adiciona as opções experimentais para download
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
            "intl.accept_languages": "en-US,en",
            "download.extensions_to_open": "",
            "plugins.always_open_pdf_externally": True,
            "download.open_pdf_in_system_reader": False,
            # Novas configurações para resolver problemas de certificado e download
            "browser.download.manager.showWhenStarting": False,
            "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream,application/pdf,application/x-pdf,application/vnd.pdf",
            "browser.download.alwaysOpenPanel": False,
        },
    )

    # Adiciona os argumentos comuns a ambos os métodos
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--lang=en-US")  # Força o Chrome a usar inglês
    # Adiciona argumentos para resolver problemas de certificado
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")

    if headless:
        chrome_options.add_argument("--headless=new")  # Modo headless moderno

    # Adiciona extensões se fornecidas
    if extensions:
        for extension in extensions:
            extension_path = os.path.join(diretorio_projeto, "extensions", extension)
            extension_dir = extension_path.replace(".crx", "")

            if os.path.exists(extension_path):
                # Verifica se já existe o diretório descompactado
                if not os.path.exists(extension_dir):
                    # Descompacta o arquivo .crx para um diretório
                    import zipfile

                    with zipfile.ZipFile(extension_path, "r") as zip_ref:
                        zip_ref.extractall(extension_dir)

                chrome_options.add_argument(f"--load-extension={extension_dir}")
            else:
                print(f"Extensão {extension} não encontrada em {extension_path}")

    # Cria o serviço usando o caminho do driver correto
    servico = Service(executable_path=caminho_driver)

    # Configurações do Selenium Wire para certificados
    seleniumwire_options = {
        "verify_ssl": True,
        "suppress_connection_errors": True,  # Suprime erros de conexão
        "ignore_http_methods": ["OPTIONS"],  # Ignora requisições OPTIONS
    }

    # Inicia o Chrome com o driver apropriado
    driver = webdriver.Chrome(
        service=servico,
        options=chrome_options,
        seleniumwire_options=seleniumwire_options,
    )

    # Maximiza a janela
    driver.maximize_window()

    # Configura o DevTools para downloads
    driver.execute_cdp_cmd(
        "Browser.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": download_dir,
            "eventsEnabled": True,
        },
    )

    # Navega para a URL
    if url.startswith("http"):
        driver.get(url)
    else:
        driver.get(f"https://{url}")

    return driver

def fill_input(xpath, valor, driver, timeout=10):
    """
    Preenche um campo de input.

    Args:
        xpath: O xpath do elemento
        valor: O valor a ser preenchido
        driver: O driver do selenium
        timeout: Tempo máximo de espera
    """
    if valor is not None:
        wait_for_page_load(driver, timeout)
        element = get_element(xpath, driver, timeout)
        element.clear()
        element.send_keys(Keys.HOME + str(valor))
        
def click_button(xpath, driver, timeout=10):
    """
    Clica em um botão.

    Args:
        xpath: O xpath do elemento
        driver: O driver do selenium
        timeout: Tempo máximo de espera
    """
    wait_for_page_load(driver, timeout)
    element = wait_for_element_to_load(xpath, driver, timeout)

    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)

    button = wait_for_element_not_disabled(xpath, driver, timeout)

    try:
        button.click()
    except:
        driver.execute_script("arguments[0].click();", button)

def get_element(xpath, driver, timeout=10):
    """
    Obtém um elemento da página.

    Args:
        xpath: O xpath do elemento
        driver: O driver do selenium
        timeout: Tempo máximo de espera
    """
    wait_for_page_load(driver, timeout)
    element = wait_for_element_to_load(xpath, driver, timeout)

    if not element.is_displayed():
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

    return wait_for_element_visibility(xpath, driver, timeout)

def get_elements(xpath, driver, timeout=10):
    try:
        wait_for_page_load(driver, timeout)
        elements = wait_for_elements_to_load(xpath, driver, timeout)
        return elements
    except Exception as e:
        print(f"Erro ao obter os elementos {xpath}: {str(e)}")
        raise e

def scroll_to_element(xpath, driver, timeout=10):
    try:
        wait_for_page_load(driver, timeout)
        element = wait_for_element_to_load(xpath, driver, timeout)

        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});",
            element,
        )
        time.sleep(0.5)
        element = wait_for_element_visibility(xpath, driver, timeout)
        return element
    except Exception as e:
        print(f"Erro ao rolar para o elemento {xpath}: {str(e)}")
        raise e

def wait_for_elements_to_load(xpath, driver, timeout=10):
    elements = WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath))
    )
    return elements

def wait_for_element_to_load(xpath, driver, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    return element

def wait_for_url(url, driver, timeout=10):
    element = WebDriverWait(driver, timeout).until(EC.url_contains(url))
    return element

def wait_for_element_visibility(xpath, driver, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )
    return element

def wait_for_element_not_disabled(xpath, driver, timeout=10):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    return element

def wait_for_page_load(driver, timeout=10):
    try:
        # Espera pelo readyState
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Pequena pausa para garantir que animações terminaram
        time.sleep(0.5)
    except Exception as e:
        print("Aviso: Timeout esperando carregamento da página")
        pass  # Não vamos levantar exceção aqui, pois nem todas as páginas usam jQuery

def get_select_option_by_text(xpath, text, driver, timeout=10):
    select_element = get_element(xpath, driver, timeout)
    driver.execute_script(
        """
        const select = arguments[0];
        const options = select.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].text.includes(arguments[1])) {
                select.value = options[i].value;
                break;
            }
        }
    """,
        select_element,
        text,
    )

def get_select_option_by_text_without_accents(xpath, text, driver, timeout=10):
    """
    Seleciona uma opção em um elemento select usando texto sem acentos e dispara o evento change.

    Args:
        xpath: O xpath do elemento select
        text: O texto a ser procurado (sem necessidade de remover acentos)
        driver: O driver do selenium
        timeout: Tempo máximo de espera
    """
    select_element = get_element(xpath, driver, timeout)
    driver.execute_script(
        """
        function removeAccents(str) {
            return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                .replace(/[áàâãä]/g, 'a')
                .replace(/[éèêë]/g, 'e')
                .replace(/[íìîï]/g, 'i')
                .replace(/[óòôõö]/g, 'o')
                .replace(/[úùûü]/g, 'u')
                .replace(/[ÁÀÂÃÄ]/g, 'A')
                .replace(/[ÉÈÊË]/g, 'E')
                .replace(/[ÍÌÎÏ]/g, 'I')
                .replace(/[ÓÒÔÕÖ]/g, 'O')
                .replace(/[ÚÙÛÜ]/g, 'U')
                .replace(/[çÇ]/g, 'c')
        }

        const select = arguments[0];
        const options = select.options;
        const searchText = arguments[1].toLowerCase();
        let optionFound = false;
        
        for (let i = 0; i < options.length; i++) {
            const optionText = removeAccents(options[i].text).toLowerCase();
            if (optionText.includes(searchText)) {
                const oldValue = select.value;
                select.value = options[i].value;
                optionFound = true;
                
                // Dispara o evento change apenas se o valor realmente mudou
                if (oldValue !== options[i].value) {
                    // Cria e dispara o evento change
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                }
                
                break;
            }
        }
        return optionFound;
    """,
        select_element,
        text.replace("'", ""),
    )

def quit_driver(driver):
    if driver is not None:
        driver.quit()

def element_exists(xpath, driver, timeout=10):
    """
    Verifica se um elemento existe na página.

    Args:
        xpath: O xpath do elemento
        driver: O driver do selenium
        timeout: Tempo máximo de espera (use valores baixos para elementos opcionais)

    Returns:
        bool: True se o elemento existe, False caso contrário
    """

    try:
        wait_for_page_load(driver, timeout)
        wait_for_element_to_load(xpath, driver, timeout)
        return True
    except:
        return False

def wait_for_download(download_dir, timeout=30):
    """
    Aguarda até que um download seja concluído na pasta especificada.

    Args:
        download_dir: Diretório onde o download será salvo
        timeout: Tempo máximo de espera em segundos

    Returns:
        str: Caminho do arquivo baixado ou None se nenhum arquivo for encontrado
    """

    start_time = time.time()
    downloaded_file = None

    while time.time() - start_time < timeout:
        # Procura por arquivos .crdownload (downloads em andamento)
        temp_files = glob.glob(os.path.join(download_dir, "*.crdownload"))
        if temp_files:
            time.sleep(0.5)  # Aguarda download
            continue

        # Procura por novos arquivos
        files = glob.glob(os.path.join(download_dir, "*"))
        if files:
            # Pega o arquivo mais recente
            downloaded_file = max(files, key=os.path.getctime)
            break

        time.sleep(0.5)

    return downloaded_file

def configure_download_behavior(driver, download_dir):
    """
    Configura o comportamento de download do Chrome usando o DevTools Protocol.

    Args:
        driver: Instância do WebDriver
        download_dir: Diretório onde os downloads serão salvos
    """

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    # Configura o DevTools para downloads
    driver.execute_cdp_cmd(
        "Browser.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": download_dir,
            "eventsEnabled": True,
        },
    )

#________________________________________________________________________________________________________________________________________________________________________________________________________________
def check_session_expiration(driver, log_signal, processamento_id, step):
    """
    Verifica se a sessão expirou, reportando o resultado via log.
    """
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text

        if "expirou" in alert_text:
            # PADRÃO: Reporta o achado específico.
            log_signal.emit(f"AVISO [Proc. #{processamento_id}]: Sessão expirada. Alerta do sistema encontrado: '{alert_text}'")
            alert.accept()
            print(f"Alerta de expiração: {alert_text}")
        else:
            # PADRÃO: Reporta um alerta inesperado.
            log_signal.emit(f"AVISO [Proc. #{processamento_id}]: Alerta inesperado bloqueando a execução: '{alert_text}'")
            alert.accept()
            print(f"Alerta inesperado: {alert_text}")

    except NoAlertPresentException:
        pass # Sessão OK.
    
    except UnexpectedAlertPresentException as e:
        # PADRÃO: Reporta um alerta inesperado (fallback).
        log_signal.emit(f"AVISO [Proc. #{processamento_id}]: Alerta inesperado (fallback): {e.alert_text}")
        print(f"Alerta inesperado (fallback): {e.alert_text}")

def wait_for_page_load_and_check_session(driver, log_signal, processamento_id, step, timeout=60):
    """
    Espera o carregamento da página e verifica a sessão, com logs padronizados.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        check_session_expiration(driver, log_signal, processamento_id, step)

    except TimeoutException:
        # PADRÃO: Reporta o erro de timeout.
        log_signal.emit(f"ERRO [Proc. #{processamento_id}]: A página ({driver.current_url}) não carregou em {timeout} segundos.")
        raise TimeoutException(f"A página não carregou em {timeout}s.")

## ADICIONAL:

def selecionar_opcao_com_verificacao(driver, xpath_opcao, xpath_elemento_condicional, timeout=5):
    """
    Seleciona uma opção e verifica se um elemento condicional aparece.
    
    Args:
        driver: WebDriver do Selenium
        xpath_opcao: XPath da opção a ser clicada
        xpath_elemento_condicional: XPath do elemento que deve aparecer após o clique (opcional)
        timeout: Tempo máximo de espera pelo elemento condicional
    
    Returns:
        bool: True se o elemento condicional apareceu, False caso contrário
    """
    try:
        click_button(xpath_opcao, driver)
        logging.info(f"Botão de selecionar Tipo de Financiamento clicado.")
        time.sleep(1)  
    except Exception as e:
        logging.error(f"Erro ao clicar no botão: {e}")

    # verificando se elemento condicional aparece:

    xpath_elemento_condicional_aparece = element_exists(xpath_elemento_condicional, driver, timeout=2)

    # Campo de valor do financiamento ENCONTRADO:
 
    if xpath_elemento_condicional_aparece:
        logging.info(f"Campo de valor do financiamento ENCONTRADO!")
        return True

    # Campo de valor do financiamento NÃO ENCONTRADO:

    logging.warning(f"Elemento condicional {xpath_elemento_condicional} não existe! ")

    return False