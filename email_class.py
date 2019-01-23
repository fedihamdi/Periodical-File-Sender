import email.message
import mimetypes
import os.path
from datetime import datetime
from smtplib import SMTP_SSL, SMTP


class EmailMessage(email.message.EmailMessage):

    def __init__(self, sender, receiver, title, text, attachment_filepath, time_unit, time_count):
        assert isinstance(sender, str) and '@' in sender
        assert isinstance(receiver, str) and '@' in receiver
        assert isinstance(title, str)
        assert isinstance(text, str)
        assert attachment_filepath is None or isinstance(attachment_filepath, str)
        assert time_unit in 'mhdwMY'
        assert isinstance(time_count, int)
        super().__init__()
        self['From'] = sender
        self['To'] = receiver
        self['Subject'] = title
        self.set_content(text)
        self.attachment_path = attachment_filepath
        self.time_unit = time_unit
        self.time_count = time_count
        self.last_sent = None
        self.next_send = None

    def send(self, server, port, username, password, tls=True):
        assert isinstance(server, str)
        assert isinstance(port, int)
        assert isinstance(username, str)
        assert isinstance(password, str)
        if self.attachment_path:
            ctype, encoding = mimetypes.guess_type(self.attachment_path)
            if ctype is None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/')
            with open(self.attachment_path, 'rb') as attachment_file:
                self.add_attachment(attachment_file.read(), maintype=maintype, subtype=subtype,
                                    filename=os.path.basename(self.attachment_path))
        if tls:
            smtp_server = SMTP_SSL(server, port)
        else:
            smtp_server = SMTP(server, port)
        smtp_server.login(username, password)
        smtp_server.send_message(self)
        smtp_server.quit()
        self.last_sent = datetime.now()
