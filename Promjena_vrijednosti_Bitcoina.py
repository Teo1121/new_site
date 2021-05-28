import requests   
from bs4 import *
import smtplib
import ssl
import time
import imaplib
import email

# constants
port = 465
context = ssl.create_default_context()
sender_mail = "racunalni.praktikum.smtp@gmail.com"
password = "9Nq5BkS4dWDz7faU"
url = 'https://www.coindesk.com/price/bitcoin' # The page with the information

# to send data
server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
server.login(sender_mail, password) 

# to recive data
mail = imaplib.IMAP4_SSL("imap.gmail.com" ) 
mail.login(sender_mail,password) 
mail.select('inbox')

# the list of email to send the data
with open("subscribe.txt", "rt") as f:
    mails = f.readlines()

while True:
    # get the html as plain text
    html = requests.get(url).text

    # get the data
    soup = BeautifulSoup(html)
    tag = soup.findAll("div",{"class":"price-large"})[0] # Element with the data
    value = (str(tag)[54:-6].replace(',',''))

    # get last sent value
    with open("last.txt","rt") as f:
        past_value = f.read()

    # check for change
    if abs(float(past_value)-float(value)) > 10:
        message = """\
Subject: Change in the value of bitcoin

The value of bitcoin has changed from """+past_value+" USD to "+ value+ """ USD.

This message was sent using Python.
To unsubscribe send an e-mail to this mail with the word unsubscribe."""

        # send new value to everyone on the list
        for m in mails:
            server.sendmail(sender_mail, m.strip("\n"), message)
            
        # store the new value
        with open("last.txt","wt") as f:
            f.write(value)  

    # get all mail in the inbox
    data = mail.search(None, 'ALL')

    # for every mail
    for i in data[1][0].decode().split():
        
        # get the message
        data = mail.fetch(i, '(RFC822)' )
        for response_part in data:
            arr = response_part[0]
            if isinstance(arr, tuple):
                msg = email.message_from_string(str(arr[1],'utf-8'))
                
                # get mail sender
                email_from = msg['from'].split('<')[1][:-1]

                # get content of the message
                if msg.is_multipart(): 
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            recived_message = part.get_payload().lower()
                            break
                else:
                    recived_message = msg.get_payload().lower()

                # check if sender wants to unsubscribe
                if recived_message.find("unsubscribe") == recived_message.find("subscribe")-2 
                    with open("subscribe.txt", "w") as f:
                        for line in mails:
                            if line.strip("\n") != email_from:
                                f.write(line)
                    with open("subscribe.txt", "r") as f:
                        mails = f.readlines()
                        
                # check if sender wants to subscribe
                elif 'subscribe' in recived_message:
                    with open("subscribe.txt", "r") as f:
                        temp = f.readlines()   
                    if email_from not in temp:
                        with open("subscribe.txt", "a") as f:
                            f.write(email_from + '\n')
                            mails.append(email_from)

        # set mail to be deleted
        mail.store(str(i), "+FLAGS", "\\Deleted")

    # delete read mail
    mail.expunge()

    # wait 10 seconds
    time.sleep(10)

