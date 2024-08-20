from handlers.request_handler import RequestHandler
from handlers.data_handler import DataHandler
from services.email_sender import EmailSender
from config.setup import (ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE, START_DATE_STR,
                          END_DATE_STR, GMAIL_SENDER_EMAIL, GMAIL_SENDER_PASSWORD,
                          GMAIL_RECEIVER_EMAIL_1, GMAIL_RECEIVER_EMAIL_2,
                          GMAIL_AUXILIAR_EMAIL_1, GMAIL_AUXILIAR_EMAIL_2,
                          CRUD_CONNECTION, SELLERS_DATA_STRUCTURE)


def start_program():
    # Obtenemos los leads cuyo vendedor coincide con alguno en la lista de vendedores
    historical_leads = CRUD_CONNECTION.find_all_and_compare(SELLERS_DATA_STRUCTURE.get_sellers_list())

    # Creamos un objeto RequestHandler y obtenemos los formularios y los leads
    request_handler = RequestHandler(ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE)
    forms = request_handler.get_forms()
    new_leads = request_handler.get_leads(forms, START_DATE_STR, END_DATE_STR)

    # Creamos un objeto DataHandler y transformamos los leads en un DataFrame
    data_handler = DataHandler(SELLERS_DATA_STRUCTURE, historical_leads, new_leads)
    data_handler.new_leads_to_dataframe()

    # Obtenemos los DataFrames para enviar por correo
    df_new_leads_to_email, df_sellers = data_handler.get_dataframes_to_email()

    # Creamos un objeto EmailSender con las credenciales de la cuenta de Gmail
    email_sender = EmailSender('smtp.gmail.com',
                               465,
                               GMAIL_SENDER_EMAIL,
                               GMAIL_SENDER_PASSWORD)

    filename_leads = f'LEADS_{"".join((START_DATE_STR.split("-")))}.xlsx'
    filename_leads_sellers = f'LEADS_VENDEDORES_{"".join((START_DATE_STR.split("-")))}.xlsx'

    attachment_paths = [filename_leads, filename_leads_sellers]
    data_frame_list = [df_new_leads_to_email, df_sellers]

    receiver_emails = [GMAIL_RECEIVER_EMAIL_1, GMAIL_RECEIVER_EMAIL_2]
    auxiliar_emails = [GMAIL_AUXILIAR_EMAIL_1, GMAIL_AUXILIAR_EMAIL_2]

    # email_sender.send_emails(receiver_emails,
    #                           'Reporte de Leads y repartición de leads por vendedor',
    #                           f'Se adjunta el reporte de leads y su repartición del día {START_DATE_STR}.',
    #                           data_frame_list, attachment_paths)

    email_sender.send_auxiliar_email(auxiliar_emails,
                                      'Reporte de Leads',
                                      f'Se enviaron los reportes de leads del día {START_DATE_STR}'
                                      f' a {GMAIL_RECEIVER_EMAIL_1} y a {GMAIL_RECEIVER_EMAIL_2}.')

    # Transformamos los nuevos leads a un formato compatible con la base de datos
    new_leads_to_db = data_handler.transform_data_to_db()

    # Insertamos los nuevos leads en la base de datos
    # CRUD_CONNECTION.create(new_leads_to_db)
