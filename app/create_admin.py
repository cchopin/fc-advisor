"""
Script to create an admin user
Usage: python -m app.create_admin <username> <password>
"""

import sys
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import Admin

def main():
    if len(sys.argv) != 3:
        print("Usage: python -m app.create_admin <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    app = create_app()
    with app.app_context():
        if Admin.query.filter_by(username=username).first():
            print(f"Error: User '{username}' already exists!")
            sys.exit(1)
        
        admin = Admin(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin '{username}' created successfully!")

if __name__ == '__main__':
    main()
