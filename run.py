from flask import Flask, render_template, url_for, request
import requests

app = Flask(__name__)

def sub_user(email):
    with open("subscribe.txt", "r") as f:
        mails = f.readlines()
        if email in mails:
            return
        
    with open("subscribe.txt","at") as f:
        f.write(email+'\n')

def unsub_user(email):
    with open("subscribe.txt", "r") as f:
        mails = f.readlines()
    
    with open("subscribe.txt","wt") as f:
        for line in mails:
            if line.strip("\n") != email:
                f.write(line)
  

@app.route("/", methods=["GET","POST"])


def index():
    if request.method == "POST":
        email = str(request.form.get('email'))
        tp = str(request.form.get('submit'))
        if '@' in email:
            if tp == "subscribe":
                sub_user(email)
                return "<p>Thanks for subscribing</p>"
            if tp == "unsubscribe":
                unsub_user(email)
                return "<p>Goodbye</p>"
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
