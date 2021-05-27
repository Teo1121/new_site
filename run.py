from flask import Flask, render_template, url_for, request
import requests

app = Flask(__name__)

def sub_user(email):
        f = open("subscribe.txt","wt")
        f.write(email)
        f.close()

  

@app.route("/", methods=["GET","POST"])


def index():
    if request.method == "POST":
        email = request.form.get('email')
        sub_user(email=email)
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)