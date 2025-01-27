# logging_handlers.py

"""
logging_handlers.py

Module containing custom logging handlers for the application.

Includes handlers for:
- Email alerts for critical errors.
- Sending logs to Slack channels.
- Logging to a database.

These handlers can be integrated into the logging configuration to provide
enhanced logging capabilities, including alerting mechanisms and centralizing logs.

Usage:
    from logging_handlers import EmailAlertHandler, SlackAlertHandler, DatabaseLogHandler

"""

import logging
import logging.handlers
import sys
import traceback
import smtplib
from email.message import EmailMessage
import requests
import json
import threading

# Additional imports for database logging
# import sqlite3  # For example, assuming we are using SQLite for demo purposes

# Import necessary modules from the application, if needed

# Define custom logging handlers

class EmailAlertHandler(logging.Handler):
    """
    A logging handler that sends email alerts for critical errors.

    This handler sends an email whenever a log record with level ERROR or higher is emitted.

    Parameters:
        mailhost (str or tuple): The mail server host, or (host, port) tuple.
        fromaddr (str): The email address that the email is sent from.
        toaddrs (list of str): A list of email addresses to send the email to.
        subject (str): The subject line of the email.
        credentials (tuple): A tuple of (username, password) for authentication.
        secure (tuple): A tuple containing arguments for starting TLS.
    """
    def __init__(self, mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None):
        super().__init__(level=logging.ERROR)  # Only handle ERROR and above
        if isinstance(mailhost, tuple):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost = mailhost
            self.mailport = None
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.credentials = credentials
        self.secure = secure

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified email addresses.
        """
        try:
            msg = self.format(record)
            email_msg = EmailMessage()
            email_msg.set_content(msg)
            email_msg['From'] = self.fromaddr
            email_msg['To'] = ', '.join(self.toaddrs)
            email_msg['Subject'] = self.subject
            smtp = smtplib.SMTP(self.mailhost, self.mailport or 0)
            if self.secure is not None:
                smtp.starttls(*self.secure)
            if self.credentials:
                smtp.login(*self.credentials)
            smtp.send_message(email_msg)
            smtp.quit()
        except Exception:
            self.handleError(record)

class SlackAlertHandler(logging.Handler):
    """
    A logging handler that sends log messages to a Slack channel.

    Parameters:
        webhook_url (str): The Slack webhook URL to send messages to.
        level (int): The minimum logging level for which to send messages.
    """
    def __init__(self, webhook_url, level=logging.ERROR):
        super().__init__(level=level)
        self.webhook_url = webhook_url
        self.lock = threading.Lock()

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified Slack webhook URL.
        """
        try:
            msg = self.format(record)
            payload = {'text': msg}
            with self.lock:
                response = requests.post(self.webhook_url, data=json.dumps(payload),
                                         headers={'Content-Type': 'application/json'})
            if response.status_code != 200:
                raise ValueError(f'Request to Slack returned error {response.status_code}, response:\n{response.text}')
        except Exception:
            self.handleError(record)

# class DatabaseLogHandler(logging.Handler):
#     """
#     A logging handler that logs messages to a database.

#     For demonstration purposes, this handler uses SQLite, but it can be adapted
#     to use any database engine.

#     Parameters:
#         db_path (str): The path to the SQLite database file.
#         level (int): The minimum logging level to handle.
#     """
#     def __init__(self, db_path='logs.db', level=logging.INFO):
#         super().__init__(level=level)
#         self.db_path = db_path
#         self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
#         self._create_table()
#         self.lock = threading.Lock()

#     def _create_table(self):
#         """
#         Creates the logs table in the database if it doesn't already exist.
#         """
#         cursor = self.conn.cursor()
#         cursor.execute('''CREATE TABLE IF NOT EXISTS logs
#                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                            created TEXT,
#                            level TEXT,
#                            logger TEXT,
#                            message TEXT,
#                            pathname TEXT,
#                            lineno INTEGER,
#                            funcname TEXT,
#                            process INTEGER,
#                            thread INTEGER,
#                            exception TEXT)''')
#         self.conn.commit()

#     def emit(self, record):
#         """
#         Emit a record.

#         Save the record to the database.
#         """
#         try:
#             # Use the formatter to get the message
#             msg = self.format(record)
#             created = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
#             levelname = record.levelname
#             logger_name = record.name
#             pathname = record.pathname
#             lineno = record.lineno
#             funcname = record.funcName
#             process = record.process
#             thread = record.thread

#             if record.exc_info:
#                 exception = self.formatException(record.exc_info)
#             else:
#                 exception = None

#             with self.lock:
#                 cursor = self.conn.cursor()
#                 cursor.execute('''INSERT INTO logs
#                                   (created, level, logger, message,
#                                    pathname, lineno, funcname,
#                                    process, thread, exception)
#                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
#                                (created, levelname, logger_name, msg,
#                                 pathname, lineno, funcname,
#                                 process, thread, exception))
#                 self.conn.commit()
#         except Exception:
#             self.handleError(record)

#     def close(self):
#         """
#         Closes the database connection.
#         """
#         self.conn.close()
#         super().close()

# Additional custom logging handlers can be added here as needed.