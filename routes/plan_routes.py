import re

from flask import Blueprint, jsonify, redirect, request

from extensions import db
from models import CandidateSite, CandidateSiteLike, Comment, User
from services.place_service import get_place_coordinates
import requests

plan_bp = Blueprint("plan", __name__)


def extract_destinations_and_purposes(travel_plan_text):
    """
    行き先と概要を正規表現で抽出する関数である。

    テキストから「行き先リスト」と「概要リスト」を正規表現で探し出し、
    それぞれの値をリストとして返す。

    Args:
        travel_plan_text (str): 解析対象の旅行プラン文字列

    Returns:
        tuple[list[str], list[str]]: (行き先リスト, 概要リスト) のタプル

    Examples:
        >>> # Python側での使用例
        >>> travel_plan = "行き先リスト:**[東京, 京都] 概要リスト:**[観光, グルメ]"
        >>> destinations, purposes = extract_destinations_and_purposes(travel_plan)

        <!-- JavaScriptから呼び出す場合の例 -->
        <script>
        fetch("/some_endpoint")
          .then(res => res.text())
          .then(text => {
            // 返ってきたテキストをPythonバックエンドに送信して解析するなど
          });
        </script>
    """
    destination_list = []
    purpose_list = []

    # 行き先リストを抽出する正規表現パターン
    destination_pattern = re.compile(r"行き先リスト:\*\*\[(.*?)\]")
    purpose_pattern = re.compile(r"概要リスト:\*\*\[(.*?)\]")

    destination_match = destination_pattern.search(travel_plan_text)
    purpose_match = purpose_pattern.search(travel_plan_text)

    if destination_match:
        destination_list = [
            item.strip() for item in destination_match.group(1).split(",")
        ]

    if purpose_match:
        purpose_list = [item.strip() for item in purpose_match.group(1).split(",")]

    return destination_list, purpose_list

import re
def extract_des_expl(text):

    # 最初の角括弧に一致する部分を非貪欲マッチで抽出
    matches = re.findall(r"\[(.*?)\]", text, re.DOTALL)
    if matches and len(matches) >= 2:
        # 1つ目の角括弧の中身をカンマで分割してリスト化
        destinations = [d.strip() for d in matches[0].split(",")]
        explanations = matches[1]
        return destinations, explanations
    else:
        return [], ""


# 手動で暫定候補地を追加
@plan_bp.route("/add_plan_manually/<int:room_id>", methods=["POST"])
def add_plan_manually(room_id):
    """
    候補地を手動で追加する関数である。

    ユーザーが入力フォームから送信した候補地と説明、座標をデータベースに保存し、
    チャット画面へリダイレクトする。

    Args:
        room_id (int): 追加対象のルームID

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- HTMLフォームから呼び出す例 -->
        <form method="POST" action="/candidate_site/42">
          <input type="text" name="place_name" value="新候補地">
          <input type="text" name="description" value="説明文">
          <button type="submit">追加</button>
        </form>
    """
    new_place_name = request.form.get("place_name")
    new_description = request.form.get("description")
    new_place_id = get_place_coordinates(new_place_name)
    print(new_place_id)
    new_plan_item = CandidateSite(
        user_id=request.args.get("user_id"),
        room_id=room_id,
        place_name=new_place_name,
        description=new_description,
        place_id=new_place_id,
    )
    db.session.add(new_plan_item)
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# 暫定的なプランから候補地を削除
@plan_bp.route("/delete_plan_item/<int:room_id>/<int:site_id>", methods=["POST"])
def delete_plan_item(room_id, site_id):
    """
    単一の候補地を削除する関数である。

    指定されたsite_idに対応するデータを探し、削除したうえでチャット画面にリダイレクトする。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 削除対象の候補地ID

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- JavaScript fetchで呼び出す例 -->
        <script>
        fetch("/candidate_site/42/100", {
          method: "DELETE"
        }).then(() => {
          window.location.reload();
        });
        </script>
    """
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    site.delete_by_user()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# 暫定的なプランを全て削除
@plan_bp.route("/delete_all_plan/<int:room_id>", methods=["DELETE"])
def delete_all_plan(room_id):
    """
    指定したルームのすべての候補地を削除する関数である。

    room_idに紐づく候補地をまとめて削除し、チャット画面へリダイレクトする。

    Args:
        room_id (int): 対象のルームID

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- JavaScript fetchで呼び出す例 -->
        <script>
        fetch("/candidate_site/42", {
          method: "DELETE"
        }).then(() => {
          window.location.href = "/chat/42";
        });
        </script>
    """
    sites = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.room_id == room_id)
    )
    if not sites:
        return redirect("/chat/" + str(room_id))
    for site in sites:
        site.delete_by_user()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# 削除された候補地を元に戻す
