from os import getenv
from flask import Flask, render_template
import requests as r
from requests.exceptions import ConnectionError
from datetime import datetime


# -------------------
# ENV VARS
# -------------------
API_ADDR = getenv("API_ADDR", None)
API_PORT = getenv("API_PORT", None)

if API_ADDR is None or API_PORT is None:
    raise ValueError("Needs API_ADDR and API_PORT environment variables.")

API_ENDPOINT = f'http://{API_ADDR}:{API_PORT}'

# -------------------
# FLASK APP
# -------------------
app = Flask(__name__)
respond_text_plain = lambda txt, code: (txt, code, {'Content-Type': 'text/plain; charset=UTF-8'})

# -------------------
# ROUTES
# -------------------
@app.route('/')
def hello_world():
    try:
        result = r.get(f'{API_ENDPOINT}/', timeout=3)
        body = result.json()

        if result.status_code >= 200 and result.status_code < 400:
            return render_template('index.html', hasTimestamps=len(body) > 0, timestamps=[
                datetime.fromisoformat(e['timestamp']).strftime('%d/%m/%Y %H:%M:%S %z')
                for e in body
            ], utcnow=datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S %z'))
        else:
            return render_template('error.html')

    except (TimeoutError, ConnectionError):
        return render_template('error.html')

@app.route('/healthz')
def healthz():
    try:
        result = r.get(f'{API_ENDPOINT}/healthz', timeout=3)

        if result.status_code >= 200 and result.status_code < 400:
            return respond_text_plain('healthy', 200)
        else:
            return respond_text_plain('unhealthy', 503)

    except (TimeoutError, ConnectionError):
        return respond_text_plain('unhealthy', 503)
