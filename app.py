# This is the main file for the Sponsorship Coordination Platform. It is a Flask application that serves the back-end

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from components.extensions import db, bcrypt
from components.models import User
from components.graphs import *

import os
import sys
from datetime import datetime
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()

# Database configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user

# Initialize the database and bcrypt
db.init_app(app)
bcrypt.init_app(app)

# Need to import after db is initialized
from components.user import *
from components.ad_request import *
from components.campaign import *
from components.flag import *
from components.api import api

# Register the api blueprint
app.register_blueprint(api)

# Create the database tables
with app.app_context():
    # If the database does not exist, create it
    db.create_all()
    # Create the admin user if it does not exist
    # Index 1 is used to get the admin user
    admin = get_user("", 1)
    if not admin:
        create_user("Admin", os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"), "Admin")
    elif admin.role != "Admin":
        print("Something went wrong, the admin user is not an admin")
        sys.exit()

def id_check(request, type, url):
    id=request.form.get('id')
    if not id: return redirect(url_for(url, error=f"{type} ID is required"))
    match type:
        case "User": result = get_user(None, id)
        case "Campaign": result = get_campaign(id)
        case "Ad request": result = get_ad_request(id)
        case _: result = None
    if not result: return redirect(url_for(url, error=f"{type} not found"))
    return result

# Login page, Allows users to login to the platform
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get("error", "")
    if request.method == 'GET':
        # Get the login page
        return render_template('login.html', error=error)
    elif request.method == 'POST':
        # Get the login credentials and check if they are correct
        email = request.form.get('email')
        password = request.form.get('pass')
        if not email or not password: return redirect(url_for('login', error='Email and password are required'))
        user = validate_user(email, password)
        if not user: return redirect(url_for('login', error='Invalid email or password'))
        # If the user is a sponsor, redirect to the sponsor dashboard
        # If the user is an influencer, redirect to the influencer dashboard
        login_user(user)
        if user.role == 'Sponsor':
            return redirect(url_for('sponsor_dashboard'))
        elif user.role == 'Influencer':
            return redirect(url_for('influencer_dashboard'))
        elif user.role == 'Admin':
            return redirect(url_for('admin'))

# Admin dashboard, Allows the admin to view all the data in the platform
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    error = request.args.get('error', '')
    page_user = request.args.get('page_user', 1, type=int)
    page_ad_request = request.args.get('page_ad_request', 1, type=int)
    page_campaign = request.args.get('page_campaign', 1, type=int)
    page_flag = request.args.get('page_flag', 1, type=int)
    form_id = request.form.get('form_id')
    if request.method == 'GET':
        # Get the admin dashboard
        users = get_users(page_user)
        ad_requests = get_ad_requests(page_ad_request)
        campaigns = get_campaigns(page_campaign)
        flags = get_flags(page_flag)
        for user in users:
            flag = get_flag(user.id, user.role)
            if flag: user.flag = flag.reason
        for i in range(len(flags.items)):
            flags.items[i] = get_user(None, flags.items[i].type_id)
        return render_template('admin.html', users=users, ad_requests=ad_requests, campaigns=campaigns, flagged=flags, error=error)
    elif request.method == 'POST' and form_id == 'flag':
        # Flag a user, or a campaign
        id = request.form.get('id')
        type = request.form.get('type')
        reason = request.form.get('reason')
        valid, message = validate_flag(type, id, reason)
        if not valid: return redirect(url_for('admin', error=message))
        create_flag(type, id, reason)
        return redirect(url_for('admin', error="User Flagged successfully"))
    elif request.method == 'POST' and form_id == "remove_flag":
        # Remove a flag
        id = request.form.get('id')
        type = request.form.get('type')
        if not type or not id: return redirect(url_for('admin', error="All fields are required"))
        delete_flag(type, id)
        return redirect(url_for('admin', error='Flag Removed successfully'))
    elif request.method == 'POST' and form_id == 'delete_user':
        # Delete a user
        user = get_user(request.form.get('email'))
        if not user: return redirect(url_for('admin', error='User Invalid'))
        # If user is Sponsor, delete all campaigns and ad requests
        for campaign in user.campaigns:
            for ad_request in campaign.ad_requests:
                delete_ad_request(ad_request.id)
            delete_campaign(campaign.id)
        # If user is Influencer, delete all ad requests
        for ad_request in user.ad_requests:
            delete_ad_request(ad_request.id)
        delete_flag(user.role, user.id)
        delete_user(user.email)
        return redirect(url_for('admin', error='User Deleted successfully'))

# Register page, Allows users to register as a Sponsor
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/sponsor', methods=['GET', 'POST'])
def register_sponsor():
    error = request.args.get('error', '')
    if request.method == 'GET':
        # Get the register page
        return render_template('register_sponsor.html', error=error)
    elif request.method == 'POST':
        # Get the registration details and create a new user
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('pass')
        confirm = request.form.get('con_pass')
        industry = request.form.get('industry')
        # Check if the form is valid
        valid, message = validate_form(name, email, password, confirm, "Sponsor", industry=industry)
        if not valid: return redirect(url_for('register_sponsor', error=message))
        # If the form is valid, create a new user and login
        sponsor = create_user(name, email, password, 'Sponsor', industry=industry)
        login_user(sponsor)
        return redirect(url_for('sponsor_dashboard'))
        
# Register page, Allows users to register as an Influencer
@app.route('/register/influencer', methods=['GET', 'POST'])
def register_influencer():
    error = request.args.get('error', '')
    if request.method == 'GET':
        # Get the register page
        return render_template('register_influencer.html', error=error)
    elif request.method == 'POST':
        # Get the registration details and create a new user
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('pass')
        confirm = request.form.get('con_pass')
        reach = request.form.get('reach')
        category = request.form.get('category')
        # Check if the form is valid
        valid, message = validate_form(name, email, password, confirm, 'Influencer', reach=reach, category=category)
        if not valid: return redirect(url_for('register_influencer', error=message))
        # If the form is valid, create a new user and login
        influencer = create_user(name, email, password, 'Influencer', category=category, reach=reach)
        login_user(influencer)
        return redirect(url_for('influencer_dashboard'))

# Sponsor dashboard, Allows sponsors to view their campaigns and create new campaigns
@app.route('/sponsor/', methods=['GET', 'POST'])
@login_required
def sponsor_dashboard():
    sponsor = current_user
    form_id = request.form.get('form_id')
    # Get the sponsor's campaigns and ad requests
    page_campaign = request.args.get('page_campaign', 1, type=int)
    page_ad_request = request.args.get('page_ad_request', 1, type=int)
    error = request.args.get('error', '')
    # Paginated Campaigns
    campaigns = get_sponsor_campaigns(sponsor.id, page_campaign)
    # Paginated Ad Requests
    campaign_id = [campaign.id for campaign in sponsor.campaigns]
    ad_requests = get_campaign_ad_requests(campaign_id, page_ad_request)
    # Check if the sponsor is flagged
    flag = get_flag(sponsor.id, sponsor.role)
    if request.method == 'GET':
        # Get the sponsor dashboard
        return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests, error=error, flag=flag)
    elif request.method == 'POST' and form_id == 'edit_profile':
        # Update the sponsor profile
        name = request.form.get('name', sponsor.name)
        password = request.form.get('password', None)
        if password is None: password = "Testing@12"
        industry = request.form.get('industry', sponsor.industry)
        # Check if the form is valid
        valid, message = validate_form(name, sponsor.email, password, password, "Sponsor", industry=industry)
        if not valid: return redirect(url_for('sponsor_dashboard', error=message))
        # If the form is valid, update the user
        if password == "Testing@12": password = None
        update_user(sponsor.email, {"name": name, "password": password, "industry": industry})
        return redirect(url_for('sponsor_dashboard', error="Profile updated successfully"))
    elif request.method == 'POST' and form_id == 'add_campaign':
        # Create a new campaign
        name = request.form.get('name')
        description = request.form.get('description')
        goals = request.form.get('goals')
        category = request.form.get('category')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        # Check if the form is valid
        valid, message = validate_campaign(name, description, start_date, end_date, category, budget, visibility, goals)
        if not valid: return redirect(url_for('sponsor_dashboard', error=message))
        # If the form is valid, create a new campaign
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        create_campaign(sponsor.id, name, description, start_date, end_date, category, budget, visibility, goals)
        return redirect(url_for('sponsor_dashboard', error="Campaign created successfully"))
    elif request.method == 'POST' and form_id == 'edit_campaign':
        # Edit a campaign
        # Make sure the campaign is valid
        campaign = id_check(request, "Campaign", "sponsor_dashboard")
        # Get the updated details
        name = request.form.get('name', campaign.name)
        description = request.form.get('description', campaign.description)
        goals = request.form.get('goals', campaign.goals)
        category = request.form.get('category', campaign.category)
        budget = request.form.get('budget', campaign.budget)
        visibility = request.form.get('visibility', campaign.visibility)
        start_date = request.form.get('start_date', campaign.start_date)
        end_date = request.form.get('end_date', campaign.end_date)
        valid, message = validate_campaign(name, description, start_date, end_date, category, budget, visibility, goals)
        if not valid: return redirect(url_for('sponsor_dashboard', error=message))
        if campaign.budget < campaign.remaining: return redirect(url_for('sponsor_dashboard', error="Budget should be greater than remaining budget"))
        # If the form is valid, update the campaign
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        update_campaign(campaign.id, {"name": name, "description": description, "start_date": start_date, "end_date": end_date, 
                                      "budget": budget, "visibility": visibility, "goals": goals, "category": category})
        return redirect(url_for('sponsor_dashboard', error="Campaign updated successfully"))
    elif request.method == 'POST' and form_id == 'delete_campaign':
        # Delete a campaign and all its ad requests
        campaign = id_check(request, "Campaign", "sponsor_dashboard")
        for ad_request in campaign.ad_requests:
            delete_ad_request(ad_request.id)
        delete_campaign(campaign.id)
        return redirect(url_for('sponsor_dashboard', error="Campaign and all associated ad requests deleted successfully"))
    elif request.method == 'POST' and form_id == 'revert_ad':
        # Accept or Reject an ad request and update the campaign budget
        ad_request = id_check(request, "Ad request", "sponsor_dashboard")
        status = request.form.get('status')
        if status not in ["Accept", "Reject"]: return redirect(url_for('sponsor_dashboard', error="Invalid status"))
        # Check if the payment amount is less than or equal to the campaign budget
        if status == 'Accept' and not validate_budget(ad_request.payment_amount, ad_request.campaign_id):
            # If the payment amount exceeds the budget, delete the ad request
            delete_ad_request(ad_request.id)
            return redirect(url_for('sponsor_dashboard', error='Payment amount exceeds budget, deleting ad request'))
        # If the payment amount is valid, update the ad request and the campaign
        update_ad_request(ad_request.id, {"status": status, "negotiate": True})
        if status == 'Accept': update_campaign(ad_request.campaign_id, {"remaining": ad_request.payment_amount})
        return redirect(url_for('sponsor_dashboard', error="Ad request updated successfully"))
    elif request.method == 'POST' and form_id == 'edit_ad':
        # Edit an ad request
        ad_request = id_check(request, "Ad request", "sponsor_dashboard")
        messages = request.form.get('messages', ad_request.messages)
        requirements = request.form.get('requirements', ad_request.requirements)
        payment_amount = request.form.get('payment_amount', ad_request.payment_amount)
        valid, message = validate_ad_request(messages, requirements, payment_amount, "Pending")
        if not valid: return redirect(url_for('sponsor_dashboard', error=message))
        # If the form is valid, update the ad request
        update_ad_request(ad_request.id, {"messages": messages, "requirements": requirements, "payment_amount": payment_amount})
        return redirect(url_for('sponsor_dashboard', error="Ad request updated successfully"))
    elif request.method == 'POST' and form_id == 'withdraw_ad':
        # Withdraw an ad request
        ad_request = id_check(request, "Ad request", "sponsor_dashboard")
        # If the ad request is valid, delete it
        delete_ad_request(ad_request.id)
        return redirect(url_for('sponsor_dashboard', error="Ad request deleted successfully"))
        
