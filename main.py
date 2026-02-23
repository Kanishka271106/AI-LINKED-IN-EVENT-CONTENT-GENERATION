from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import urllib.parse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime
from dotenv import load_dotenv

from pydantic import BaseModel
from backend.database import init_db, get_db, Event, Image, Post, LinkedInToken
from backend.image_processor import ImageProcessor
from backend.linkedin_api import LinkedInAPI
from backend.caption_generator import CaptionGenerator
from PIL import Image as PILImage, ImageEnhance
import io
import base64
import numpy as np
import cv2

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Event Photo Curator", version="1.0.0")

class CropData(BaseModel):
    x: int
    y: int
    width: int
    height: int

class Adjustments(BaseModel):
    brightness: float
    contrast: float
    saturation: float

class EditRequest(BaseModel):
    crop: CropData
    adjustments: Adjustments
    auto_enhance: bool
    mask: Optional[str] = None

# Create necessary directories
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
STATIC_DIR = "static"
TEMPLATE_DIR = "templates"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Initialize services
image_processor = ImageProcessor(
    quality_threshold=float(os.getenv("QUALITY_THRESHOLD", 0.6)),
    blur_threshold=float(os.getenv("BLUR_THRESHOLD", 100)),
    duplicate_threshold=int(os.getenv("DUPLICATE_THRESHOLD", 5))
)
linkedin_api = LinkedInAPI()
caption_generator = CaptionGenerator()

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    print("\n" + "="*70)
    print("  LinkedIn Event Photo Curator - AI-Powered Content Generation")
    print("="*70)
    print("\n  Initializing application...")
    
    init_db()
    print("   [OK] Database initialized")
    print(f"   [OK] Upload directory: {UPLOAD_DIR}")
    print("   [OK] AI engine ready")
    
    # Check LinkedIn Config
    if os.getenv("LINKEDIN_CLIENT_ID") and os.getenv("LINKEDIN_CLIENT_SECRET"):
        print("   [OK] LinkedIn API configured")
    else:
        print("   [WARNING] LinkedIn API credentials MISSING in .env file!")
        print("             Social posting features will not work.")
    
    print("\n" + "="*70)
    print("  SERVER READY!")
    print("="*70)
    print(f"\n   URL: http://localhost:8000")
    print(f"   Documentation: README.md")
    print(f"   Need help? Check SETUP_GUIDE.md")
    print("\n" + "="*70)
    print("  Tips:")
    print("   - Connect LinkedIn before uploading photos")
    print("   - Upload 10-15 images for best results")
    print("   - AI selects best 10 images automatically")
    print("   - Press Ctrl+C to stop the server")
    print("="*70 + "\n")


# ============= Frontend Routes =============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


# ============= Upload & Processing Endpoints =============

