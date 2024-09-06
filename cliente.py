from ftplib import FTP
import os

# Conecta ao servidor FTP 127.0.0.1 com usuário e senha teste1 e 12345
ip = "192.168.0.197"
usuario = "teste1"
senha = "12345"

ftp = FTP(ip)
ftp.login(user=usuario, passwd=senha)

def listar_arquivos():
    arquivos = ftp.nlst()
    print("\nArquivos disponíveis no servidor:\n")
    for i, arquivo in enumerate(arquivos):
        print(f"{i + 1} - {arquivo}")
    return arquivos

def baixar_arquivo(arquivos):
    try:
        numero = int(input("\nDigite o número do arquivo que deseja baixar: "))
        if 1 <= numero <= len(arquivos):
            nome_arquivo = arquivos[numero - 1]
            caminho_download = os.path.join(os.path.expanduser("~"), "Downloads", nome_arquivo)
            with open(caminho_download, 'wb') as file:
                ftp.retrbinary('RETR ' + nome_arquivo, file.write)
            print(f"Download do arquivo '{nome_arquivo}' concluído e salvo em '{caminho_download}'.")
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida. Por favor, digite um número.")
    except Exception as e:
        print(f"Ocorreu um erro ao baixar o arquivo: {e}")

def upload_arquivo():
    try:
        # Solicita ao usuário o caminho completo do arquivo
        caminho_arquivo = input("Digite o caminho completo do arquivo que deseja fazer upload (ex: C:/Users/SeuUsuario/Documents/arquivo.txt): ")
        
        # Remove aspas duplas do início e do fim do caminho
        caminho_arquivo = caminho_arquivo.strip('"')

        if os.path.isfile(caminho_arquivo):
            nome_arquivo = os.path.basename(caminho_arquivo)
            with open(caminho_arquivo, 'rb') as file:
                ftp.storbinary(f'STOR {nome_arquivo}', file)
            print(f"Upload do arquivo '{nome_arquivo}' concluído.")
        else:
            print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
    except Exception as e:
        print(f"Ocorreu um erro ao fazer o upload: {e}")

def menu_listar_arquivos():
    while True:
        arquivos = listar_arquivos()
        print("\n--- Menu de Arquivos ---")
        print("1 - Download de arquivo")
        print("2 - Voltar ao menu principal")
        opcao = input("\nDigite a opção desejada: ")

        if opcao == "1":
            if arquivos:
                baixar_arquivo(arquivos)
        elif opcao == "2":
            break
        else:
            print("Opção inválida. Tente novamente.")
        input("\nPressione Enter para continuar...")  # Espera o usuário pressionar Enter
        limpar_terminal()

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Interface de linha de comando legível
while True:
    limpar_terminal()
    print("\n--- Menu Principal FTP ---")
    print("1 - Listar arquivos")
    print("2 - Upload de arquivo")
    print("3 - Sair")
    opcao = input("Digite a opção desejada: ")

    if opcao == "1":
        menu_listar_arquivos()
    elif opcao == "2":
        upload_arquivo()
    elif opcao == "3":
        ftp.quit()
        print("Conexão encerrada.")
        break
    else:
        print("Opção inválida. Tente novamente.")
    input("\nPressione Enter para continuar...")  # Espera o usuário pressionar Enter
