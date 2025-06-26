from .extensions import db
from .models import Ad_request
from datetime import date
import re

def validate_ad_request(messages, requirements, payment_amount, status = None):
    # Check if all fields are filled
    if not messages or not requirements or not payment_amount: return False, "All fields are required"
    # Check if messages, requirements are not too long
    if len(messages) > 250 or len(requirements) > 250: return False, "Messages and Requirements should be less than 250 characters"
    # Check if payment amount is a number
    if not re.search(r'^\d+(\.\d+)?$', payment_amount): return False, "Payment amount should be a number"
    # Check if status is valid
    if status and status not in ["Pending", "Accept", "Reject"]: return False, "Invalid status"
    return True, ""

def create_ad_request(messages, requirements, payment_amount, status, negotiate, campaign_id, influencer_id = None):
    # Create ad request
    # Influencer_id is optional, empty ad requests which will be filled by influencers
    created = date.today()
    ad_request = Ad_request(campaign_id=campaign_id, influencer_id=influencer_id, messages=messages, requirements=requirements,
                            payment_amount=payment_amount, status=status, negotiate=negotiate, created_on=created)
    db.session.add(ad_request)
    db.session.commit()
    return ad_request

def get_ad_request(ad_request_id):
    # Get ad request
    ad_request = Ad_request.query.filter_by(id=ad_request_id).first()
    return ad_request

def update_ad_request(ad_request_id, params):
    # Update ad request
    print(ad_request_id)
    ad_request = get_ad_request(ad_request_id)
    for key in params:
        if not params[key]: continue
        if key == "status" and params[key] == "Accept":
            ad_request.accepted_on = date.today()
        elif key == "status" and params[key] == "Reject":
            ad_request.rejected_on = date.today()
        setattr(ad_request, key, params[key])
    db.session.commit()
    return ad_request

def delete_ad_request(ad_request_id):
    # Delete ad request
    ad_request = get_ad_request(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    return ad_request

def get_ad_requests(page):
    # Get all ad requests
    if page == -1:
        # Pagination bypass, incase all Ad Requests are required
        ad_requests = Ad_request.query.all()
        return ad_requests
    ad_requests = Ad_request.query.paginate(page=page, per_page=5, error_out=False)
    return ad_requests

def get_campaign_ad_requests(campaign_id, page):
    # Get ad requests associated with campaign
    if page == -1:
        # Pagination bypass, incase all Ad Requests are required
        ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(campaign_id)).all()
        return ad_requests
    ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(campaign_id)).paginate(page=page, per_page=5, error_out=False)
    return ad_requests

def get_influencer_ad_requests(influencer_id, page):
    # Get ad requests associated with influencer
    if page == -1:
        # Pagination bypass, incase all Ad Requests are required
        ad_requests = Ad_request.query.filter_by(influencer_id=influencer_id).all()
        return ad_requests
    ad_requests = Ad_request.query.filter_by(influencer_id=influencer_id).paginate(page=page, per_page=5, error_out=False)
    return ad_requests