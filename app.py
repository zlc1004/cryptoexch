import flask
import json
import hashlib
import qrcode
import io
import requests
import time
import os
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


uri = os.getenv("mongodb_url")
webhook = os.getenv("MAIN_WEBHOOK")
txidWebhook = os.getenv("TXID_WEBHOOK")

dbClient = MongoClient(uri, server_api=ServerApi('1'))
db=dbClient["users"]

tokens = ""

app = flask.Flask(__name__, static_folder="public", static_url_path="")


def randomString(length=10):
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    return "".join(random.choice(letters) for i in range(length))


def sendWebhook(msg, webhook=webhook):
    return requests.post(webhook, json={"content": msg})


def timeStr():
    return "<t:" + str(int(time.time())) + ">"


def log(requestType, msg, ip):
    out = ""
    out += timeStr()
    out += " `"
    out += requestType
    out += "` `"
    out += ip
    out += "` `"
    out += msg
    out += "`"
    sendWebhook(out)


def logTxid(txid, ip):
    out = ""
    out += timeStr()
    out += " `"
    out += "TXID"
    out += "` `"
    out += txid
    out += "` `"
    out += ip
    out += "`"
    sendWebhook(out, txidWebhook)


def validateToken(username, ip, token) -> bool:
    return token == (
        hashlib.sha256(
            (username + "," + getUsers(flask.request).get(username, "") + "," + ip).encode()
        ).hexdigest()
    )


def getToken(username, password, ip) -> str:
    return hashlib.sha256((username + "," + password + "," + ip).encode()).hexdigest()

def combineDicts(dictlist):
    out={}
    for i in dictlist:
        out.update(i)
    return out
    

def getUsers(req) -> dict:
    try:
        print(req.url_root.split("/")[2])
        collection=db[(req.url_root.split("/")[2])]
        print(collection)
        print("collection")
    except IndexError:
        print("creating collection")
        db.create_collection(req.url_root.split("/")[2])
        print("created collection")
        return {}
    print("getting collection")
    cur=combineDicts(collection.find())
    print("got collection")
    return cur


def getAddress() -> dict:
    with open("priv/address.json", "r") as f:
        return json.load(f)


def getAmount(coin, invoiceType) -> dict:
    with open("priv/amount.json", "r") as f:
        return json.load(f)[coin + str(invoiceType)]


def serve_qr(text):
    pil_img = qrcode.make(text)
    img_io = io.BytesIO()
    pil_img.save(img_io, "JPEG")
    img_io.seek(0)
    return flask.send_file(img_io, mimetype="image/jpeg")


def addTxid(txid):
    with open("priv/txid.txt", "a") as f:
        f.write(txid + "\n")


def getIP(req: flask.Request) -> str:
    if req.headers.get("X-Forwarded-For", False):
        return req.headers.get("X-Forwarded-For")
    return req.remote_addr


@app.route("/")
def index():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    return flask.send_from_directory("static", "index.html")


@app.route("/deposit")
def deposit():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    return flask.send_from_directory("static", "deposit.html")


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    if flask.request.method == "GET":
        return flask.send_from_directory("static", "withdraw.html")
    elif flask.request.method == "POST":
        return flask.send_from_directory("static", "withdrawerror.html")


@app.route("/upgrade")
def upgrade():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    return flask.send_from_directory("static", "upgrade.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        if getUsers(flask.request).get(username, False) == password:
            resp = flask.make_response(flask.redirect("/home"))
            resp.set_cookie("username", username)
            resp.set_cookie("token", getToken(
                username, password, getIP(flask.request)))
            log(
                "INFO",
                "Login Successful, user: " + username + ", pass:" + password,
                getIP(flask.request),
            )
            return resp
        else:
            log(
                "FAIL",
                "Login FAIL, user: " + username + ", pass:" + password,
                getIP(flask.request),
            )
            return flask.send_from_directory("static", "loginerror.html")
    elif flask.request.method == "GET":
        if validateToken(
            flask.request.cookies.get("username", ""),
            getIP(flask.request),
            flask.request.cookies.get("token"),
        ):
            return flask.redirect("/home")
        return flask.send_from_directory("static", "login.html")


@app.route("/home")
def home():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    return flask.send_from_directory("static", "home.html")


@app.route("/forgot")
def forgot():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    return flask.send_from_directory("static", "forgot.html")


@app.route("/logout")
def logout():
    log(flask.request.method, flask.request.full_path, getIP(flask.request))
    resp = flask.make_response(flask.redirect("/"))
    resp.set_cookie("username", "", expires=0)
    resp.set_cookie("token", "", expires=0)
    return resp


@app.route("/api", methods=["POST"])
def api():
    if flask.request.form.get("ping", "false") == "true":
        return "1"
    return ""


@app.route("/address/<address>")
def address(address):
    return serve_qr(address)


@app.route("/invoice/<invoiceType>")
def invoice(invoiceType):
    log(
        flask.request.method,
        flask.request.full_path + " " + invoiceType,
        getIP(flask.request),
    )
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    invoiceType = invoiceType.split("-")
    if (invoiceType[0] in getAddress().keys()) and (invoiceType[1] in list("1234")):
        with open("static/invoice.html", "r") as f:
            invoiceHTML = f.read()
        amount = getAmount(invoiceType[0], invoiceType[1])
        invoiceHTML = invoiceHTML % (
            str(amount),
            invoiceType[0],
            getAddress()[invoiceType[0]],
            getAddress()[invoiceType[0]],
        )
        return invoiceHTML
    return flask.redirect("/logout")


@app.route("/success", methods=["POST"])
def success():
    if not validateToken(
        flask.request.cookies.get("username", ""),
        getIP(flask.request),
        flask.request.cookies.get("token"),
    ):
        return flask.redirect("/login")
    addTxid(flask.request.form["txid"])
    log(
        "INFO",
        "Transaction Successful, txid: " + flask.request.form["txid"],
        flask.request.remote_addr,
    )
    logTxid(flask.request.form["txid"], getIP(flask.request))
    return flask.send_from_directory("static", "success.html")


@app.route("/gettoken")
def getTokenRoute():
    global tokens
    tokens = randomString(15)
    logTxid("New token: " + tokens, getIP(flask.request))
    return "ok"


@app.route("/newuser/<username>/<password>/<token>")
def newUser(username, password, token):
    global tokens
    if tokens == "":
        return "please get a token first"
    if token == tokens:
        collection=db.get_collection(flask.request.url_root.split("/")[2])
        collection.insert_one({username: password})
        tokens = ""

        return "ok"
    return "invalid token"


@app.route("/register")
def register():
    return flask.send_from_directory("static", "register.html")

@app.route("/test")
def test():
    return flask.request.url_root.split("/")[2]

if __name__ == "__main__":
    app.run(port=8000)
