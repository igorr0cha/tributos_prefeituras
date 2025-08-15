# 🤖 Tributos Prefeituras BOT

## 📖 Sobre o Projeto

Este projeto consiste em uma coleção de BOTs desenvolvidos para automatizar o processo de emissão de guias de tributos em diversas prefeituras do Brasil, agilizando e otimizando a rotina fiscal.

---

## 🏛️ Prefeituras Atendidas

Abaixo está a lista das prefeituras que já possuem automação/estão em desenvolvimento. Clique no link para acessar o portal correspondente.

| Prefeitura | Link para o Portal | Nome do Arquivo/BOT | Observações | Status |
| :--- | :--- | :--- | :--- | :--- |
| 🏙️ **São Paulo (SP)** | [Acessar Portal](https://itbi.prefeitura.sp.gov.br/forms/frm_sql.aspx?tipo=SQL#/) | `sao_paulo.py` |  | _em desenvolvimento_ |
| 🏙️ **Goiânia (GO)** | [Acessar Portal](https://itbi.goiania.go.gov.br/sistemas/saces/asp/saces00000f0.asp?sigla=sisti) | `goiania.py` |  | _em desenvolvimento_ |
| 🏙️ **João Pessoa (PB)** | [Acessar Portal](https://receita.joaopessoa.pb.gov.br/itbi/paginas/portal/login.html) | `joao_pessoa.py` | Ex: Necessita de Login. Uma vez emitido a guia, consta-se na dívida ativa - *ATENÇÃO* | _em desenvolvimento_ |
| *(futuras prefeituras ...)* | | | | |

---

## 🚀 Como Utilizar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/tributos_prefeituras.git](https://github.com/seu-usuario/tributos_prefeituras.git)
    ```
2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure as variáveis de ambiente:**
    - Crie um arquivo `.env` na raiz do projeto.
    - Adicione as credenciais ou caminhos necessários (ex: `USUARIO_PORTAL=seu_usuario`).
4.  **Execute o BOT desejado:**
    ```bash
    python nome_do_bot_cidade.py
    ```

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem Principal:** Python
* **Automação Web:** Selenium / Playwright / etc.
* **Bibliotecas Adicionais:** Pandas / Openpyxl / etc.

---

## 📝 Observações Gerais

* Certifique-se de que os **drivers de navegador** (como o ChromeDriver) estejam atualizados e compatíveis com a versão do seu navegador.
* Alguns portais de prefeitura podem sofrer alterações em seus layouts, o que pode exigir manutenção nos BOTs.
* *Adicione aqui qualquer outra informação ou detalhe importante sobre o projeto.*

---

## 🤝 Como Contribuir

Contribuições são bem-vindas! Se você deseja adicionar um novo BOT para uma prefeitura ou melhorar um existente, siga os passos:

1.  Faça um **Fork** deste repositório.
2.  Crie uma nova **Branch**: `git checkout -b feature/nome-da-cidade`.
3.  Faça suas alterações e **Commite**: `git commit -m 'feat: Adiciona BOT para a cidade X'`.
4.  Envie para a sua Branch: `git push origin feature/nome-da-cidade`.
5.  Abra um **Pull Request**.

---

## 📄 Licença

Este projeto está sob a licença [MIT - colocar licença documentall](link-para-sua-licenca).