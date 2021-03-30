"""
ckanext-systeminfo
Copyright (c) 2018 Keitaro AB

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import re
import smtplib
import cgi
from paste.deploy.converters import asbool
from socket import error as socket_error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from smtplib import SMTPRecipientsRefused

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config


log = logging.getLogger(__name__)

SMTP_SERVER = config.get('smtp.server', '')
SMTP_USER = config.get('smtp.user', '')
SMTP_PASSWORD = config.get('smtp.password', '')
SMTP_FROM = config.get('smtp.mail_from')


def send_email(content, to, subject, file=None):
    '''Sends email
       :param content: The body content for the mail.
       :type string:
       :param to: To whom will be mail sent
       :type string:
       :param subject: The subject of mail.
       :type string:
       :rtype: string
       '''

    msg = MIMEMultipart('alternative')

    from_ = SMTP_FROM

    if isinstance(to, basestring):
        to = [to]

    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = ','.join(to)

    msg.attach(MIMEText(content, 'html', _charset='utf-8'))
    msg.attach(MIMEText(re.sub(r'<[^<]+?>', '', content), 'plain', _charset='utf-8'))
    if isinstance(file, cgi.FieldStorage):
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.file.read())
        Encoders.encode_base64(part)

        extension = file.filename.split('.')[-1]

        part.add_header('Content-Disposition', 'attachment; filename=attachment.{0}'.format(extension))

        msg.attach(part)

    try:
        s = smtplib.SMTP(SMTP_SERVER)
        if SMTP_USER:
            s.login(SMTP_USER, SMTP_PASSWORD)
        s.sendmail(from_, to, msg.as_string())
        s.quit()
        response_dict = {
            'success' : True,
            'message' : 'Email message was successfully sent.'
        }
        return response_dict
    except SMTPRecipientsRefused:
        error = {
            'success': False,
            'error': {
                'fields': {'recepient' : 'Invalid email recepient, maintainer not found'}
            }
        }
        return error
    except socket_error:
        log.critical('Could not connect to email server. Have you configured the SMTP settings?')
        error_dict = {
            'success': False,
            'message' : 'An error occured while sending the email. Try again.'
        }
        return error_dict
