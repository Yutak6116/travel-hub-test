from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from extensions import db
from models import Friend, User

friend_bp = Blueprint("friend", __name__)


@friend_bp.route("/friend_list")
def friend_list():
    if "user_id" not in session:
        return redirect(url_for("oauth.index"))
    current_user_id = session.get("user_id")
    friends = Friend.query.filter_by(user_id=current_user_id).all()
    friends_details = [User.query.get(friend.friend_id) for friend in friends]
    return render_template("friend_list.html", friends=friends_details)


@friend_bp.route("/update_friend/<int:friend_id>", methods=["POST"])
def update_friend(friend_id):
    if "google_id" not in session:
        return redirect(url_for("oauth.index"))
    friend = Friend.query.get(friend_id)
    if not friend or friend.user_id != session.get("user_id"):
        flash("権限がありません。")
        return redirect(url_for("friend.friend_list"))
    new_name = request.form.get("friend_name")
    if not new_name:
        flash("表示名を入力してください。")
        return redirect(url_for("friend.friend_list"))
    friend.display_name = new_name
    db.session.commit()
    flash("フレンド表示名を更新しました。")
    return redirect(url_for("friend.friend_list"))


@friend_bp.route("/add_friend", methods=["POST"])
def add_friend():
    if "user_id" not in session:
        return redirect(url_for("oauth.index"))
    current_user_id = session.get("user_id")
    friend_email = request.form.get("friend_email")
    if not friend_email:
        flash("メールアドレスを入力してください。")
        return redirect(url_for("friend.friend_list"))
    friend_user = User.query.filter_by(email=friend_email).first()
    if not friend_user:
        flash("フレンドが見つかりません。")
        return redirect(url_for("friend.friend_list"))
    existing_friend = Friend.query.filter_by(
        user_id=current_user_id, friend_id=friend_user.id
    ).first()
    if existing_friend:
        flash("すでに追加されているフレンドです。")
        return redirect(url_for("friend.friend_list"))
    new_friend = Friend(user_id=current_user_id, friend_id=friend_user.id)
    db.session.add(new_friend)
    db.session.commit()
    flash("フレンドを追加しました。")
    return redirect(url_for("friend.friend_list"))
