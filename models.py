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
    start_time = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Date, nullable=False)
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

# 旅行プランのテキストモデル
class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)
    markdown = db.Column(db.Text, nullable=False)

# 実際に行く旅行プランのモデル
class TravelPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)
    place_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=True)    # その場所に行く日付
    place_id = db.Column(db.String(255), nullable=True) # place_idは、services/place_services.pyのget_place_coordinates関数で取得する(引数は行く場所名)
    comments = db.relationship('PlaceComment', backref='travel_plan_item', lazy=True)
    rating = db.Column(db.Integer, nullable=False)  #いいね数
    order = db.Column(db.Integer, nullable=True)
    # start_time = db.Column(db.DateTime, nullable=True)
    # end_time = db.Column(db.DateTime, nullable=True)
    # Google Places APIのplace_idを保存するカラム
    
    
# 全候補地のモデル
class AllTravelPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)
    place_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    place_id = db.Column(db.String(255), nullable=False)
    comments = db.relationship('PlaceComment', backref='travel_plan_item', lazy=True)
    rating = db.Column(db.Integer, nullable=False)
    # Google Places APIのplace_idを保存するカラム
    # start_time = db.Column(db.DateTime, nullable=True)
    # end_time = db.Column(db.DateTime, nullable=True)

# 削除した候補地

class DeletedTravelPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('travel_group.id'), nullable=False)
    place_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    place_id = db.Column(db.String(255), nullable=False)
    # start_time = db.Column(db.DateTime, nullable=True)
    # end_time = db.Column(db.DateTime, nullable=True)    
    # Google Places APIのplace_idを保存するカラム

class PlaceComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)