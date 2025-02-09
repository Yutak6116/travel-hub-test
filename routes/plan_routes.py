from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from extensions import db
from models import TravelPlan, TravelPlanItem, AllTravelPlanItem, DeletedTravelPlanItem
from services.place_service import get_place_coordinates

plan_bp = Blueprint('plan', __name__)

import re

def extract_destinations_and_purposes(travel_plan_text):
    destination_list = []
    purpose_list = []
    
    # 行き先リストを抽出する正規表現パターン
    destination_pattern = re.compile(r'行き先リスト:\*\*\[(.*?)\]')
    purpose_pattern = re.compile(r'概要リスト:\*\*\[(.*?)\]')
    
    destination_match = destination_pattern.search(travel_plan_text)
    purpose_match = purpose_pattern.search(travel_plan_text)
    
    if destination_match:
        destination_list = [item.strip() for item in destination_match.group(1).split(',')]
    
    if purpose_match:
        purpose_list = [item.strip() for item in purpose_match.group(1).split(',')]
        
    print(destination_list, purpose_list)
    
    return destination_list, purpose_list

# 関数get_all_place_id_in_travelplanitem を作る
# place_idを格納したあとのTravelPlanItemを返す。(query.all()で取得)

# 同様に、関数get_all_place_id_in_alltravelplanitem を作る

@plan_bp.route('/add_plan/<int:room_id>', methods=['POST'])
def add_plan(room_id):
    travel_plan_text = TravelPlan.query.filter_by(room_id=room_id).order_by(TravelPlan.id.desc()).first().markdown
    destinations, purposes = extract_destinations_and_purposes(travel_plan_text)
    # TravelPlanItemのroom_id=room_idのデータを削除
    TravelPlanItem.query.filter_by(room_id=room_id).delete()
    n = 0
    t = 0   #何番目に行くか
    for i in range(len(destinations)):
        if str(destinations[i]).isdecimal():
            n = int(destinations[i])
            continue
        new_place_id = get_place_coordinates(destinations[i])
        new_plan_item = TravelPlanItem(
            room_id=room_id, 
            place_name=destinations[i], 
            description=purposes[i], 
            date = n, place_id = 
            new_place_id, 
            order=t
            )
        # すでにリストに追加されている候補地は入れない
        if AllTravelPlanItem.query.filter_by(room_id=room_id, place_name=destinations[i]).first():
            continue
        new_all_plan_item = AllTravelPlanItem(
            room_id=room_id, 
            place_name=destinations[i], 
            description=purposes[i], 
            place_id = new_place_id)
        db.session.add(new_plan_item)
        db.session.add(new_all_plan_item)
        t += 1
    
    db.session.commit()

    return redirect('/chat/' + str(room_id))

# 暫定的なプランから候補地を削除
@plan_bp.route('/delete_plan/<int:room_id>/<int:id>', methods=['POST'])
#　一つの旅行で複数回行く候補地があることも考慮し、idを引数にする
def delete_plan_item(room_id,id):
    # TravelPlanItemのデータを削除
    TravelPlanItem.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect('/chat/' + str(room_id))

# すべての候補地から候補地を削除
@plan_bp.route('/delete_from_all_plan_item/<int:room_id>', methods=['POST'])
def delete_from_all_plan_item(room_id, place_name):
    # AllTravelPlanItemのデータを削除
    AllTravelPlanItem.query.filter_by(room_id=room_id, place_name=place_name).delete()
    new_deleted_plan = DeletedTravelPlanItem(room_id=room_id, place_name=place_name)
    db.session.add(new_deleted_plan)
    db.session.commit()

    return redirect('/chat/' + str(room_id))

# 削除された候補地を元に戻す
@plan_bp.route('/restore_deleted_plan_item/<int:room_id>', methods=['POST'])
def restore_deleted_plan_item(room_id, place_name):
    # DeletedTravelPlanItemのデータを削除
    DeletedTravelPlanItem.query.filter_by(room_id=room_id, place_name=place_name).delete()
    new_all_plan_item = AllTravelPlanItem.query.filter_by(room_id=room_id, place_name=place_name).first()
    db.session.add(new_all_plan_item)
    db.session.commit()

    return redirect('/chat/' + str(room_id))

@plan_bp.route('/delete_all_plan/<int:room_id>', methods=['POST'])
def delete_all_plan(room_id):
    # TravelPlanItemのデータを削除
    TravelPlanItem.query.filter_by(room_id=room_id).delete()
    db.session.commit()

    return redirect('/chat/' + str(room_id))

# 手動で暫定候補地を追加
@plan_bp.route('/add_plan_manually/<int:room_id>', methods=['POST'])
def add_plan_manually(room_id):
    new_place_name = request.form.get('place_name')
    new_description = request.form.get('description')
    new_place_id = get_place_coordinates(new_place_name)
    new_plan_item = TravelPlanItem(
        room_id=room_id, 
        place_name=new_place_name, 
        description=new_description, 
        place_id=new_place_id, 
        order=0
    )
    new_all_plan_item = AllTravelPlanItem(
        room_id=room_id, 
        place_name=new_place_name, 
        description=new_description, 
        place_id=new_place_id
    )
    db.session.add(new_plan_item)
    db.session.add(new_all_plan_item)
    db.session.commit()

    return redirect('/chat/' + str(room_id))

# 手動で全候補地に追加
@plan_bp.route('/add_all_plan_manually/<int:room_id>', methods=['POST'])
def add_all_plan_manually(room_id):
    new_place_name = request.form.get('place_name')
    new_description = request.form.get('description')
    new_place_id = get_place_coordinates(new_place_name)
    new_all_plan_item = AllTravelPlanItem(
        room_id=room_id, 
        place_name=new_place_name, 
        description=new_description, 
        place_id=new_place_id
    )
    db.session.add(new_all_plan_item)
    db.session.commit()

    return redirect('/chat/' + str(room_id))