from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from extensions import db
from models import Friend

friend_bp = Blueprint('friend', __name__)

@friend_bp.route('/friend_list')
def friend_list():
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    # DBからフレンド情報を取得
    friends = Friend.query.all()
    return render_template('friend_list.html', friends=friends)

@friend_bp.route('/update_friend/<int:friend_id>', methods=['POST'])
def update_friend(friend_id):
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    friend = Friend.query.get(friend_id)
    if not friend or friend.user_email != session.get('email'):
        flash('権限がありません。')
        return redirect(url_for('friend.friend_list'))
    new_name = request.form.get('friend_name')
    if not new_name:
        flash('表示名を入力してください。')
        return redirect(url_for('friend.friend_list'))
    friend.friend_name = new_name
    db.session.commit()
    flash('フレンド表示名を更新しました。')
    return redirect(url_for('friend.friend_list'))

@friend_bp.route('/add_friend', methods=['POST'])
def add_friend():
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    user_email = session.get('email')
    friend_email = request.form.get('friend_email')
    friend_name = request.form.get('friend_name')
    if not friend_email or not friend_name:
        flash('メールアドレスと表示名を入力してください。')
        return redirect(url_for('friend.friend_list'))
    
    # 重複登録のチェック（すでに登録済みの場合）
    existing_friend = Friend.query.filter_by(user_email=user_email, friend_email=friend_email).first()
    if existing_friend:
        flash('すでに追加されているフレンドです。')
        return redirect(url_for('friend.friend_list'))
    
    new_friend = Friend(user_email=user_email, friend_email=friend_email, friend_name=friend_name)
    db.session.add(new_friend)
    db.session.commit()
    flash('フレンドを追加しました。')
    return redirect(url_for('friend.friend_list'))