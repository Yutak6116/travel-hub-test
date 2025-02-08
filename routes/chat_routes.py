from flask import Blueprint, redirect, url_for, session, request, render_template, flash
from flask_socketio import emit, join_room
import markdown
from extensions import db, socketio
from models import TravelGroup, GroupInvitation, ChatMessage, TravelPlan
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
    travel_plan = TravelPlan.query.filter_by(room_id=room_id).order_by(TravelPlan.id.desc()).first()
    travel_plan_markdown = travel_plan.markdown if travel_plan else ""
    return render_template('chat.html', user=user_info, history=history, room=room, travel_plan_markdown=travel_plan_markdown)

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
        response = requests.post(
            "https://us-central1-goukan2house.cloudfunctions.net/travel_helper",
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
            if "旅行プラン" in reply_text:
                travel_plan = TravelPlan(room_id=room, markdown=reply_text)
                db.session.add(travel_plan)
            db.session.commit()
            emit('receive_message', ai_data, room=str(room))
        else:
            # エラーハンドリング（必要に応じて）
            pass