from flask import Blueprint, render_template

from models import CandidateSite
from flask import Blueprint, redirect, url_for, session, request, render_template, flash
from extensions import db
from models import CandidateSite, AcceptedSchedule

map_bp = Blueprint("map", __name__)


def travel_plan_item_to_dict(item):
    return {
        "id": item.id,
        "room_id": item.room_id,
        "place_name": item.place_name,
        "description": item.description,
        "date": item.date,
        "place_id": item.place_id,
        "rating": item.rating,
        "order": item.order,
    }



def all_travel_plan_item_to_dict(item):
    return {
        "id": item.id,
        "room_id": item.room_id,
        "place_name": item.place_name,
        "description": item.description,
        "place_id": item.place_id,
        "rating": item.rating,
    }



@map_bp.route("/show_map/<int:room_id>")
def show_map(room_id):
    travel_plan_items = CandidateSite.query.filter_by(
        room_id=room_id, enable=True
    ).all()
    travel_plan_items_dict = [
        travel_plan_item_to_dict(item) for item in travel_plan_items
    ]
    all_travel_plan_items = CandidateSite.query.filter_by(room_id=room_id).all()
    all_travel_plan_items_dict = [
        all_travel_plan_item_to_dict(item) for item in all_travel_plan_items
    ]
    return render_template(
        "maps.html",
        room_id=room_id,
        travel_plan_items=travel_plan_items_dict,
        all_travel_plan_items=all_travel_plan_items_dict,
    )


@map_bp.route("/plan_list")
def plan_list():
    pass