# Influencer dashboard, Allows influencers to view their ad requests and create new ad requests
@app.route('/influencer/', methods=['GET', 'POST'])
@login_required
def influencer_dashboard():
    influencer = current_user
    form_id = request.form.get('form_id')
    # Get the influencer's ad requests
    page = request.args.get('page', 1, type=int)
    error = request.args.get('error', '')
    # Paginated Ad Requests
    ad_requests = get_influencer_ad_requests(influencer.id, page)
    # Check if the influencer is flagged
    flag = get_flag(influencer.id, influencer.role)
    if request.method == 'GET':
        # Get the influencer dashboard
        return render_template('influencer_dashboard.html', influencer=influencer, ad_requests=ad_requests, error=error, flag=flag)
    elif request.method == 'POST' and form_id == 'edit_profile':
        # Update the influencer profile
        name = request.form.get('name', influencer.name)
        password = request.form.get('password', influencer.password)
        category = request.form.get('category', influencer.category)
        reach = request.form.get('reach', influencer.reach)
        valid, message = validate_form(name, influencer.email, password, password, "Influencer", category=category, reach=reach)
        if not valid: return redirect(url_for('influencer_dashboard', error=message))
        # If the form is valid, update the user
        update_user(influencer.email, {"name": name, "password": password, "category": category, "reach": reach})
        return redirect(url_for('influencer_dashboard', error="Profile updated successfully"))
    elif request.method == 'POST' and form_id == 'revert_ad':
        # Accept or Reject an ad request and update the campaign budget
        ad_request = id_check(request, "Ad request", "influencer_dashboard")
        status = request.form.get('status')
        if status not in ["Accept", "Reject"]: return redirect(url_for('influencer_dashboard', error="Invalid status"))
        # Check if the payment amount is less than or equal to the campaign remaining budget
        if status == 'Accept' and not validate_budget(ad_request.payment_amount, ad_request.campaign_id):
            # If the payment amount exceeds the budget, delete the ad request
            delete_ad_request(ad_request.id)
            return redirect(url_for("influencer_dashboard", error='Payment amount exceeds budget, deleting ad request'))
        # If the payment amount is valid, update the ad request and the campaign
        update_ad_request(ad_request.id, {"status": status, "negotiate": True})
        if status == 'Accept': update_campaign(ad_request.campaign_id, {"remaining": ad_request.payment_amount})
        return redirect(url_for('influencer_dashboard', error="Ad request updated successfully"))
    elif request.method == 'POST' and form_id == 'negotiate_ad':
        # Negotiate an ad request
        ad_request = id_check(request, "Ad request", "influencer_dashboard")
        payment_amount = request.form.get('payment_amount')
        # If the payment amount is valid, update the ad request
        update_ad_request(ad_request.id, {"payment_amount": payment_amount, "negotiate": True, "status": "Pending"})
        return redirect(url_for('influencer_dashboard', error="Ad request updated successfully"))

