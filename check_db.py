from backend.database import SessionLocal, Event, Image, Post
from sqlalchemy import desc
import os

db = SessionLocal()

print("--- RECENT EVENTS ---")
events = db.query(Event).order_by(desc(Event.id)).limit(5).all()
for e in events:
    print(f"Event ID: {e.id}, Name: {e.name}, Created: {e.created_at}, Total Uploaded: {e.total_uploaded}, Selected: {e.total_selected}")
    
    # Check images for this event
    images = db.query(Image).filter(Image.event_id == e.id).all()
    print(f"  Images in DB: {len(images)}")
    for img in images[:3]: # Show first 3
        print(f"    - {img.filename} (Sharpness: {img.sharpness_score}, Selected: {img.is_selected})")
    if len(images) > 3:
        print("    ...")

print("\n--- RECENT POST ATTEMPTS ---")
posts = db.query(Post).order_by(desc(Post.id)).limit(5).all()
for p in posts:
    print(f"Post ID: {p.id}, Event ID: {p.event_id}, Status: {p.status}, Error: {p.error_message}")

db.close()
