from handlers.request_handler import RequestHandler
from handlers.data_handler import DataHandler
from services.leads_email_sender import LeadEmailSender
from config.setup import (ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE, START_DATE_STR,
                          END_DATE_STR, CRUD_CONNECTION, SELLERS_DATA_STRUCTURE, LEAD_EMAIL_SENDER,
                          RECEIVER_EMAILS, CONFIRMATION_EMAILS, HTML_TEMPLATE_RENDERER, ATTACHMENT_PATHS,
                          LEAD_EMAIL_SUBJECT, LEAD_EMAIL_BODY, CONFIRMATION_EMAIL_SUBJECT, CONFIRMATION_EMAIL_BODY)
import time


def measure_execution_time(func, *args, **kwargs):
    """
    Mide el tiempo de ejecución de una función.

    :param func: La función a medir.
    :param args: Argumentos posicionales para la función.
    :param kwargs: Argumentos de palabras clave para la función.
    :return: El resultado de la función y el tiempo de ejecución en segundos.
    """
    start_time = time.time()  # Tiempo de inicio
    result = func(*args, **kwargs)  # Ejecuta la función con los argumentos proporcionados
    end_time = time.time()  # Tiempo de finalización
    execution_time = end_time - start_time  # Calcula el tiempo de ejecución

    return result, execution_time


def start_program():
    # Obtenemos los leads cuyo vendedor coincide con alguno en la lista de vendedores
    historical_leads = CRUD_CONNECTION.find_all_and_compare(SELLERS_DATA_STRUCTURE.get_sellers_list())

    # Creamos un objeto RequestHandler y obtenemos los formularios y los leads
    request_handler = RequestHandler(ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE)
    # forms = request_handler.get_forms()
    # new_leads = request_handler.get_leads(forms, START_DATE_STR, END_DATE_STR)

    forms, exec_time = measure_execution_time(request_handler.get_forms)
    print(f"Tiempo de ejecución de get_forms(): {exec_time:.6f} segundos")
    new_leads, exec_time = measure_execution_time(request_handler.get_leads, forms, START_DATE_STR, END_DATE_STR)
    print(f"Tiempo de ejecución de get_leads(): {exec_time:.6f} segundos")

    # Creamos un objeto DataHandler y transformamos los leads en un DataFrame
    data_handler = DataHandler(SELLERS_DATA_STRUCTURE, historical_leads, new_leads)
    # data_handler.new_leads_to_dataframe()
    result, exec_time = measure_execution_time(data_handler.new_leads_to_dataframe)
    print(f"Tiempo de ejecución de new_leads_to_dataframe(): {exec_time:.6f} segundos")

    # Obtenemos los DataFrames para enviar por correo
    # df_new_leads_to_email, df_sellers = data_handler.get_dataframes_to_email()
    # [df_new_leads_to_email, df_sellers], exec_time = measure_execution_time(data_handler.get_dataframes_to_email)
    # print(f"Tiempo de ejecución de get_dataframes_to_email(): {exec_time:.6f} segundos")
    ([dict_lead_detail_to_email,dict_lead_sellers_to_email],
     exec_time) = measure_execution_time(data_handler.get_dataframes_to_email)
    print(f"Tiempo de ejecución de get_dataframes_to_email(): {exec_time:.6f} segundos")

    list_of_list_of_dictionaries = [[dict_lead_detail_to_email, dict_lead_sellers_to_email]]

    html_content = HTML_TEMPLATE_RENDERER.render(dict_lead_sellers_to_email['dataframe'])

    LEAD_EMAIL_SENDER.send_lead_emails(LEAD_EMAIL_SUBJECT,
                                       LEAD_EMAIL_BODY + html_content,
                                       CONFIRMATION_EMAILS,
                                       list_of_list_of_dictionaries,
                                       ATTACHMENT_PATHS)

    LEAD_EMAIL_SENDER.send_emails(CONFIRMATION_EMAIL_SUBJECT,
                                  CONFIRMATION_EMAIL_BODY + html_content,
                                  CONFIRMATION_EMAILS)

    # Transformamos los nuevos leads a un formato compatible con la base de datos
    new_leads_to_db = data_handler.transform_data_to_db()

    # Insertamos los nuevos leads en la base de datos
    # CRUD_CONNECTION.create(new_leads_to_db)
