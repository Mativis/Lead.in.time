import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
from db_manager import DatabaseManager

def parse_date_safely(date_val):
    """Converte datas brasileiras DD-MM-YYYY ou ISO com segurança, evitando ambiguidades no pandas."""
    if pd.isna(date_val) or not date_val:
        return pd.NaT
    date_str = str(date_val).strip()
    try:
        # Tenta o formato DD-MM-YYYY
        return pd.to_datetime(date_str, format="%d-%m-%Y", errors="raise")
    except Exception:
        try:
            # Tenta formato ISO ou formato padrão do pandas
            return pd.to_datetime(date_str, errors="coerce")
        except Exception:
            return pd.NaT

def format_br_date(date_val):
    """Formata uma data para o padrão brasileiro DD/MM/YYYY"""
    if pd.isna(date_val) or not date_val:
        return "Data não informada"
    try:
        # Se for string, tenta converter
        if isinstance(date_val, str):
            date_obj = parse_date_safely(date_val)
        else:
            date_obj = date_val
        
        # Se for Timestamp ou datetime, formata
        if pd.notna(date_obj):
            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime("%d/%m/%Y")
            else:
                return str(date_obj)
        return "Data inválida"
    except Exception:
        return str(date_val)

# Configuração da página Streamlit
st.set_page_config(
    page_title="Lead.in.time - CRM de Leads",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar gerenciador de banco de dados
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

db = st.session_state.db

# Injeção de CSS customizado para aparência premium
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        
        /* Fontes globais */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Título do Sidebar */
        .sidebar-title {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 1.8rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* Badges de Status elegantes */
        .badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin: 2px;
        }
        .badge-pending {
            background-color: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border-color: rgba(245, 158, 11, 0.3);
        }
        .badge-done {
            background-color: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border-color: rgba(16, 185, 129, 0.3);
        }
        .badge-cancelled {
            background-color: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border-color: rgba(239, 68, 68, 0.3);
        }
        
        /* Cartões de Métrica Premium */
        .metric-card-custom {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-radius: 12px;
            padding: 22px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: white;
            margin-bottom: 15px;
        }
        .metric-card-custom:hover {
            transform: translateY(-4px);
            border-color: rgba(59, 130, 246, 0.4);
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
        }
        .metric-title {
            font-size: 0.9rem;
            color: #94a3b8;
            font-weight: 500;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .metric-desc {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 5px;
        }
        
        /* Container do formulário */
        .form-container {
            background-color: rgba(30, 41, 59, 0.3);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Cartões de Métrica Financeira com Borda Colorida */
        .metric-card-financial {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-radius: 12px;
            padding: 12px 14px;
            border-left: 5px solid #3b82f6;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: white;
            margin-bottom: 15px;
        }
        .metric-card-financial:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }
        .metric-card-financial .metric-title {
            font-size: 0.75rem !important;
            color: #94a3b8 !important;
            font-weight: 600 !important;
            margin-bottom: 4px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        .metric-card-financial .metric-value {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            color: #f8fafc !important;
        }
        .metric-card-financial .metric-desc {
            font-size: 0.68rem !important;
            color: #64748b !important;
            margin-top: 4px !important;
        }
        .card-blue { border-left-color: #3b82f6; }
        .card-green { border-left-color: #10b981; }
        .card-yellow { border-left-color: #f59e0b; }
        .card-red { border-left-color: #ef4444; }

        /* Estilos do Funil de Vendas */
        .funnel-container {
            margin: 20px 0;
            display: flex;
            flex-direction: column;
            gap: 12px;
            width: 100%;
        }
        .funnel-stage-wrapper {
            display: flex;
            align-items: center;
            width: 100%;
        }
        .funnel-stage {
            padding: 14px 22px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            transition: width 0.5s ease-in-out;
        }
        .funnel-stage-1 {
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
            width: 100%;
        }
        .funnel-stage-2 {
            background: linear-gradient(90deg, #8b5cf6, #6d28d9);
        }
        .funnel-stage-3 {
            background: linear-gradient(90deg, #10b981, #047857);
        }
        .funnel-label {
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .funnel-value {
            font-size: 1.15rem;
            font-weight: 700;
        }
        .funnel-conversion-rate {
            color: #f8fafc;
            font-size: 0.9rem;
            background: rgba(255,255,255,0.15);
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

def render_status_badge(status: str) -> str:
    """Retorna o código HTML para a badge correspondente ao status."""
    if status == "Realizado":
        return f'<span class="badge badge-done">✅ Realizado</span>'
    elif status == "Não realizado":
        return f'<span class="badge badge-cancelled">❌ Não realizado</span>'
    else:
        return f'<span class="badge badge-pending">⏳ Pendente</span>'

# --- TELA DE ASSISTENTE DE CREDENCIAIS ---
if not db.is_configured():
    st.title("🎯 Bem-vindo ao Lead.in.time")
    st.subheader("Configuração Inicial do Banco de Dados (AuthToken)")
    
    st.info("Para que o sistema funcione, você precisa conectar a URL do Web App gerada na sua planilha Google Sheets e informar o AuthToken definido.")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Passo a Passo para Configuração:
        1. **Crie a Planilha Google**: Crie uma nova planilha vazia.
        2. **Configure o Apps Script**: 
           - Acesse **Extensões > Apps Script** na planilha.
           - Cole todo o código do arquivo `AppScript.js`.
           - Escolha seu **AuthToken** na variável no topo do código.
           - Clique em **Salvar** (ícone de disquete).
        3. **Inicialize as Tabelas**:
           - Na planilha recém-recarregada, clique no menu superior **"Sistema de Leads" > "Configurar Banco de Dados"** e autorize.
        4. **Implante como Web App**:
           - No editor do Apps Script, clique em **Implantar > Nova implantação**.
           - Clique no ícone de engrenagem e escolha **Aplicativo da Web**.
           - Em *Quem tem acesso*, selecione **Qualquer pessoa**.
           - Clique em **Implantar**, dê as permissões e copie a **URL do aplicativo da Web** gerada.
        """)
        
        # Formulário de configuração
        with st.form("config_form"):
            web_app_url = st.text_input("URL do Web App do Google", placeholder="https://script.google.com/macros/s/.../exec")
            auth_token = st.text_input("Chave de Verificação (AuthToken)", type="password", placeholder="Chave secreta configurada no script")
            submit_config = st.form_submit_button("Salvar e Conectar")
            
            if submit_config:
                if not web_app_url or not auth_token:
                    st.error("Por favor, preencha todos os campos.")
                elif not web_app_url.startswith("https://script.google.com/"):
                    st.error("A URL fornecida parece não ser um Web App válido do Google.")
                else:
                    try:
                        db.save_configuration(web_app_url, auth_token)
                        st.success("Configuração salva com sucesso! Conectando...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar configuração: {e}")
                        
    with col2:
        st.markdown("### Exemplo da Estrutura das Abas")
        st.code("""
leads:
ID | Nome | Data Contato | Material de Interesse | ...

users:
Username | Nome | Password Hash | Role

logs:
Data/Hora | Usuário | Ação | ID do Lead | ...
        """, language="text")
        
    st.stop()

# --- TELA DE LOGIN ---
if 'user' not in st.session_state:
    st.markdown('<div style="text-align: center; margin-top: 50px;">', unsafe_allow_html=True)
    st.markdown('<h1 class="sidebar-title" style="font-size: 3rem;">Gerenciamento Inteligente de Leads</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>Acesso ao Sistema</h3>", unsafe_allow_html=True)
            username_input = st.text_input("Nome de Usuário (Username)", placeholder="Ex: admin").strip()
            password_input = st.text_input("Senha", type="password", placeholder="Sua senha")
            login_btn = st.form_submit_button("Entrar", use_container_width=True)
            
            if login_btn:
                if not username_input or not password_input:
                    st.error("Preencha todos os campos para continuar.")
                else:
                    with st.spinner("Autenticando..."):
                        try:
                            user_data = db.authenticate_user(username_input, password_input)
                            
                            if user_data:
                                st.session_state.user = user_data
                                st.success(f"Bem-vindo, {user_data['nome']}!")
                                st.rerun()
                            else:
                                st.error("Usuário ou senha incorretos.")
                        except Exception as e:
                            st.error(f"Erro de conexão com o banco de dados: {e}")
                            st.info("Verifique se o Web App da Planilha está acessível e se o AuthToken está correto.")
                            
    st.stop()

# --- MENU LATERAL (SIDEBAR) ---
current_user = st.session_state.user

with st.sidebar:
    st.markdown(f'<div class="sidebar-title">Lead.in.time</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.05);">
        <span style="font-size: 0.8rem; color: #94a3b8; display: block;">Usuário Ativo:</span>
        <span style="font-weight: 600; color: #f8fafc; font-size: 1.05rem;">{current_user['nome']}</span>
        <span style="display: block; font-size: 0.75rem; color: #3b82f6; font-weight: 600; text-transform: uppercase;">Role: {current_user['role']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Opções do Menu
    menu_options = ["📈 Dashboards e Relatórios", "🗂️ Gerenciador de Leads", "➕ Adicionar Lead"]
    
    # Apenas Admin visualiza Logs de Alterações
    if current_user['role'] == "Admin":
        menu_options.append("📜 Log de Alterações")
        
    menu_options.append("⚙️ Configurações")
    
    page = st.radio("Navegação", menu_options)
    
    st.markdown("<br><hr style='opacity: 0.15;'><br>", unsafe_allow_html=True)
    
    # Botão de Logout
    if st.button("🚪 Sair do Sistema", use_container_width=True):
        del st.session_state.user
        st.rerun()

# --- CARREGAR DADOS DO GOOGLE SHEETS ---
@st.cache_data(ttl=60) # Cache de 60 segundos para evitar requisições duplicadas
def fetch_leads_cached():
    return db.get_leads()

try:
    df_leads = fetch_leads_cached()
except Exception as e:
    st.error(f"Erro ao carregar banco de dados: {e}")
    st.info("Caso queira reconfigurar o acesso à planilha, remova os arquivos `web_app_url.txt` e `auth_token.txt` locais.")
    st.stop()

# --- CONTROLE DE PÁGINAS ---

# 1. DASHBOARDS E RELATÓRIOS
if page == "📈 Dashboards e Relatórios":
    st.title("📈 Dashboards e Relatórios")
    st.markdown("Visão analítica criteriosa e exportação de dados do sistema de leads.")
    
    if df_leads.empty:
        st.warning("Nenhum lead cadastrado no momento. Insira registros para visualizar gráficos e métricas.")
    else:
        # Converter coluna de data para objeto datetime de forma robusta
        df_leads_with_dates = df_leads.copy()
        
        # Aplicar parse_date_safely e garantir que seja timezone-naive
        df_leads_with_dates["_Datetime"] = df_leads_with_dates["Data Contato"].apply(parse_date_safely)
        # Remover timezone se existir
        df_leads_with_dates["_Datetime"] = pd.to_datetime(df_leads_with_dates["_Datetime"], errors='coerce')
        df_leads_with_dates["_Datetime"] = df_leads_with_dates["_Datetime"].dt.tz_localize(None)
        
        # Remover linhas com data inválida
        df_leads_with_dates = df_leads_with_dates.dropna(subset=['_Datetime'])
        
        if df_leads_with_dates.empty:
            st.warning("Nenhum lead com data válida encontrado.")
        else:
            # Obter datas min/max para inicializar seletores
            min_date_val = df_leads_with_dates["_Datetime"].min().date()
            max_date_val = df_leads_with_dates["_Datetime"].max().date()
            
            # Filtro de Data Global
            st.markdown("<div class='form-container' style='margin-bottom: 25px;'>", unsafe_allow_html=True)
            st.subheader("📅 Filtro de Período")
            col_d1, col_d2, col_d3 = st.columns([2, 2, 2])
            with col_d1:
                data_de = st.date_input("De", min_date_val, min_value=min_date_val, max_value=max_date_val)
            with col_d2:
                data_ate = st.date_input("Até", max_date_val, min_value=min_date_val, max_value=max_date_val)
            with col_d3:
                st.markdown("<br>", unsafe_allow_html=True)
                ignore_date = st.checkbox("Ver todo o histórico (ignorar filtro de data)", value=False)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Converter os valores do date_input para Timestamp
            data_de_ts = pd.to_datetime(data_de)
            data_ate_ts = pd.to_datetime(data_ate) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            
            # Filtrar o dataframe principal para o dashboard
            if ignore_date:
                df_leads_dash = df_leads_with_dates.copy()
            else:
                df_leads_dash = df_leads_with_dates[
                    (df_leads_with_dates["_Datetime"] >= data_de_ts) &
                    (df_leads_with_dates["_Datetime"] <= data_ate_ts)
                ]
            
            if df_leads_dash.empty:
                st.warning("Nenhum lead encontrado para o período selecionado. Tente ampliar o intervalo de datas.")
            else:
                # Cálculos de Métricas
                total_leads = len(df_leads_dash)
                total_valor = df_leads_dash["Valor"].sum()
                ticket_medio = df_leads_dash["Valor"].mean() if total_leads > 0 else 0.0
                
                # Faturamento por Status de Cirurgia
                faturamento_confirmado = df_leads_dash[df_leads_dash["Status Cirurgia"] == "Realizado"]["Valor"].sum()
                faturamento_pendente = df_leads_dash[df_leads_dash["Status Cirurgia"] == "Pendente"]["Valor"].sum()
                faturamento_perdido = df_leads_dash[df_leads_dash["Status Cirurgia"] == "Não realizado"]["Valor"].sum()
                
                # Contagens para o Funil
                consultas_realizadas = len(df_leads_dash[df_leads_dash["Status Consulta"] == "Realizado"])
                cirurgias_realizadas = len(df_leads_dash[df_leads_dash["Status Cirurgia"] == "Realizado"])
                
                # Taxas de conversão
                taxa_consulta_total = (consultas_realizadas / total_leads * 100) if total_leads > 0 else 0.0
                taxa_cirurgia_total = (cirurgias_realizadas / total_leads * 100) if total_leads > 0 else 0.0
                taxa_cirurgia_consulta = (cirurgias_realizadas / consultas_realizadas * 100) if consultas_realizadas > 0 else 0.0
                
                # Inicializar Abas
                tab_resumo, tab_graficos, tab_procedimentos, tab_exportar = st.tabs([
                    "📊 Resumo & Funil", 
                    "📈 Gráficos & Tendências", 
                    "🏷️ Desempenho por Procedimento", 
                    "📥 Relatório & Exportação"
                ])
                
                # --- TAB 1: RESUMO & FUNIL ---
                with tab_resumo:
                    st.subheader("Painel Financeiro")
                    col_m1, col_m2 = st.columns(2)
                    
                    with col_m1:
                        st.markdown(f"""
                        <div class="metric-card-financial card-green">
                            <div class="metric-title">Faturamento Confirmado</div>
                            <div class="metric-value">R$ {faturamento_confirmado:,.2f}</div>
                            <div class="metric-desc">Cirurgias concluídas com sucesso</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_m2:
                        st.markdown(f"""
                        <div class="metric-card-financial card-yellow">
                            <div class="metric-title">Faturamento Pendente</div>
                            <div class="metric-value">R$ {faturamento_pendente:,.2f}</div>
                            <div class="metric-desc">Cirurgias com status pendente</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    col_m3, col_m4 = st.columns(2)
                        
                    with col_m3:
                        st.markdown(f"""
                        <div class="metric-card-financial card-red">
                            <div class="metric-title">Faturamento Perdido</div>
                            <div class="metric-value">R$ {faturamento_perdido:,.2f}</div>
                            <div class="metric-desc">Cirurgias não realizadas</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_m4:
                        st.markdown(f"""
                        <div class="metric-card-financial card-blue">
                            <div class="metric-title">Pipeline Total</div>
                            <div class="metric-value">R$ {total_valor:,.2f}</div>
                            <div class="metric-desc">Valor total potencial dos leads</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Cards Secundários
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.markdown(f"""
                        <div class="metric-card-custom">
                            <div class="metric-title">Ticket Médio (Lead)</div>
                            <div class="metric-value">R$ {ticket_medio:,.2f}</div>
                            <div class="metric-desc">Valor médio por lead no período</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s2:
                        st.markdown(f"""
                        <div class="metric-card-custom">
                            <div class="metric-title">Taxa de Conversão em Consulta</div>
                            <div class="metric-value">{taxa_consulta_total:.1f}%</div>
                            <div class="metric-desc">{consultas_realizadas} consultas concluídas de {total_leads} leads</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s3:
                        st.markdown(f"""
                        <div class="metric-card-custom">
                            <div class="metric-title">Taxa de Conversão Cirúrgica</div>
                            <div class="metric-value">{taxa_cirurgia_total:.1f}%</div>
                            <div class="metric-desc">{cirurgias_realizadas} cirurgias de {total_leads} leads ({taxa_cirurgia_consulta:.1f}% pós-consulta)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.subheader("🎯 Funil de Vendas e Conversão")
                    st.markdown("Acompanhe a eficiência da jornada do lead desde a captação até o procedimento cirúrgico final.")
                    
                    # Funil Visual Customizado em HTML/CSS
                    w_leads = 100
                    w_consultas = max(15, min(100, taxa_consulta_total))
                    w_cirurgias = max(15, min(100, taxa_cirurgia_total))
                    
                    st.markdown(f"""
                    <div class="funnel-container">
                        <div class="funnel-stage-wrapper">
                            <div class="funnel-stage funnel-stage-1" style="width: {w_leads}%;">
                                <span class="funnel-label">📥 1. Leads de Entrada</span>
                                <span class="funnel-value">{total_leads} leads <span class="funnel-conversion-rate">100%</span></span>
                            </div>
                        </div>
                        <div class="funnel-stage-wrapper">
                            <div class="funnel-stage funnel-stage-2" style="width: {w_consultas}%;">
                                <span class="funnel-label">🩺 2. Consultas Realizadas</span>
                                <span class="funnel-value">{consultas_realizadas} consultas <span class="funnel-conversion-rate">{taxa_consulta_total:.1f}% do total</span></span>
                            </div>
                        </div>
                        <div class="funnel-stage-wrapper">
                            <div class="funnel-stage funnel-stage-3" style="width: {w_cirurgias}%;">
                                <span class="funnel-label">🔪 3. Cirurgias Concluídas</span>
                                <span class="funnel-value">{cirurgias_realizadas} cirurgias <span class="funnel-conversion-rate">{taxa_cirurgia_total:.1f}% do total</span></span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Adicionar dica de negócios
                    st.info("💡 **Dica de Otimização:** Focar no aumento da taxa de conversão de Consultas para Cirurgias (atualmente de {:.1f}%) é o caminho mais curto para aumentar o faturamento sem gastar mais com novos leads.".format(taxa_cirurgia_consulta))
                
                # --- TAB 2: GRÁFICOS & TENDÊNCIAS ---
                with tab_graficos:
                    st.subheader("Tendências e Distribuições")
                    col_c1, col_c2 = st.columns(2)
                    
                    with col_c1:
                        # Distribuição de Status Consulta
                        df_status_c = df_leads_dash["Status Consulta"].value_counts().reset_index()
                        df_status_c.columns = ["Status", "Quantidade"]
                        
                        chart_c = alt.Chart(df_status_c).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta("Quantidade:Q"),
                            color=alt.Color("Status:N", scale=alt.Scale(
                                domain=["Pendente", "Realizado", "Não realizado"],
                                range=["#f59e0b", "#10b981", "#ef4444"]
                            ), title="Status Consulta"),
                            tooltip=["Status", "Quantidade"]
                        ).properties(
                            title="Distribuição - Status Consulta",
                            height=280
                        )
                        st.altair_chart(chart_c, use_container_width=True)
                        
                    with col_c2:
                        # Distribuição de Status Cirurgia
                        df_status_s = df_leads_dash["Status Cirurgia"].value_counts().reset_index()
                        df_status_s.columns = ["Status", "Quantidade"]
                        
                        chart_s = alt.Chart(df_status_s).mark_arc(innerRadius=50).encode(
                            theta=alt.Theta("Quantidade:Q"),
                            color=alt.Color("Status:N", scale=alt.Scale(
                                domain=["Pendente", "Realizado", "Não realizado"],
                                range=["#f59e0b", "#10b981", "#ef4444"]
                            ), title="Status Cirurgia"),
                            tooltip=["Status", "Quantidade"]
                        ).properties(
                            title="Distribuição - Status Cirurgia",
                            height=280
                        )
                        st.altair_chart(chart_s, use_container_width=True)
                    
                    st.markdown("<br><hr>", unsafe_allow_html=True)
                    
                    # Gráficos Temporais (Linha do Tempo)
                    st.subheader("Evolução Mensal de Captação e Faturamento")
                    
                    # Agrupar leads por mês de contato
                    df_leads_dash = df_leads_dash.copy()
                    df_leads_dash["Mes_Ano"] = df_leads_dash["_Datetime"].dt.strftime("%Y-%m")
                    
                    if df_leads_dash["Mes_Ano"].dropna().empty:
                        st.info("Dados temporais indisponíveis para gerar gráficos de evolução.")
                    else:
                        df_temporal = df_leads_dash.groupby("Mes_Ano").agg(
                            Qtd_Leads=("ID", "count"),
                            Faturamento_Potencial=("Valor", "sum")
                        ).reset_index()
                        
                        # Calcular Faturamento Realizado por mês
                        realizados_por_mes = df_leads_dash[df_leads_dash["Status Cirurgia"] == "Realizado"].groupby("Mes_Ano")["Valor"].sum().reset_index()
                        realizados_por_mes.columns = ["Mes_Ano", "Faturamento_Realizado"]
                        
                        df_temporal = pd.merge(df_temporal, realizados_por_mes, on="Mes_Ano", how="left").fillna(0.0)
                        df_temporal = df_temporal.sort_values("Mes_Ano")
                        
                        col_t1, col_t2 = st.columns(2)
                        
                        with col_t1:
                            # Gráfico de Linha: Leads captados por mês
                            chart_leads_time = alt.Chart(df_temporal).mark_area(
                                line={"color": "#3b82f6"},
                                color=alt.Gradient(
                                    gradient="linear",
                                    stops=[alt.GradientStop(color="#3b82f6", offset=0),
                                           alt.GradientStop(color="transparent", offset=1)],
                                    x1=1, y1=1, x2=1, y2=0
                                ),
                                opacity=0.3
                            ).encode(
                                x=alt.X("Mes_Ano:N", title="Mês/Ano"),
                                y=alt.Y("Qtd_Leads:Q", title="Qtd. Novos Leads"),
                                tooltip=["Mes_Ano", "Qtd_Leads"]
                            ).properties(
                                title="Volume de Entrada de Leads",
                                height=300
                            )
                            st.altair_chart(chart_leads_time, use_container_width=True)
                            
                        with col_t2:
                            # Gráfico de Barras Agrupado: Faturamento Potencial vs Realizado
                            df_temp_melt = df_temporal.melt(
                                id_vars=["Mes_Ano"], 
                                value_vars=["Faturamento_Potencial", "Faturamento_Realizado"],
                                var_name="Tipo Faturamento",
                                value_name="Valor (R$)"
                            )
                            df_temp_melt["Tipo Faturamento"] = df_temp_melt["Tipo Faturamento"].replace({
                                "Faturamento_Potencial": "Potencial",
                                "Faturamento_Realizado": "Realizado (Confirmado)"
                            })
                            
                            chart_revenue_time = alt.Chart(df_temp_melt).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                                x=alt.X("Mes_Ano:N", title="Mês/Ano"),
                                y=alt.Y("Valor (R$):Q", title="Faturamento (R$)"),
                                color=alt.Color("Tipo Faturamento:N", scale=alt.Scale(
                                    domain=["Potencial", "Realizado (Confirmado)"],
                                    range=["#3b82f6", "#10b981"]
                                ), title="Tipo"),
                                xOffset="Tipo Faturamento:N",
                                tooltip=["Mes_Ano", "Tipo Faturamento", "Valor (R$)"]
                            ).properties(
                                title="Faturamento Potencial vs Confirmado",
                                height=300
                            )
                            st.altair_chart(chart_revenue_time, use_container_width=True)
                
                # --- TAB 3: DESEMPENHO POR PROCEDIMENTO ---
                with tab_procedimentos:
                    st.subheader("Desempenho por Procedimento / Material de Interesse")
                    st.markdown("Análise de lucratividade, volumes e taxa de fechamento por tipo de serviço.")
                    
                    # Agrupar dados por Material de Interesse
                    df_material = df_leads_dash.groupby("Material de Interesse").agg(
                        Total_Leads=("ID", "count"),
                        Valor_Potencial=("Valor", "sum")
                    ).reset_index()
                    
                    # Calcular Cirurgias Realizadas e Faturamento Confirmado por Material
                    cirurgias_realizadas_mat = df_leads_dash[df_leads_dash["Status Cirurgia"] == "Realizado"].groupby("Material de Interesse").agg(
                        Cirurgias_Realizadas=("Status Cirurgia", "count"),
                        Faturamento_Confirmado=("Valor", "sum")
                    ).reset_index()
                    
                    df_material = pd.merge(df_material, cirurgias_realizadas_mat, on="Material de Interesse", how="left").fillna(0.0)
                    
                    # Cálculos adicionais
                    df_material["Taxa_Conversao"] = (df_material["Cirurgias_Realizadas"] / df_material["Total_Leads"] * 100)
                    df_material["Ticket_Medio"] = (df_material["Valor_Potencial"] / df_material["Total_Leads"])
                    
                    # Ordenar por volume de faturamento confirmado
                    df_material = df_material.sort_values(by="Faturamento_Confirmado", ascending=False).reset_index(drop=True)
                    
                    if df_material.empty:
                        st.info("Nenhum material encontrado.")
                    else:
                        # Mostrar Gráfico comparativo de materiais de interesse
                        chart_mat_perf = alt.Chart(df_material).mark_bar(cornerRadiusEnd=4).encode(
                            y=alt.Y("Material de Interesse:N", title="Material/Procedimento", sort="-x"),
                            x=alt.X("Faturamento_Confirmado:Q", title="Faturamento Confirmado (R$)"),
                            color=alt.value("#10b981"),
                            tooltip=["Material de Interesse", "Total_Leads", "Faturamento_Confirmado", "Taxa_Conversao"]
                        ).properties(
                            title="Procedimentos mais Lucrativos (Faturamento Confirmado)",
                            height=280
                        )
                        st.altair_chart(chart_mat_perf, use_container_width=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Tabela de Desempenho Estilizada
                        df_material_display = df_material.copy()
                        df_material_display["Valor_Potencial"] = df_material_display["Valor_Potencial"].apply(lambda v: f"R$ {v:,.2f}")
                        df_material_display["Faturamento_Confirmado"] = df_material_display["Faturamento_Confirmado"].apply(lambda v: f"R$ {v:,.2f}")
                        df_material_display["Ticket_Medio"] = df_material_display["Ticket_Medio"].apply(lambda v: f"R$ {v:,.2f}")
                        df_material_display["Taxa_Conversao"] = df_material_display["Taxa_Conversao"].apply(lambda v: f"{v:.1f}%")
                        
                        df_material_display.columns = [
                            "Material de Interesse", "Total Leads", "Valor Potencial", 
                            "Cirurgias Concluídas", "Faturamento Realizado", "Taxa Conversão", "Ticket Médio"
                        ]
                        
                        st.dataframe(df_material_display, use_container_width=True)
                
                # --- TAB 4: RELATÓRIO & EXPORTAÇÃO ---
                with tab_exportar:
                    st.subheader("Exportador Avançado de Dados")
                    
                    # Filtros adicionais interativos específicos para a exportação
                    col_ef1, col_ef2, col_ef3 = st.columns(3)
                    with col_ef1:
                        export_consulta = st.multiselect(
                            "Filtrar Status de Consulta", 
                            ["Pendente", "Realizado", "Não realizado"], 
                            default=["Pendente", "Realizado", "Não realizado"],
                            key="exp_c"
                        )
                    with col_ef2:
                        export_cirurgia = st.multiselect(
                            "Filtrar Status de Cirurgia", 
                            ["Pendente", "Realizado", "Não realizado"], 
                            default=["Pendente", "Realizado", "Não realizado"],
                            key="exp_s"
                        )
                    with col_ef3:
                        materiais_unicos = sorted(list(df_leads_dash["Material de Interesse"].unique()))
                        export_material = st.multiselect(
                            "Filtrar por Material de Interesse", 
                            materiais_unicos, 
                            default=materiais_unicos,
                            key="exp_m"
                        )
                    
                    # Filtros adicionais de busca e valor
                    col_ef4, col_ef5 = st.columns([2, 2])
                    with col_ef4:
                        export_busca = st.text_input("🔍 Buscar por nome do Lead", placeholder="Digite um nome para filtrar...", key="exp_b")
                    with col_ef5:
                        min_val = float(df_leads_dash["Valor"].min()) if not df_leads_dash["Valor"].empty else 0.0
                        max_val = float(df_leads_dash["Valor"].max()) if not df_leads_dash["Valor"].empty else 100000.0
                        if min_val == max_val:
                            max_val = min_val + 1000.0
                        
                        export_valores = st.slider(
                            "Filtrar Faixa de Valor (R$)", 
                            min_value=float(min_val), 
                            max_value=float(max_val), 
                            value=(float(min_val), float(max_val)),
                            format="R$ %.2f",
                            key="exp_v"
                        )
                    
                    # Filtragem no DataFrame
                    filtered_export_df = df_leads_dash[
                        (df_leads_dash["Status Consulta"].isin(export_consulta)) &
                        (df_leads_dash["Status Cirurgia"].isin(export_cirurgia)) &
                        (df_leads_dash["Material de Interesse"].isin(export_material)) &
                        (df_leads_dash["Valor"] >= export_valores[0]) &
                        (df_leads_dash["Valor"] <= export_valores[1])
                    ]
                    
                    if export_busca:
                        filtered_export_df = filtered_export_df[
                            filtered_export_df["Nome"].str.lower().str.contains(export_busca.lower())
                        ]
                    
                    st.markdown(f"**Leads Filtrados:** {len(filtered_export_df)} de {len(df_leads_dash)}")
                    
                    # Exibição da tabela final formatada
                    display_export_df = filtered_export_df.copy()
                    display_export_df["Valor"] = display_export_df["Valor"].apply(lambda v: f"R$ {v:,.2f}")
                    # Formatar a data para exibição
                    display_export_df["Data Contato"] = display_export_df["Data Contato"].apply(format_br_date)
                    st.dataframe(display_export_df[[
                        "Nome", "Data Contato", "Material de Interesse", "Valor", 
                        "Status Consulta", "Status Cirurgia", "Observações", "Criado Por", "Criado Em"
                    ]], use_container_width=True)
                    
                    # Botão de exportação
                    cols_to_drop = ["_Datetime", "Mes_Ano"]
                    cols_to_drop = [col for col in cols_to_drop if col in filtered_export_df.columns]
                    csv_data_exp = filtered_export_df.drop(columns=cols_to_drop, errors="ignore").to_csv(index=False, encoding="utf-8-sig")
                    st.download_button(
                        label="📥 Exportar Dados Filtrados (CSV)",
                        data=csv_data_exp,
                        file_name=f"relatorio_leads_completo_{datetime.now().strftime('%d_%m_%Y')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

# 2. GERENCIADOR DE LEADS (COM DATAS FORMATADAS)
elif page == "🗂️ Gerenciador de Leads":
    st.title("🗂️ Gerenciador de Leads")
    st.markdown("Visualize, busque, edite e gerencie as informações de leads.")
    
    # Campo de busca e filtros rápidos
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("🔍 Buscar lead por Nome ou Observação", placeholder="Digite para buscar...")
    with col_s2:
        status_c_filter = st.selectbox("Status Consulta", ["Todos", "Pendente", "Realizado", "Não realizado"])
    with col_s3:
        status_s_filter = st.selectbox("Status Cirurgia", ["Todos", "Pendente", "Realizado", "Não realizado"])
        
    # Aplicar filtros
    filtered_df = df_leads.copy()
    
    if search_query:
        query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["Nome"].str.lower().str.contains(query) | 
            filtered_df["Observações"].str.lower().str.contains(query)
        ]
        
    if status_c_filter != "Todos":
        filtered_df = filtered_df[filtered_df["Status Consulta"] == status_c_filter]
        
    if status_s_filter != "Todos":
        filtered_df = filtered_df[filtered_df["Status Cirurgia"] == status_s_filter]
        
    if filtered_df.empty:
        st.info("Nenhum lead encontrado com os filtros aplicados.")
    else:
        # Armazenar ID do lead que está sendo editado ou excluído em session_state
        if 'edit_lead_id' not in st.session_state:
            st.session_state.edit_lead_id = None
        if 'delete_lead_id' not in st.session_state:
            st.session_state.delete_lead_id = None

        # Exibição em cartões expansíveis interativos (visual premium)
        for idx, row in filtered_df.iterrows():
            lead_id = str(row["ID"])
            lead_name = str(row["Nome"])
            
            # Badge de status de consulta e cirurgia para colocar no título do expander
            badge_c = render_status_badge(row["Status Consulta"])
            badge_s = render_status_badge(row["Status Cirurgia"])
            
            # Formatar a data para exibição
            data_formatada = format_br_date(row["Data Contato"])
            
            with st.expander(f"👤 {lead_name} — {row['Material de Interesse']} (R$ {float(row['Valor']):,.2f})", expanded=(st.session_state.edit_lead_id == lead_id)):
                # Detalhamento do Lead em Colunas
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    # Usar data formatada aqui
                    st.markdown(f"**Data de Contato:** {data_formatada}")
                    st.markdown(f"**Material de Interesse:** {row['Material de Interesse']}")
                    st.markdown(f"**Valor do Lead:** R$ {float(row['Valor']):,.2f}")
                    
                with col_info2:
                    st.markdown(f"**Status de Consulta:**")
                    st.markdown(badge_c, unsafe_allow_html=True)
                    
                    st.markdown(f"**Status de Cirurgia:**")
                    st.markdown(badge_s, unsafe_allow_html=True)
                    
                with col_info3:
                    # Formatar as datas de criação e atualização também
                    criado_em_formatado = format_br_date(row["Criado Em"]) if pd.notna(row["Criado Em"]) else "Data não informada"
                    atualizado_em_formatado = format_br_date(row["Atualizado Em"]) if pd.notna(row["Atualizado Em"]) else "Data não informada"
                    st.markdown(f"**Criado por:** {row['Criado Por']} ({criado_em_formatado})")
                    st.markdown(f"**Atualizado por:** {row['Atualizado Por']} ({atualizado_em_formatado})")
                    
                st.markdown(f"**Observações:** \n\n {row['Observações'] if row['Observações'] else '*(Sem observações)*'}")
                
                # Ações (Editar / Deletar)
                st.markdown("<br>", unsafe_allow_html=True)
                col_btn1, col_btn2, _ = st.columns([1, 1, 3])
                
                with col_btn1:
                    if st.button("✏️ Editar Registro", key=f"btn_edit_{lead_id}"):
                        st.session_state.edit_lead_id = lead_id
                        st.session_state.delete_lead_id = None
                        st.rerun()
                        
                with col_btn2:
                    if current_user["role"] == "Admin":
                        if st.button("🗑️ Excluir Registro", key=f"btn_del_{lead_id}"):
                            st.session_state.delete_lead_id = lead_id
                            st.session_state.edit_lead_id = None
                            st.rerun()
                    else:
                        st.button("🔒 Excluir Registro (Admin Only)", key=f"btn_del_disabled_{lead_id}", disabled=True)
                
                # Se este lead estiver selecionado para exclusão (apenas Admin)
                if st.session_state.delete_lead_id == lead_id and current_user["role"] == "Admin":
                    st.markdown("<div style='border: 1px solid red; padding: 15px; border-radius: 8px; background-color: rgba(239, 68, 68, 0.05); margin-top: 15px;'>", unsafe_allow_html=True)
                    st.warning(f"⚠️ Tem certeza de que deseja excluir permanentemente o lead **'{lead_name}'**?")
                    col_conf1, col_conf2 = st.columns([1, 4])
                    with col_conf1:
                        if st.button("Confirmar Exclusão", key=f"conf_del_{lead_id}", type="primary"):
                            with st.spinner("Excluindo..."):
                                try:
                                    db.delete_lead(lead_id, lead_name, current_user["username"], current_user["role"])
                                    st.session_state.delete_lead_id = None
                                    st.cache_data.clear() # Limpa cache do streamlit
                                    st.success("Lead excluído com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir lead: {e}")
                    with col_conf2:
                        if st.button("Cancelar", key=f"cancel_del_{lead_id}"):
                            st.session_state.delete_lead_id = None
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # Se este lead estiver selecionado para Edição
                if st.session_state.edit_lead_id == lead_id:
                    st.markdown("<div class='form-container' style='margin-top: 20px;'>", unsafe_allow_html=True)
                    st.markdown("### Formulário de Edição")
                    
                    with st.form(key=f"form_edit_{lead_id}"):
                        # Converter a data de string para date object para o date_input
                        try:
                            # Tentar converter a data do formato DD-MM-YYYY
                            date_obj = parse_date_safely(str(row["Data Contato"]).strip())
                            if pd.isna(date_obj):
                                raise ValueError("Data inválida")
                            if hasattr(date_obj, 'tz') and date_obj.tz is not None:
                                date_obj = date_obj.tz_localize(None)
                            date_obj = date_obj.date()
                        except Exception:
                            date_obj = datetime.today().date()
                            
                        val_nome = st.text_input("Nome", value=str(row["Nome"]))
                        val_data = st.date_input("Data de Contato", value=date_obj)
                        val_material = st.text_input("Material de Interesse", value=str(row["Material de Interesse"]))
                        val_valor = st.number_input("Valor (R$)", min_value=0.0, value=float(row["Valor"]), format="%.2f")
                        
                        val_consulta = st.selectbox(
                            "Status de Consulta", 
                            ["Pendente", "Realizado", "Não realizado"], 
                            index=["Pendente", "Realizado", "Não realizado"].index(row["Status Consulta"])
                        )
                        val_cirurgia = st.selectbox(
                            "Status de Cirurgia", 
                            ["Pendente", "Realizado", "Não realizado"], 
                            index=["Pendente", "Realizado", "Não realizado"].index(row["Status Cirurgia"])
                        )
                        val_obs = st.text_area("Observações", value=str(row["Observações"]))
                        
                        col_form_btn1, col_form_btn2 = st.columns([1, 4])
                        with col_form_btn1:
                            submit_edit = st.form_submit_button("Salvar Alterações", type="primary")
                        with col_form_btn2:
                            cancel_edit = st.form_submit_button("Cancelar Edição")
                            
                        if submit_edit:
                            if not val_nome:
                                st.error("O nome do lead não pode ficar em branco.")
                            else:
                                with st.spinner("Atualizando no Google Sheets..."):
                                    # Formatar data de volta para DD-MM-YYYY
                                    data_formatted = val_data.strftime("%d-%m-%Y")
                                    updated_payload = {
                                        "Nome": val_nome,
                                        "Data Contato": data_formatted,
                                        "Material de Interesse": val_material,
                                        "Valor": val_valor,
                                        "Status Consulta": val_consulta,
                                        "Status Cirurgia": val_cirurgia,
                                        "Observações": val_obs
                                    }
                                    try:
                                        db.update_lead(lead_id, updated_payload, current_user["username"])
                                        st.session_state.edit_lead_id = None
                                        st.cache_data.clear() # Limpa o cache
                                        st.success("Lead atualizado com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao salvar alterações: {e}")
                                        
                        if cancel_edit:
                            st.session_state.edit_lead_id = None
                            st.rerun()
                            
                    st.markdown("</div>", unsafe_allow_html=True)

# 3. ADICIONAR LEAD
elif page == "➕ Adicionar Lead":
    st.title("➕ Adicionar Lead")
    st.markdown("Cadastre um novo lead no banco de dados do sistema.")
    
    with st.container():
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        
        with st.form("new_lead_form", clear_on_submit=True):
            nome_lead = st.text_input("Nome do Lead", placeholder="Digite o nome completo...")
            data_lead = st.date_input("Data de Contato", value=datetime.today().date())
            material_lead = st.text_input("Material de Interesse", placeholder="Ex: Prótese de Silicone, Lentes de Contato...")
            valor_lead = st.number_input("Valor Estimado (R$)", min_value=0.0, step=100.0, value=0.0, format="%.2f")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                status_c = st.selectbox("Status de Consulta", ["Pendente", "Realizado", "Não realizado"])
            with col_s2:
                status_s = st.selectbox("Status de Cirurgia", ["Pendente", "Realizado", "Não realizado"])
                
            obs_lead = st.text_area("Observações", placeholder="Adicione observações importantes sobre o lead...")
            
            submit_lead = st.form_submit_button("Cadastrar Lead", type="primary", use_container_width=True)
            
            if submit_lead:
                if not nome_lead:
                    st.error("Por favor, informe o Nome do Lead.")
                else:
                    with st.spinner("Salvando no Google Sheets..."):
                        try:
                            # Formatar a data no padrão brasileiro DD-MM-YYYY antes de salvar
                            data_formatted = data_lead.strftime("%d-%m-%Y")
                            
                            db.add_lead(
                                nome=nome_lead,
                                data_contato=data_formatted,
                                material=material_lead,
                                valor=valor_lead,
                                status_consulta=status_c,
                                status_cirurgia=status_s,
                                observacoes=obs_lead,
                                criado_por=current_user["username"]
                            )
                            
                            st.cache_data.clear() # Limpa cache do Streamlit
                            st.success(f"Lead '{nome_lead}' cadastrado com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao salvar lead no Google Sheets: {e}")
                            
        st.markdown("</div>", unsafe_allow_html=True)

# 4. LOG DE ALTERAÇÕES (ADMIN ONLY)
elif page == "📜 Log de Alterações" and current_user['role'] == "Admin":
    st.title("📜 Vigilância e Auditoria de Logs")
    st.markdown("Registro minucioso de todas as operações e alterações de informações realizadas no sistema.")
    
    # Carregar logs
    try:
        df_logs = db.get_logs()
    except Exception as e:
        st.error(f"Erro ao carregar logs: {e}")
        st.stop()
        
    if df_logs.empty:
        st.info("Nenhum registro de log encontrado.")
    else:
        # Formatar as datas dos logs
        if "Data/Hora" in df_logs.columns:
            df_logs["Data/Hora"] = df_logs["Data/Hora"].apply(format_br_date)
        
        # Filtros para os Logs
        col_fl1, col_fl2, col_fl3 = st.columns([1, 1, 2])
        
        with col_fl1:
            usuarios_log = ["Todos"] + list(df_logs["Usuário"].unique())
            filtro_usuario = st.selectbox("Filtrar por Usuário", usuarios_log)
            
        with col_fl2:
            acoes_log = ["Todos"] + list(df_logs["Ação"].unique())
            filtro_acao = st.selectbox("Filtrar por Ação", acoes_log)
            
        with col_fl3:
            busca_log = st.text_input("🔍 Buscar termo nos detalhes", placeholder="Digite palavras chaves de alteração...")
            
        # Aplicar filtros
        filtered_logs = df_logs.copy()
        
        if filtro_usuario != "Todos":
            filtered_logs = filtered_logs[filtered_logs["Usuário"] == filtro_usuario]
            
        if filtro_acao != "Todos":
            filtered_logs = filtered_logs[filtered_logs["Ação"] == filtro_acao]
            
        if busca_log:
            filtered_logs = filtered_logs[filtered_logs["Descrição Detalhada"].str.lower().str.contains(busca_log.lower())]
            
        if filtered_logs.empty:
            st.warning("Nenhum log encontrado para os critérios de pesquisa informados.")
        else:
            st.markdown(f"Exibindo **{len(filtered_logs)}** registros de logs ordenados pelo mais recente.")
            
            # Exibir dataframe estilizado
            st.dataframe(
                filtered_logs[[
                    "Data/Hora", "Usuário", "Ação", "ID do Lead", 
                    "Descrição Detalhada", "Campo Alterado", "Valor Antigo", "Valor Novo"
                ]], 
                use_container_width=True
            )

# 5. CONFIGURAÇÕES
elif page == "⚙️ Configurações":
    st.title("⚙️ Configurações e Segurança")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        st.subheader("Alterar Minha Senha")
        
        with st.form("change_password_form", clear_on_submit=True):
            current_pwd = st.text_input("Senha Atual", type="password")
            new_pwd = st.text_input("Nova Senha", type="password")
            confirm_new_pwd = st.text_input("Confirmar Nova Senha", type="password")
            submit_pwd = st.form_submit_button("Alterar Senha", use_container_width=True)
            
            if submit_pwd:
                if not current_pwd or not new_pwd or not confirm_new_pwd:
                    st.error("Preencha todos os campos do formulário.")
                elif new_pwd != confirm_new_pwd:
                    st.error("A nova senha e a confirmação não coincidem.")
                else:
                    try:
                        # Verificar se senha atual é correta
                        auth_check = db.authenticate_user(current_user["username"], current_pwd)
                        if auth_check:
                            db.change_password(current_user["username"], new_pwd)
                            st.success("Senha alterada com sucesso!")
                        else:
                            st.error("A senha atual digitada está incorreta.")
                    except Exception as e:
                        st.error(f"Erro ao alterar senha: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_c2:
        if current_user["role"] == "Admin":
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            st.subheader("🧑‍💼 Gerenciamento de Usuários")
            st.markdown("Cadastre novos usuários com permissões específicas no sistema.")
            
            # Form para criar novos usuários
            with st.form("new_user_form", clear_on_submit=True):
                new_username = st.text_input("Nome de Usuário (Username)", placeholder="Ex: joao.silva").strip()
                new_name = st.text_input("Nome Completo do Usuário", placeholder="Ex: João Silva")
                new_pwd_input = st.text_input("Senha Inicial", type="password", placeholder="Senha de no mínimo 6 caracteres")
                new_role = st.selectbox("Perfil de Acesso (Role)", ["User", "Admin"])
                
                submit_user = st.form_submit_button("Cadastrar Novo Usuário", type="primary", use_container_width=True)
                
                if submit_user:
                    if not new_username or not new_name or not new_pwd_input:
                        st.error("Todos os campos do formulário de usuário são obrigatórios.")
                    elif len(new_pwd_input) < 4:
                        st.error("A senha deve ter pelo menos 4 caracteres.")
                    else:
                        with st.spinner("Cadastrando usuário no Google Sheets..."):
                            try:
                                db.add_user(
                                    username=new_username,
                                    nome=new_name,
                                    password=new_pwd_input,
                                    role=new_role,
                                    actor=current_user["username"]
                                )
                                st.success(f"Usuário '{new_username}' cadastrado com sucesso como '{new_role}'!")
                            except ValueError as ve:
                                st.error(str(ve))
                            except Exception as e:
                                st.error(f"Erro ao criar usuário: {e}")
                                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Listar usuários
            with st.expander("Ver lista de usuários cadastrados"):
                try:
                    usuarios_lista = db.get_users()
                    st.dataframe(pd.DataFrame(usuarios_lista), use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao listar usuários: {e}")
        else:
            st.markdown("<div class='form-container' style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown("### Permissões do Usuário")
            st.info("Seu perfil de acesso é **Usuário Padrão**. Apenas Administradores podem gerenciar usuários ou cadastrar novos perfis no sistema.")
            st.markdown("</div>", unsafe_allow_html=True)