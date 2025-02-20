from flask import Flask, request, redirect, url_for, jsonify, render_template
import pandas as pd
import threading
from datetime import datetime

app = Flask(__name__)

# Example Users Dictionary (replace with actual data)
users = {
    "kk": {"identifier": "kk", "address": "123 Street", "region": "North"},
    "ll": {"identifier": "ll", "address": "456 Avenue", "region": "South"},
}

log_lock = threading.Lock()
df_ele = pd.DataFrame(columns=['identifier', 'usage', 'timestamp'])  # Initialize DataFrame

def write_log(identifier, timestamp, usage):
    """Appends meter data to log.txt."""
    with open("log.txt", "a") as f:
        f.write(f"{identifier},{timestamp},{usage}\n")

@app.route("/company/meter", methods=["GET", "POST"])
def meter_uploading():
    if request.method == "POST":
        identifier = request.form["identifier"]
        usage = request.form["usage"]

        if identifier in users:
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Update DataFrame (Ensure global usage)
            global df_ele
            new_row = {'identifier': identifier, 'usage': usage, 'timestamp': timestamp}
            new_df = pd.DataFrame([new_row])
            df_ele = pd.concat([df_ele, new_df], ignore_index=True)
            print(df_ele)

            # Append to log file
            with log_lock:
                try:
                    write_log(identifier, timestamp, usage)
                    return redirect(url_for("meter_uploaded", identifier=identifier, timestamp=timestamp, usage=usage))
                except Exception as e:
                    return jsonify({'message': 'Data uploading failed.'})

        return render_template("meter_upload.html", error="Invalid credentials. Try again.")

    return render_template("meter_upload.html", error=None)

@app.route("/meter_uploaded")
def meter_uploaded():
    identifier = request.args.get("identifier")
    timestamp = request.args.get("timestamp")
    usage = request.args.get("usage")
    return render_template("upload_success.html", identifier=identifier, timestamp=timestamp, usage=usage)

if __name__ == "__main__":
    app.run(debug=True)
