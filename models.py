from extensions import db
import datetime

# フレンドテーブルのモデル
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)  # 自分のメールアドレス
    friend_email = db.Column(db.String(100), nullable=False)  # 追加する相手のメールアドレス
    friend_name = db.Column(db.String(100), nullable=False)   # 表示名
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

# チャットメッセージのモデル
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)

# 旅行プランのモデル
class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)
    markdown = db.Column(db.Text, nullable=False)