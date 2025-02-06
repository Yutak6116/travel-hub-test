from flask import Flask, redirect, url_for, session, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# アップロード先の設定
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# SQLAlchemy の設定（SQLite の例）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# フレンドテーブルのモデル
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)  # 申請者 or 自分のメールアドレス
    friend_email = db.Column(db.String(100), nullable=False)  # 追加する相手のメールアドレス
    friend_name = db.Column(db.String(100), nullable=False)   # 追加する相手の名前
    __table_args__ = (
        db.UniqueConstraint('user_email', 'friend_email', name='unique_user_friend'),
    )

# グループ作成用のモデル
class TravelGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    icon_path = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    creator_email = db.Column(db.String(100), nullable=False)
    creator_name = db.Column(db.String(100), nullable=False)

# グループ招待用モデル
class GroupInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)
    invited_email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, rejected

# Google OAuth 2.0の設定
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = '286034041289-kf1q4emv7eo7a5f6bvdctg3jgn64sh8k.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
REDIRECT_URI = "http://localhost:5000/callback"

flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
    redirect_uri=REDIRECT_URI
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
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

    return redirect(url_for('travels'))

@app.route('/travels')
def travels():
    if 'google_id' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    # ユーザーが作成したグループ
    creator_groups = TravelGroup.query.filter_by(creator_email=user_email).all()
    # ユーザーが承諾した招待のグループを取得
    accepted_invitations = GroupInvitation.query.filter_by(invited_email=user_email, status='accepted').all()
    accepted_group_ids = [inv.group_id for inv in accepted_invitations]
    invited_groups = TravelGroup.query.filter(TravelGroup.id.in_(accepted_group_ids)).all() if accepted_group_ids else []
    # 旅行予定一覧には作成グループと承諾済みの招待グループを表示
    travels = creator_groups + invited_groups
    # 参加待ち（pending）の招待を取得
    pending_invitations = GroupInvitation.query.filter_by(invited_email=user_email, status='pending').all()
    return render_template('travels.html', travels=travels, invitations=pending_invitations)

@app.route('/group_creation', methods=['GET', 'POST'])
def group_creation():
    if 'google_id' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        travel_title = request.form.get('travel_title')
        travel_icon = request.files.get('travel_icon')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        # 選択されたフレンドのメールアドレスリスト（チェックボックスの値）
        selected_friends = request.form.getlist('selected_friends')
        # フレンド以外の招待メール（カンマ区切り）
        invite_emails = request.form.get('invite_emails')
        
        # 日付文字列をDate型に変換
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except Exception as e:
            flash('日付の形式が不正です。')
            return redirect(url_for('group_creation'))
        
        # アップロードされたファイルの処理（例）
        icon_path = None
        if travel_icon and travel_icon.filename:
            filename = secure_filename(travel_icon.filename)
            icon_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            travel_icon.save(icon_path)
        
        creator_email = session.get('email')
        creator_name = session.get('name')
        
        new_group = TravelGroup(
            title=travel_title,
            icon_path=icon_path,
            start_date=start_date,
            end_date=end_date,
            creator_email=creator_email,
            creator_name=creator_name 
        )
        db.session.add(new_group)
        db.session.commit()

        # 招待処理：グループ作成者以外の全ての招待先に対して GroupInvitation を作成
        invitees = set(selected_friends)  # チェックボックスで選んだフレンド（メールアドレス）
        if invite_emails:
            # カンマ区切りのメールアドレスを追加
            for email in invite_emails.split(','):
                invitees.add(email.strip())
        # 作成者自身への招待は除外
        if creator_email in invitees:
            invitees.remove(creator_email)
        
        for email in invitees:
            invitation = GroupInvitation(group_id=new_group.id, invited_email=email, status='pending')
            db.session.add(invitation)
        db.session.commit()

        flash('グループが作成され、招待が送信されました。')
        return redirect(url_for('travels'))
    
    # GETの場合は、ログイン中のユーザーのフレンド情報のみを取得
    friends = Friend.query.filter_by(user_email=session.get('email')).all()
    return render_template('group_creation.html', friends=friends)

@app.template_filter('get_group_title')
def get_group_title(group_id):
    group = TravelGroup.query.get(group_id)
    return group.title if group else '不明なグループ'

@app.template_filter('get_inviter_info')
def get_inviter_info(group_id):
    group = TravelGroup.query.get(group_id)
    if group:
        return f"{group.creator_name} ({group.creator_email})"
    return "不明な招待者"

@app.route('/handle_invitation/<int:invitation_id>', methods=['POST'])
def handle_invitation(invitation_id):
    if 'google_id' not in session:
        return redirect(url_for('index'))
    invitation = GroupInvitation.query.get(invitation_id)
    if not invitation or invitation.invited_email != session.get('email'):
        flash('権限がありません。')
        return redirect(url_for('travels'))
    action = request.form.get('action')
    if action == 'accept':
        invitation.status = 'accepted'
        flash('参加を承諾しました。')
    else:
        invitation.status = 'rejected'
        flash('参加を拒否しました。')
    db.session.commit()
    return redirect(url_for('travels'))

@app.route('/friend_list')
def friend_list():
    if 'google_id' not in session:
        return redirect(url_for('index'))
    # DBからフレンド情報を取得
    friends = Friend.query.all()
    return render_template('friend_list.html', friends=friends)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'google_id' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    friend_email = request.form.get('friend_email')
    friend_name = request.form.get('friend_name')
    if not friend_email or not friend_name:
        flash('メールアドレスと表示名を入力してください。')
        return redirect(url_for('friend_list'))
    
    # 重複登録のチェック（すでに登録済みの場合）
    existing_friend = Friend.query.filter_by(user_email=user_email, friend_email=friend_email).first()
    if existing_friend:
        flash('すでに追加されているフレンドです。')
        return redirect(url_for('friend_list'))
    
    new_friend = Friend(user_email=user_email, friend_email=friend_email, friend_name=friend_name)
    db.session.add(new_friend)
    db.session.commit()
    flash('フレンドを追加しました。')
    return redirect(url_for('friend_list'))

@app.route('/update_friend/<int:friend_id>', methods=['POST'])
def update_friend(friend_id):
    if 'google_id' not in session:
        return redirect(url_for('index'))
    friend = Friend.query.get(friend_id)
    if not friend or friend.user_email != session.get('email'):
        flash('権限がありません。')
        return redirect(url_for('friend_list'))
    new_name = request.form.get('friend_name')
    if not new_name:
        flash('表示名を入力してください。')
        return redirect(url_for('friend_list'))
    friend.friend_name = new_name
    db.session.commit()
    flash('フレンド表示名を更新しました。')
    return redirect(url_for('friend_list'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # 既存のテーブルを削除
        db.create_all()  # 新しいスキーマでテーブル作成
    app.run(debug=True)