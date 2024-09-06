from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters, ConversationHandler
from ftplib import FTP
import os
import tempfile

# Substitua pelo seu token
TOKEN = '7261112826:AAGCjjfMtVhdzrTHdSWUZ-YKZnUt8I2Iozw'

# Configurações do FTP
FTP_IP = "127.0.0.1"  # Altere para o IP do seu servidor FTP
FTP_USER = "teste1"
FTP_PASS = "12345"

# Configuração do diretório temporário
TEMP_DIR = tempfile.gettempdir()  # Diretório temporário padrão

# Conecta ao servidor FTP
ftp = FTP(FTP_IP)
ftp.login(user=FTP_USER, passwd=FTP_PASS)

# Função para exibir o diretório raiz
def mostrar_diretorio_raiz(ftp):
    try:
        # Muda para o diretório raiz
        ftp.cwd('C:/Users/guilh/OneDrive/Engenharia Comp/Sistemas Distribuídos/Trabalho SD/Pasta-Compartilhada')
        print("Diretório atual:", ftp.pwd())
    except Exception as e:
        print("Diretório atual:", ftp.pwd())
        print(f"Erro ao verificar o diretório raiz: {e}")

# Exibe o diretório raiz do servidor FTP
mostrar_diretorio_raiz(ftp)

# Etapas da conversa
BAIXAR, UPLOAD = range(2)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Olá! Use /listar para listar arquivos, use /upload para enviar um arquivo e /baixar para baixar um arquivo.\n'
        'Digite o número do arquivo para baixar após usar /baixar.'
    )

async def listar(update: Update, context: CallbackContext):
    try:
        arquivos = ftp.nlst()
        if arquivos:
            response = "\n".join(f"{i + 1} - {arquivo}" for i, arquivo in enumerate(arquivos))
        else:
            response = "Nenhum arquivo encontrado."
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro ao listar arquivos: {e}")

async def upload(update: Update, context: CallbackContext):
    await update.message.reply_text("Envie um arquivo no chat para enviar ao servidor.")
    return UPLOAD

async def upload_file(update: Update, context: CallbackContext):
    if update.message.document:
        document = update.message.document
        arquivo_local = os.path.join(TEMP_DIR, document.file_name)

        try:
            # Baixa o arquivo enviado para um diretório temporário
            file = await document.get_file()
            await file.download_to_drive(arquivo_local)

            # Tente mudar para o diretório raiz
            try:
                ftp.cwd('/')
                print("Mudado para o diretório raiz.")
                current_dir = ftp.pwd()
                print(f"Diretório atual: {current_dir}")
            except Exception as e:
                print(f"Erro ao mudar para o diretório raiz: {e}")

            # Agora, mude para o diretório específico
            try:
                ftp.cwd('Pasta-Compartilhada')
                print(f"Mudado para o diretório 'Pasta-Compartilhada'.")
                current_dir = ftp.pwd()
                print(f"Diretório atual: {current_dir}")
            except Exception as e:
                print(f"Erro ao mudar para o diretório 'Pasta-Compartilhada': {e}")

            # Faz o upload para o servidor FTP
            with open(arquivo_local, 'rb') as file:
                ftp.storbinary(f'STOR {document.file_name}', file)

            os.remove(arquivo_local)  # Remove o arquivo temporário após o upload
            await update.message.reply_text(f"Arquivo '{document.file_name}' enviado e armazenado no servidor FTP.")

            # Lista os arquivos existentes no servidor FTP e envia a lista para o usuário
            arquivos = ftp.nlst()
            if arquivos:
                response = "\n".join(f"{i + 1} - {arquivo}" for i, arquivo in enumerate(arquivos))
            else:
                response = "Nenhum arquivo encontrado."
            await update.message.reply_text(f"Arquivos no servidor:\n{response}")
        except Exception as e:
            await update.message.reply_text(f"Ocorreu um erro ao fazer upload do arquivo: {e}")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Por favor, envie um arquivo para upload.")
        return UPLOAD



async def baixar(update: Update, context: CallbackContext):
    await update.message.reply_text("Digite o número do arquivo para baixar:")
    return BAIXAR

async def baixar_file(update: Update, context: CallbackContext):
    if update.message.text:
        try:
            numero = int(update.message.text)
            arquivos = ftp.nlst()
            if 1 <= numero <= len(arquivos):
                nome_arquivo = arquivos[numero - 1]
                caminho_download = os.path.join(TEMP_DIR, nome_arquivo)

                # Baixa o arquivo do servidor FTP
                with open(caminho_download, 'wb') as file:
                    ftp.retrbinary(f'RETR {nome_arquivo}', file.write)

                # Envia o arquivo para o usuário
                with open(caminho_download, 'rb') as file:
                    await update.message.reply_document(document=InputFile(file, filename=nome_arquivo))

                os.remove(caminho_download)  # Remove o arquivo temporário após o envio
            else:
                await update.message.reply_text("Número inválido.")
        except ValueError:
            await update.message.reply_text("Por favor, forneça um número válido.")
        except Exception as e:
            await update.message.reply_text(f"Ocorreu um erro ao baixar o arquivo: {e}")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Por favor, forneça um número válido.")
        return BAIXAR

def main():
    # Cria o Application e passa o token do bot
    application = Application.builder().token(TOKEN).build()

    # Define o handler para conversas
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('upload', upload), CommandHandler('baixar', baixar)],
        states={
            UPLOAD: [MessageHandler(filters.Document.ALL, upload_file)],
            BAIXAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, baixar_file)]
        },
        fallbacks=[]
    )

    # Adiciona os handlers de comando e mensagem
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('listar', listar))
    application.add_handler(conversation_handler)

    # Inicia o bot
    application.run_polling()

if __name__ == '__main__':
    main()
