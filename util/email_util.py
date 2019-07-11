import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_credentials(path):
  import json
  enc = json.load(open(path, 'r'))
  assert('email' in enc)
  assert('pass' in enc)
  assert('host' in enc)
  assert('port' in enc)
  return enc
  
def dummy_send_email(credential_path, content, subject = 'info', mime_type = "html"):
  credentials = load_credentials(credential_path)
  f = credentials['email']
  t = credentials['email']
  p = credentials['pass']
  host = credentials['host']
  port = credentials['port']

  mime_content = MIMEText(content, mime_type)
  send_email(f, t, subject, p, host, port, mime_content)

def send_email(from_addr, 
  to_addr, 
  subject, 
  password, host, port, 
  mime_content):

  sender_email = from_addr
  receiver_email = to_addr

  message = MIMEMultipart("alternative")
  message["Subject"] = subject
  message["From"] = sender_email
  message["To"] = receiver_email

  # Turn these into plain/html MIMEText objects
  part1 = mime_content

  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)

  # Create secure connection with server and send email
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(host, port, context=context) as server:
      server.login(sender_email, password)
      server.sendmail(
          sender_email, receiver_email, message.as_string()
      )

if __name__ == '__main__':
  credential_path = '/Users/AlexG/github/EdreamProject/util/email.json'
  dummy_send_email(credential_path, 'ok')