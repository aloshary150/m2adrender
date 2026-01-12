from flask import Flask, render_template, request, redirect, send_from_directory, flash
import os, httpx, datetime, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key_here"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ====== بياناتك الأصلية (كما هي) ======
BOT_TOKEN = "8366818255:AAFcG_h7OzidDuUHWkLdpGFbbtXuvWFYJl0"
CHAT_ID = "8492067756"
PASSWORD = "aloshary150"

# ====== ملفات التخزين ======
VISITS_FILE = "visits.json"

# تجاهل البوتات
BOT_KEYWORDS = ["bot", "crawler", "spider", "telegram", "facebook"]

# إنشاء ملف الزيارات إن لم يكن موجودًا
if not os.path.exists(VISITS_FILE):
    with open(VISITS_FILE, "w") as f:
        json.dump({}, f)


# =================== أدوات مساعدة ===================
def load_visits():
    with open(VISITS_FILE, "r") as f:
        return json.load(f)


def save_visits(data):
    with open(VISITS_FILE, "w") as f:
        json.dump(data, f)


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    httpx.post(url, data={"chat_id": CHAT_ID, "text": text})


def is_bot(user_agent):
    ua = user_agent.lower()
    return any(bot in ua for bot in BOT_KEYWORDS)


def get_device_type(user_agent):
    ua = user_agent.lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "📱 موبايل"
    elif "ipad" in ua or "tablet" in ua:
        return "📲 تابلت"
    elif "windows" in ua or "macintosh" in ua or "linux" in ua:
        return "💻 كمبيوتر"
    return "❓ غير معروف"


def get_location(ip):
    try:
        r = httpx.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        data = r.json()
        return data.get("country_name", "غير معروف"), data.get("city", "غير معروف")
    except:
        return "غير معروف", "غير معروف"


def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def send_file_to_telegram(filepath, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(filepath, "rb") as f:
        files = {"document": (filename, f)}
        data = {"chat_id": CHAT_ID}
        return httpx.post(url, data=data, files=files).json()


# =================== الصفحة الرئيسية ===================
@app.route("/", methods=["GET", "POST"])
def index():
    # -------- إشعار الدخول --------
    ip = get_client_ip()
    user_agent = request.headers.get("User-Agent", "Unknown")

    if not is_bot(user_agent):
        visits = load_visits()
        today = datetime.date.today().isoformat()

        # إشعار مرة واحدة يوميًا لكل IP
        if ip not in visits or visits[ip] != today:
            visits[ip] = today
            save_visits(visits)

            device = get_device_type(user_agent)
            country, city = get_location(ip)
            time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = f"""
🚨 دخول جديد للموقع

🌐 IP: {ip}
📱 الجهاز: {device}
🖥 المتصفح:
{user_agent}

📍 الموقع: {country} - {city}
🕒 الوقت: {time_now}
"""
            send_telegram_message(message)

    # -------- رفع الملفات --------
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)

                telegram_response = send_file_to_telegram(save_path, filename)
                if telegram_response.get("ok"):
                    flash("File uploaded and sent successfully!", "success")
                else:
                    flash("File uploaded but failed to send.", "error")

                return redirect("/")

        if "password" in request.form:
            if request.form["password"] == PASSWORD:
                files = os.listdir(UPLOAD_FOLDER)
                return render_template("files.html", files=files)
            else:
                flash("Incorrect password!", "error")

    return render_template("index.html")


# =================== التحميل والحذف ===================
@app.route("/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Deleted file: {filename}", "success")
    else:
        flash("File not found.", "error")
    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/main")
def main():
    return render_template("main.html")


# =================== تشغيل التطبيق ===================
if __name__ == "__main__":
    app.run()