# Campaign page, Allows users to view the details of a campaign
@app.route('/campaign/<id>', methods=['GET', 'POST'])
@login_required
def campaign(id):
    user = current_user
    form_id = request.form.get('form_id')
    page = request.args.get('page', 1, type=int)
    error = request.args.get('error', '')
    # Get the campaign details and ad requests
    campaign = get_campaign(id)
    ad_requests = get_campaign_ad_requests([id], page)
    if request.method == 'GET':
        # Get the campaign page
        return render_template('campaign.html', user=user, campaign=campaign, ad_requests=ad_requests, error=error)
    elif request.method == 'POST' and form_id == 'add_ad_request':
        # Create a new ad request
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        valid, message = validate_ad_request(messages, requirements, payment_amount, "Pending")
        # Check if the form is valid
        if not valid: return redirect(url_for('campaign', id = id, error=message))
        # If the form is valid, create a new ad request
        create_ad_request(messages, requirements, payment_amount, 'Pending', False, id)
        return redirect(url_for('campaign', id=id, error="Ad Request Created successfully"))
    elif request.method == 'POST' and form_id == 'send_request':
        # Send a request to a sponsor only for Influencers
        ad_request = id_check(request, "Ad request", "campaign")
        payment_amount = request.form.get('payment_amount')
        # Update the ad request with the payment amount and status
        update_ad_request(ad_request.id, {"payment_amount": payment_amount, "status": "Pending", "negotiate": True, "influencer_id": user.id})
        return redirect(url_for('campaign', id=id, error="Ad request sent successfully"))
    elif request.method == 'POST' and form_id == 'revert_ad':
        # Accept or Reject an ad request for both Sponsors and Influencers
        ad_request = id_check(request, "Ad request", "campaign")
        status = request.form.get('status')
        if status not in ["Accept", "Reject"]: return redirect(url_for('campaign', id=id, error="Invalid status"))
        # Check if the payment amount is less than or equal to the campaign budget
        if status == 'Accept' and not validate_budget(ad_request.payment_amount, ad_request.campaign_id):
            # If the payment amount exceeds the budget, delete the ad request
            delete_ad_request(ad_request.id)
            return redirect(url_for('campaign', id=id, error='Payment amount exceeds budget, deleting ad request'))
        # If the payment amount is valid, update the ad request and the campaign
        update_ad_request(ad_request.id, {"status": status, "negotiate": True})
        if status == 'Accept': update_campaign(ad_request.campaign_id, {"remaining": ad_request.payment_amount})
        return redirect(url_for('campaign', id=id, error="Ad request updated successfully"))
    elif request.method == 'POST' and form_id == 'negotiate_ad':
        # Negotiate an ad request only for Influencers
        ad_request = id_check(request, "Ad request", "campaign")
        payment_amount = request.form.get('payment_amount')
        # Update the ad request with the payment amount and status
        update_ad_request(ad_request.id, {"payment_amount": payment_amount, "negotiate": True, "status": "Pending"})
        return redirect(url_for('campaign', id=id, error="Ad request updated successfully"))
    elif request.method == 'POST' and form_id == 'edit_ad':
        # Edit an ad request only for Sponsors
        ad_request = id_check(request, "Ad request", "campaign")
        if ad_request.status != "Pending" or ad_request.negotiate: return redirect(url_for('campaign', id=id, error="Ad Request cannot be updated at the moment"))
        messages = request.form.get('messages', ad_request.messages)
        requirements = request.form.get('requirements', ad_request.requirements)
        payment_amount = request.form.get('payment_amount', ad_request.payment_amount)
        valid, message = validate_ad_request(messages, requirements, payment_amount, "Pending")
        if not valid: return redirect(url_for('campaign', id=id, error=message))
        # If the form is valid, update the ad request
        update_ad_request(ad_request.id, {"messages": messages, "requirements": requirements, "payment_amount": payment_amount})
        return redirect(url_for('campaign', id=id, error="Ad request updated successfully"))
    elif request.method == 'POST' and form_id == 'withdraw_ad':
        # Withdraw an ad request only for Sponsors
        ad_request = id_check(request, "Ad request", "campaign")
        # If the ad request is valid, delete it
        delete_ad_request(ad_request.id)
        return redirect(url_for('campaign', id=id, error="Ad request deleted successfully"))

