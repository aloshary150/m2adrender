from flask import Flask, render_template, request, redirect
import os
import json
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

PASSWORD = "aloshary150"
FILES_DB = "files.json"

# Cloudinary config (ENV VARS)
cloudinary.config(
    cloud_name=os.environ.get("dozrkzrr0"),
    api_key=os.environ.get("427765477913586"),
    api_secret=os.environ.get("3043CuLsgBbJLNBt7phTOmU6LCU"),
    secure=True
)

# ---------------- Helpers ----------------
def load_files():
    if not os.path.exists(FILES_DB):
        return []
    with open(FILES_DB, "r") as f:
        return json.load(f)

def save_files(files):
    with open(FILES_DB, "w") as f:
        json.dump(files, f)

# ---------------- Routes ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Upload file
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:
                upload = cloudinary.uploader.upload(
                    file,
                    folder="aloshary",
                    resource_type="auto"
                )

                files = load_files()
                files.append({
                    "name": file.filename,
                    "url": upload["secure_url"],
                    "public_id": upload["public_id"]
                })
                save_files(files)

            return redirect("/")

        # Admin login
        if "password" in request.form:
            if request.form["password"] == PASSWORD:
                files = load_files()
                return render_template("files.html", files=files)

    return render_template("index.html")


@app.route("/delete/<public_id>", methods=["POST"])
def delete(public_id):
    cloudinary.uploader.destroy(public_id)

    files = load_files()
    files = [f for f in files if f["public_id"] != public_id]
    save_files(files)

    return redirect("/")


@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
