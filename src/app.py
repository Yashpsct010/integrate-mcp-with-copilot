"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session
from .database import get_db, Activity, User, Registration, create_tables

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    # Run migration if needed
    from .migrate_data import migrate_data
    migrate_data()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants"""
    activities = db.query(Activity).all()
    result = {}
    
    for activity in activities:
        # Get participants for this activity
        registrations = db.query(Registration).filter(
            Registration.activity_id == activity.id,
            Registration.status == "registered"
        ).all()
        
        participants = []
        for reg in registrations:
            user = db.query(User).filter(User.id == reg.user_id).first()
            if user:
                participants.append(user.email)
        
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participants
        }
    
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find or create the user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create new user (extract name from email)
        name = email.split('@')[0].title()
        user = User(email=email, name=name, role="student")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Check if user is already registered
    existing_registration = db.query(Registration).filter(
        Registration.user_id == user.id,
        Registration.activity_id == activity.id,
        Registration.status == "registered"
    ).first()
    
    if existing_registration:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Check capacity
    current_participants = db.query(Registration).filter(
        Registration.activity_id == activity.id,
        Registration.status == "registered"
    ).count()
    
    if current_participants >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is at full capacity"
        )

    # Create registration
    registration = Registration(
        user_id=user.id,
        activity_id=activity.id,
        status="registered"
    )
    db.add(registration)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find the user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Find the registration
    registration = db.query(Registration).filter(
        Registration.user_id == user.id,
        Registration.activity_id == activity.id,
        Registration.status == "registered"
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Delete the registration
    db.delete(registration)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
