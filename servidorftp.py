from pyftpdlib.authorizers import DummyAuthorizer 
from pyftpdlib.handlers import FTPHandler 
from pyftpdlib.servers import FTPServer 

# Configuração do servidor FTP
authorizer = DummyAuthorizer()
# Conceder permissões de leitura, escrita e listagem no diretório 'Pasta-Compartilhada'
authorizer.add_user('teste1', '12345', 'C:/Users/anton/Desktop/Arquivos', perm='lwr')

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(('192.168.0.222', 21), handler)

print("Servidor FTP iniciado...")
server.serve_forever()
