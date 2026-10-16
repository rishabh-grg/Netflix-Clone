```python
from flask import Flask, request, send_from_directory
from pathlib import Path
import os
import json
import gspread

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(str(PUBLIC_DIR), "index.html")


@app.route("/signin.html", methods=["GET"])
def signin():
    return send_from_directory(str(PUBLIC_DIR), "signin.html")


@app.route("/continue", methods=["POST"])
def save_input():
    email = request.form.get("email", "").strip()

    if not email:
        return "Please enter an email or mobile number.", 400

    try:
        spreadsheet_id = os.environ["SPREADSHEET_ID"]
        credentials_info = json.loads(
            os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        )

        client = gspread.service_account_from_dict(credentials_info)
        spreadsheet = client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet("Sheet1")

        sheet.append_row([email])

        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Success</title>
        </head>
        <body>
            <h2>Success!</h2>
            <p>Your email or mobile number has been saved.</p>
            <a href="/signin.html">Go back</a>
        </body>
        </html>
        """, 200

    except Exception:
        app.logger.exception("Google Sheets submission failed")
        return (
            "Could not save your input. Check the Vercel runtime logs.",
            500
        )


@app.route("/debug-files", methods=["GET"])
def debug_files():
    return {
        "public_directory_exists": PUBLIC_DIR.is_dir(),
        "index_exists": (PUBLIC_DIR / "index.html").is_file(),
        "signin_exists": (PUBLIC_DIR / "signin.html").is_file(),
        "routes": str(app.url_map)
    }


@app.route("/health-check", methods=["GET"])
def health_check():
    return {
        "status": "Flask is running",
        "routes": str(app.url_map)
    }, 200


@app.route("/<path:filename>", methods=["GET"])
def public_files(filename):
    root = PUBLIC_DIR.resolve()
    file_path = (root / filename).resolve()

    if not file_path.is_relative_to(root):
        return "Not Found", 404

    if file_path.is_file():
        return send_from_directory(str(root), filename)

    return "Page not found", 404


if __name__ == "__main__":
    app.run(debug=False)
```
