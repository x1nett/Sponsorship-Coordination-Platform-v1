from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from components.models import User, Ad_request, Campaign
from components.extensions import bcrypt, industries, categories

# Initialize the database connection and session
engine = create_engine('sqlite:///instance/sponsorship_platform.db')
Session = sessionmaker(bind=engine)
session = Session()

user_id=2
campaign_id=1
# Initialize Faker for generating random data
fake = Faker()

# Function to create sample users
def create_sample_sponsors(n):
    users = []
    global user_id
    for _ in range(n):
        email = fake.email()
        password = fake.password(special_chars=True, digits=True, upper_case=True, lower_case=True)
        print(f"Sponsor email: {email}, password: {password}")
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            id=user_id,
            role='Sponsor',
            name=fake.name(),
            email=email,
            password=password,
            industry=fake.random_element(elements=industries),
            created_on=fake.date_this_year(before_today=True)
        )
        users.append(user)
        user_id+=1
    return users

def create_sample_influencers(n):
    users = []
    global user_id
    for _ in range(n):
        email = fake.email()
        password = fake.password(special_chars=True, digits=True, upper_case=True, lower_case=True)
        print(f"Influencer email: {email}, password: {password}")
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            id=user_id,
            role='Influencer',
            name=fake.name(),
            email=email,
            password=password,
            category=fake.random_element(elements=categories),
            reach=fake.random_number(digits=5),
            created_on=fake.date_this_year(before_today=True)
        )
        user_id+=1
        users.append(user)
    return users

# Function to create sample campaigns
def create_sample_campaigns_public(users, n):
    campaigns = []
    global campaign_id
    for _ in range(n):
        sponsor = fake.random_element(users)
        budget = fake.random_number(digits=5)
        campaign = Campaign(
            id=campaign_id,
            sponsor_id=sponsor.id,
            name=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            goals=fake.text(max_nb_chars=200),
            category=fake.random_element(elements=categories),
            budget=budget,
            remaining=budget,
            visibility='Public',
            start_date=fake.date_this_year(before_today=True),
            end_date=fake.date_this_year(after_today=True),
            created_on=fake.date_this_year(before_today=True)
        )
        campaign_id+=1
        campaigns.append(campaign)
    return campaigns

def create_sample_campaigns_private(users, n):
    campaigns = []
    global campaign_id
    for _ in range(n):
        sponsor = fake.random_element(users)
        budget = fake.random_number(digits=5)
        campaign = Campaign(
            id=campaign_id,
            sponsor_id=sponsor.id,
            name=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            goals=fake.text(max_nb_chars=200),
            category=fake.random_element(elements=categories),
            budget=budget,
            remaining=budget,
            visibility='Private',
            start_date=fake.date_this_year(before_today=True),
            end_date=fake.date_this_year(after_today=True),
            created_on=fake.date_this_year(before_today=True)
        )
        campaign_id+=1
        campaigns.append(campaign)
    return campaigns

# Function to create sample ad requests
def create_sample_ad_requests(users, campaigns, n):
    ad_requests = []
    ad_request_id=1
    for _ in range(n):
        influencer = fake.random_element(users)
        campaign = fake.random_element(campaigns)
        ad_request = Ad_request(
            id=ad_request_id,
            influencer_id=influencer.id,
            campaign_id=campaign.id,
            messages=fake.text(max_nb_chars=200),
            requirements=fake.text(max_nb_chars=200),
            payment_amount=fake.random_number(digits=4),
            status='Pending',
            negotiate=fake.boolean(),
            created_on=fake.date_this_year(before_today=True)
        )
        ad_request_id+=1
        ad_requests.append(ad_request)
    return ad_requests

# Generate sample data
sponsors = create_sample_sponsors(3)
influencers = create_sample_influencers(3)
public_campaigns = create_sample_campaigns_public(sponsors, 10)
private_campaigns = create_sample_campaigns_private(sponsors, 10)
ad_requests = create_sample_ad_requests(influencers, public_campaigns, 30)

# Add data to session and commit
session.add_all(sponsors)
session.add_all(influencers)
session.add_all(public_campaigns)
session.add_all(private_campaigns)
session.add_all(ad_requests)
sponsors = create_sample_sponsors(12)
influencers = create_sample_influencers(12)
public_campaigns = create_sample_campaigns_public(sponsors, 100)
private_campaigns = create_sample_campaigns_private(sponsors, 100)
session.add_all(sponsors)
session.add_all(influencers)
session.add_all(public_campaigns)
session.add_all(private_campaigns)
session.commit()

print("Sample data generated and committed to the database!")
