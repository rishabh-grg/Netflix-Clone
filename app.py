
from flask import Flask, request, send_from_directory
from pathlib import Path
import os
import json
import gspread

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory(str(PUBLIC_DIR), "index.html")

@app.route("/continue", methods=["GET", "POST"])
def continue_route():
    if request.method == "GET":
        return "Continue route is working. Submit the form using POST."

    email = request.form.get("email", "").strip()

    if not email:
        return "Please enter an email or mobile number.", 400

    return f"Form received successfully for: {email}"


@app.route("/signin.html")
def signin():
    return send_from_directory(str(PUBLIC_DIR), "signin.html")


@app.route("/<path:filename>")
def public_files(filename):
    file_path = (PUBLIC_DIR / filename).resolve()

    # Prevent access to files outside the public folder.
    if not file_path.is_relative_to(PUBLIC_DIR.resolve()):
        return "Not Found", 404

    if file_path.is_file():
        return send_from_directory(str(PUBLIC_DIR), filename)

    return "Not Found", 404


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
        <h2>Success!</h2>
        <p>Your input has been saved to Google Sheets.</p>
        <a href="/signin.html">Go back</a>
        """

    except Exception:
        app.logger.exception("Could not save input to Google Sheets")
        return "Could not save your input. Please check the configuration.", 500

@app.route("/debug-files")
def debug_files():
    return {
        "base_directory": str(BASE_DIR),
        "public_directory": str(PUBLIC_DIR),
        "public_directory_exists": PUBLIC_DIR.is_dir(),
        "index_exists": (PUBLIC_DIR / "index.html").is_file(),
        "signin_exists": (PUBLIC_DIR / "signin.html").is_file()
    }


if __name__ == "__main__":
    app.run(debug=False)
