"""
Data migration script to populate database with initial activity data
"""

from .database import create_tables, SessionLocal, Activity, User, Registration
from datetime import datetime

# Current in-memory activities data
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


def migrate_data():
    """Migrate initial data to database"""
    print("Creating database tables...")
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_activities = db.query(Activity).count()
        if existing_activities > 0:
            print(f"Database already has {existing_activities} activities. Skipping migration.")
            return
        
        print("Migrating activities and participants...")
        
        # Create activities and collect users
        user_emails = set()
        
        for name, details in initial_activities.items():
            # Create activity
            activity = Activity(
                name=name,
                description=details["description"],
                schedule=details["schedule"],
                max_participants=details["max_participants"]
            )
            db.add(activity)
            
            # Collect user emails
            for email in details["participants"]:
                user_emails.add(email)
        
        # Commit activities first
        db.commit()
        
        # Create users
        users_dict = {}
        for email in user_emails:
            # Extract name from email (simple approach)
            name = email.split('@')[0].title()
            user = User(
                email=email,
                name=name,
                role="student"
            )
            db.add(user)
            users_dict[email] = user
        
        # Commit users
        db.commit()
        
        # Create registrations
        for name, details in initial_activities.items():
            activity = db.query(Activity).filter(Activity.name == name).first()
            
            for email in details["participants"]:
                user = users_dict[email]
                registration = Registration(
                    user_id=user.id,
                    activity_id=activity.id,
                    status="registered"
                )
                db.add(registration)
        
        # Final commit
        db.commit()
        
        print(f"Successfully migrated {len(initial_activities)} activities and {len(user_emails)} users")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_data()
