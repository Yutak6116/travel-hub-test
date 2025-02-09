from flask import Blueprint, redirect, url_for, session, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import os
from config import REDIRECT_URI, GOOGLE_CLIENT_ID

oauth_bp = Blueprint('oauth', __name__)

flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
    redirect_uri=REDIRECT_URI
)

@oauth_bp.route('/')
def index():
    return render_template('example.html')

@oauth_bp.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@oauth_bp.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        return 'State mismatch error', 400

    credentials = flow.credentials
    request_session = google_requests.Request()

    id_info = id_token.verify_oauth2_token(
        credentials.id_token, request_session, GOOGLE_CLIENT_ID
    )

    session['google_id'] = id_info.get("sub")
    session['email'] = id_info.get("email")
    session['name'] = id_info.get("name")

    return redirect(url_for('group.travels'))

@oauth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')