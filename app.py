import os
from flask import Flask
from models import db

app = Flask(__name__)
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

app.register_blueprint(oauth_bp)
app.register_blueprint(group_bp)
app.register_blueprint(friend_bp)

import routes

with app.app_context():
    print(app.url_map)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # 既存のテーブルを削除
        db.create_all()  # 新しいスキーマでテーブル作成
    app.run(debug=True)