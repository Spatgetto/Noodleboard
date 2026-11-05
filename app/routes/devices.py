from flask import Blueprint, jsonify, request, url_for
from app import db    
from app.models import Device
from app.services.validators import is_valid_ip
from sqlalchemy.exc import IntegrityError

devices_bp = Blueprint("devices", __name__)

# GET /devices/ 
# Retrieves all devices
@devices_bp.route("/", methods=["GET"])
def get_devices():
    devices = Device.query.all()

    return jsonify([device.export_data() for device in devices])

# POST /devices/
# Creates a new device
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
        name = data["name"].strip(),
        vendor = data["vendor"].strip(),
        mgmt_address = data["mgmt_address"].strip()
    )

    db.session.add(device)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Database integrity constraint violated"}, 409

    return (
        {"message": "Device created successfully"}, 
        201, 
        {"Location": url_for("devices.get_device", device_id=device.device_id)}
    )

# GET /devices/<device_id>
# Retrieves a specific device by its ID
@devices_bp.route("/<int:device_id>", methods=["GET"])
def get_device(device_id):
    device = db.session.get(Device, device_id)
    if not device:
        return {"message": "Device not found"}, 404
    return device.export_data()

# PUT /devices/<device_id>
# Replaces/Updates a specific device by its ID
@devices_bp.route("/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    device = db.session.get(Device, device_id)
    if not device:
        return {"message": "Device not found"}, 404

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

    device.name = data["name"].strip()
    device.vendor = data["vendor"].strip()
    device.mgmt_address = data["mgmt_address"].strip()

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Database integrity constraint violated"}, 409

    return {"message": "Device updated successfully"}
    