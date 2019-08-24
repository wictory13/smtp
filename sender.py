import os
from zipfile import ZipFile
from smtp import Smtp

ATTACHMENT_SIZE = 8 * 1024 * 1024


class Sender:
    def __init__(self, attachments, attachments_names, host, port, name,
                 email, password, recipient, cc, content_type, bcc):
        self.attachments = attachments
        self.attachments_names = attachments_names
        self.attachs_to_send = []
        self.part_attachs = []
        self.smtp = Smtp(host, port, name, email, password, recipient, cc,
                         content_type, bcc)

    def send(self, text, subject, zip_attch, archive_name):
        if zip_attch:
            self.archive_zip(archive_name)
        elif self.attachments:
            for i in range(len(self.attachments)):
                attach_name = self.attachments_names[i]
                if os.path.getsize(self.attachments[i]) > ATTACHMENT_SIZE:
                    attach_parts = self.cut_attachment(
                        self.attachments[i], attach_name)
                    self.part_attachs.append(attach_parts)
                else:
                    self.attachs_to_send.append(
                        (self.attachments[i], attach_name))
        if self.part_attachs:
            for j in range(len(self.part_attachs)):
                for i in range(len(self.part_attachs[j])):
                    self.connect_and_send_headers()
                    if i == 0 and j == 0:
                        self.attachs_to_send.append(self.part_attachs[j][i])
                        self.smtp.send_data(
                            text, subject or 'part{}/{}'.format(
                                i + 1, len(self.part_attachs[j])),
                            self.attachs_to_send)
                    else:
                        self.smtp.send_data(
                            '', 'part{}/{}'.format(
                                i + 1, len(self.part_attachs[j])),
                            [self.part_attachs[j][i]])
                    self.smtp.quit()
        else:
            self.connect_and_send_headers()
            self.smtp.send_data(text, subject, self.attachs_to_send)
            self.smtp.quit()
        if zip_attch:
            os.remove(self.attachs_to_send[0][0])
        if self.part_attachs:
            for part_attach in self.part_attachs:
                for part_attach_names in part_attach:
                    os.remove(part_attach_names[1])

    @staticmethod
    def cut_attachment(attachment, attachment_name):
        attach_parts = []
        k = 1
        with open(attachment, 'r') as f:
            while True:
                data = f.read(ATTACHMENT_SIZE)
                if not data:
                    break
                name, ext = os.path.splitext(attachment_name)
                new_filename = name + '.part' + str(k) + ext
                with open(new_filename, 'w') as f2:
                    f2.write(data)
                k += 1
                attach_parts.append(
                    (new_filename, new_filename))
        return attach_parts

    def connect_and_send_headers(self):
        self.smtp.connect()
        self.smtp.ehlo()
        self.smtp.start_tls()
        self.smtp.wrap_socket()
        self.smtp.auth_login()
        self.smtp.mail_from()
        if self.smtp.bcc != '':
            for address in self.smtp.bcc.split(', '):
                self.smtp.rcpt_to(address)
        self.smtp.rcpt_to(self.smtp.recipient_email)
        self.smtp.data()

    def archive_zip(self, archive_name):
        archive_to_send = (archive_name or 'archive') + '.zip'
        with ZipFile(archive_to_send, 'w') as archive:
            for attach in self.attachments:
                archive.write(attach)
        self.attachs_to_send.append((archive_to_send, archive_to_send))
