import ipaddress

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_device_data(data, partial=False):
    required_fields = {"name", "mgmt_address", "vendor"}

    if not isinstance(data, dict) or not data:
        return False

    if not data.keys() <= required_fields:
        return False

    if not partial and not required_fields <= data.keys():
        return False

    for field in ("name", "vendor"):
        if field in data:
            if not isinstance(data[field], str) or not data[field].strip():
                return False

    if "mgmt_address" in data:
        if not isinstance(data["mgmt_address"], str):
            return False
        if not is_valid_ip(data["mgmt_address"].strip()):
            return False

    return True