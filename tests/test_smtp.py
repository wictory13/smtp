import base64
import smtp
import unittest
from unittest.mock import patch


class TestSmtp(unittest.TestCase):
    @patch('smtp.socket.socket.connect')
    @patch('smtp.socket.socket.recv')
    def test_connect(self, p_recv, p_connect):
        sender = smtp.Smtp(
            'smtp.yandex.ru', 587, '', '', '', '', '', '', '')
        p_recv.return_value = b'220-ok\r\n'
        sender.connect()
        p_connect.assert_called_with(('smtp.yandex.ru', 587))

    @patch('smtp.socket.socket.connect')
    @patch('smtp.socket.socket.recv')
    def test_fail_connect(self, p_recv, p_connect):
        sender = smtp.Smtp(
            'smtp.example.com', 111, '', '', '', '', '', '', '')
        p_recv.return_value = b'421-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException,
                'Невозможно установить соединение с сервером'):
            sender.connect()
        p_connect.assert_called_with(('smtp.example.com', 111))

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_ehlo(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.side_effect = [b'220-ok\r\n', b'250-ok\r\n', b'250 ok\r\n']
        sender.ehlo()
        p_sendall.assert_called_with(b'ehlo localhost\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_ehlo(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'550-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException,
                'Невозможно подключиться к серверу'):
            sender.ehlo()
        p_sendall.assert_called_with(b'ehlo localhost\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_start_tls(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'220-ok\r\n'
        sender.start_tls()
        p_sendall.assert_called_with(b'starttls\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_start_tls(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'421-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException,
                'Невозмоможно передать данные, используя TLS'):
            sender.start_tls()
        p_sendall.assert_called_with(b'starttls\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_auth_login(self, p_recv, p_sendall):
        sender = smtp.Smtp(
            '', 10, '', 'example111@example.com',
            'aaaaaa123', '', '', '', '')
        p_recv.side_effect = [b'334-ok\r\n', b'334-ok\r\n', b'235-ok\r\n']
        sender.auth_login()
        p_sendall.assert_called_with(
            base64.b64encode('aaaaaa123'.encode()) + b'\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_auth_login(self, p_recv, _):
        sender = smtp.Smtp(
            'rgvd', 10, '', 'example111@example.com',
            'aaaaaa123', '', '', '', '')
        p_recv.side_effect = [b'334-ok\r\n', b'235-ok\r\n', b'452-ok\r\n']
        with self.assertRaisesRegex(smtp.SmtpException, 'Ошибка авторизации'):
            sender.auth_login()

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_mail_from(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'250-ok\r\n'
        sender.mail_from()
        p_sendall.assert_called_with(b'mail from: <>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_mail_from(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'452-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException,
                'Невозможно отправить письмо с этого адреса'):
            sender.mail_from()
        p_sendall.assert_called_with(b'mail from: <>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_rcpt_to(self, p_recv, p_sendall):
        sender = smtp.Smtp(
            '', 10, '', '', '', 'example112@example.com',
            '', '', '')
        p_recv.return_value = b'250-ok\r\n'
        sender.rcpt_to('example112@example.com')
        p_sendall.assert_called_with(b'rcpt to: <example112@example.com>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_rcpt_to(self, p_recv, p_sendall):
        sender = smtp.Smtp(
            '', 10, '', '', '', 'example112@example.com',
            '', '', '')
        p_recv.return_value = b'451-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException,
                'Невозможно отправить письмо на этот адрес'):
            sender.rcpt_to('example112@example.com')
        p_sendall.assert_called_with(b'rcpt to: <example112@example.com>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_data(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'354-ok\r\n'
        sender.data()
        p_sendall.assert_called_with(b'data\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_data(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'554-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException, 'Невозможно передать данные'):
            sender.data()
        p_sendall.assert_called_with(b'data\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_send_data(self, p_recv, _):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'250-ok\r\n'
        sender.send_data('aa', 'aaaa', '')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_send_data(self, p_recv, _):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'552-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException, 'Невозможно отправить данные'):
            sender.send_data('aa', 'aaaa', '')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_quit(self, p_recv, p_sendall):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'221-ok\r\n'
        sender.quit()
        p_sendall.assert_called_with(b'quit\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_fail_quit(self, p_recv, _):
        sender = smtp.Smtp('', 10, '', '', '', '', '', '', '')
        p_recv.return_value = b'500-not ok\r\n'
        with self.assertRaisesRegex(
                smtp.SmtpException, ''):
            sender.quit()

    def test_extract_codes(self):
        codes = '334-aaa\r\n334-bbb\r\n235-ccc\r\n'
        self.assertEqual(['334', '334', '235'], smtp.extract_codes(codes))
