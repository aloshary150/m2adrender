from flask import Flask, render_template, request, redirect, send_from_directory, flash
import os
import requests

app = Flask(__name__)
app.secret_key = "secret_key_here"  # ضروري للرسائل المؤقتة (flash)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# بيانات بوت التليغرام
BOT_TOKEN = "8366818255:AAFcG_h7OzidDuUHWkLdpGFbbtXuvWFYJl0"  # غيره بتوكنك
CHAT_ID = "رقم_الشات_الخاص_بك_أو_المجموعة"  # مثال: "-123456789" للمجموعة، أو رقم حسابك

PASSWORD = "aloshary150"

def send_file_to_telegram(filepath, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(filepath, "rb") as f:
        files = {"document": (filename, f)}
        data = {"chat_id": CHAT_ID}
        response = requests.post(url, data=data, files=files)
    return response.json()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                save_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(save_path)

                # إرسال الملف لتليغرام بعد الرفع
                telegram_response = send_file_to_telegram(save_path, file.filename)
                if telegram_response.get("ok"):
                    flash("تم رفع الملف وإرساله لتليغرام بنجاح!", "success")
                else:
                    flash("تم رفع الملف لكن حدث خطأ في الإرسال لتليغرام.", "error")

                return redirect("/")
        if "password" in request.form:
            if request.form["password"] == PASSWORD:
                files = os.listdir(UPLOAD_FOLDER)
                return render_template("files.html", files=files)
            else:
                flash("كلمة المرور غير صحيحة!", "error")
    return render_template("index.html")

@app.route("/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"تم حذف الملف: {filename}", "success")
    else:
        flash("الملف غير موجود.", "error")
    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/main")
def main():
    return render_template("main.html")

if __name__ == "__main__":
    app.run(debug=True)
