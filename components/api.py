from .user import *
from .campaign import *
from .ad_request import *
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

# Register the routes
@api.route('/api/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    if request.method == 'GET':
        user_id = request.args.get('id')
        user_email = request.args.get('email')
        if not user_id and not user_email: return jsonify({"error": "No User Id or email provided"}), 400
        if user_id == 1: return jsonify({"error": "Invalid User Id"}), 400
        if user_id: user = get_user(None, user_id)
        if user_email == "admin@gmail.com": return jsonify({"error": "Invalid User Email"}), 400
        if user_email: user = get_user(user_email)
        user = {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "industry": user.industry, "reach": user.reach, "category": user.category}
        return jsonify(user), 200
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        industry = request.form.get('industry')
        reach = request.form.get('reach')
        category = request.form.get('category')
        valid, message = validate_form(name, email, password, password, role, reach, industry, category)
        if not valid: return jsonify({"error": message}), 400
        user = create_user(name, email, password, role, industry, reach, category)
        user = {"User": {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "industry": user.industry, "reach": user.reach, "category": user.category}, "message": "User Created Successfully"}
        return jsonify(user), 201
    elif request.method == 'PUT':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email and not password: return jsonify({"error": "Email and Password not provided"}), 400
        user = get_user(email)
        if not user or user.id == 1: return jsonify({"error": "Invalid user"}), 400
        name = request.form.get('name', user.name)
        cpass = request.form.get('change_password', password)
        industry = request.form.get('industry', user.industry)
        reach = request.form.get('reach', user.reach)
        category = request.form.get('category', user.category)
        valid, message = validate_form(name, email, cpass, cpass, user.role, reach, industry, category)
        user = update_user(email, {"name": name, "industry": industry, "reach": reach, "category": category, "password": cpass})
        user = {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "industry": user.industry, "reach": user.reach, "category": user.category}
        user = {"User": user, "message": "User Updated Successfully"}
        return jsonify(user), 200
    elif request.method == 'DELETE':
        email = request.args.get('email')
        password = request.args.get('password')
        if not email and not password: return jsonify({"error": "Email and Password not provided"}), 400
        user = validate_user(email, password)
        if user.id != 1: return jsonify({"error": "Invalid user"}), 400
        del_email = request.args.get('delete_email')
        del_id = request.args.get('id')
        if not del_email and not del_id: return jsonify({"error": "No User Id or email provided"}), 400
        if del_id and del_id == 1: return jsonify({"error": "Invalid User Id"}), 400
        if del_email and del_email == "admin@gmail.com": return jsonify({"error": "Invalid User Email"}), 400
        if del_id: delete_user(get_user(None, del_id).email)
        if del_email: delete_user(del_email)
        return jsonify({"message": "Deleted User Successfully"}), 200

@api.route('/api/users', methods=['GET'])
def users():
    users = get_users(-1)
    users_t = []
    for user in users:
        if user.id == 1: continue
        user = {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "industry": user.industry, "reach": user.reach, "category": user.category}
        users_t.append(user)
    return jsonify(users), 200

@api.route('/api/campaign', methods=['GET', 'POST', 'PUT', 'DELETE'])
def campaign():
    if request.method == 'GET':
        campaign_id = request.args.get('id')
        if not campaign_id: return jsonify({"error": "No Campaign Id provided"}), 400
        campaign = get_campaign(campaign_id)
        campaign.sponor_name = get_user(None, campaign.sponsor_id).name
        campaign = {"id": campaign.id, "sponsor": campaign.sponsor_name, "name": campaign.name, "description": campaign.description, "goals": campaign.goals, 
                    "category": campaign.category, "budget": campaign.budget, "remaining": campaign.remaining, "visibility": campaign.visibility, 
                    "start_date": campaign.start_date, "end_date": campaign.end_date}
        return jsonify(campaign), 200
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email and not password: return jsonify({"error": "Email and Password not provided"}), 400
        sponsor = validate_user(email, password)
        if not sponsor or sponsor.role != "Sponsor": return jsonify({"error": "Invalid User"}), 400
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        category = request.form.get('category')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        goals = request.form.get('goals')
        valid, message = validate_campaign(name, description, start_date, end_date, category, budget, visibility, goals)
        if not valid: return jsonify({"error": message}), 400
        campaign = create_campaign(sponsor.id, name, description, start_date, end_date, category, budget, visibility, goals)
        campaign = {"Campaign":{"id": campaign.id, "sponsor": sponsor.name, "name": campaign.name, "description": campaign.description, "goals": campaign.goals, 
                    "category": campaign.category, "budget": campaign.budget, "remaining": campaign.remaining, "visibility": campaign.visibility, 
                    "start_date": campaign.start_date, "end_date": campaign.end_date}, "message": "Campaign Created Successfully"}
        return jsonify(campaign), 201
    elif request.method == 'PUT':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email and not password: return jsonify({"error": "Email and Password not provided"}), 400
        sponsor = validate_user(email, password)
        if not sponsor or sponsor.role != "Sponsor": return jsonify({"error": "Invalid User"}), 400
        campaign_id = request.form.get('id')
        if not campaign_id: return jsonify({"error": "No Campaign Id provided"}), 400
        campaign = get_campaign(campaign_id)
        if not campaign: return jsonify({"error": "Invalid Campaign Id"}), 400
        name = request.form.get('name', campaign.name)
        description = request.form.get('description', campaign.description)
        start_date = request.form.get('start_date', campaign.start_date)
        end_date = request.form.get('end_date', campaign.end_date)
        category = request.form.get('category', campaign.category)
        budget = request.form.get('budget', campaign.budget)
        visibility = request.form.get('visibility', campaign.visibility)
        goals = request.form.get('goals', campaign.goals)
        valid, message = validate_campaign(name, description, start_date, end_date, category, budget, visibility, goals)
        if not valid: return jsonify({"error": message}), 400
        campaign = update_campaign(campaign_id, {"name": name, "description": description, "start_date": start_date, "end_date": end_date, "category": category, "budget": budget, "visibility": visibility, "goals": goals})
        campaign = {"Campaign": {"id": campaign.id, "sponsor": sponsor.name, "name": campaign.name, "description": campaign.description, "goals": campaign.goals, 
                    "category": campaign.category, "budget": campaign.budget, "remaining": campaign.remaining, "visibility": campaign.visibility, 
                    "start_date": campaign.start_date, "end_date": campaign.end_date}, "message": "Campaign Updated Successfully"}
        return jsonify(campaign), 200
    elif request.method == 'DELETE':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email and not password: return jsonify({"error": "Email and Password not provided"}), 400
        sponsor = validate_user(email, password)
        if not sponsor or sponsor.role not in ["Sponsor", "Admin"]: return jsonify({"error": "Invalid User"}), 400
        campaign_id = request.form.get('id')
        if not campaign_id: return jsonify({"error": "No Campaign Id provided"}), 400
        campaign = get_campaign(campaign_id)
        if not campaign: return jsonify({"error": "Invalid Campaign Id"}), 400
        ad_requests = get_campaign_ad_requests(campaign_id, -1)
        for ad_request in ad_requests:
            delete_ad_request(ad_request.id)
        delete_campaign(campaign_id)
        return jsonify({"message": "Deleted Campaign and associated Ad Requests Successfully"}), 200
    
@api.route('/api/campaigns', methods=['GET'])
def campaigns():
    campaigns = get_campaigns(-1)
    campaigns_t = []
    for campaign in campaigns:
        if campaign.visibility == "Private": continue
        campaign = {"id": campaign.id, "name": campaign.name, "description": campaign.description, "goals": campaign.goals, 
                    "category": campaign.category, "budget": campaign.budget, "remaining": campaign.remaining,
                    "visibility": campaign.visibility, "start_date": campaign.start_date, "end_date": campaign.end_date}
        campaigns_t.append(campaign)
    return jsonify(campaigns), 200

@api.route('/api/ad_requests', methods=['GET'])
def ad_requests():
    ad_requests = get_ad_requests(-1)
    ad_requests_t = []
    for ad_request in ad_requests:
        ad_request = {"id": ad_request.id, "influencer_id": ad_request.influencer_id, "campaign_id": ad_request.campaign_id, 
                      "messages": ad_request.messages, "requirements": ad_request.requirements, "payment_amount": ad_request.payment_amount,
                      "status": ad_request.status, "negotiate": ad_request.negotiate}
        ad_requests_t.append(ad_request)
    return jsonify(ad_requests), 200        