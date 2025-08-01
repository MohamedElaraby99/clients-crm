#!/usr/bin/env python3
"""
Database initialization script for the Flask CRM application.
"""

from app import create_app, db
from app.models import User, Client

def init_database():
    """Initialize the database with tables and admin user."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate them
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists")
        
        print("Database initialization completed successfully!")

if __name__ == '__main__':
    init_database() 