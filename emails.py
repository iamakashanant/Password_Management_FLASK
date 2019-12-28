import logging
from datetime import datetime
from os import path
import jinja2
import boto3
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


SES_REGION_NAME = 'us-east-1'
SES_KEY = 'AKIA3PYGYYWFJUGSAZME'
SES_SECRET = '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'
SES_SENDER_EMAIL = 'tech@magentaconnect.com'

jinja_loader = jinja2.FileSystemLoader(path.join(path.dirname(path.dirname(__file__)), 'templates'))
jinja_env = jinja2.Environment(loader=jinja_loader)


def load_template(templatepath=None, context={}):
    if not templatepath:
        return ""
    template = jinja_env.get_template(templatepath)
    return template.render(context)


# @app.celery_task
def async_send_email(subject, template_data, recipients=[], attachments=[]):
    try:
        email_client = boto3.client(
            'ses',
            region_name=SES_REGION_NAME,
            aws_access_key_id=SES_KEY,
            aws_secret_access_key=SES_SECRET
        )

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = ",".join(recipients)

        body = MIMEText(template_data, 'html')
        msg.attach(body)

        for file in attachments:
            fp = open(file, 'rb')
            attachment = MIMEApplication(fp.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=file.split("/")[-1])
            msg.attach(attachment)

        email_client.send_raw_email(
            Source=SES_SENDER_EMAIL,
            Destinations=recipients,
            RawMessage={'Data': msg.as_string()}
        )

        STATUS = "SUCCESS : Email Sent"

    except Exception as e:
        STATUS = str(e)

    log_text = f'''
    -------------------------------------------------------------------------------
    RECIPIENT = {recipients}
    SUBJECT   = {subject}
    DATE      = {datetime.now()}
    STATUS    = {STATUS}
    -------------------------------------------------------------------------------
    '''
    logging.debug(log_text)


########################################################################################################################
# -------------------- DO NOT MODIFY THIS CODE WITHOUT CONSULTING ---------------------------------------------------- #
#
#                   ADDING CELERY TO SENDING EMAIL FUNCTIONS
#
########################################################################################################################
def send_email(subject, recipients, template_path, context = {}, attachments=[]):
    template_data = load_template(template_path, context)
    return async_send_email(subject, template_data, recipients, attachments)
