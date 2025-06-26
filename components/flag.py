from .extensions import db
from .models import Flagged
from datetime import date

def validate_flag(type, type_id, reason):
    # Check if all fields are filled
    if not type or not type_id or not reason: return False, "All fields are required"
    # Check if type is valid
    if type not in ["Sponsor", "Influencer"]: return False, "Invalid type"
    return True, ""

def create_flag(type, type_id, reason):
    # Create flag
    created = date.today()
    flag = Flagged(type=type, type_id=type_id, reason=reason, created_on=created)
    db.session.add(flag)
    db.session.commit()
    return flag

def get_flag(type_id, type):
    # Get flag
    flag = Flagged.query.filter_by(type_id=type_id, type=type).first()
    return flag

def delete_flag(type, type_id):
    # Delete flag
    flag = get_flag(type_id, type)
    if flag.type != type: return None
    db.session.delete(flag)
    db.session.commit()
    return flag

def get_flags(page):
    # Get all flags
    if page == -1:
        flags = Flagged.query.all()
        return flags
    flags = Flagged.query.paginate(page=page, per_page=5, error_out=False)
    return flags