import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db


class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    google_id: Mapped[str] = mapped_column(db.String(100), nullable=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), nullable=True)
    picture: Mapped[str] = mapped_column(db.String(200), nullable=True)
    friends: Mapped[List["Friend"]] = relationship(
        "Friend", backref="user", lazy=True, foreign_keys="Friend.user_id"
    )
    groups: Mapped[List["TravelGroup"]] = relationship(
        "TravelGroup", backref="user", lazy=True
    )


# フレンドテーブルのモデル
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)


# グループ作成用のモデル
class TravelGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    icon_path = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    creator_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# グループ招待用モデル
class GroupInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey("travel_group.id"), nullable=False)
    inviting_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    invited_email = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, accepted, rejected


# チャットメッセージのモデル
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    username = db.Column(db.String(100), nullable=False, default="")
    message = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("travel_group.id"), nullable=False)

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.username = User.query.filter_by(user_id=self.user_id).first().name

class AISuggest(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("travel_group.id"), nullable=False
    )
    markdown: Mapped[str] = mapped_column(db.Text, nullable=False)


# 旅行プランの候補地.
# ユーザーが候補地を追加するときに作られる．
class CandidateSite(db.Model):
    __tablename__ = "candidate_site"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    place_id: Mapped[str] = mapped_column(db.String(255), nullable=False)
    place_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    like: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", backref="candidate_site", lazy=True
    )
    room_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("travel_group.id"), nullable=False
    )
    enable: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<CandidateSite {self.place_name}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "place_id": self.place_id,
            "place_name": self.place_name,
            "description": self.description,
            "like": self.like,
            "comments": [c.to_dict() for c in self.comments],
            "group_id": self.room_id,
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

    def add_comment(self, comment: "Comment"):
        self.comments.append(comment)

    def delete_comment(self, comment: "Comment"):
        self.comments.remove(comment)

    def add_like(self):
        self.like += 1

    def delete_like(self):
        self.like -= 1

    def delete_by_user(self):
        self.enable = False

    def restore_by_user(self):
        self.enable = True


# 候補地に対するコメント
class Comment(db.Model):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    site_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("candidate_site.id"), nullable=False
    )
    comment: Mapped[str] = mapped_column(db.Text, nullable=False)
    like: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.DateTime, nullable=False, default=datetime.datetime.now
    )

    def __repr__(self) -> str:
        return f"<Comment {self.comment}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "site_id": self.site_id,
            "comment": self.comment,
            "like": self.like,
            "created_at": self.created_at,
        }

#     def from_dict(self, data: dict):
#         for field in ["user_id", "site_id", "comment", "like", "created_at"]:
#             if field in data:
#                 setattr(self, field, data[field])


# AIによって生成された旅行プラン
class AcceptedSchedule(db.Model):
    __tablename__ = "accepted_schedule"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    place_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("candidate_site.place_id"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("travel_group.id"), nullable=False
    )
    place_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    date: Mapped[int] = mapped_column(db.Integer, nullable=False)  # 0-indexed
    order: Mapped[int] = mapped_column(db.Integer, nullable=False)  # 0-indexed

    def __repr__(self) -> str:
        return f"<AcceptedSchedule {self.site_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "site_id": self.site_id,
            "group_id": self.room_id,
            "date": self.date,
            "order": self.order,
        }

    def from_dict(self, data: dict):
        for field in ["site_id", "group_id", "date", "order"]:
            if field in data:
                setattr(self, field, data[field])


class CandidateSiteLike(db.Model):
    __tablename__ = "candidate_site_like"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    site_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("candidate_site.id"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        db.DateTime, default=datetime.datetime.now
    )
