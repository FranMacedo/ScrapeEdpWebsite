import ssl
import smtplib
import pandas as pd

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .sec_vars import pwd, sd_email
import base64
import os


def color_fail_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """

    color = 'red' if val == 'download fail' else 'black'
    return 'color: %s' % color


def custom_style(conditions):

    def style_f(x):
        for c_txt, c_class in conditions.items():
            if str(x).lower() == str(c_txt).lower():
                return f'<span class={c_class}>{x}</span>'
        return str(x)

    return style_f


# def style_f(x): return f'<span class="fail">{x}</span>' if x == 'download fail' else str(x)


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
    text-align: center;
  }

  .mystyle tr:hover {
    background: silver;
    cursor: pointer;
    
  }
  .danger{
    color: red
  }

  .danger-back{
    background-color: #ff6969;
  }

  .success{
    color: green;
  }

  .success-back{
    background-color: #7fd496;
  }

  .warning{
    color: yellow
  }

  .warning-back{
    background-color: #faf8a5;
  }
 
  """


def send_auto_email(receiver_email, title, text, df=pd.DataFrame(), conditions={}, file_path=None, file_name=None):
    """
    Function that sends automatic emails.
    receiver_email: email to send to
    title: title/subject of email
    text: body/text of email. Can be in html format or just plain old text. will be incorporated in a div in top of body.
    df: if you want to render a pandas DataFrame inside them email body as an html table (after text). do not fill if don't need.
    conditions: dict with KEYS - text that can be found in a cell of df that you want to format with a specific class and 
                          VALUES - what class to format that text with ('danger', 'danger-back', 'success', ...).
    file_path: attachment of any kind, only if you want to. leave empty otherwise.
    file_name: name of attached file, only if you want to. leave empty and name will be last element of file_path.

    example:
    send_auto_email(
                    receiver_email='youremail@gmail.com', 
                    title='download 15/06',
                    text='Data Downloaded', 
                    df=df, 
                    condition_class='danger', 
                    condition_txt='this is very wrong',
                    file_path='your_file_path.pdf', 
                    file_name='something_else_maybe.pdf', 
                    )
    """

    password = base64.b64decode(pwd).decode("utf-8")
    sender_email = base64.b64decode(sd_email).decode("utf-8")
    message = MIMEMultipart()
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    if not df.empty:
        if conditions:
            style_f = custom_style(conditions)
            df_txt = df.to_html(formatters={d: style_f for d in df.columns.tolist()}, classes='mystyle', escape=False)
        else:
            df_txt = df.to_html(classes='mystyle', escape=False)
    else:
        df_txt = ''

    html = f"""\
    <html>
      <head>
        <title>HTML Pandas Dataframe with CSS</title>
        <style>{css_txt}</style>
      </head>
      
      <body>
        <div>
          {text}
        </div>
        <div>
          {df_txt}
        </div>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    # message.attach(part1)
    message.attach(part2)

    # Open PDF file in binary mode
    if file_path:
        with open(file_path, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)
        if file_name:
            f_name = file_name
        else:
            f_name = os.path.split(file_path)[1]
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {f_name}",
        )
        message.attach(part)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


file_path = 'downloads/logs/cpe_info_2020-06-16 11h_27m.csv'
df = pd.read_csv(file_path)
send_auto_email('lisboaenovarobot@gmail.com', 'download 15/06',
                'Dados de download de uma data especifica', df=df, conditions={'True': 'success-back', 'Ativo': 'success-back', 'row 1': 'warning-back'})
