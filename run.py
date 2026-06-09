import os
import sys
import subprocess

def check_dependencies():
    """Verifica se os pacotes necessários estão instalados. Se não, instala."""
    required_libs = {
        "streamlit": "streamlit",
        "requests": "requests",
        "pandas": "pandas"
    }
    
    missing = []
    for module_name, pip_name in required_libs.items():
        try:
            # Tentar importar o módulo principal
            if "." in module_name:
                parts = module_name.split(".")
                mod = __import__(parts[0])
                for part in parts[1:]:
                    mod = getattr(mod, part)
            else:
                __import__(module_name)
        except (ImportError, AttributeError):
            missing.append(pip_name)
            
    if missing:
        print(f"=== Dependências ausentes detectadas: {', '.join(missing)} ===")
        requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        
        if os.path.exists(requirements_file):
            print("Instalando dependências através do requirements.txt...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
                print("Instalação concluída com sucesso!")
            except subprocess.CalledProcessError as e:
                print(f"Erro ao rodar pip install -r: {e}")
                sys.exit(1)
        else:
            print("Instalando pacotes ausentes via pip...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
                print("Instalação concluída com sucesso!")
            except subprocess.CalledProcessError as e:
                print(f"Erro ao rodar pip install: {e}")
                sys.exit(1)
    else:
        print("Todas as dependências estão presentes.")

def main():
    # Mudar diretório de trabalho para a pasta deste script para garantir caminhos relativos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. Verificar e instalar dependências
    print("Verificando dependências...")
    check_dependencies()
    
    # 2. Executar o Streamlit
    print("Iniciando o servidor Lead.in.time...")
    
    # Caminho do app.py
    app_path = "app.py"
    
    try:
        # Importar a interface CLI do Streamlit diretamente para rodar no mesmo processo
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", app_path]
        sys.exit(stcli.main())
    except Exception as e:
        print(f"Erro ao iniciar via Streamlit CLI ({e}). Tentando rodar via subprocesso...")
        # Fallback caso haja alterações estruturais nas versões do Streamlit
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
        except KeyboardInterrupt:
            print("\nServidor finalizado pelo usuário.")

if __name__ == "__main__":
    main()
