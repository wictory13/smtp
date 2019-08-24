from base64 import b64encode
from datetime import datetime
from mimetypes import guess_type
import os


class Mail:
    def __init__(self, sender_name, sender_email, recipient_email,
                 text, cc, subject, content_type, attachments):
        self.date = datetime.strftime(datetime.now(), '%a, %d %b %Y %H:%M:%S')
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        self.cc = self.set_cc(cc)
        self.subject = self.set_subject(subject)
        self.text = text
        self.content_type = content_type
        self.email = self.create_email()
        self.attach = self.create_attach(attachments)
        self.full_text = (self.email + self.attach + '\r\n.\r\n').encode()

    def set_cc(self, cc):
        if cc:
            return 'Cc: {}\n'.format(cc)
        return ''

    def set_subject(self, subject):
        if subject:
            return 'Subject: {}\n'.format(subject)
        return ''

    def create_attach(self, attachments):
        if attachments:
            text = ''
            for filename, new_filename in attachments:
                with open(filename, 'rb') as f:
                    file = f.read()
                text += 'Content-Disposition: attachment; ' \
                        'filename="{}"\nContent-Transfer-Encoding: ' \
                        'base64\nContent-Type: {}; name="{}"\n\n\n{}\n' \
                        '--border\n'.format(
                            new_filename, guess_type(new_filename)[0],
                            os.path.split(filename)[1],
                            b64encode(file).decode())
            return text
        return ''

    def create_email(self):
        mail_text = 'Content-Type: multipart/mixed; boundary=border\n' \
                    'From: {} <{}>\nTo: {}\n{}{}' \
                    'MIME-Version: 1.0\nDate: {}\n' \
                    'Return-Path: {}\n\n--border\n' \
                    'Content-Transfer-Encoding: 8bit\n' \
                    'Content-Type: text/{}; charset=utf-8\n\n{}' \
                    '\n--border\n'.format(
                        self.sender_name, self.sender_email,
                        self.recipient_email, self.cc, self.subject,
                        self.date, self.sender_email,
                        self.content_type, self.text)
        return mail_text
