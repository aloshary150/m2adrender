from flask import Flask, render_template, request, redirect, send_from_directory
import os
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PASSWORD = "aloshary150"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# إعدادات بوت تليغرام
BOT_TOKEN = "8366818255:AAFcG_h7OzidDuUHWkLdpGFbbtXuvWFYJl0"
CHAT_ID = "8366818255"

def send_telegram_file(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID, "caption": caption}
        response = requests.post(url, files=files, data=data)
    return response.json()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                
                # أرسل الملف لتليغرام
                send_telegram_file(filepath, caption=f"تم رفع ملف: {file.filename}")
                
            return redirect("/")
        if "password" in request.form:
            if request.form["password"] == PASSWORD:
                files = os.listdir(UPLOAD_FOLDER)
                return render_template("files.html", files=files)
    return render_template("index.html")

@app.route("/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/main")
def main():
    return render_template("main.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect("/")
