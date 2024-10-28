class SellerPriorityDataStructure:
    def __init__(self, priority_sellers_handler):
        self.priority_sellers_handler = priority_sellers_handler

    def add_seller(self, seller, priority):
        self.priority_sellers_handler.add(seller, priority)

    def add_sellers(self, sellers):
        for seller in sellers:
            self.add_seller(seller, seller['priority'])

    def update_seller(self, seller_id, new_data):
        self.priority_sellers_handler.update(seller_id, new_data)

    def get_sellers_quantity(self):
        return self.priority_sellers_handler.get_quantity()

    def remove_seller(self):
        return self.priority_sellers_handler.remove()

    def get_sellers_list(self):
        """Devuelve una lista de vendedores ordenados por prioridad sin alterar la cola original."""
        sellers = []

        # Extraer todos los elementos de la cola
        while self.get_sellers_quantity() > 0:
            priority, count, seller = self.priority_sellers_handler.sellers_queue.get()
            sellers.append((priority, count, seller))

        # Restaurar los elementos en la cola
        for priority, count, seller in sellers:
            self.priority_sellers_handler.add(seller, priority)

        return [seller for priority, _, seller in sellers]