@plan_bp.route("/restore_deleted_plan_item/<int:room_id>/<int:site_id>/restore", methods=["POST"])
def restore_deleted_plan_item(room_id, site_id):
    """
    削除状態の候補地を元に戻す関数である。

    対象サイトが削除状態の場合に、それを復元しチャット画面へリダイレクトする。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 復元対象の候補地ID

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- HTMLフォームによる操作例 -->
        <form method="POST" action="/candidate_site/42/100/restore">
          <button type="submit">復元</button>
        </form>
    """
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    site.restore_by_user()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# いいねをトグル
@plan_bp.route(
    "/candidate_site/<int:room_id>/<int:site_id>/toggle_like", methods=["POST"]
)
def toggle_like(room_id, site_id):
    """
    候補地の「いいね」を切り替える関数である。

    ユーザーがすでにいいねをしていれば取り消し、していなければ新たにいいねをする。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 候補地のID

    Returns:
        JSONResponse: いいねの状態と新規のいいね数（liked/disliked, likeCount など）

    Examples:
        <!-- JS fetch例 -->
        <script>
        fetch("/candidate_site/42/100/toggle_like", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: new URLSearchParams({
            "user_id": "999"
          })
        })
          .then(res => res.json())
          .then(data => console.log(data));
        </script>
    """
    current_user_id = request.form.get("user_id")
    like_entry = CandidateSiteLike.query.filter_by(
        user_id=current_user_id, site_id=site_id
    ).first()
    site = CandidateSite.query.get(site_id)
    if not site:
        return jsonify({"error": "Site not found"}), 404

    if like_entry:
        # OFF
        db.session.delete(like_entry)
        site.like -= 1 if site.like > 0 else 0
        db.session.commit()
        return jsonify({"message": "disliked", "likeCount": site.like})
    else:
        # ON
        new_like = CandidateSiteLike(user_id=current_user_id, site_id=site_id)
        db.session.add(new_like)
        site.like += 1
        db.session.commit()
        return jsonify({"message": "liked", "likeCount": site.like})


# 候補地に対するいいね数を取得
@plan_bp.route(
    "/candidate_site/<int:room_id>/<int:site_id>/like_count", methods=["GET"]
)
def get_like_count(room_id, site_id):
    """
    候補地の「いいね」数を取得する関数である。

    候補地に対して現在いくつ「いいね」が付いているかを返す。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 候補地のID

    Returns:
        JSONResponse: likeCountを含むJSON

    Examples:
        <!-- JS fetch例 -->
        <script>
        fetch("/candidate_site/42/100/like_count")
          .then(res => res.json())
          .then(data => console.log("いいね数:", data.likeCount));
        </script>
    """
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return jsonify({"error": "Site not found"}), 404
    return jsonify({"likeCount": site.like})


