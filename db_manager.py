import os
import json
import hashlib
import pandas as pd
import requests

# Constantes de segurança
SALT = b"lead_in_time_salt_2026"
ITERATIONS = 100000

URL_FILE = "web_app_url.txt"
TOKEN_FILE = "auth_token.txt"

def hash_password(password: str) -> str:
    """Gera o hash PBKDF2 SHA-256 de uma senha."""
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), SALT, ITERATIONS)
    return pwd_hash.hex()

class DatabaseManager:
    def __init__(self):
        self.url_path = URL_FILE
        self.token_path = TOKEN_FILE

    def _get_streamlit_secrets(self) -> dict:
        """Retorna a configuração de secrets do Streamlit, se disponível."""
        try:
            import streamlit as st
            secrets = getattr(st, "secrets", None)
            if not secrets:
                return {}

            # Suporta secrets aninhados dentro de [google_sheets]
            if "google_sheets" in secrets:
                secrets = secrets["google_sheets"]

            return {k: str(v).strip() for k, v in dict(secrets).items()}
        except Exception:
            return {}

    def get_secrets_configuration(self) -> dict:
        """Retorna a configuração do Streamlit secrets se estiver disponível."""
        secrets = self._get_streamlit_secrets()
        return {
            "web_app_url": secrets.get("web_app_url", ""),
            "auth_token": secrets.get("auth_token", "")
        }

    def is_configured(self) -> bool:
        """Verifica se a URL do Web App e o Token de Verificação foram definidos."""
        secrets = self.get_secrets_configuration()
        if secrets["web_app_url"] and secrets["auth_token"]:
            return True

        return os.path.exists(self.url_path) and os.path.exists(self.token_path)

    def save_configuration(self, web_app_url: str, auth_token: str):
        """Salva a URL do Web App e o Token localmente em arquivos txt."""
        with open(self.url_path, "w", encoding="utf-8") as f:
            f.write(web_app_url.strip())
            
        with open(self.token_path, "w", encoding="utf-8") as f:
            f.write(auth_token.strip())

    def get_web_app_url(self) -> str:
        """Retorna a URL cadastrada para o Web App."""
        secrets = self.get_secrets_configuration()
        if secrets["web_app_url"]:
            return secrets["web_app_url"]

        if os.path.exists(self.url_path):
            with open(self.url_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    def get_auth_token(self) -> str:
        """Retorna o token cadastrado."""
        secrets = self.get_secrets_configuration()
        if secrets["auth_token"]:
            return secrets["auth_token"]

        if os.path.exists(self.token_path):
            with open(self.token_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    def send_request(self, action: str, payload: dict = None) -> dict:
        """Envia uma requisição HTTP POST segura para o Web App da planilha."""
        if not self.is_configured():
            raise FileNotFoundError("Configuração ausente. Configure a URL do Web App e o AuthToken.")
            
        url = self.get_web_app_url()
        token = self.get_auth_token()
        
        body = {
            "token": token,
            "action": action,
            "payload": payload or {}
        }
        
        try:
            # Enviamos como JSON e definimos timeout para evitar travamentos
            response = requests.post(url, json=body, timeout=15)
            
            # Apps Script às vezes redireciona (302). O requests trata isso por padrão,
            # mas precisamos validar o status code da resposta final
            if response.status_code != 200:
                raise Exception(f"Erro do Servidor Google (Status {response.status_code}). Verifique a URL do Web App.")
                
            result = response.json()
            if not result.get("success", False):
                raise Exception(result.get("error", "Erro desconhecido na API do Google Sheets."))
                
            return result
        except requests.exceptions.Timeout:
            raise Exception("Tempo limite esgotado ao tentar comunicar com a planilha Google. Tente novamente.")
        except requests.exceptions.RequestException as re:
            raise Exception(f"Erro de conexão com o Web App Google: {re}")
        except json.JSONDecodeError:
            raise Exception("A resposta do Google Sheets não é um JSON válido. Verifique se o Web App foi implantado corretamente e permite acesso público.")

    # --- SISTEMA DE USUÁRIOS E AUTENTICAÇÃO ---

    def authenticate_user(self, username: str, password: str) -> dict:
        """Autentica o usuário comparando o hash da senha."""
        result = self.send_request("getUsers")
        users_list = result.get("data", [])
        
        username_lower = username.strip().lower()
        target_hash = hash_password(password)
        
        for user in users_list:
            if str(user.get("Username", "")).strip().lower() == username_lower:
                if str(user.get("Password Hash", "")) == target_hash:
                    return {
                        "username": user["Username"],
                        "nome": user["Nome"],
                        "role": user["Role"]
                    }
        return None

    def change_password(self, username: str, new_password: str) -> bool:
        """Altera a senha de um usuário."""
        new_hash = hash_password(new_password)
        payload = {
            "username": username,
            "new_hash": new_hash
        }
        result = self.send_request("changePassword", payload)
        return result.get("success", False)

    def get_users(self) -> list:
        """Retorna a lista de usuários (removendo os hashes por segurança)."""
        result = self.send_request("getUsers")
        users_list = result.get("data", [])
        return [{"username": u["Username"], "nome": u["Nome"], "role": u["Role"]} for u in users_list]

    def add_user(self, username: str, nome: str, password: str, role: str, actor: str) -> bool:
        """Adiciona um novo usuário ao sistema."""
        pwd_hash = hash_password(password)
        payload = {
            "username": username,
            "nome": nome,
            "pwd_hash": pwd_hash,
            "role": role,
            "actor": actor
        }
        result = self.send_request("addUser", payload)
        return result.get("success", False)

    # --- OPERAÇÕES DE LEADS (CRUD) ---

    def get_leads(self) -> pd.DataFrame:
        """Busca todos os leads e retorna como DataFrame."""
        result = self.send_request("getLeads")
        records = result.get("data", [])
        
        if not records:
            return pd.DataFrame(columns=[
                'ID', 'Nome', 'Data Contato', 'Material de Interesse', 'Valor', 
                'Status Consulta', 'Status Cirurgia', 'Observações', 'Origem',
                'Criado Por', 'Criado Em', 'Atualizado Por', 'Atualizado Em'
            ])
            
        df = pd.DataFrame(records)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0.0)
        
        # Garantir que a coluna Origem exista
        if 'Origem' not in df.columns:
            df['Origem'] = 'Não informada'
            
        return df

    def add_lead(self, nome: str, data_contato: str, material: str, valor: float, 
                 origem: str, status_consulta: str, status_cirurgia: str, 
                 observacoes: str, criado_por: str) -> str:
        """Adiciona um novo lead na aba 'leads' com suporte a origem."""
        payload = {
            "nome": nome,
            "data_contato": data_contato,
            "material": material,
            "valor": float(valor),
            "origem": origem,  # Novo campo de origem
            "status_consulta": status_consulta,
            "status_cirurgia": status_cirurgia,
            "observacoes": observacoes,
            "criado_por": criado_por
        }
        result = self.send_request("addLead", payload)
        return result.get("id", "")

    def update_lead(self, lead_id: str, updated_data: dict, atualizado_por: str) -> bool:
        """Atualiza os campos de um lead existente, incluindo origem."""
        payload = {
            "lead_id": lead_id,
            "updated_data": updated_data,
            "user": atualizado_por
        }
        result = self.send_request("updateLead", payload)
        return result.get("success", False)

    def delete_lead(self, lead_id: str, lead_name: str, deletado_por: str, user_role: str) -> bool:
        """Deleta um lead se o usuário for Admin."""
        if user_role != "Admin":
            raise PermissionError("Apenas administradores podem realizar exclusões de registros.")
            
        payload = {
            "lead_id": lead_id,
            "lead_name": lead_name,
            "user": deletado_por
        }
        result = self.send_request("deleteLead", payload)
        return result.get("success", False)

    # --- MÉTODOS ADICIONAIS PARA ANÁLISE POR ORIGEM ---

    def get_leads_by_origin(self, origem: str = None) -> pd.DataFrame:
        """Retorna leads filtrados por origem."""
        df = self.get_leads()
        if df.empty:
            return df
        
        if origem and origem != "Todas":
            df = df[df['Origem'] == origem]
        
        return df

    def get_origin_statistics(self) -> dict:
        """Retorna estatísticas agregadas por origem."""
        df = self.get_leads()
        if df.empty:
            return {}
        
        stats = {}
        for origem in df['Origem'].unique():
            df_origem = df[df['Origem'] == origem]
            stats[origem] = {
                'total_leads': len(df_origem),
                'valor_total': df_origem['Valor'].sum(),
                'ticket_medio': df_origem['Valor'].mean(),
                'consultas_realizadas': len(df_origem[df_origem['Status Consulta'] == 'Realizado']),
                'cirurgias_realizadas': len(df_origem[df_origem['Status Cirurgia'] == 'Realizado']),
                'faturamento_confirmado': df_origem[df_origem['Status Cirurgia'] == 'Realizado']['Valor'].sum(),
                'taxa_conversao_consulta': (len(df_origem[df_origem['Status Consulta'] == 'Realizado']) / len(df_origem) * 100) if len(df_origem) > 0 else 0,
                'taxa_conversao_cirurgia': (len(df_origem[df_origem['Status Cirurgia'] == 'Realizado']) / len(df_origem) * 100) if len(df_origem) > 0 else 0
            }
        
        return stats

    # --- VIGILÂNCIA E AUDITORIA (LOGS) ---

    def get_logs(self) -> pd.DataFrame:
        """Retorna todos os logs de auditoria ordenados do mais recente ao mais antigo."""
        result = self.send_request("getLogs")
        records = result.get("data", [])
        
        if not records:
            return pd.DataFrame(columns=[
                'Data/Hora', 'Usuário', 'Ação', 'ID do Lead', 
                'Descrição Detalhada', 'Campo Alterado', 'Valor Antigo', 'Valor Novo'
            ])
            
        df = pd.DataFrame(records)
        df = df.iloc[::-1].reset_index(drop=True)
        return df

    # --- MÉTODOS DE VALIDAÇÃO ---

    def validate_origin(self, origem: str) -> bool:
        """Valida se a origem é uma das opções permitidas."""
        valid_origins = ["Instagram (Trafego Orgânico)", "Meta Ads (Trafego Pago)", "Indicação"]
        return origem in valid_origins

    def get_valid_origins(self) -> list:
        """Retorna a lista de origens válidas."""
        return ["Instagram (Trafego Orgânico)", "Meta Ads (Trafego Pago)", "Indicação"]