import smtplib
import ssl
from email.message import EmailMessage
from dotenv import dotenv_values

smtp_server = dotenv_values(".env").get("smtp_server")
smtp_server_port = dotenv_values(".env").get("smtp_server_port")
sender_email = dotenv_values(".env").get("sender_email")
password = dotenv_values(".env").get("password")

assert smtp_server is not None
assert smtp_server_port is not None
assert sender_email is not None
assert password is not None


def send(msg, sender_email):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_server_port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
        

def email(subject, text):
    receiver_email = sender_email

    # Build Email Message
    msg = EmailMessage()
    msg["to"] = receiver_email
    msg["from"] = sender_email
    msg["subject"] = subject
    msg.set_content(text)

    # Send message
    send(msg, sender_email)
    
    
if __name__ == "__main__":
    subject = "Message one"
    text = "Message one"
    email(subject, text)