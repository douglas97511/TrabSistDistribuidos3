import Pyro5.api
import datetime


class Product:
    def __init__(self, code, name, description, quantity, price, min_stock):
        self.code = code
        self.name = name
        self.description = description
        self.quantity = quantity
        self.price = price
        self.min_stock = min_stock
        self.movements = []

    def add_entry(self, quantity):
        self.quantity += quantity
        self.movements.append((datetime.datetime.now(), "entrada", quantity))

    def add_exit(self, quantity):
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.movements.append((datetime.datetime.now(), "saída", quantity))

    def get_stock_status(self):
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "quantity": self.quantity,
            "price": self.price,
            "min_stock": self.min_stock,
        }

# Classe que representa um usuário do sistema
class User:
    def __init__(self, name, public_key, client_object):
        self.name = name
        self.public_key = public_key
        self.client_object = client_object

# Classe que representa o sistema de gestão de estoque
class StockManagementSystem:
    def __init__(self):
        self.users = {}  # Dicionário de usuários (nome do usuário -> objeto do usuário)
        self.products = {}  # Dicionário de produtos (código do produto -> objeto do produto)
        self.clients = {}  # Dicionário de clientes (nome do cliente -> objeto do cliente)
    @Pyro5.api.expose
    def register_user(self, name, public_key, client_object):
        print(public_key)
        print("Usuarios cadastrados: ", self.users)
        print("Name:", name)
        if name not in self.users:
            user = User(name, public_key, client_object)
            self.users[name] = user
            print(self.users[name], self.users[name].name, self.users, self.users[name].public_key)
            return f"Usuário {name} registrado com sucesso."
        else:
            print("else")
            return f"Usuário {name} já está registrado."


    @Pyro5.api.expose
    def record_entry(self, user_name, code, name, description, quantity, price, min_stock, signature):
        if user_name in self.users:
            user = self.users[user_name]
            if code in self.products:
                print("Produto adicionado")
                product = self.products[code]
                # Verificar a assinatura digital com a chave pública do usuário
                if self.verify_signature(signature, user.public_key):
                    print("Assinatura digital válida.")
                    product.add_entry(quantity)
                    # Verificar se a quantidade após a entrada atingiu o estoque mínimo
                    if product.quantity <= product.min_stock:
                        self.notify_replenishment(user_name, product)
                    return f"Entrada de {quantity} unidades de {product.name} registrada."
                else:
                    print("Assinatura digital inválida.")
                    return "Assinatura digital inválida."
            else:
                print(name, code)
                product = Product(code, name, description, quantity, price, min_stock)
                self.products[code] = product
                return f"Produto {name} ({code}) adicionado ao estoque."

        else:
            return "Usuário não encontrado."

    def record_exit(self, code, user_name, quantity, signature):
        if user_name in self.users:
            user = self.users[user_name]
            if code in self.products:
                product = self.products[code]
                # Verificar a assinatura digital com a chave pública do usuário
                if self.verify_signature(signature, user.public_key):
                    product.add_exit(quantity)
                    return f"Saída de {quantity} unidades de {product.name} registrada."
                else:
                    return "Assinatura digital inválida."
            else:
                return "Produto não encontrado."
        else:
            return "Usuário não encontrado."

    def verify_signature(self, signature, public_key):
        # Implemente a verificação da assinatura digital aqui
        # Use a chave pública para verificar a assinatura
        # Retorne True se a assinatura for válida, caso contrário, retorne False
        return True
    @Pyro5.api.expose
    def generate_stock_report(self):
        # Implemente a geração de relatórios aqui
        # Isso pode incluir produtos em estoque, movimentação de estoque e produtos sem saída
        pass
    @Pyro5.api.expose 
    def notify_replenishment(self, user_name, product):
        # Método para notificar o gestor quando um produto atinge o estoque mínimo
        print("produto fora de esoque")
        print(user_name, self.users)
        if user_name in self.users:
            print("user in clientes")
            client = self.users[user_name]
            print(client.client_object)

            auxObject = Pyro5.api.Proxy(client.client_object)
            print("ok1")
            auxObject.notify_replenishment(product.code)
            print("ok3")
    @Pyro5.api.expose
    def notify_unsold_products(self):
        # Método para enviar relatórios periódicos sobre produtos não vendidos
        for product in self.products.values():
            if product.quantity == 0:
                for user_name in self.clients:
                    client = self.clients[user_name]
                    client.notify_unsold_products(product)

    def __reduce__(self):
        return (self.__class__, (self.name, self.public_key))

# Configurar o servidor PyRO
if __name__ == "__main__":
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(StockManagementSystem())
    ns.register("stock_management_system", uri)
    print("Servidor PyRO pronto.")
    daemon.requestLoop()
