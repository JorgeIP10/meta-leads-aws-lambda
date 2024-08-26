import os
from datetime import datetime, timedelta
from db.postgres.postgres_connection import PostgresConnection
import psycopg2
from db.postgres.postgres_crud import PostgresCrud
from handlers.sellers.seller_priority_data_structure import SellerPriorityDataStructure
from handlers.sellers.sellers_queue_handler import SellersQueueHandler
import queue
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# load_dotenv()

# Token de acceso de la página
ACCESS_TOKEN_PAGE = os.getenv('ACCESS_TOKEN_PAGE')

# El ID de la página o del objeto al que quieres acceder
PAGE_ID = os.getenv('PAGE_ID')

# La URL base de la API de Graph
URL_BASE = os.getenv('URL_BASE')

# Credenciales de la cuenta de Gmail que envía el correo
GMAIL_SENDER_EMAIL = os.getenv('GMAIL_SENDER_EMAIL')
GMAIL_SENDER_PASSWORD = os.getenv('GMAIL_SENDER_PASSWORD')

# Correos de los destinatarios
GMAIL_RECEIVER_EMAIL_1 = os.getenv('GMAIL_RECEIVER_EMAIL_1')
GMAIL_RECEIVER_EMAIL_2 = os.getenv('GMAIL_RECEIVER_EMAIL_2')

# Correos de los destinatarios auxiliares
GMAIL_AUXILIAR_EMAIL_1 = os.getenv('GMAIL_AUXILIAR_EMAIL_1')
GMAIL_AUXILIAR_EMAIL_2 = os.getenv('GMAIL_AUXILIAR_EMAIL_2')

print(datetime.now())

start_date = datetime.now() - timedelta(hours=29)
end_date = datetime.now() - timedelta(hours=29)
print(start_date)

# Convertimos las fechas a strings
START_DATE_STR = start_date.strftime('%d-%m-%Y')
END_DATE_STR = end_date.strftime('%d-%m-%Y')
print(START_DATE_STR)

CONNECTION = PostgresConnection(os.getenv('HOSTNAME'),
                                os.getenv('DATABASE'),
                                os.getenv('DB_USERNAME'),
                                os.getenv('DB_PASSWORD'),
                                os.getenv('PORT'),
                                psycopg2.connect
                                )
CONNECTION.create_connection_cursor()
CRUD_CONNECTION = PostgresCrud(CONNECTION)

SELLER_ID_1 = int(os.getenv('SELLER_ID_1'))
SELLER_NAME_1 = os.getenv('SELLER_NAME_1')
SELLER_ID_2 = int(os.getenv('SELLER_ID_2'))
SELLER_NAME_2 = os.getenv('SELLER_NAME_2')
SELLER_ID_3 = int(os.getenv('SELLER_ID_3'))
SELLER_NAME_3 = os.getenv('SELLER_NAME_3')
SELLER_ID_4 = int(os.getenv('SELLER_ID_4'))
SELLER_NAME_4 = os.getenv('SELLER_NAME_4')

sellers_queue = queue.PriorityQueue()
SELLERS_DATA_STRUCTURE = SellerPriorityDataStructure(SellersQueueHandler(sellers_queue))
SELLERS_DATA_STRUCTURE.add_seller({'id': SELLER_ID_1, 'name': SELLER_NAME_1}, 2)
SELLERS_DATA_STRUCTURE.add_seller({'id': SELLER_ID_2, 'name': SELLER_NAME_2}, 2)
SELLERS_DATA_STRUCTURE.add_seller({'id': SELLER_ID_3, 'name': SELLER_NAME_3}, 2)
SELLERS_DATA_STRUCTURE.add_seller({'id': SELLER_ID_4, 'name': SELLER_NAME_4}, 2)
