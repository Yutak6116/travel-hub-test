import eventlet
eventlet.monkey_patch()  # ← ここを追加！

import os
from extensions import app, db, socketio

app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# db.create_all() を main ブロック外で実行することで、Render上でもDB初期化されるようにする
with app.app_context():
    db.create_all()

# Google OAuth 2.0の設定
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Blueprint のインポートと登録
from routes.oauth_routes import oauth_bp
from routes.group_routes import group_bp
from routes.friend_routes import friend_bp
from routes.chat_routes import chat_bp
from routes.map_routes import map_bp
from routes.plan_routes import plan_bp
from routes.profile_routes import profile_bp

app.register_blueprint(oauth_bp)
app.register_blueprint(group_bp)
app.register_blueprint(friend_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(plan_bp)
app.register_blueprint(map_bp)
app.register_blueprint(profile_bp)

import routes

# 本番環境向けの修正
# if __name__ == "__main__":
#     with app.app_context():
#         db.drop_all()
#         db.create_all()  # 初回のみテーブル作成（drop_all() を削除）

#     # Renderの環境変数 PORT を取得
#     port = int(os.environ.get("PORT", 10000))
#     socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)

# __main__ に依存せずアプリ起動時にDB初期化する
with app.app_context():
    db.create_all()  # テーブルが存在しない場合のみ作成

if __name__ == "__main__":
    # Render環境では __main__ ブロックが実行されないので、ここには初期化処理を入れない
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)