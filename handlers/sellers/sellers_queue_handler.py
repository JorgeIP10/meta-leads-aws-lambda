from handlers.sellers.priority_sellers_handler import PrioritySellersHandler
import queue
import itertools


# Class for handling sellers with queue library
class SellersQueueHandler(PrioritySellersHandler):
    def __init__(self, sellers_queue: queue.PriorityQueue):
        self.sellers_queue = sellers_queue
        self.counter = itertools.count()  # Contador para el desempate

    def add(self, seller, priority):
        count = next(self.counter)
        self.sellers_queue.put((priority, count, seller))

    def update(self, seller_id, new_data, priority: int = None):
        temp_queue = queue.PriorityQueue()
        while not self.sellers_queue.empty():
            priority, count, seller = self.sellers_queue.get()
            if seller['id'] == seller_id:
                seller.update(new_data)
                if priority is not None:
                    temp_queue.put((priority, count, seller))
            temp_queue.put((priority, count, seller))
        self.sellers_queue = temp_queue

    def remove(self):
        """Eliminar y devolver el elemento con la mayor prioridad (menor valor)."""
        if self.sellers_queue.empty():
            return None
        return self.sellers_queue.get()

    def get_quantity(self):
        return self.sellers_queue.qsize()

    def get_highest_priority_sellers_count(self):
        priorities_list = []
        temp_queue = queue.PriorityQueue()

        while not self.sellers_queue.empty():
            priority, count, seller = self.sellers_queue.get()
            priorities_list.append(priority)
            temp_queue.put((priority, count, seller))

        self.sellers_queue = temp_queue

        maximum_priority = min(priorities_list)
        count = 0

        for priority in priorities_list:
            if priority != maximum_priority:
                count += 1

        if count != 0:
            quantity_highest_priority = len(priorities_list) - count
        else:
            quantity_highest_priority = 0

        return quantity_highest_priority

    def remove_highest_priority(self):
        """Eliminar todos los elementos con la mayor prioridad."""
        if self.sellers_queue.empty():
            return

        # Paso 1: Extraer todos los elementos y encontrar la mayor prioridad
        items = []
        while not self.sellers_queue.empty():
            items.append(self.sellers_queue.get())

        # Encontrar la mayor prioridad
        highest_priority = min(item[0] for item in items)  # La prioridad más alta tiene el valor más bajo
        lowest_priority = max(item[0] for item in items)

        if highest_priority != lowest_priority:
            # Paso 2: Filtrar elementos con la mayor prioridad y restaurar los demás
            remaining_items = [item for item in items if item[0] != highest_priority]
            highest_priority_items = [item for item in items if item[0] == highest_priority]
        else:
            remaining_items = [item for item in items]
            highest_priority_items = remaining_items

        # Restaurar los elementos que no tienen la mayor prioridad
        for item in remaining_items:
            self.sellers_queue.put(item)

        return [item[2] for item in highest_priority_items]  # Devolver solo los vendedores
