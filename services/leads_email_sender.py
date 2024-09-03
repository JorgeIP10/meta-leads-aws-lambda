import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from io import BytesIO
from services.email_sender import EmailSender


class LeadEmailSender(EmailSender):
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def create_excel_attachment(self, dictionaries_list):
        # Guardar el DataFrame en un buffer BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for dictionary in dictionaries_list:
                dictionary['dataframe'].to_excel(writer, index=False, sheet_name=dictionary['sheet_name'])
                # dataframe.to_excel(writer, index=False, sheet_name='Resumen')
        buffer.seek(0)

        return buffer

    def send_emails(self, subject, body, destination_emails):
        for destination_email in destination_emails:
            msg = EmailMessage()
            msg['From'] = self.username
            msg['To'] = destination_email
            msg['Subject'] = subject
            msg.set_content(body, subtype='html')

            # Enviar el correo
            with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f'Correo enviado a {destination_email}')

    def send_lead_emails(self, subject, body, destination_emails, list_of_list_of_dictionaries, filename_list):
        for destination_email in destination_emails:
            msg = EmailMessage()
            msg['From'] = self.username
            msg['To'] = destination_email
            msg['Subject'] = subject
            msg.set_content(body, subtype='html')

            # Crear y adjuntar un archivo Excel por cada DataFrame en la lista
            for index, list_of_dictionaries in enumerate(list_of_list_of_dictionaries):
                buffer = self.create_excel_attachment(list_of_dictionaries)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(buffer.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=filename_list[index])
                msg.add_attachment(part.get_payload(decode=True), maintype='application', subtype='octet-stream',
                                   filename=filename_list[index])

            # Enviar el correo
            with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f'Correo de leads enviado a {destination_email}')
