from flask import Blueprint, redirect, url_for, session, request, render_template, flash
from extensions import db
from models import TravelPlanItem, AllTravelPlanItem

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/show_map/<int:room_id>')
def show_map(room_id):
    # プランを取得
    travel_plan_items = TravelPlanItem.query.all()
    
    # 全てのプランを取得
    all_travel_plan_items = AllTravelPlanItem.query.all()
    
    return render_template('maps.html', 
                         travel_plan_items=travel_plan_items,
                         all_travel_plan_items=all_travel_plan_items,
                         room_id=room_id)

@plan_bp.route('/plan_list')
def plan_list():
    pass
