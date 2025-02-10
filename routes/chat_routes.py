import markdown
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import re
from flask_socketio import emit, join_room

from extensions import db, socketio
from models import ChatMessage, GroupInvitation, TravelGroup, AISuggest, User, CandidateSite
from services.place_service import get_place_coordinates

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat/<int:room_id>")
def chat(room_id):
    if "google_id" not in session:
        return redirect(url_for("oauth.index"))
    room = TravelGroup.query.get_or_404(room_id)
    current_user_id = session.get("user_id")
    current_email = session.get("email")
    # 作成者ならアクセス可能、または招待されている場合
    has_access = room.creator_user_id == current_user_id
    invited = GroupInvitation.query.filter_by(
        group_id=room_id, invited_email=current_email
    ).first()
    if not (has_access or invited):
        flash("このルームへの参加権がありません。")
        return redirect(url_for("group.travels"))
    user_info = {
        "name": session.get("name"),
        "email": current_email,
        "id": current_user_id,
    }
    history_objs = ChatMessage.query.filter_by(room_id=room_id).all()
    history = []
    for msg in history_objs:
        msg_html = markdown.markdown(msg.message)
        history.append({"username": msg.username, "message": msg_html})
    # 追加：候補地一覧（enable=True のもの）を取得する
    from models import CandidateSite  # インポートを必要に応じて

    candidate_sites = (
        CandidateSite.query.filter_by(room_id=room_id, enable=True)
        .order_by(CandidateSite.id.desc())
        .all()
    )
    return render_template(
        "chat.html",
        user=user_info,
        history=history,
        room=room,
        candidate_sites=candidate_sites,
    )


@socketio.on("join")
def handle_join(data):
    room = data["room"]
    join_room(room)


@socketio.on("send_message")
def handle_send_message(data):
    room = data.get("room")
    message = data.get("message")
    user_id = session.get("user_id")
    msg = ChatMessage(user_id=user_id, message=message, room_id=room)
    db.session.add(msg)
    db.session.commit()
    emit("receive_message", data, room=str(room))

   #  todo: AIの返信を追加
    if "@AI" in data.get("message", ""):
        # まず「Loading」と表示
        loading_msg = {"room": room, "user": "travel AI", "message": "Loading"}
        if User.query.filter_by(name="travel AI").first() is None:
            ai = User(name="travel AI")
        emit("receive_message", loading_msg, room=str(room))
        ai_loading = ChatMessage(username="travel AI", message="Loading", room_id=room)
        db.session.add(ai_loading)
        db.session.commit()

        # ルームのチャット履歴を取得（昇順）
        conversation_objs = (
            ChatMessage.query.filter_by(room_id=room).order_by(ChatMessage.id).all()
        )
        conversation = ""
        for m in conversation_objs:
            conversation += f"{m.username}: {m.message}\n"

        # Cloud Function へPOSTリクエスト送信
        response = requests.post(
            "https://us-central1-goukan2house.cloudfunctions.net/travel_helper",
            headers={"Content-Type": "application/json"},
            json={"conversation": conversation},
        )
        if response.ok:
            # JSONから候補の返信部分のみ抽出
            data_json = response.json()
            candidate_text = data_json["candidates"][0]["content"]["parts"][0]["text"]

            reply_text = candidate_text.strip()
            ai_data = {"room": room, "user": "travel AI", "message": reply_text}
            # DBに最終的なチャットメッセージとして保存
            ai_msg = ChatMessage(username="travel AI", message=reply_text, room_id=room)
            db.session.add(ai_msg)
            if "旅行プラン" in reply_text:
                travel_plan = AISuggest(room_id=room, markdown=reply_text)
                db.session.add(travel_plan)
                destination, explanation = chat_message_to_dict(reply_text)
                if destination:
                    for i in len(destination):
                        place_id = get_place_coordinates(destination[i])
                        site = CandidateSite(
                            user_id=user_id,
                            place_name=destination[i],
                            description=explanation[i],
                            room_id=room,
                            place_id=place_id,
                        )
                        db.session.add(site)
            db.session.commit()
            
            
            redirect(url_for("chat.chat", room_id=room))
        else:
            # エラーハンドリング（必要に応じて）
            pass

def chat_message_to_dict(text):
    matches = re.findall(r"\[(.*?)\]", text, re.DOTALL)
    if matches and len(matches) >= 2:
        # 1つ目の角括弧の中身をカンマで分割してリスト化
        destinations = [d.strip() for d in matches[0].split(",")]
        explanations = matches[1]
        return destinations, explanations
    else:
        return []


@chat_bp.route("/invite/<int:room_id>", methods=["POST"])
def chat_invite(room_id):
    if "google_id" not in session:
        return jsonify({"error": "認証が必要です"}), 401

    invite_email = request.form.get("invite_email")
    if not invite_email:
        return jsonify({"error": "メールアドレスが必要です"}), 400

    # 既存の招待情報との重複をチェック
    existing_invitation = GroupInvitation.query.filter_by(
        group_id=room_id, invited_email=invite_email
    ).first()
    if existing_invitation:
        return jsonify({"error": "既に招待済みです"}), 400

    invitation = GroupInvitation(
        group_id=room_id, invited_email=invite_email, status="pending"
    )
    db.session.add(invitation)
    db.session.commit()
    return jsonify({"success": True}), 200
