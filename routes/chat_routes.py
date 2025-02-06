from flask import Blueprint, redirect, url_for, session, request, render_template, flash
from flask_socketio import emit, join_room
from extensions import db, socketio
from models import TravelGroup, GroupInvitation, ChatMessage

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
    history = ChatMessage.query.filter_by(room_id=room_id).all()
    return render_template('chat.html', user=user_info, history=history, room=room)

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