import datetime
from typing import List, Optional

from extensions import db


# フレンドテーブルのモデル
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)  # 自分のメールアドレス
    friend_email = db.Column(
        db.String(100), nullable=False
    )  # 追加する相手のメールアドレス
    friend_name = db.Column(db.String(100), nullable=False)  # 表示名
    __table_args__ = (
        db.UniqueConstraint("user_email", "friend_email", name="unique_user_friend"),
    )


# グループ作成用のモデル
class TravelGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    icon_path = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    creator_email = db.Column(db.String(100), nullable=False)
    creator_name = db.Column(db.String(100), nullable=False)


# グループ招待用モデル
class GroupInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("travel_group.id"), nullable=False)
    invited_email = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, accepted, rejected


# チャットメッセージのモデル
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("travel_group.id"), nullable=False)


# 旅行プランの候補地.
# ユーザーが候補地を追加するときに作られる．
class CandidateSite(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    place_id: str = db.Column(db.String(255), nullable=True)
    place_name: str = db.Column(db.String(100), nullable=False)
    description: Optional[str] = db.Column(db.Text, nullable=True)
    like: int = db.Column(db.Integer, nullable=False, default=0)
    # comments: List["Comment"] = db.relationship(
    #     "Comment", backref="candidate_site", lazy=True
    # )
    room_id: int = db.Column(
        db.Integer, db.ForeignKey("travel_group.id"), nullable=False
    )  # which group this site belongs to
    enable: bool = db.Column(
        db.Boolean, nullable=False, default=True
    )  # False if user delete this site

    def __repr__(self):
        return f"<CandidateSite {self.place_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "place_id": self.place_id,
            "place_name": self.place_name,
            "description": self.description,
            "like": self.like,
            # "comments": [c.to_dict() for c in self.comments],
            "group_id": self.group_id,
            "enable": self.enable,
        }

    def from_dict(self, data: dict):
        for field in [
            "user_id",
            "place_id",
            "place_name",
            "description",
            "like",
            # "comments",
            "group_id",
            "enable",
        ]:
            if field in data:
                setattr(self, field, data[field])

    # def add_comment(self, comment: "Comment"):
    #     self.comments.append(comment)

    # def delete_comment(self, comment: "Comment"):
    #     self.comments.remove(comment)

    def add_like(self):
        self.like += 1

    def delete_like(self):
        self.like -= 1

    def delete_by_user(self):
        self.enable = False

    def restore_by_user(self):
        self.enable = True


# 候補地に対するコメント
# class Comment(db.Model):
#     id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     site_id: int = db.Column(
#         db.Integer, db.ForeignKey("candidate_site.id"), nullable=False
#     )
#     comment: str = db.Column(db.Text, nullable=False)
#     like: int = db.Column(db.Integer, nullable=False, default=0)
#     created_at: datetime.datetime = db.Column(
#         db.DateTime, nullable=False, default=datetime.datetime.now
#     )

#     def __repr__(self):
#         return f"<Comment {self.comment}>"

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "site_id": self.site_id,
#             "comment": self.comment,
#             "like": self.like,
#             "created_at": self.created_at,
#         }

#     def from_dict(self, data: dict):
#         for field in ["user_id", "site_id", "comment", "like", "created_at"]:
#             if field in data:
#                 setattr(self, field, data[field])


# AIによって生成された旅行プラン
class AcceptedSchedule(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id: int = db.Column(
        db.Integer, db.ForeignKey("candidate_site.id"), nullable=False
    )
    room_id: int = db.Column(
        db.Integer, db.ForeignKey("travel_group.id"), nullable=False
    )
    date: int = db.Column(db.Integer, nullable=False)  # 0-indexed
    order: int = db.Column(db.Integer, nullable=False)  # 0-indexed

    def __repr__(self):
        return f"<AcceptedRSchedule {self.site_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "site_id": self.site_id,
            "group_id": self.group_id,
            "date": self.date,
            "order": self.order,
        }

    def from_dict(self, data: dict):
        for field in ["site_id", "group_id", "date", "order"]:
            if field in data:
                setattr(self, field, data[field])
