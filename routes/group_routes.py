from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from models import TravelGroup, GroupInvitation, Friend
from extensions import db
import datetime
import os
from werkzeug.utils import secure_filename

group_bp = Blueprint('group', __name__)

@group_bp.app_template_filter('get_group_title')
def get_group_title(group_id):
    group = TravelGroup.query.get(group_id)
    return group.title if group else '不明なグループ'

@group_bp.app_template_filter('get_inviter_info')
def get_inviter_info(group_id):
    group = TravelGroup.query.get(group_id)
    if group:
        return f"{group.creator_name} ({group.creator_email})"
    return "不明な招待者"

@group_bp.route('/travels')
def travels():
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
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

@group_bp.route('/group_creation', methods=['GET', 'POST'])
def group_creation():
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    if request.method == 'POST':
        travel_title = request.form.get('travel_title')
        travel_icon = request.files.get('travel_icon')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        # 日付文字列をDate型に変換
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except Exception as e:
            flash('日付の形式が不正です。')
            return redirect(url_for('group.group_creation'))
        
        # アップロードされたファイルの処理（例）
        icon_path = None
        if travel_icon and travel_icon.filename:
            filename = secure_filename(travel_icon.filename)
            icon_path = os.path.join(group_bp.config['UPLOAD_FOLDER'], filename)
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

        # フレンド選択による招待
        selected_friends = request.form.getlist('selected_friends')
        if selected_friends:
            for friend_email in selected_friends:
                invitation = GroupInvitation(
                    group_id=new_group.id,
                    invited_email=friend_email,
                    status='pending'
                )
                db.session.add(invitation)
        
        # 入力されたメールアドレスによる招待（空文字は除外）
        invite_emails = request.form.getlist('invite_emails[]')
        if invite_emails:
            for email in invite_emails:
                email = email.strip()
                if email:
                    invitation = GroupInvitation(
                        group_id=new_group.id,
                        invited_email=email,
                        status='pending'
                    )
                    db.session.add(invitation)
        
        db.session.commit()
        flash("グループを作成し、招待を送信しました。")
        return redirect(url_for('group.travels'))
    
    # GETの場合は、ログイン中のユーザーのフレンド情報のみを取得
    friends = Friend.query.filter_by(user_email=session.get('email')).all()
    return render_template('group_creation.html', friends=friends)

@group_bp.route('/handle_invitation/<int:invitation_id>', methods=['POST'])
def handle_invitation(invitation_id):
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    invitation = GroupInvitation.query.get(invitation_id)
    if not invitation or invitation.invited_email != session.get('email'):
        flash('権限がありません。')
        return redirect(url_for('group.travels'))
    action = request.form.get('action')
    if action == 'accept':
        invitation.status = 'accepted'
        flash('参加を承諾しました。')
    else:
        invitation.status = 'rejected'
        flash('参加を拒否しました。')
    db.session.commit()
    return redirect(url_for('group.travels'))