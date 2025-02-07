from flask import Blueprint, redirect, url_for, session, request, render_template, flash
from flask_socketio import emit, join_room
from extensions import db, socketio
from models import TravelGroup, GroupInvitation, ChatMessage
from services.place_service import get_place_coordinates
import os

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
    message = data['message']
    
    # @map: から始まるメッセージの場合
    if message.startswith('@map:'):
        location = message[5:].strip()
        # 場所の緯度・経度を取得
        coordinates = get_place_coordinates(location)
        
        if coordinates:
            # Google Maps Embed API を使用して、地図を埋め込む
            map_url = f"https://www.google.com/maps/embed/v1/place?key=AIzaSyCBGzcVWp3SZFKS1TixOfBOgjkIuKtz_wM&q={coordinates['latitude']},{coordinates['longitude']}&zoom=15"
            # 地図の埋め込みコード
            map_html = f'<iframe width="100%" height="400" frameborder="0" style="border:0" src="{map_url}" allowfullscreen></iframe>'
            # メッセージを更新
            data['message'] = f"Location: {location}\n{map_html}"
        else:
            data['message'] = f"Could not find location: {location}"
    
    msg = ChatMessage(username=data['user'], message=data['message'], room_id=room)
    db.session.add(msg)
    db.session.commit()
    emit('receive_message', data, room=str(room))
