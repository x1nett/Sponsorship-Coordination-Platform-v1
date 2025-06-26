from .extensions import db, categories
from .models import Campaign
import re
from datetime import date, datetime

def validate_campaign(name, description, start_date, end_date, category, budget, visibility, goals):
    # Check if all fields are filled
    if not name or not description or not start_date or not end_date or not category or not budget or not goals or not visibility: return False, "All fields are required"
    # Check if name, description, goals are not too long
    if len(name) > 45 or len(description) > 250 or len(goals) > 250: return False, "Name, Description and Goals should be less than 250 characters"
    # Check if start date is before end date
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    if start_date > end_date: return False, "Start date should be before end date"
    # Check if category is valid
    if category not in categories: return False, "Invalid category"
    # Check if budget is a number
    if not re.search(r'^\d+(\.\d+)?$', budget): return False, "Budget should be a number"
    # Check if visibility is valid
    if visibility not in ["Public", "Private"]: return False, "Invalid visibility"
    return True, ""

def validate_budget(payment_amount, id):
    # Check if payment amount is less than or equal to budget
    campaign = get_campaign(id)
    if payment_amount > campaign.remaining: return False
    return True

def create_campaign(sponsor_id, name, description, start_date, end_date, category, budget, visibility, goals):
    # Create campaign
    created = date.today()
    campaign = Campaign(sponsor_id=sponsor_id, name=name, description=description, start_date=start_date, 
                        end_date=end_date, category=category, budget=budget, remaining=budget, visibility=visibility, goals=goals,
                        created_on=created)
    db.session.add(campaign)
    db.session.commit()
    return campaign

def get_campaign(campaign_id):
    # Get campaign
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    return campaign

def update_campaign(campaign_id, params):
    # Update campaign
    campaign = get_campaign(campaign_id)
    for key in params:
        if not params[key]: continue
        if key == "budget" and float(params[key]) != campaign.budget:
            campaign.remaining = float(params[key]) - (campaign.budget - campaign.remaining)
        if key == "remaining":
            campaign.remaining = campaign.remaining - float(params[key])
            continue
        setattr(campaign, key, params[key])
    db.session.commit()
    return campaign

def delete_campaign(campaign_id):
    # Delete campaign
    campaign = get_campaign(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    return campaign

def get_campaigns(page):
    # Get all campaigns
    if page == -1:
        # Pagination bypass, incase all campaigns are required
        campaigns = Campaign.query.all()
        return campaigns
    campaigns = Campaign.query.paginate(page=page, per_page=5, error_out=False)
    return campaigns

def get_sponsor_campaigns(sponsor_id, page):
    # Get campaigns associated with sponsor
    if page == -1:
        # Pagination bypass, incase all campaigns are required
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
        return campaigns
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).paginate(page=page, per_page=5, error_out=False)
    return campaigns

def search_campaign(name, budget, category, page):
    # Search via name
    campaigns = Campaign.query.filter_by(visibility="Public").filter(Campaign.ad_requests.any())
    if category: campaigns = campaigns.filter_by(category=category)
    if name: campaigns = Campaign.query.filter(Campaign.name.like('%' + name + '%'))
    # Sort based on budget
    if budget == "Descending":
        campaigns = campaigns.order_by(Campaign.budget.desc())
    elif budget == "Ascending":
        campaigns = campaigns.order_by(Campaign.budget.asc())
    campaigns = campaigns.paginate(page=page, per_page=5, error_out=False)
    return campaigns