import os
from datetime import datetime, timedelta, timezone
from db.postgres.postgres_connection import PostgresConnection
import psycopg2
from repositories.db_crud import DBCrud
from db.postgres.postgres_leads_crud import PostgresLeadsCrud
from db.postgres.postgres_person_crud import PostgresPersonCrud
from db.postgres.postgres_campaigns_crud import PostgresCampaignsCrud
from handlers.sellers.seller_priority_data_structure import SellerPriorityDataStructure
from handlers.sellers.sellers_queue_handler import SellersQueueHandler
import queue
from services.leads_email_sender import LeadEmailSender
from templates.html_template_renderer import HTMLTemplateRenderer
import pandas as pd


class Setup:
    def __init__(self, access_token_page, page_id, url_base, start_date_str, end_date_str, leads_crud_connection: DBCrud,
                 campaigns_crud_connection: DBCrud, lead_email_sender, receiver_emails, confirmation_emails,
                 campaigns_seller_leads_object_list):
        self.access_token_page = access_token_page
        self.page_id = page_id
        self.url_base = url_base
        self.start_date_str = start_date_str
        self.end_date_str = end_date_str
        self.leads_crud_connection = leads_crud_connection
        self.campaigns_crud_connection = campaigns_crud_connection
        self.lead_email_sender = lead_email_sender
        self.receiver_emails = receiver_emails
        self.confirmation_emails = confirmation_emails
        self.html_template_renderer = None
        self.attachment_paths = None
        self.lead_email_subject = None
        self.lead_email_body = None
        self.confirmation_email_subject = None
        self.confirmation_email_body = None
        self.campaigns_seller_leads_object_list = campaigns_seller_leads_object_list
        self.get_day_start_end_utc()

    def get_day_start_end_utc(self):
        local_time = datetime.now()

        if not self.start_date_str:
            local_start_time_utc_minus_5 = local_time - timedelta(days=1)
            self.start_date_str = local_start_time_utc_minus_5.strftime('%d-%m-%Y')

        if not self.end_date_str:
            local_end_time_utc_minus_5 = local_time
            self.end_date_str = local_end_time_utc_minus_5.strftime('%d-%m-%Y')
        else:
            end_date = datetime.strptime(self.end_date_str, '%d-%m-%Y')
            end_date = end_date + timedelta(days=1)
            self.end_date_str = end_date.strftime('%d-%m-%Y')

        print("Fecha de inicio UTC:", self.start_date_str)
        print("Fecha de fin UTC:", self.end_date_str)


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

START_DATE_STR = ''
END_DATE_STR = ''

connection = PostgresConnection(os.getenv('HOSTNAME'),
                                os.getenv('DATABASE'),
                                os.getenv('DB_USERNAME'),
                                os.getenv('DB_PASSWORD'),
                                os.getenv('PORT'),
                                psycopg2.connect
                                )
connection.create_connection_cursor()
person_crud_connection = PostgresPersonCrud(connection)
leads_crud_connection = PostgresLeadsCrud(connection, person_crud_connection)
campaigns_crud_connection = PostgresCampaignsCrud(connection)

sellers_campaigns = campaigns_crud_connection.get_sellers_campaigns()

campaigns_seller_leads_object_list = []

for sellers_campaign in sellers_campaigns:
    sellers_queue = queue.PriorityQueue()
    sellers_data_structure = SellerPriorityDataStructure(SellersQueueHandler(sellers_queue))
    sellers_data_structure.add_sellers(sellers_campaign['sellers'])
    campaigns_seller_leads_object_list.append({
        'campaign': sellers_campaign['general_campaign_name'],
        'sellers_data_structure': sellers_data_structure,
        'leads': [],
        'leads_dataframe': pd.DataFrame()
    })


receiver_emails = [GMAIL_RECEIVER_EMAIL_1, GMAIL_RECEIVER_EMAIL_2]
confirmation_emails = [GMAIL_CONFIRMATION_EMAIL_1, GMAIL_CONFIRMATION_EMAIL_2, GMAIL_CONFIRMATION_EMAIL_3]
lead_email_sender = LeadEmailSender('smtp.gmail.com',
                                    465,
                                    GMAIL_SENDER_EMAIL,
                                    GMAIL_SENDER_PASSWORD)

setup_instance = Setup(ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE, START_DATE_STR,
                       END_DATE_STR, leads_crud_connection, campaigns_crud_connection, lead_email_sender,
                       receiver_emails, confirmation_emails, campaigns_seller_leads_object_list)

filename_leads_detail = f'LEADS_{"".join((setup_instance.start_date_str.split("-")))}.xlsx'
setup_instance.attachment_paths = [filename_leads_detail]

setup_instance.lead_email_subject = 'Reporte de Leads'
setup_instance.lead_email_body = (f'<p>Se adjunta el reporte de leads y su repartición del día'
                                  f'<b>{setup_instance.start_date_str}</b>.</p>')

setup_instance.confirmation_email_subject = 'Confirmación de envío de reporte de Leads'
setup_instance.confirmation_email_body = (f'<p>Se enviaron los reportes de leads del día'
                                          f'<b>{setup_instance.start_date_str}</b> a <b>{GMAIL_RECEIVER_EMAIL_1}</b>'
                                          f'y a <b>{GMAIL_RECEIVER_EMAIL_2}</b>.</p>')

setup_instance.html_template_renderer = HTMLTemplateRenderer()
