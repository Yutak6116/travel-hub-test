from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from extensions import db
from models import TravelPlan, TravelPlanItem, AllTravelPlanItem, DeletedTravelPlanItem

plan_bp = Blueprint('plan', __name__)

import re

def extract_destinations_and_purposes(travel_plan_text):
    # 行ごとに分割
    lines = travel_plan_text.split('\n')
    
    n=0
    # 目的地と目的を格納するリスト
    destinations = []
    purposes = []
    
    # 行き先を抽出する正規表現パターン
    start_pattern = re.compile(r'\d+日目')
    end_pattern = re.compile(r'費用概算')
    
    # フラグを初期化
    recording = False
    
    for line in lines:
        # 「1日目」から「費用概算」までの行を記録
        if start_pattern.match(line):
            n += 1
            recording = True
            # 何日目かを抽出
            destinations.append(n)
            purposes.append(n)
            continue
        if end_pattern.match(line):
            break
        
        if recording:
            # 行き先と目的を抽出
            match = re.search(r'(.+?):\s*(.+)', line)
            if match:
                destinations.append(match.group(1).strip())
                purposes.append(match.group(2).strip())
    
    return destinations, purposes

# 関数get_all_place_id_in_travelplanitem を作る
# place_idを格納したあとのTravelPlanItemを返す。(query.all()で取得)

# 同様に、関数get_all_place_id_in_alltravelplanitem を作る

@plan_bp.route('/add_plan/<int:room_id>', methods=['POST'])
def add_plan(room_id):
    travel_plan_text = TravelPlan.query.filter_by(room_id=room_id).order_by(TravelPlan.id.desc()).first().markdown
    print(travel_plan_text)
    destination, purposes = extract_destinations_and_purposes(travel_plan_text)
    n = 0
    for i in range(len(destination)):
        if destination[i].isdecimal():
            n = int(destination[i])
            continue
        new_plan_item = TravelPlanItem(room_id=room_id, place_name=destination[i], description=purposes[i], date = n)
        new_all_plan_item = AllTravelPlanItem(room_id=room_id, place_name=destination[i], description=purposes[i])
        db.session.add(new_plan_item)
        db.session.add(new_all_plan_item)
    
    db.session.commit()
    
    travelplanitem = TravelPlanItem.query.filter_by(room_id=room_id).all()
    print(travelplanitem)
    
    alltravelplanitem = AllTravelPlanItem.query.filter_by(room_id=room_id).all()
    print(alltravelplanitem)
    
    return redirect('/chat/' + str(room_id))
    