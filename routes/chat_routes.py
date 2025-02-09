from flask import Blueprint, redirect, url_for, session, request, render_template, flash, jsonify
from flask_socketio import emit, join_room
import markdown
from extensions import db, socketio
from models import TravelGroup, GroupInvitation, ChatMessage, CandidateSite, AcceptedSchedule
import requests  # 追加

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/<int:room_id>')
def chat(room_id):
    if 'google_id' not in session:
        return redirect(url_for('oauth.index'))
    room = TravelGroup.query.get_or_404(room_id)
    current_email = session.get('email')
    # 作成者ならアクセス可能
    has_access = (room.creator_email == current_email)
    # または招待されている場合
    invited = GroupInvitation.query.filter_by(group_id=room_id, invited_email=current_email).first()
    if not (has_access or invited):
        flash('このルームへの参加権がありません。')
        return redirect(url_for('group.travels'))
    user_info = {
        'name': session.get('name'),
        'email': current_email
    }
    history_objs = ChatMessage.query.filter_by(room_id=room_id).all()
    # Markdown を HTML に変換
    history = []
    for msg in history_objs:
        msg_html = markdown.markdown(msg.message)
        history.append({
            'username': msg.username,
            'message': msg_html
        })
        # 最新のTravelPlanを取得（存在すれば）
    # あげられている候補地
    enabled_site = CandidateSite.query.filter_by(room_id=room_id, enable=True).order_by(CandidateSite.like.desc()).all()
    # ごみ箱行きになった候補地
    disabled_site = CandidateSite.query.filter_by(room_id=room_id, enable=False).order_by(CandidateSite.like.desc()).all()
    # 実際の旅行プラン
    accepted_site = AcceptedSchedule.query.filter_by(room_id=room_id).order_by(AcceptedSchedule.order.desc()).all()
    
    # 全候補地を取得
    enabled_list = []
    disabled_list = []
    accepted_list = []
    if enabled_site:
        for site in enabled_site:
            enabled_list.append({
                'site_id': site.id,
                'place_name': site.place_name,
                'description': site.description,
                'like': site.like,
                # 'comments': [c.conmment for c in site.comments]
            })
    
    if disabled_site:
        for site in disabled_site:
            disabled_list.append({
                'site_id': site.id,
                'place_name': site.place_name,
                'description': site.description,
                'like': site.like,
                # 'comments': [c.conmment for c in site.comments]
            })
    
    if accepted_site:
        for site in accepted_site:
            accepted_list.append({
                'site_id': site.id,
                'place_name': site.place_name,
                'description': site.description,
                'like': site.like,
                # 'comments': [c.conmment for c in site.comments]
            })
                
    
    return render_template('chat.html', user=user_info, history=history, room=room, 
                           enabled_list=enabled_list, disabled_list=disabled_list, accepted_list=accepted_list)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    room = data.get('room')
    msg = ChatMessage(username=data['user'], message=data['message'], room_id=room)
    db.session.add(msg)
    db.session.commit()
    emit('receive_message', data, room=str(room))
    
    if '@AI' in data.get('message', ''):
        # まず「Loading」と表示
        loading_msg = {"room": room, "user": "travel AI", "message": "Loading"}
        emit('receive_message', loading_msg, room=str(room))
        ai_loading = ChatMessage(username="travel AI", message="Loading", room_id=room)
        db.session.add(ai_loading)
        db.session.commit()
        
        # ルームのチャット履歴を取得（昇順）
        conversation_objs = ChatMessage.query.filter_by(room_id=room).order_by(ChatMessage.id).all()
        conversation = ""
        for m in conversation_objs:
            conversation += f"{m.username}: {m.message}\n"
            
        # Cloud Function へPOSTリクエスト送信
        # 提案bot
        response = requests.post(
            "https://us-central1-goukan2house.cloudfunctions.net/teian_help",
            headers={"Content-Type": "application/json"},
            json={"conversation": conversation}
        )
        if response.ok:
            # JSONから候補の返信部分のみ抽出
            data_json = response.json()
            candidate_text = data_json["candidates"][0]["content"]["parts"][0]["text"]
            
            reply_text = candidate_text.strip()
            ai_data = {
                "room": room,
                "user": "travel AI",
                "message": reply_text
            }
            # DBに最終的なチャットメッセージとして保存
            ai_msg = ChatMessage(username="travel AI", message=reply_text, room_id=room)
            db.session.add(ai_msg)
            db.session.commit()
        else:
            # エラーハンドリング（必要に応じて）
            pass
        
@chat_bp.route('/route_define/int:<room_id>', methods=['POST'])
def route_define(room_id):
    


@chat_bp.route('/invite/<int:room_id>', methods=['POST'])
def chat_invite(room_id):
    if 'google_id' not in session:
        return jsonify({'error': '認証が必要です'}), 401

    invite_email = request.form.get('invite_email')
    if not invite_email:
        return jsonify({'error': 'メールアドレスが必要です'}), 400

    # 既存の招待情報との重複をチェック
    existing_invitation = GroupInvitation.query.filter_by(
        group_id=room_id,
        invited_email=invite_email
    ).first()
    if existing_invitation:
        return jsonify({'error': '既に招待済みです'}), 400

    invitation = GroupInvitation(group_id=room_id, invited_email=invite_email, status='pending')
    db.session.add(invitation)
    db.session.commit()
    return jsonify({'success': True}), 200