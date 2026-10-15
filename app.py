
from flask import Flask, request, send_from_directory
from pathlib import Path
import os
import json
import gspread

app = Flask(__name__)

# Locate the project and website folders
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

# Google Sheets configuration
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

# Read Google credentials securely from Vercel
credentials_info = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
)

# Connect to Google Sheets
client = gspread.service_account_from_dict(credentials_info)

spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.worksheet("Sheet1")


# Display the homepage
@app.route("/")
def home():
    return send_from_directory(PUBLIC_DIR, "index.html")


# Display the sign-in page
@app.route("/signin.html")
def signin():
    return send_from_directory(PUBLIC_DIR, "signin.html")


# Serve the CSS file
@app.route("/Style.CSS")
def stylesheet():
    return send_from_directory(PUBLIC_DIR, "Style.CSS")


# Receive the email or mobile number and save it
@app.route("/continue", methods=["POST"])
def save_input():
    email = request.form.get("email", "").strip()

    if not email:
        return "Please enter an email or mobile number.", 400

    try:
        sheet.append_row([email])
        return """
        <h2>Success!</h2>
        <p>Your input has been saved to Google Sheets.</p>
        <a href="/signin.html">Go back</a>
        """

    except Exception:
        app.logger.exception(
            "Could not save input to Google Sheets"
        )
        return "Could not save your input. Please try again.", 500


if __name__ == "__main__":
    app.run(debug=False)
