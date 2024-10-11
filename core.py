import time
from handlers.request_handler import RequestHandler
from handlers.data_handler import DataHandler
from config.setup import (ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE, START_DATE_STR,
                          END_DATE_STR, LEADS_CRUD_CONNECTION, SELLERS_DATA_STRUCTURE, LEAD_EMAIL_SENDER,
                          RECEIVER_EMAILS, CONFIRMATION_EMAILS, HTML_TEMPLATE_RENDERER, ATTACHMENT_PATHS,
                          LEAD_EMAIL_SUBJECT, LEAD_EMAIL_BODY, CONFIRMATION_EMAIL_SUBJECT, CONFIRMATION_EMAIL_BODY)


def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time

    return result, execution_time


def start_program():
    historical_leads = LEADS_CRUD_CONNECTION.find_all_and_compare(SELLERS_DATA_STRUCTURE.get_sellers_list())

    request_handler = RequestHandler(ACCESS_TOKEN_PAGE, PAGE_ID, URL_BASE)
    forms = request_handler.get_forms()
    new_leads = request_handler.get_leads(forms, START_DATE_STR, END_DATE_STR)

    data_handler = DataHandler(SELLERS_DATA_STRUCTURE, historical_leads, new_leads)
    data_handler.new_leads_to_dataframe()

    dict_lead_detail_to_email, dict_lead_sellers_to_email = data_handler.get_dataframes_to_email()

    list_of_list_of_dictionaries = [[dict_lead_detail_to_email, dict_lead_sellers_to_email]]

    html_content = HTML_TEMPLATE_RENDERER.render(dict_lead_sellers_to_email['dataframe'])

    LEAD_EMAIL_SENDER.send_lead_emails(LEAD_EMAIL_SUBJECT,
                                       LEAD_EMAIL_BODY + html_content,
                                       RECEIVER_EMAILS,
                                       list_of_list_of_dictionaries,
                                       ATTACHMENT_PATHS)
    LEAD_EMAIL_SENDER.send_emails(CONFIRMATION_EMAIL_SUBJECT,
                                  CONFIRMATION_EMAIL_BODY + html_content,
                                  CONFIRMATION_EMAILS)

    new_leads_to_db = data_handler.transform_data_to_db()

    LEADS_CRUD_CONNECTION.create(new_leads_to_db)
