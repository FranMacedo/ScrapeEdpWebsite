import ssl
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sec_vars import pwd, sd_email
import base64
# m = 'lisboaenovarobot@gmail.com'


def color_fail_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """

    color = 'red' if val == 'download fail' else 'black'
    return 'color: %s' % color


def style_f(x): return f'<span class="fail">{x}</span>' if x == 'download fail' else str(x)


css_txt = """

  .mystyle {
    font-size: 11pt;
    font-family: Arial;
    border-collapse: collapse;
    border: 1px solid silver;
    text-align: center;
  }

  .mystyle td,
  th {
    padding: 5px;
    text-align: center;
  }

  .mystyle tr:nth-child(even) {
    background: #e0e0e0;
    text-align: center;
  }

  .mystyle tr:hover {
    background: silver;
    cursor: pointer;
    
  }
  .fail{
    color: red
  }
  """


def send_auto_email(receiver_email, title, text, df):
    # sender_email = m
    # receiver_email = m
    password = base64.b64decode(pwd).decode("utf-8")
    sender_email = base64.b64decode(sd_email).decode("utf-8")
    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message

    html = f"""\
  <html>
    <head>
      <title>HTML Pandas Dataframe with CSS</title>
      <style>{css_txt}</style>
    </head>
    
    <body>
      <p>
        {text}
      </p>
      <div>
        {df.to_html(formatters={d: style_f for d in df.columns.tolist()}, classes='mystyle', escape=False)}
      </div>
    </body>
  </html>
  """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


# df = pd.read_csv('downloads/logs/cpe_info_2020-06-15 23h_40m.csv')
# send_auto_email(m, 'download 15/06', 'Dados de download de uma data especifica', df)
