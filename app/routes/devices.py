from flask import Blueprint, jsonify, request
from app import db    
from app.models import Device
from app.services.validators import is_valid_ip
from sqlalchemy.exc import IntegrityError

devices_bp = Blueprint("devices", __name__)

@devices_bp.route("/", methods=["GET"])
def get_devices():
    devices = Device.query.all()

    return jsonify([device.export_data() for device in devices])

@devices_bp.route("/", methods=["POST"])
def create_device():
    data = request.get_json()

    if not data or not all(
        field in data
        for field in ("name", "mgmt_address", "vendor")
    ):
        return {"message": "Invalid request body"}, 400
    
    for field in ("name", "vendor"):
        if not isinstance(data[field], str) or not data[field].strip():
            return {"message": f"Invalid {field}"}, 400

    if not isinstance(data["mgmt_address"], str) or not is_valid_ip(data["mgmt_address"]):
        return {"message": "Invalid management IP address"}, 400

    device = Device(
        name=data["name"],
        mgmt_address=data["mgmt_address"],
        vendor=data["vendor"]
    )

    db.session.add(device)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Database integrity constraint violated"}, 409

    return {"message": "Device created successfully"}, 201
    
@devices_bp.route("/<int:device_id>", methods=["GET"])
def get_device(device_id):
    device = db.session.get(Device, device_id)
    if not device:
        return {"message": "Device not found"}, 404
    return device.export_data()