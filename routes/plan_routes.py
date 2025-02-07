from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from extensions import db
from models import TravelPlanItem, AllTravelPlanItem, DeletedTravelPlanItem

plan_bp = Blueprint('plan', __name__)

import re

def extract_destinations(travel_plan_text):
    # 行ごとに分割
    lines = travel_plan_text.split('\n')
    
    # 行き先を格納するリスト
    destinations = []
    
    # 行き先を抽出する正規表現パターン
    pattern = re.compile(r'^\d+日目|^移動手段|^予算|^場所|^会話の要約|^旅行プラン')
    
    for line in lines:
        # 行が日付や移動手段、予算、場所のセクションで始まる場合はスキップ
        if pattern.match(line):
            continue
        
        # 行き先を抽出
        match = re.search(r'([^\s]+)(で|に|の|へ|から)', line)
        if match:
            destinations.append(match.group(1))
    
    return destinations

# 関数get_all_place_id_in_travelplanitem を作る
# place_idを格納したあとのTravelPlanItemを返す。(query.all()で取得)

# 同様に、関数get_all_place_id_in_alltravelplanitem を作る

@plan_bp.route('/add_plan', methods=['POST'])
def add_plan():
    
    
    
    
    
    