# Search page, Allows users to search for influencers and sponsors
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    user = current_user
    form_id = request.form.get('form_id')
    # Get the search page
    # Get the search results based on the user's role
    campaign = []
    page = request.args.get('page', 1, type=int)
    error = request.args.get('error', '')
    name = request.args.get('name', '')
    sort = request.args.get('sort', None)
    if sort == "None": sort = None
    category = request.args.get('category', None)
    if category == "None": category = None
    if request.method == 'GET' and user.role == 'Influencer':
        campaigns = search_campaign(name, sort, category, page)
        filter_dic = {"name": name, "sort": sort, "category": category}
        return render_template('search.html', type=user.role, results=campaigns, campaign=campaign, id=user.id, filter_dic=filter_dic, error=error)
    elif request.method == 'GET' and user.role == 'Sponsor':
        influencers = search_user(name, sort, category, page)
        campaign = get_sponsor_campaigns(user.id, -1)
        filter_dic = {"name": name, "sort": sort, "category": category}
        return render_template('search.html', type=user.role, results=influencers, campaign=campaign, id=None, filter_dic=filter_dic, error=error)
    elif request.method == 'POST' and form_id == 'search_name':
        # Search for influencers or campaigns
        page = 1
        name = request.form.get('search')
        sort = request.form.get('sort')
        category = request.form.get('category')
        if user.role == 'Sponsor':
            # Search for influencers
            results = search_user(name, sort, category, page)
            campaign = get_sponsor_campaigns(user.id, -1)
        elif user.role == 'Influencer':
            # Search for campaigns
            results = search_campaign(name, sort, category, page)
        filter_dic = {"name":"", "sort": None, "category": None}
        if name: filter_dic["name"] = name
        if sort: filter_dic["sort"] = sort
        if category: filter_dic["category"] = category
        return render_template('search.html', type=user.role, results=results, campaign=campaign, id=user.id, filter_dic=filter_dic, error=error)
    elif request.method == 'POST' and form_id == 'ad_request':
        results = search_user(None, None, None, page)
        # Create a new ad request
        influencer_id = request.form.get('id')
        campaign_id = request.form.get('campaign_id')
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        # Check if the form is valid
        valid, message = validate_ad_request(messages, requirements, payment_amount, "Pending")
        if not valid: return redirect(url_for('search', error=message))
        create_ad_request(messages, requirements, payment_amount, 'Pending', False, campaign_id, influencer_id)
        return redirect(url_for('search', error="Ad request sent successfully"))

