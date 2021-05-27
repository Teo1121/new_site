import requests
from bs4 import *
import smtplib
import ssl
import time
import imaplib
import email

port = 465  # For SSL
context = ssl.create_default_context() # Create a secure SSL context
sender_mail = "racunalni.praktikum.smtp@gmail.com"
password = "9Nq5BkS4dWDz7faU"


url = 'https://www.coindesk.com/price/bitcoin' # stranica s cijenom
server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
server.login(sender_mail, password)
with open("subscribe.txt", "r") as f:
    mails = f.readlines()

mail = imaplib.IMAP4_SSL("imap.gmail.com" )
mail.login(sender_mail,password)
mail.select('inbox')

while True:
    html = r = requests.get(url).text

    soup = BeautifulSoup(html)
    tag = soup.findAll("div",{"class":"price-large"})[0] # element u kojem se nalazi cijena
    value = (str(tag)[54:-6].replace(',',''))

    f = open("last.txt","rt")
    past_value = f.read()
    f.close()
    print(value)

    if abs(float(past_value)-float(value)) > 10:
        print("change")
        message = """\
Subject: Change in the value of bitcoin

The value of bitcoin has changed from """+past_value+" USD to "+ value+ """ USD.

This message was sent using Python.
To unsubscribe send an e-mail to this mail with the word unsubscribe."""

        for m in mails:
            server.sendmail(sender_mail, m.strip("\n"), message)

        f = open("last.txt","wt")
        f.write(value)
        f.close()
    
    else:
        print("no change")
        for m in mails:
            print(m.strip("\n"))
    
    

    data = mail.search(None, 'ALL')
    for i in data[1][0].decode().split():
        data = mail.fetch(i, '(RFC822)' )
        for response_part in data:
            arr = response_part[0]
            if isinstance(arr, tuple):
                msg = email.message_from_string(str(arr[1],'utf-8'))
                email_from = msg['from'].split('<')[1][:-1]
                print('From : ' + email_from + '\n')
                if msg.is_multipart():
                    for part in msg.walk():
                        multipart_payload = msg.get_payload()
                        for sub_message in multipart_payload:
                            if sub_message.get_content_type() == "text/plain":
                                recived_message = sub_message.get_payload().lower()
                                break
                        break
                else:  # Not a multipart message, payload is simple string
                    recived_message = sub_message.get_payload().lower()

                if 'unsubscribe' in recived_message:
                    with open("subscribe.txt", "w") as f:
                        for line in mails:
                            if line.strip("\n") != email_from:
                                f.write(line)
                    with open("subscribe.txt", "r") as f:
                        mails = f.readlines()
                elif 'subscribe' in recived_message:
                    with open("subscribe.txt", "r") as f:
                        temp = f.readlines()
                        
                    if email_from not in temp:
                        with open("subscribe.txt", "a") as f:
                            f.write(email_from + '\n')
                            mails.append(email_from)


        mail.store(str(i), "+FLAGS", "\\Deleted")

    mail.expunge()
    
    time.sleep(10)

