import re

from flask import Blueprint, redirect, request

from extensions import db
from models import CandidateSite, Comment
from services.place_service import get_place_coordinates

plan_bp = Blueprint("plan", __name__)


def extract_destinations_and_purposes(travel_plan_text):
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


# 関数get_all_place_id_in_travelplanitem を作る
# place_idを格納したあとのTravelPlanItemを返す。(query.all()で取得)

# 同様に、関数get_all_place_id_in_alltravelplanitem を作


# NEED
# @plan_bp.route('/add_plan/<int:room_id>', methods=['POST'])
# def add_plan(room_id):
#     travel_plan_text = TravelPlan.query.filter_by(room_id=room_id).order_by(TravelPlan.id.desc()).first().markdown
#     destinations, purposes = extract_destinations_and_purposes(travel_plan_text)
#     # TravelPlanItemのroom_id=room_idのデータを削除
#     TravelPlanItem.query.filter_by(room_id=room_id).delete()
#     n = 0
#     t = 0   #何番目に行くか
#     for i in range(len(destinations)):
#         if str(destinations[i]).isdecimal():
#             n = int(destinations[i])
#             continue
#         new_place_id = get_place_coordinates(destinations[i])
#         new_plan_item = TravelPlanItem(
#             room_id=room_id,
#             place_name=destinations[i],
#             description=purposes[i],
#             date = n, place_id =
#             new_place_id,
#             order=t
#             )
#         # すでにリストに追加されている候補地は入れない
#         if AllTravelPlanItem.query.filter_by(room_id=room_id, place_name=destinations[i]).first():
#             continue
#         new_all_plan_item = AllTravelPlanItem(
#             room_id=room_id,
#             place_name=destinations[i],
#             description=purposes[i],
#             place_id = new_place_id)
#         db.session.add(new_plan_item)
#         db.session.add(new_all_plan_item)
#         t += 1

#     db.session.commit()


# 手動で暫定候補地を追加
@plan_bp.route("/candidate_site/<int:room_id>", methods=["POST"])
def add_plan_manually(room_id):
    new_place_name = request.form.get("place_name")
    new_description = request.form.get("description")
    new_place_id = get_place_coordinates(new_place_name)
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
@plan_bp.route("/candidate_site/<int:room_id>/<int:site_id>", methods=["DELETE"])
def delete_plan_item(room_id, site_id):
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    site.delete_by_user()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# 暫定的なプランを全て削除
@plan_bp.route("/candidate_site/<int:room_id>", methods=["DELETE"])
def delete_all_plan(room_id):
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
@plan_bp.route("/candidate_site/<int:room_id>/<int:site_id>/restore", methods=["POST"])
def restore_deleted_plan_item(room_id, site_id):
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    site.restore_by_user()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# いいねを追加
@plan_bp.route("/candidate_site/<int:room_id>/<int:site_id>/like", methods=["POST"])
def like_plan_item(room_id, site_id):
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    site.add_like()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# いいねを取り消す
@plan_bp.route("/candidate_site/<int:room_id>/<int:site_id>/dislike", methods=["POST"])
def dislike_plan_item(room_id, site_id):
    site = db.session.scalar(
        db.select(CandidateSite).where(CandidateSite.id == site_id)
    )
    if not site:
        return redirect("/chat/" + str(room_id))
    site.delete_like()
    db.session.commit()
    return redirect("/chat/" + str(room_id))


# コメントを追加
@plan_bp.route("/candidate_site/<int:room_id>/<int:site_id>/comment", methods=["POST"])
def comment_plan_item(room_id, site_id):
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
