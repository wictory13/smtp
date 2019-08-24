import os
import sys
from PyQt5.QtWidgets import (QApplication, QCheckBox,
                             QFileDialog, QGridLayout, QHeaderView,
                             QInputDialog, QLabel,
                             QLineEdit, QTextEdit,
                             QTableWidget, QPushButton, QWidget)

from sender import Sender
from smtp import SmtpException


class Window(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setWindowTitle('smtp-client')

        host = QLabel('Host:')
        port = QLabel('Port:')
        name = QLabel('Name:')
        email = QLabel('Sender:')
        recipient = QLabel('Rcpt To:')
        cc = QLabel('CC:')
        bcc = QLabel('BCC:')
        subject = QLabel('Subject:')
        text = QLabel('Text:')
        self.attachLabel = QLabel('Attachments:')

        self.content_type = 'plain'

        self.attachments = []

        self.current_state = QLabel(
            'Заполните обязательные поля перед отправкой')

        self.hostEdit = QLineEdit()
        self.defaultStyleSheet = self.hostEdit.styleSheet()
        self.hostEdit.setPlaceholderText('smtp.example.com')

        self.portEdit = QLineEdit()
        self.portEdit.setFixedWidth(60)
        self.portEdit.setPlaceholderText('587')

        self.nameEdit = QLineEdit()

        self.emailEdit = QLineEdit()
        self.emailEdit.setPlaceholderText('example111@example.com')

        self.password = ''

        self.recipientEdit = QLineEdit()
        self.recipientEdit.setPlaceholderText('example112@example.com')

        self.ccEdit = QLineEdit()
        self.bccEdit = QLineEdit()
        self.subjectEdit = QLineEdit()
        self.textEdit = QTextEdit()

        self.required_fields = [
            self.hostEdit, self.portEdit, self.emailEdit, self.recipientEdit]

        self.btnClear = QPushButton('clear')
        self.btnClear.setFixedWidth(60)
        self.btnClear.clicked.connect(self.clear)

        self.btnSend = QPushButton('send')
        self.btnSend.setFixedWidth(60)
        self.btnSend.clicked.connect(self.check_fields)

        self.btnAdd = QPushButton('+')
        self.btnAdd.setFixedWidth(30)
        self.btnAdd.clicked.connect(self.add_files)

        self.btnHtml = QCheckBox('Send as html')
        self.btnHtml.clicked.connect(self.clicked_html)

        self.btnArchive = QCheckBox('As ZIP archive:')
        self.btnArchive.clicked.connect(self.clicked_archive)
        self.archiveEdit = QLineEdit()
        self.archiveEdit.setDisabled(True)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(host, 0, 0)
        self.grid.addWidget(self.hostEdit, 0, 1, 1, 2)

        self.grid.addWidget(port, 0, 3)
        self.grid.addWidget(self.portEdit, 0, 4, 1, 1)

        self.grid.addWidget(email, 1, 0)
        self.grid.addWidget(self.emailEdit, 1, 1, 1, 2)

        self.grid.addWidget(name, 1, 3)
        self.grid.addWidget(self.nameEdit, 1, 4, 1, 4)

        self.grid.addWidget(recipient, 2, 0)
        self.grid.addWidget(self.recipientEdit, 2, 1, 1, 7)

        self.grid.addWidget(cc, 3, 0)
        self.grid.addWidget(self.ccEdit, 3, 1, 1, 7)

        self.grid.addWidget(bcc, 4, 0)
        self.grid.addWidget(self.bccEdit, 4, 1, 1, 7)

        self.grid.addWidget(subject, 5, 0)
        self.grid.addWidget(self.subjectEdit, 5, 1, 1, 7)

        self.grid.addWidget(self.btnHtml, 6, 0, 1, 7)

        self.grid.addWidget(text, 7, 0)
        self.grid.addWidget(self.textEdit, 8, 0, 1, 8)

        self.grid.addWidget(self.attachLabel, 9, 0, 1, 7)
        self.attachLabel.hide()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.horizontalHeader().hide()
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.table.setFixedHeight(100)
        self.grid.addWidget(self.table, 10, 0, 1, 8)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.hide()

        self.grid.addWidget(self.btnArchive, 11, 0, 1, 2)
        self.grid.addWidget(self.archiveEdit, 11, 2, 1, 1)

        self.grid.addWidget(self.btnAdd, 11, 5)

        self.grid.addWidget(self.btnClear, 11, 6)

        self.grid.addWidget(self.btnSend, 11, 7)

        self.grid.addWidget(self.current_state, 12, 0, 1, 7)

        self.setLayout(self.grid)
        self.resize(650, 700)

    def clear(self):
        self.hostEdit.clear()
        self.portEdit.clear()
        self.nameEdit.clear()
        self.emailEdit.clear()
        self.recipientEdit.clear()
        self.ccEdit.clear()
        self.bccEdit.clear()
        self.subjectEdit.clear()
        self.textEdit.clear()
        self.btnHtml.setChecked(False)
        self.btnArchive.setChecked(False)
        self.archiveEdit.clear()
        for field in self.required_fields:
            field.setStyleSheet(self.defaultStyleSheet)
        self.current_state.setText(
            'Заполните обязательные поля перед отправкой')
        self.table.setRowCount(0)
        self.attachments.clear()
        self.table.hide()
        self.part_attachs.clear()

    def check_fields(self):
        unrequired = 0
        for field in self.required_fields:
            if field.text():
                field.setStyleSheet(self.defaultStyleSheet)
            else:
                field.setStyleSheet(
                    "border-color: red; border-style: solid; border-width: 2;")
                unrequired += 1
        if unrequired:
            self.current_state.setText('Заполните выделенные поля')
        else:
            self.send()

    def send(self):
        self.btnSend.setDisabled(True)
        self.show_dialog()
        try:
            attachment_names = self.get_attachments_names()
            Sender(self.attachments, attachment_names, self.hostEdit.text(),
                   self.portEdit.text(), self.nameEdit.text(),
                   self.emailEdit.text(), self.password,
                   self.recipientEdit.text(), self.ccEdit.text(),
                   self.content_type, self.bccEdit.text()).send(
                self.textEdit.toPlainText(), self.subjectEdit.text(),
                self.btnArchive.isChecked(), self.archiveEdit.text())
        except SmtpException as e:
            self.current_state.setText(e.message)
        except Exception:
            self.current_state.setText('Невозможно отправить письмо. Поробуйте ещё раз')
        else:
            self.current_state.setText('Письмо успешно отправлено')
        self.btnSend.setDisabled(False)

    def get_attachments_names(self):
        return [self.table.cellWidget(i, 1).text()
                for i in range(len(self.attachments))]

    def clicked_html(self):
        if self.btnHtml.isChecked():
            self.content_type = 'html'
        else:
            self.content_type = 'plain'

    def show_dialog(self):
        text, ok = QInputDialog.getText(
            self, 'Password', 'Enter your password:', QLineEdit.Password)
        if ok:
            self.password = text
            self.current_state.setText('Письмо отправляется')

    def clicked_archive(self):
        if self.btnArchive.isChecked():
            self.archiveEdit.setDisabled(False)
        else:
            self.archiveEdit.clear()
            self.archiveEdit.setDisabled(True)

    def delete_frame(self):
        self.sender().setStyleSheet(self.defaultStyleSheet)

    def add_files(self):
        self.table.show()
        files = QFileDialog.getOpenFileNames()
        self.attachments.extend(files[0])
        self.table.setRowCount(len(self.attachments))
        for i in range(len(self.attachments)):
            self.create_row(i)
        if not self.table.rowCount():
            self.table.hide()
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        if self.table.rowCount() > 3:
            self.table.setFixedHeight(175)
        else:
            self.table.setFixedHeight(100)

    def change_file(self):
        files = QFileDialog.getOpenFileName()
        if files[0]:
            idx = self.table.indexAt(self.sender().pos()).row()
            self.table.removeRow(idx)
            self.attachments.pop(idx)
            self.table.insertRow(idx)
            self.attachments.insert(idx, files[0])
            self.create_row(idx)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()

    def create_row(self, idx):
        self.table.setCellWidget(idx, 0, QLabel(self.attachments[idx]))
        fileNameEdit = QLineEdit()
        fileNameEdit.setText(os.path.split(self.attachments[idx])[1])
        self.table.setCellWidget(idx, 1, fileNameEdit)
        btnDelete = QPushButton('delete')
        btnDelete.clicked.connect(self.delete_row)
        self.table.setCellWidget(idx, 2, btnDelete)
        btnChange = QPushButton('...')
        btnChange.clicked.connect(self.change_file)
        self.table.setCellWidget(idx, 3, btnChange)

    def delete_row(self):
        idx = self.table.indexAt(self.sender().pos()).row()
        self.table.removeRow(idx)
        self.attachments.pop(idx - 1)
        if not self.table.rowCount():
            self.table.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
