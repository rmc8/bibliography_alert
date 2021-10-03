import os
import ssl
import smtplib
from typing import Optional, List

from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class Gmail:
    def __init__(self, from_: str, to: Optional[str] = None, cc: Optional[str] = None,
                 bcc: Optional[str] = None, subject: str = "", body: str = "",
                 host: str = "smtp.gmail.com", port=465, sep: str = ",") -> None:
        self.from_: str = from_
        self.to: Optional[str] = to
        self.cc: Optional[str] = cc
        self.bcc: Optional[str] = bcc
        self.subject: str = subject
        self.body: str = body
        self.attachment: List[str] = []
        context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(host=host, port=port, context=context)
        self.sep = sep
    
    def login(self, user: str, password: str) -> None:
        self.server.login(user=user, password=password)
    
    def add_attachment(self, attachment_path: str) -> None:
        self.attachment.append(attachment_path)
    
    def attachment_len(self) -> int:
        return len(self.attachment)
    
    def _set_attachment(self, msg):
        for file_path in self.attachment:
            if not os.path.exists(file_path):
                continue
            file_name: str = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=file_name)
            part["Content-Disposition"] = f'attachment; filename="{file_name}"'
            msg.attach(part)
        return msg
    
    def _create_msg(self, is_html: bool):
        msg = MIMEMultipart()
        msg.attach(MIMEText(self.body, "html" if is_html else "plain"))
        msg["Subject"] = self.subject
        msg["From"] = self.from_
        msg["To"] = self.to
        msg["Cc"] = self.cc
        msg["Bcc"] = self.bcc
        msg["Date"] = formatdate()
        return self._set_attachment(msg)
    
    @staticmethod
    def _split_addrs(addrs: Optional[str], sep: str):
        if type(addrs) is str:
            return addrs.split(sep)
        return []
    
    def _get_recipients_list(self) -> list:
        to: list = self._split_addrs(self.to, self.sep)
        cc: list = self._split_addrs(self.to, self.sep)
        bcc: list = self._split_addrs(self.to, self.sep)
        return to + cc + bcc
    
    def send(self, is_html: bool = False) -> None:
        msg = self._create_msg(is_html=is_html)
        recipients_list: list = self._get_recipients_list()
        self.server.sendmail(from_addr=self.from_, to_addrs=recipients_list, msg=msg.as_string())
    
    def close(self) -> None:
        self.server.close()
