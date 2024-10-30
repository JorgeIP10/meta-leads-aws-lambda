import time
from handlers.request_handler import RequestHandler
from handlers.data_handler import DataHandler
from config.setup import setup_instance


def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time

    return result, execution_time


def start_program():
    historical_sellers_repartition_list = setup_instance.leads_crud_connection.find_all_and_compare(
        setup_instance.campaigns_seller_leads_object_list
    )

    request_handler = RequestHandler(setup_instance.access_token_page, setup_instance.page_id, setup_instance.url_base)
    forms = request_handler.get_forms()
    new_leads = request_handler.get_leads(forms, setup_instance.start_date_str, setup_instance.end_date_str)

    # setup_instance.campaigns_crud_connection.create(new_leads)

    data_handler = DataHandler(setup_instance.campaigns_seller_leads_object_list, historical_sellers_repartition_list, new_leads)
    data_handler.new_leads_to_dataframe()
    leads_to_email_dict_lists = data_handler.get_dataframes_to_email()
    html_content = ''

    for leads_to_email_dict_list in leads_to_email_dict_lists:
        _, dict_lead_sellers_to_email = leads_to_email_dict_list
        html_content += setup_instance.html_template_renderer.render(dict_lead_sellers_to_email['dataframe'])
        html_content += '<br>'

    setup_instance.lead_email_sender.send_lead_emails(setup_instance.lead_email_subject,
                                                      setup_instance.lead_email_body + html_content,
                                                      setup_instance.receiver_emails,
                                                      leads_to_email_dict_lists,
                                                      setup_instance.attachment_paths)

    setup_instance.lead_email_sender.send_emails(setup_instance.confirmation_email_subject,
                                                 setup_instance.confirmation_email_body + html_content,
                                                 setup_instance.confirmation_emails)

    new_leads_to_db_list = data_handler.transform_data_to_db()

    # setup_instance.leads_crud_connection.create(new_leads_to_db_list)
