import os
from extensions import app, db, socketio

app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Google OAuth 2.0の設定
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Blueprint のインポートと登録
from routes.oauth_routes import oauth_bp
from routes.group_routes import group_bp
from routes.friend_routes import friend_bp
from routes.chat_routes import chat_bp
from routes.profile_routes import profile_bp

app.register_blueprint(oauth_bp)
app.register_blueprint(group_bp)
app.register_blueprint(friend_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(profile_bp)

import routes

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()  # 既存のテーブルを削除
        db.create_all()  # 新しいスキーマでテーブル作成
    # socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)