# Stats page, Allows users to view the statistics of the platform
@app.route('/stats', methods=['GET'])
@login_required
def stats():
    user = current_user
    # Get the stats page
    user_graph = encode_image(user_over_time())
    campaign_graph = encode_image(campaigns_over_time(user.id))
    ad_request_graph = encode_image(ad_request_over_time(user.id, user.role.lower()))
    ad_request_status_graph = encode_image(ad_request_status_distribution(user.id, user.role.lower()))
    payment_amount_distribution_graph = encode_image(payment_amount_distribution(user.id, user.role.lower()))
    if user.role == "Sponsor":
        return render_template('stats.html', user=user, campaign_graph=campaign_graph, ad_request_graph=ad_request_graph, ad_request_status_graph=ad_request_status_graph, payment_amount_distribution_graph=payment_amount_distribution_graph)
    elif user.role == "Influencer":
        return render_template('stats.html', user=user, ad_request_graph=ad_request_graph, ad_request_status_graph=ad_request_status_graph, payment_amount_distribution_graph=payment_amount_distribution_graph)
    return render_template('stats.html', user=user, user_graph=user_graph, campaign_graph=campaign_graph, ad_request_graph=ad_request_graph,
                           ad_request_status_graph=ad_request_status_graph, payment_amount_distribution_graph=payment_amount_distribution_graph)

@app.route('/logout')
@login_required
def logout():
    # Logout the user
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)