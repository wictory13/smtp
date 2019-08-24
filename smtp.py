import base64
from mail import Mail
import socket
import ssl


def extract_codes(answer):
    codes = []
    for string in answer.split('\r\n'):
        codes.append(string[:3])
    return list(filter(None, codes))


class SmtpException(Exception):
    def __init__(self, text):
        self.message = text


class Smtp:
    def __init__(self, host, port, sender_name, sender_email,
                 password, recipient_email, cc,
                 content_type, bcc):
        self.socket_ = socket.socket()
        self.host = host
        self.port = int(port)
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.password = password
        self.recipient_email = recipient_email
        self.cc = cc
        self.bcc = bcc
        self.content_type = content_type

    def get_server_answer(self, command=None):
        if command:
            self.socket_.sendall(command)
        answer = b''
        if command and command.startswith(b'ehlo'):
            error_codes = [b'550', b'500', b'501', b'504', b'421']
            while b'250 ' not in answer:
                answer += read_str(self.socket_)
                if any(error_code in answer for error_code in error_codes):
                    break
        else:
            answer += read_str(self.socket_)
        return answer.decode()

    def connect(self):
        self.socket_ = socket.socket()
        self.socket_.connect((self.host, self.port))
        ans = self.get_server_answer()
        ans_codes = extract_codes(ans)
        if '220' not in ans_codes:
            raise SmtpException('Невозможно установить соединение с сервером')

    def ehlo(self):
        ans = self.get_server_answer('ehlo localhost\r\n'.encode())
        ans_codes = extract_codes(ans)
        if '250' not in ans_codes:
            raise SmtpException('Невозможно подключиться к серверу')

    def start_tls(self):
        ans = self.get_server_answer('starttls\r\n'.encode())
        ans_codes = extract_codes(ans)
        if '220' not in ans_codes:
            raise SmtpException('Невозмоможно передать данные, используя TLS')

    def wrap_socket(self):
        self.socket_ = ssl.wrap_socket(
            self.socket_, ssl_version=ssl.PROTOCOL_SSLv23)

    def auth_login(self):
        ans = self.get_server_answer('auth login\r\n'.encode()) + \
              self.get_server_answer(
                  base64.b64encode(self.sender_email.encode()) + b'\r\n') + \
              self.get_server_answer(
                  base64.b64encode(self.password.encode()) + b'\r\n')
        ans_codes = extract_codes(ans)

        if ans_codes.count('334') != 2 or '235' not in ans_codes:
            raise SmtpException('Ошибка авторизации')

    def mail_from(self):
        ans = self.get_server_answer(
            'mail from: <{}>\r\n'.format(self.sender_email).encode())
        ans_code = extract_codes(ans)
        if '250' not in ans_code:
            raise SmtpException('Невозможно отправить письмо с этого адреса')

    def rcpt_to(self, recipient_email):
        ans = self.get_server_answer(
            'rcpt to: <{}>\r\n'.format(recipient_email).encode())
        ans_code = extract_codes(ans)
        if '250' not in ans_code:
            raise SmtpException('Невозможно отправить письмо на этот адрес')

    def data(self):
        ans = self.get_server_answer('data\r\n'.encode())
        ans_code = extract_codes(ans)
        if '354' not in ans_code:
            raise SmtpException('Невозможно передать данные')

    def send_data(self, text, subject, attachments):
        mail = Mail(self.sender_name, self.sender_email, self.recipient_email,
                    text, self.cc, subject,
                    self.content_type, attachments)
        ans = self.get_server_answer(mail.full_text)
        ans_code = extract_codes(ans)
        if '250' not in ans_code:
            raise SmtpException(ans)

    def quit(self):
        ans = self.get_server_answer('quit\r\n'.encode())
        ans_code = extract_codes(ans)
        if '221' not in ans_code:
            raise SmtpException('')


def read_str(ss):
    answer = b''
    while not answer.endswith(b'\r\n'):
        answer += ss.recv(1)
    return answer
