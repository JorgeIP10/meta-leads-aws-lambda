import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from io import BytesIO

class EmailSender:
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def create_excel_attachment(self, dataframe):
        # Guardar el DataFrame en un buffer BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
        buffer.seek(0)

        return buffer

    def send_auxiliar_email(self, to_emails, subject, body):
        for to_email in to_emails:
            msg = EmailMessage()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.set_content(body)

            # Enviar el correo
            with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f'Correo de confirmación enviado a {to_email}')

    def send_emails(self, to_emails, subject, body, dataframe_list, filename_list):
        for to_email in to_emails:
            msg = EmailMessage()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.set_content(body)

            # Crear y adjuntar un archivo Excel por cada DataFrame en la lista
            for index, dataframe in enumerate(dataframe_list):
                buffer = self.create_excel_attachment(dataframe)
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

            print(f'Correo de leads enviado a {to_email}')
