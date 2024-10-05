import os
from datetime import datetime, timedelta
from db.postgres.postgres_connection import PostgresConnection
import psycopg2
from db.postgres.postgres_leads_crud import PostgresLeadsCrud
from db.postgres.postgres_person_crud import PostgresPersonCrud
from handlers.sellers.seller_priority_data_structure import SellerPriorityDataStructure
from handlers.sellers.sellers_queue_handler import SellersQueueHandler
import queue
from services.leads_email_sender import LeadEmailSender
from templates.html_template_renderer import HTMLTemplateRenderer
# from dotenv import load_dotenv
#
# # Load environment variables from the .env file
# load_dotenv()

ACCESS_TOKEN_PAGE = os.getenv('ACCESS_TOKEN_PAGE')

PAGE_ID = os.getenv('PAGE_ID')

URL_BASE = os.getenv('URL_BASE')

GMAIL_SENDER_EMAIL = os.getenv('GMAIL_SENDER_EMAIL')
GMAIL_SENDER_PASSWORD = os.getenv('GMAIL_SENDER_PASSWORD')

GMAIL_RECEIVER_EMAIL_1 = os.getenv('GMAIL_RECEIVER_EMAIL_1')
GMAIL_RECEIVER_EMAIL_2 = os.getenv('GMAIL_RECEIVER_EMAIL_2')

GMAIL_CONFIRMATION_EMAIL_1 = os.getenv('GMAIL_CONFIRMATION_EMAIL_1')
GMAIL_CONFIRMATION_EMAIL_2 = os.getenv('GMAIL_CONFIRMATION_EMAIL_2')
GMAIL_CONFIRMATION_EMAIL_3 = os.getenv('GMAIL_CONFIRMATION_EMAIL_3')

print(datetime.now())

start_date = datetime.now() - timedelta(hours=1)
end_date = datetime.now() - timedelta(hours=1)
print(start_date)

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
PERSON_CRUD_CONNECTION = PostgresPersonCrud(CONNECTION)
LEADS_CRUD_CONNECTION = PostgresLeadsCrud(CONNECTION, PERSON_CRUD_CONNECTION)

SELLER_ID_1 = int(os.getenv('SELLER_ID_1'))
SELLER_NAME_1 = os.getenv('SELLER_NAME_1')
SELLER_ID_2 = int(os.getenv('SELLER_ID_2'))
SELLER_NAME_2 = os.getenv('SELLER_NAME_2')
SELLER_ID_3 = int(os.getenv('SELLER_ID_3'))
SELLER_NAME_3 = os.getenv('SELLER_NAME_3')
SELLER_ID_4 = int(os.getenv('SELLER_ID_4'))
SELLER_NAME_4 = os.getenv('SELLER_NAME_4')
SELLER_ID_5 = int(os.getenv('SELLER_ID_5'))
SELLER_NAME_5 = os.getenv('SELLER_NAME_5')

sellers_queue = queue.PriorityQueue()
SELLERS_DATA_STRUCTURE = SellerPriorityDataStructure(SellersQueueHandler(sellers_queue))
SELLERS_DATA_STRUCTURE.add_seller(
    {
        'id': SELLER_ID_1,
        'name': SELLER_NAME_1,
        'fixed_amount_of_leads': 1,
        'additional_leads': 0
    }, 2
)
SELLERS_DATA_STRUCTURE.add_seller(
    {
        'id': SELLER_ID_2,
        'name': SELLER_NAME_2,
        'fixed_amount_of_leads': 0,
        'additional_leads': 0
    }, 2
)
SELLERS_DATA_STRUCTURE.add_seller(
    {
        'id': SELLER_ID_3,
        'name': SELLER_NAME_3,
        'fixed_amount_of_leads': 0,
        'additional_leads': 0
    }, 2
)
SELLERS_DATA_STRUCTURE.add_seller(
    {
        'id': SELLER_ID_4,
        'name': SELLER_NAME_4,
        'fixed_amount_of_leads': 0,
        'additional_leads': 0
    }, 2
)
SELLERS_DATA_STRUCTURE.add_seller(
    {
        'id': SELLER_ID_5,
        'name': SELLER_NAME_5,
        'fixed_amount_of_leads': 0,
        'additional_leads': 0
    }, 2
)

FILENAME_LEADS_DETAIL = f'LEADS_{"".join((START_DATE_STR.split("-")))}.xlsx'
FILENAME_LEADS_SELLERS = f'LEADS_VENDEDORES_{"".join((START_DATE_STR.split("-")))}.xlsx'
ATTACHMENT_PATHS = [FILENAME_LEADS_DETAIL, FILENAME_LEADS_SELLERS]

LEAD_EMAIL_SENDER = LeadEmailSender('smtp.gmail.com',
                                    465,
                                    GMAIL_SENDER_EMAIL,
                                    GMAIL_SENDER_PASSWORD)

RECEIVER_EMAILS = [GMAIL_RECEIVER_EMAIL_1, GMAIL_RECEIVER_EMAIL_2, GMAIL_CONFIRMATION_EMAIL_1]
CONFIRMATION_EMAILS = [GMAIL_CONFIRMATION_EMAIL_1, GMAIL_CONFIRMATION_EMAIL_2, GMAIL_CONFIRMATION_EMAIL_3]

LEAD_EMAIL_SUBJECT = 'Reporte de Leads'
LEAD_EMAIL_BODY = f'<p>Se adjunta el reporte de leads y su repartición del día <b>{START_DATE_STR}</b>.</p>'

CONFIRMATION_EMAIL_SUBJECT = 'Confirmación de envío de reporte de Leads'
CONFIRMATION_EMAIL_BODY = f'<p>Se enviaron los reportes de leads del día <b>{START_DATE_STR}</b>' \
                          f' a <b>{GMAIL_RECEIVER_EMAIL_1}</b> y a <b>{GMAIL_RECEIVER_EMAIL_2}</b>.</p>'

HTML_TEMPLATE_RENDERER = HTMLTemplateRenderer()
