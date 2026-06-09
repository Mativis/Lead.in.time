# 🎯 Lead.in.time — CRM de Leads com Google Sheets (API Web App)

**Lead.in.time** é um sistema CRM moderno e elegante construído com **Streamlit** (Python) e integrado ao **Google Sheets** como banco de dados em nuvem. A comunicação é realizada por meio de uma API Web nativa do Google Apps Script protegida por uma chave de segurança (**AuthToken**).

---

## 🚀 Funcionalidades Principais

- **Visual Premium**: Layout responsivo com tema de cores moderno, cartões de métricas responsivos e estilo HSL.
- **Identidade Visual de Status**: Indicação clara de Consulta e Cirurgia com badges coloridos e intuitivos:
  - ⏳ **Pendente** (Amarelo)
  - ✅ **Realizado** (Verde)
  - ❌ **Não realizado** (Vermelho)
- **Controle de Acesso (RBAC)**:
  - **Administrador**: Gerenciamento total de leads, exclusão de registros, gerenciamento de usuários e acesso à vigilância de logs de auditoria.
  - **Usuário Padrão**: Criação e edição de leads. A exclusão de registros é estritamente bloqueada.
- **Logs de Auditoria Críticos**: Auditoria minuciosa que mapeia quem executou a ação, quando e, em caso de atualizações, qual campo foi alterado, mostrando o valor anterior e o novo valor.
- **Formatos Locais**: Datas no formato brasileiro `DD-MM-YYYY`.
- **Dashboards e Relatórios**: Métricas de topo de funil, gráficos comparativos de conversão e exportador de dados para CSV com filtros.

---

## 🛠️ Guia de Configuração Simplificado (Passo a Passo)

Você **não** precisa configurar nada no Google Cloud Console (GCP). Toda a conexão é feita via Google Apps Script.

### Passo 1: Configurar a Planilha Google
1. Crie uma nova planilha vazia no seu [Google Sheets](https://sheets.google.com).
2. Acesse **Extensões > Apps Script** no menu superior.
3. Apague o código padrão e cole o conteúdo do arquivo [AppScript.js](file:///c:/Users/Joaom/Documents/Lead.in.time/AppScript.js).
4. No topo do script, você verá a linha:
   ```javascript
   const AUTH_TOKEN = "LEAD_IN_TIME_SECRET_TOKEN";
   ```
   Altere `"LEAD_IN_TIME_SECRET_TOKEN"` para um token/senha de sua preferência (guarde essa chave, pois você precisará dela para configurar o Streamlit).
5. Salve o arquivo (ícone do disquete).
6. Volte à planilha e recarregue a página. Você verá um novo menu chamado **"Sistema de Leads"** no topo.
7. Clique em **"Sistema de Leads" > "Configurar Banco de Dados"** e autorize a execução do script. Ele criará as abas `leads`, `users` e `logs` com os cabeçalhos e as contas de teste iniciais.

### Passo 2: Publicar a API (Web App)
1. No editor do Apps Script, clique no botão **Implantar** (canto superior direito) > **Nova implantação**.
2. Clique no ícone de engrenagem ao lado de "Selecionar tipo" e escolha **Aplicativo da Web**.
3. Defina as configurações:
   - **Descrição**: API CRM Leads
   - **Executar como**: Eu (seu-email@gmail.com)
   - **Quem tem acesso**: Qualquer pessoa (*Nota: Qualquer pessoa poderá enviar dados para a URL, mas a requisição será sumariamente rejeitada caso o AuthToken não seja idêntico ao definido no Passo 1, garantindo segurança total*).
4. Clique em **Implantar** e autorize o acesso à sua conta.
5. Copie a **URL do aplicativo da Web** gerada (ex: `https://script.google.com/macros/s/.../exec`).

### Passo 3: Executar o Aplicativo
1. Inicie o sistema rodando o arquivo `run.py`:
   ```bash
   python run.py
   ```
2. O sistema detectará que não há conexões salvas e abrirá o assistente de setup no seu navegador.
3. Cole a **URL do Web App** obtida no Passo 2 e o seu **AuthToken** nos campos indicados e clique em **Salvar e Conectar**.
4. O app salvará as chaves localmente nos arquivos `web_app_url.txt` e `auth_token.txt` e iniciará a tela de Login!

---

## 🔑 Credenciais Padrão do Sistema
Após a configuração da planilha pelo Apps Script, os seguintes acessos estarão configurados:

| Perfil | Usuário (Username) | Senha | Nível de Acesso |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Acesso completo, exclusões, logs de auditoria e cadastro de usuários |
| **Usuário Padrão** | `user` | `user123` | Leitura, cadastro e edição de leads. Sem exclusões ou visualização de logs |

> 💡 *Você pode alterar sua senha a qualquer momento na aba **Configurações**.*

---

## 📂 Estrutura do Projeto

* `app.py`: Interface Streamlit, roteamento de páginas e customizações visuais.
* `db_manager.py`: Conector HTTP que conversa com a API do Google Sheets transmitindo o AuthToken.
* `run.py`: Executável inteligente que verifica e instala dependências e inicia o Streamlit.
* `AppScript.js`: Script de API e estruturação automática a ser rodado dentro do Google Sheets.
* `requirements.txt`: Lista de dependências Python.
