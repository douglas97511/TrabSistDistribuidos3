import Pyro5.api
import threading

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

#Pyro5.api.config.SERIALIZER = 'marshal'

# Classe que representa o cliente do sistema de gestão de estoque
class StockManagementClient:

    def notify_replenishment(self, product_code):
        # Método chamado pelo servidor para notificar sobre a reposição de estoque
        print(f"Produto {product_code} atingiu o estoque mínimo. É necessário repor o estoque.")

    def notify_unsold_products(self, product):
        # Método chamado pelo servidor para enviar relatórios de produtos não vendidos
        print(f"Produto {product['name']} ({product['code']}) não foi vendido.")


def keysGenerator():

    # Gerar um par de chaves RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Exponente público padrão (Fermat F4)
        key_size=2048,          # Tamanho da chave (pode ser 2048, 3072, 4096, etc.)
        backend=default_backend()
    )

    # Obter a chave pública correspondente
    public_key = private_key.public_key()

    # Serializar as chaves para armazenamento ou transmissão
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Salvar as chaves em arquivos
    with open("private_key.pem", "wb") as f:
        f.write(private_key_pem)

    with open("public_key.pem", "wb") as f:
        f.write(public_key_pem)

    print("Chaves geradas e salvas com sucesso!")
    return [private_key_pem, public_key_pem]



# Configurar o cliente PyRO
if __name__ == "__main__":

    # Registrar objeto cliente
    daemon = Pyro5.api.Daemon()
    uri = daemon.register(StockManagementClient())

    # Gerar chaves
    keys = keysGenerator()
    private_key = keys[0]
    public_key = keys[1]

    # Pegar objeto do servidor

    servidor_nomes = Pyro5.api.locate_ns()
    server_uri = servidor_nomes.lookup("stock_management_system")
    #server_uri = "PYRONAME:stock_management_system"  # URI do servidor PyRO

    

    with Pyro5.api.Proxy(server_uri) as server:
        name = "NomeDoGestor2"  # Nome do gestor de estoque
        response = server.register_user(name,public_key, uri)
        print(response)
        # O cliente agora está registrado no servidor e pronto para receber notificações e relatórios
        


    #colocar request loop dentro de uma thread
    threading.Thread(target=daemon.requestLoop).start()