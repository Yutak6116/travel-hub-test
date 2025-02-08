from flask import Blueprint, render_template, session, redirect, url_for

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    user_info = {
        'name': session.get('name'),
        'email': session.get('email')
    }
    return render_template('profile.html', user=user_info)