# コメントを追加
@plan_bp.route("/candidate_site/<int:room_id>/<int:site_id>/comment", methods=["POST"])
def comment_plan_item(room_id, site_id):
    """
    候補地にコメントを追加する関数である。

    ユーザーIDとコメント内容を受け取り、該当候補地にコメントを追加して
    チャット画面へリダイレクトする。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 候補地のID

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- JS fetch例 -->
        <script>
        fetch("/candidate_site/42/100/comment", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: new URLSearchParams({
            "user_id": "999",
            "comment": "行きたい場所です！"
          })
        });
        </script>
    """
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    new_comment = Comment(
        user_id=request.form.get("user_id"),
        site_id=site_id,
        comment=request.form.get("comment"),
    )
    site.add_comment(new_comment)
    db.session.add(new_comment)
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# コメントを削除
@plan_bp.route(
    "/candidate_site/<int:room_id>/<int:site_id>/comment/<int:comment_id>",
    methods=["DELETE"],
)
def delete_comment_plan_item(room_id, site_id, comment_id):
    """
    候補地に紐づくコメントを削除する関数である。

    指定されたコメントIDのコメントを削除し、チャット画面へリダイレクトする。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 候補地のID
        comment_id (int): 削除するコメントのID

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- JS fetch例 -->
        <script>
        fetch("/candidate_site/42/100/comment/50", {
          method: "DELETE"
        }).then(() => {
          window.location.href = "/chat/42";
        });
        </script>
    """
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    comment = db.session.scalar(db.select(Comment).where(Comment.id == comment_id))
    if not comment:
        return redirect("/chat/" + str(room_id))
    site.delete_comment(comment)
    db.session.delete(comment)
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# 候補地の詳細情報を取得
@plan_bp.route("/get_site_detail/<int:room_id>/<int:site_id>", methods=["GET"])
def get_site_detail(room_id, site_id):
    """
    候補地の詳細情報を取得する関数である。

    候補地の基本情報およびコメントリストを取得し、JSON形式で返す。

    Args:
        room_id (int): 対象のルームID
        site_id (int): 候補地のID

    Returns:
        JSONResponse: 候補地情報（place_name, description, like など）とコメントリスト

    Examples:
        <!-- JS fetch例 -->
        <script>
        fetch("/candidate_site/42/100")
          .then(res => res.json())
          .then(data => {
            // data.place_name, data.description, data.comments などを利用
            console.log(data);
          });
        </script>
    """
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return jsonify({"error": "site not found"}), 404
    # コメントユーザー名取得用
    site_dict = site.to_dict()
    enriched_comments = []
    for c in site.comments:
        user_name = None
        user_obj = db.session.scalar(db.select(User).where(User.id == c.user_id))
        if user_obj:
            user_name = user_obj.name
        comment_data = c.to_dict()
        comment_data["user_name"] = user_name if user_name else "Unknown"
        enriched_comments.append(comment_data)
    site_dict["comments"] = enriched_comments
    return jsonify(site_dict)

# 旅行プランの確定
@plan_bp.route("/confirm_plan/<int:room_id>", methods=["POST"])
def confirm_plan(room_id):
    """
    旅行プランを確定する関数である。

    ユーザーが最終的に確定した旅行プランをデータベースに保存し、
    チャット画面へリダイレクトする。

    Args:
        room_id (int): 対象のルームID
        start_date (str): 旅行開始日
        end_date (str): 旅行終了日
        budget (int): 予算
        remarks (str): 備考
        候補地のリスト(dict): place_name, likes, comments

    Returns:
        Response: 処理完了後のリダイレクトレスポンス

    Examples:
        <!-- HTMLフォームから呼び出す例 -->
        <form method="POST" action="/confirm_plan/42">
          <button type="submit">確定</button>
        </form>
    """
    
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    start_location = request.form.get("start_location")
    budget = request.form.get("budget")
    remarks = request.form.get("remarks")
    # 候補地のリストを取得
    candidate_list = []
    candidate_sites = CandidateSite.query.filter_by(room_id=room_id, enable=True).all()
    for site in candidate_sites:
        place_name = site.place_name
        likes = site.like
        comments = [c.to_dict() for c in site.comments]
        site_dict = {
            "place_name": place_name,
            "likes": likes,
            "comments": comments,
        }
        candidate_list.append(site_dict)
    
    # 削除された候補地のリストを取得
    deleted_list = []
    deleted_sites = CandidateSite.query.filter_by(room_id=room_id, enable=False).all()
    for site in deleted_sites:
        place_name = site.place_name
        likes = site.like
        comments = [c.to_dict() for c in site.comments]
        site_dict = {
            "place_name": place_name,
            "likes": likes,
            "comments": comments,
        }
        deleted_list.append(site_dict)
    
    
    response = requests.post(
        "https://us-central1-goukan2house.cloudfunctions.net/root_help2",
        headers={"Content-Type": "application/json"},
        json={
            "start_date": start_date,
            "end_date": end_date,
            "start_location": start_location,
            "budget": budget,
            "remarks": remarks,
            "candidate_list": candidate_list,
            "deleted_list": deleted_list
        },
    )
    json={
            "start_date": start_date,
            "end_date": end_date,
            "start_location": start_location,
            "budget": budget,
            "remarks": remarks,
            "candidate_list": candidate_list,
            "deleted_list": deleted_list
        }
    print(json)
    if response.ok:
        data_json = response.json()
    else:
        print("Error", response.status_code, response.text)
    # 旅行プランの確定処理
    candidate_text = data_json["candidates"][0]["content"]["parts"][0]["text"]

    reply_text = candidate_text.strip()
            
    print(reply_text)
    
    destinations, purposes = extract_destinations_and_purposes(reply_text)
    
    print(destinations)
    print(purposes)
    
    return destinations, purposes
    
