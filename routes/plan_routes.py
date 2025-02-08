from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from extensions import db
from models import TravelPlan, TravelPlanItem, AllTravelPlanItem, DeletedTravelPlanItem

plan_bp = Blueprint('plan', __name__)

import re

def extract_destinations_and_purposes(travel_plan_text):
    # 行ごとに分割
    lines = travel_plan_text.split('\n')
    
    n = 0
    # 目的地と目的を格納するリスト
    destinations = []
    purposes = []
    
    # 行き先を抽出する正規表現パターン
    start_pattern = re.compile(r'\*{0,2}\d+日目\*{0,2}')
    end_pattern = re.compile(r'\*{0,2}費用概算\*{0,2}')
    
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

        # コロンが半角、全角のいずれかをAIが出力するので、それらに対応する正規表現を用意
        if recording:
            # 行き先と目的を抽出
            match = re.search(r'(.+?)：\s*(.+)', line)
            if match:
                destination = re.sub(r'^[\*\-\s]+', '', match.group(1).strip())
                purpose = re.sub(r'^[\*\s]+', '', match.group(2).strip())
                destinations.append(destination)
                purposes.append(purpose)
            
            if not match:
                match = re.search(r'(.+?):\s*(.+)', line)
                if match:
                    destination = re.sub(r'^[\*\-\s]+', '', match.group(1).strip())
                    purpose = re.sub(r'^[\*\s]+', '', match.group(2).strip())
                    destinations.append(destination)
                    purposes.append(purpose)
                    
    return destinations, purposes

# 関数get_all_place_id_in_travelplanitem を作る
# place_idを格納したあとのTravelPlanItemを返す。(query.all()で取得)

# 同様に、関数get_all_place_id_in_alltravelplanitem を作る

@plan_bp.route('/add_plan/<int:room_id>', methods=['POST'])
def add_plan(room_id):
    travel_plan_text = TravelPlan.query.filter_by(room_id=room_id).order_by(TravelPlan.id.desc()).first().markdown
    print(travel_plan_text)
    destination, purposes = extract_destinations_and_purposes(travel_plan_text)
    # TravelPlanItemのroom_id=room_idのデータを削除
    TravelPlanItem.query.filter_by(room_id=room_id).delete()
    n = 0
    for i in range(len(destination)):
        if str(destination[i]).isdecimal():
            n = int(destination[i])
            continue
        new_plan_item = TravelPlanItem(room_id=room_id, place_name=destination[i], description=purposes[i], date = n)
        new_all_plan_item = AllTravelPlanItem(room_id=room_id, place_name=destination[i], description=purposes[i])
        db.session.add(new_plan_item)
        db.session.add(new_all_plan_item)
    
    db.session.commit()

    return redirect('/chat/' + str(room_id))
    