@app.post("/api/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process event images"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed")
    
    # Create new event
    event = Event(
        name=f"Event {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        total_uploaded=len(files)
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Create event directory
    event_dir = os.path.join(UPLOAD_DIR, f"event_{event.id}")
    os.makedirs(event_dir, exist_ok=True)
    
    # Save uploaded files
    saved_files = []
    for file in files:
        # Validate file type
        if not file.content_type.startswith("image/"):
            continue
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(event_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_files.append({
            "filename": file.filename,
            "unique_filename": unique_filename,
            "path": file_path
        })
    
    # Process images with AI
    image_paths = [f["path"] for f in saved_files]
    processing_results = image_processor.batch_process(image_paths)
    
    # Save image records to database and enhance selected ones
    for result in processing_results["all_results"]:
        is_selected = result["filename"] in [
            img["filename"] for img in processing_results["selected_images"]
        ]
        
        # Skip images that failed processing
        if "error" in result and result["error"]:
            print(f"   [WARNING] Skipping failed image: {result['filename']} - {result['error']}")
            continue
            
        filepath = result["path"]
        # Automatically enhance high-quality selected images
        if is_selected and not result.get("is_blur"):
            try:
                print(f"   [AI] Enhancing best photo (fast mode): {result['filename']} (Score: {result['quality_score']})")
                filepath = image_processor.enhance_image(filepath, fast=True)
            except Exception as e:
                print(f"   [ERROR] Enhancement failed for {result['filename']}: {e}")
        
        try:
            image_record = Image(
                event_id=event.id,
                filename=result["filename"],
                filepath=filepath,
                quality_score=result["quality_score"],
                sharpness_score=result.get("sharpness_score", 0.0),
                brightness_score=result.get("brightness_score", 0.0),
                contrast_score=result.get("contrast_score", 0.0),
                is_blur=result.get("is_blur", False),
                is_duplicate=result.get("is_duplicate", False),
                is_selected=is_selected
            )
            db.add(image_record)
        except Exception as e:
            print(f"   [ERROR] Database entry failed for {result['filename']}: {e}")
    
    # Update event stats
    event.total_selected = len(processing_results["selected_images"])
    db.commit()
    
    print(f"   [DONE] Event {event.id} processed. {event.total_selected} images selected and enhanced.")
    
    # Create response with image IDs
    response_images = []
    # Re-fetch images to get IDs and correct data
    db_images = db.query(Image).filter(Image.event_id == event.id).all()
    
    for img in db_images:
        response_images.append({
            "id": img.id,
            "filename": img.filename,
            "url": f"/uploads/{img.filepath.replace(UPLOAD_DIR, '').lstrip(os.sep).replace(os.sep, '/')}",
            "quality_score": img.quality_score,
            "sharpness_score": img.sharpness_score,
            "brightness_score": img.brightness_score,
            "contrast_score": img.contrast_score,
            "is_blur": img.is_blur,
            "is_duplicate": img.is_duplicate,
            "is_selected": img.is_selected
        })
    
    return {
        "success": True,
        "event_id": event.id,
        "total_uploaded": len(saved_files),
        "total_selected": event.total_selected,
        "summary": processing_results["summary"],
        "images": response_images
    }


@app.get("/api/events/{event_id}/images")
async def get_event_images(event_id: int, db: Session = Depends(get_db)):
    """Get all images for an event"""
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    images = db.query(Image).filter(Image.event_id == event_id).all()
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_images": len(images),
        "total_selected": event.total_selected,
        "images": [
            {
                "id": img.id,
                "filename": img.filename,
                "url": f"/uploads/{img.filepath.replace(UPLOAD_DIR, '').lstrip(os.sep).replace(os.sep, '/')}",
                "quality_score": img.quality_score,
                "is_blur": img.is_blur,
                "is_duplicate": img.is_duplicate,
                "is_selected": img.is_selected,
                "is_posted": img.is_posted
            }
            for img in images
        ]
    }


@app.post("/api/images/{image_id}/toggle-select")
async def toggle_image_selection(image_id: int, db: Session = Depends(get_db)):
    """Toggle image selection status"""
    
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image.is_selected = not image.is_selected
    
    # Update event selected count
    event = db.query(Event).filter(Event.id == image.event_id).first()
    event.total_selected = db.query(Image).filter(
        Image.event_id == image.event_id,
        Image.is_selected == True
    ).count()
    
    db.commit()
    
    return {
        "success": True,
        "image_id": image_id,
        "is_selected": image.is_selected,
        "total_selected": event.total_selected
    }


@app.post("/api/images/{image_id}/enhance")
async def enhance_image_endpoint(image_id: int, db: Session = Depends(get_db)):
    """Manually enhance an image"""
    
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Enhance the image
        old_path = image.filepath
        new_path = image_processor.enhance_image(old_path, fast=True)
        
        # Update database if path changed
        if new_path != old_path:
            image.filepath = new_path
            db.commit()
            db.refresh(image)
        
        return {
            "success": True,
            "image_id": image_id,
            "url": f"/uploads/{image.filepath.replace(UPLOAD_DIR, '').lstrip(os.sep).replace(os.sep, '/')}",
            "filename": image.filename
        }
    except Exception as e:
        print(f"Enhancement error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enhance image: {str(e)}")


@app.post("/api/images/{image_id}/edit")
async def edit_image_endpoint(image_id: int, request: EditRequest, db: Session = Depends(get_db)):
    """Apply manual edits to an image"""
    
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Load image
        img = PILImage.open(image.filepath)
        
        # 1. Apply auto-enhance if requested (do this first so manual tweaks apply on top)
        if request.auto_enhance:
            # We can use the existing enhance_image logic but without saving yet
            # For simplicity, we'll just call the method and reload the result for further processing
            # or better: integrate the enhancement steps here.
            # Let's call the existing one since it's "solid"
            enhanced_path = image_processor.enhance_image(image.filepath, fast=True)
            img = PILImage.open(enhanced_path)
        
        # 2. Apply Crop
        c = request.crop
        img = img.crop((c.x, c.y, c.x + c.width, c.y + c.height))
        
        # 3. Apply Adjustments
        if request.adjustments.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(request.adjustments.brightness)
            
        if request.adjustments.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(request.adjustments.contrast)
            
        if request.adjustments.saturation != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(request.adjustments.saturation)
            
        # 4. Apply Mask (Erase)
        if request.mask and "base64," in request.mask:
            header, data = request.mask.split("base64,")
            mask_bytes = base64.b64decode(data)
            mask_img = PILImage.open(io.BytesIO(mask_bytes)).convert("L")
            # Resize mask to match cropped image if needed
            mask_img = mask_img.resize(img.size, PILImage.Resampling.LANCZOS)
            
            # Simple erase: where mask is white (drawn), we fill with neutral/blurred color
            # or just paste over with white for now as a "brush"
            # To actually "erase" in a meaningful way, we'd need inpainting.
            # For now, we'll just let the user paint over with white (since mask is white)
            overlay = PILImage.new("RGB", img.size, (255, 255, 255))
            img.paste(overlay, (0, 0), mask_img)

        # Save new version
        base, ext = os.path.splitext(image.filepath)
        # Avoid double suffixes
        if "_edited" not in base:
            new_path = f"{base}_edited{ext}"
        else:
            new_path = image.filepath
            
        img.save(new_path, quality=95)
        
        # Update database
        image.filepath = new_path
        db.commit()
        db.refresh(image)
        
        return {
            "success": True,
            "image_id": image_id,
            "url": f"/uploads/{image.filepath.replace(UPLOAD_DIR, '').lstrip(os.sep).replace(os.sep, '/')}",
            "filename": image.filename
        }
        
    except Exception as e:
        print(f"Edit error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to edit image: {str(e)}")


# ============= LinkedIn OAuth Endpoints =============

@app.get("/api/auth/linkedin")
async def linkedin_auth():
    """Initiate LinkedIn OAuth flow"""
    auth_url = linkedin_api.get_authorization_url(state=str(uuid.uuid4()))
    return {"auth_url": auth_url}


@app.get("/linkedin/callback")
async def linkedin_callback(code: str = None, error: str = None, error_description: str = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    """Handle LinkedIn OAuth callback"""
    
    if error:
        print(f"LinkedIn Auth Error: {error} - {error_description}")
        reason_enc = urllib.parse.quote(error)
        desc_enc = urllib.parse.quote(error_description or "")
        return RedirectResponse(url=f"/?auth=error&reason={reason_enc}&desc={desc_enc}")

    if not code:
        return RedirectResponse(url="/?auth=error&reason=no_code")
    
    try:
        # Exchange code for token
        token_data = linkedin_api.exchange_code_for_token(code)
        
        # Get user info
        user_info = linkedin_api.get_user_info(token_data["access_token"])
        
        # Store token in database
        existing_token = db.query(LinkedInToken).filter(
            LinkedInToken.user_email == user_info["email"]
        ).first()
        
        if existing_token:
            existing_token.access_token = token_data["access_token"]
            existing_token.expires_at = token_data["expires_at"]
        else:
            new_token = LinkedInToken(
                user_email=user_info["email"],
                access_token=token_data["access_token"],
                expires_at=token_data["expires_at"]
            )
            db.add(new_token)
        
        db.commit()
        
        # Redirect back to main app with success message
        return RedirectResponse(url="/?auth=success")
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"LinkedIn auth error: {error_msg}")
        traceback.print_exc()
        msg_enc = urllib.parse.quote(error_msg)
        return RedirectResponse(url=f"/?auth=error&reason=exchange_failed&detail={msg_enc}")


@app.get("/api/test-error")
async def test_error():
    """Test endpoint to verify error toast"""
    return RedirectResponse(url="/?auth=error&reason=test_reason&detail=This is a test detailed error message")

@app.get("/api/auth/status")
async def auth_status(db: Session = Depends(get_db)):
    """Check if user is authenticated with LinkedIn"""
    
    token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
    
    if not token:
        return {"authenticated": False}
    
    # Check if token is still valid
    is_valid = linkedin_api.validate_token(token.access_token)
    
    return {
        "authenticated": is_valid,
        "user_email": token.user_email if is_valid else None,
        "expires_at": token.expires_at.isoformat() if is_valid else None
    }


# ============= Caption Generation =============

class CaptionRequest(BaseModel):
    event_id: int
    keywords: Optional[List[str]] = None
    custom_context: Optional[str] = None

@app.post("/api/generate-caption")
async def generate_caption_endpoint(request: CaptionRequest, db: Session = Depends(get_db)):
    """Generate AI caption for the event"""
    event = db.query(Event).filter(Event.id == request.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get selected images count
    selected_count = db.query(Image).filter(
        Image.event_id == request.event_id, 
        Image.is_selected == True
    ).count()
    
    if selected_count == 0:
        # Fallback to total uploaded if none selected yet
        selected_count = event.total_uploaded
    
    caption = caption_generator.generate_caption(
        event_name=event.name,
        num_photos=selected_count,
        keywords=request.keywords,
        custom_context=request.custom_context
    )
    
    return {"caption": caption}


# ============= LinkedIn Posting Endpoint =============

class PostDBRequest(BaseModel):
    caption: Optional[str] = None

@app.post("/api/post/linkedin/{event_id}")
async def post_to_linkedin(
    event_id: int,
    request: PostDBRequest,
    db: Session = Depends(get_db)
):
    caption = request.caption
    """Post selected images to LinkedIn"""
    
    # Get event and selected images
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    selected_images = db.query(Image).filter(
        Image.event_id == event_id,
        Image.is_selected == True
    ).all()
    
    if not selected_images:
        raise HTTPException(status_code=400, detail="No images selected")
    
    # Get LinkedIn token
    token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated with LinkedIn")
    
    # Validate token
    if not linkedin_api.validate_token(token.access_token):
        raise HTTPException(status_code=401, detail="LinkedIn token expired. Please re-authenticate.")
    
    # Create post record
    post = Post(
        event_id=event_id,
        num_images=len(selected_images),
        status="pending"
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    try:
        # Get user info for person URN
        user_info = linkedin_api.get_user_info(token.access_token)
        person_urn = f"urn:li:person:{user_info['id']}"
        
        # Prepare image paths
        image_paths = [img.filepath for img in selected_images]
        
        # Post to LinkedIn
        if len(image_paths) > 0:
            linkedin_response = linkedin_api.create_image_post(
                access_token=token.access_token,
                person_urn=person_urn,
                image_paths=image_paths[:9],  # LinkedIn max 9 images
                caption=caption or f"Event highlights from {event.name} 📸 #professional #networking #events"
            )
            
            # Update post record
            post.status = "success"
            post.linkedin_post_id = linkedin_response.get("id")
            
            # Mark images as posted
            for img in selected_images:
                img.is_posted = True
            
            db.commit()
            
            return {
                "success": True,
                "post_id": post.id,
                "linkedin_post_id": post.linkedin_post_id,
                "num_images": len(image_paths)
            }
    
    except Exception as e:
        post.status = "failed"
        post.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to post to LinkedIn: {str(e)}")


# ============= Audit Logs =============

@app.get("/api/logs")
async def get_logs(db: Session = Depends(get_db)):
    """Get audit logs"""
    
    posts = db.query(Post).order_by(Post.posted_at.desc()).limit(50).all()
    
    return {
        "logs": [
            {
                "id": post.id,
                "event_id": post.event_id,
                "posted_at": post.posted_at.isoformat(),
                "linkedin_post_id": post.linkedin_post_id,
                "num_images": post.num_images,
                "status": post.status,
                "error_message": post.error_message
            }
            for post in posts
        ]
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get application statistics"""
    
    total_events = db.query(Event).count()
    total_images = db.query(Image).count()
    total_posts = db.query(Post).filter(Post.status == "success").count()
    total_selected = db.query(Image).filter(Image.is_selected == True).count()
    
    return {
        "total_events": total_events,
        "total_images_processed": total_images,
        "total_images_selected": total_selected,
        "total_posts": total_posts
    }


# ============= Health Check =============

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)