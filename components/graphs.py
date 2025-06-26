import matplotlib.pyplot as plt
from datetime import date
import io
import base64

from .models import Campaign, Ad_request, User

# Set the backend of matplotlib to Agg
plt.switch_backend('Agg')

def get_month(date1):
    # Extraacting month number
    month = date1.month
    # Returning month name
    match month:
        case 1:
            return "January"
        case 2:
            return "February"
        case 3:
            return "March"
        case 4:
            return "April"
        case 5:
            return "May"
        case 6:
            return "June"
        case 7:
            return "July"
        case 8:
            return "August"
        case 9:
            return "September"
        case 10:
            return "October"
        case 11:
            return "November"
        case 12:
            return "December"
        case _:
            return "Invalid month"

def encode_image(image):
    # Save the plot to a BytesIO object
    img = io.BytesIO()
    image.savefig(img, format='png')
    img.seek(0)
    image.close()
    # Encode the image in base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    return img_base64

def ad_request_over_time(id, type):
    # Get all the ad requests
    if type == "influencer":
        ad_requests = Ad_request.query.filter_by(influencer_id=id).all()
    elif type == "sponsor":
        campaign_ids = [campaign.id for campaign in Campaign.query.filter_by(sponsor_id=id).all()]
        ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(campaign_ids)).all()
    elif type == "admin":
        ad_requests = Ad_request.query.all()
    # Get the date of creation of each ad request
    dates = [ad.created_on for ad in ad_requests]
    # Get dates for this year
    dates = [get_month(date1) for date1 in dates if date1.year == date.today().year]
    # Make a dictionary
    date_dict = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0, "July": 0, "August": 0, "September": 0, "October": 0, "November": 0, "December": 0}
    for date1 in dates:
        date_dict[date1] += 1
    # Plot the graph
    plt.figure(figsize=(12, 5))
    plt.bar(list(date_dict.keys()), date_dict.values())
    plt.xlabel('Months of the Year ' + str(date.today().year))
    plt.ylabel('Number of Ad Requests')
    plt.title('Ad Requests Over Time')
    return plt
    
def campaigns_over_time(id):
    # Get all the campaigns
    if id == 1:
        campaigns = Campaign.query.all()
    else:
        campaigns = Campaign.query.filter_by(sponsor_id=id).all()
    # Get the date of creation of each campaign
    dates = [campaign.created_on for campaign in campaigns]
    # Get dates for this year
    dates = [get_month(date1) for date1 in dates if date1.year == date.today().year]
    # Make a dictionary
    date_dict = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0, "July": 0, "August": 0, "September": 0, "October": 0, "November": 0, "December": 0}
    for date1 in dates:
        date_dict[date1] += 1
    # Plot the graph
    plt.figure(figsize=(12, 5))
    plt.bar(list(date_dict.keys()), date_dict.values())
    plt.xlabel('Months of the Year ' + str(date.today().year))
    plt.ylabel('Number of Campaigns')
    plt.title('Campaigns Over Time')
    return plt
    
def user_over_time():
    # Get all the users
    users = User.query.all()
    # Get the date of creation of each user
    dates = [user.created_on for user in users]
    # Get dates for this year
    dates = [get_month(date1) for date1 in dates if date1.year == date.today().year]
    # Make a dictionary
    date_dict = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0, "July": 0, "August": 0, "September": 0, "October": 0, "November": 0, "December": 0}
    for date1 in dates:
        date_dict[date1] += 1
    # Plot the graph
    plt.figure(figsize=(12, 5))
    plt.bar(list(date_dict.keys()), date_dict.values())
    plt.xlabel('Months of the Year ' + str(date.today().year))
    plt.ylabel('Number of Users')
    plt.title('Users Over Time')
    return plt

def ad_request_status_distribution(id, type):
    # Get all the ad requests
    if type == "influencer":
        ad_requests = Ad_request.query.filter_by(influencer_id=id).all()
    elif type == "sponsor":
        campaign_ids = [campaign.id for campaign in Campaign.query.filter_by(sponsor_id=id).all()]
        ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(campaign_ids)).all()
    else:
        ad_requests = Ad_request.query.all()
    # Get the status of each ad request
    statuses = [ad.status for ad in ad_requests]
    # Make a dictionary
    status_dict = {"Pending": 0, "Accept": 0, "Reject": 0}
    colors = ["#66b3ff", "#99ff99", "#ff9999"]
    for status in statuses:
        status_dict[status] += 1
    print(status_dict)
    names = [key for key,value in status_dict.items() if value!=0]
    values = [value for value in status_dict.values() if value!=0]
    # Plot the graph
    plt.pie(values, labels=names, colors=colors)
    plt.title('Ad Request Status Distribution')
    return plt

def payment_amount_distribution(id, type):
    # Get all the ad requests
    if type == "influencer":
        ad_requests = Ad_request.query.filter_by(influencer_id=id).all()
    elif type == "sponsor":
        campaign_ids = [campaign.id for campaign in Campaign.query.filter_by(sponsor_id=id).all()]
        ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(campaign_ids)).all()
    else:
        ad_requests = Ad_request.query.all()
    # Get the payment amount of each ad request
    payment_amounts = [ad.payment_amount for ad in ad_requests]
    # Plot the graph
    plt.hist(payment_amounts)
    plt.xlabel('Payment Amount')
    plt.ylabel('Number of Ad Requests')
    plt.title('Payment Amount Distribution')
    return plt

'''
def campaign_categories_distribution(id):
    # Get all the campaigns
    if id == -1:
        campaigns = Campaign.query.all()
    else:
        campaigns = Campaign.query.filter_by(sponsor_id=id).all()
    # Get the category of each campaign
    categories = [campaign.category for campaign in campaigns]
    # Plot the graph
    plt.figure(figsize=(12, 5))
    plt.hist(categories)
    plt.xlabel('Category')
    plt.ylabel('Number of Campaigns')
    plt.title('Campaign Categories Distribution')
    return plt
'''