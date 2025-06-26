from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# db and bcrypt initialized here, so that they can be imported in other files
db = SQLAlchemy()
bcrypt = Bcrypt()

# Industry list for Sponsors
industries = [
    "Technology", "Finance", "Healthcare", "Education", "Manufacturing", "Retail", 
    "Real-Estate", "Entertainment", "Transportation", "Agriculture", "Automotive", 
    "Construction", "Energy", "Food-and-Beverage", "Hospitality", "Insurance", 
    "Media", "Pharmaceuticals", "Professional-Services", "Public-Sector", 
    "Telecommunications", "Utilities", "Logistics", "Mining", "Non-Profit", 
    "Aerospace", "Biotechnology", "Chemicals", "Consulting", "Defense", "Fashion", 
    "Furniture", "Human-Resources", "Legal", "Luxury-Goods", "Packaging", 
    "Publishing", "Recreation", "Security", "Sports", "Tourism", 
    "Waste-Management", "Wholesale"
]

# Category list for Influencers and Campaigns
categories = [
    "Beauty", "Fashion", "Fitness", "Health", "Travel", "Food", "Lifestyle", 
    "Gaming", "Technology", "Photography", "Music", "Parenting", "Finance", 
    "Education", "Sports", "Art", "Home-Decor", "Pets", "Automotive", "Books", 
    "DIY", "Environment", "Entertainment", "Business", "Spirituality", "Dating", 
    "Career", "Event-Planning", "Gaming-Cosplay", "Luxury", "Outdoors", 
    "Wellness", "Mental-Health", "Non-Profit", "Comedy", "News", 
    "Personal-Development", "Relationship", "Social-Justice", "Sustainable-Living", 
    "Tech-Gadgets", "Videography", "Yoga", "Crypto", "Investment", "Real-Estate"
]