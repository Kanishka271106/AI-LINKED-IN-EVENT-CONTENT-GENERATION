import sys
import subprocess
import os

try:
    print("================ RUNTIME DEPENDENCY FIX ================", flush=True)
    # Physically force installation of google-genai directly inside the runtime container
    subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "google-generativeai"], stdout=sys.stdout)
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", "google-genai", "google-auth", "pydantic>=2.0"], stdout=sys.stdout)
    
    # Print the installed packages directly to the Railway Deploy logs so we can see what's happening
    output = subprocess.check_output([sys.executable, "-m", "pip", "list"])
    print(output.decode("utf-8"), flush=True)
    print("========================================================", flush=True)
except Exception as e:
    print(f"Runtime fix failed: {e}", flush=True)

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
from backend.chatbot_manager import ChatbotManager
from PIL import Image as PILImage, ImageEnhance
import io
import base64
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Curator", version="1.0.0")

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
chatbot_manager = ChatbotManager()

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    print("\n" + "="*70)
    print("  Curator - AI-Powered Content Generation")
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
    
    # Check Gemini AI Config
    if os.getenv("GEMINI_API_KEY"):
        print("   [OK] Gemini AI engine configured")
    else:
        print("   [WARNING] GEMINI_API_KEY MISSING in .env file!")
        print("             AI caption generation will use fallback templates.")
    
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
    
    # Get last authenticated user for association
    last_token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
    user_email = last_token.user_email if last_token else None

    # Create new event
    event = Event(
        name=f"Event {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        total_uploaded=len(files),
        user_email=user_email
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
    
    # Save image records to database and enhance selected ones in parallel
    def enhance_and_create_image(result):
        is_selected = result["filename"] in [
            img["filename"] for img in processing_results["selected_images"]
        ]
        
        # Skip images that failed processing
        if "error" in result and result["error"]:
            print(f"   [WARNING] Skipping failed image: {result['filename']} - {result['error']}")
            return None
            
        filepath = result["path"]
        # Automatic enhancement removed per user request. 
        # Curation logic remains (is_selected), but images stay original initially.
        
        return {
            "event_id": event.id,
            "filename": result["filename"],
            "filepath": filepath,
            "quality_score": result["quality_score"],
            "sharpness_score": result.get("sharpness_score", 0.0),
            "brightness_score": result.get("brightness_score", 0.0),
            "contrast_score": result.get("contrast_score", 0.0),
            "is_blur": result.get("is_blur", False),
            "is_duplicate": result.get("is_duplicate", False),
            "is_selected": is_selected
        }

    # Enhancement can be CPU heavy, but IO bound for saving
    with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as executor:
        image_data_list = list(executor.map(enhance_and_create_image, processing_results["all_results"]))

    # Save to DB (must be in main thread or handle session carefully)
    for img_data in image_data_list:
        if img_data:
            try:
                image_record = Image(**img_data)
                db.add(image_record)
            except Exception as e:
                print(f"   [ERROR] Database entry failed for {img_data['filename']}: {e}")
    
    # Update event stats
    event.total_selected = len(processing_results["selected_images"])
    db.commit()
    
    print(f"   [DONE] Event {event.id} processed. {event.total_selected} images selected as candidates.")
    
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
        "created_at": event.created_at.isoformat(),
        "total_images": len(images),
        "total_selected": event.total_selected,
        "user_email": event.user_email,
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
            
            # Improved erase: Use OpenCV inpainting for natural fill
            # 1. Convert PIL image to OpenCV BGR
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # 2. Process mask
            # Convert base64 mask to OpenCV image
            mask_np = np.frombuffer(mask_bytes, dtype=np.uint8)
            mask_img_cv = cv2.imdecode(mask_np, cv2.IMREAD_UNCHANGED)
            
            # CRITICAL: Crop the mask using the same coordinates as the image
            # The mask was drawn on the FULL image in the editor
            # Ensure coordinates are within bounds of the mask
            mh, mw = mask_img_cv.shape[:2]
            x1, y1 = max(0, c.x), max(0, c.y)
            x2, y2 = min(mw, c.x + c.width), min(mh, c.y + c.height)
            mask_img_cv = mask_img_cv[y1:y2, x1:x2]
            
            # Ensure mask matches cropped image size exactly (handling rounding differences)
            if mask_img_cv.shape[:2] != img_cv.shape[:2]:
                mask_img_cv = cv2.resize(mask_img_cv, (img_cv.shape[1], img_cv.shape[0]))
            
            # Get mask from alpha channel or grayscale
            if mask_img_cv.shape[2] == 4:
                _, mask_final = cv2.threshold(mask_img_cv[:, :, 3], 10, 255, cv2.THRESH_BINARY)
            else:
                gray_mask = cv2.cvtColor(mask_img_cv, cv2.COLOR_BGR2GRAY)
                _, mask_final = cv2.threshold(gray_mask, 10, 255, cv2.THRESH_BINARY)
            
            # Dilation: Expand the mask slightly to cover edges of the erased object better
            kernel = np.ones((5,5), np.uint8)
            mask_final = cv2.dilate(mask_final, kernel, iterations=1)
            
            # 3. Apply Inpainting
            # Using Telea algorithm with larger radius for better fill
            inpainted = cv2.inpaint(img_cv, mask_final, 7, cv2.INPAINT_TELEA)
            
            # 4. Convert back to PIL
            img = PILImage.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))

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
        print(f"   [ERROR] LinkedIn Callback hit WITHOUT 'code' parameter. Redirect URI might be misconfigured.")
        print(f"           Full Request URL: {request.url}")
        return RedirectResponse(url="/?auth=error&reason=no_code&detail=LinkedIn_did_not_provide_an_authorization_code_check_Redirect_URI")
    
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


# ============= Caption Generation & Preferences =============

class PreferenceRequest(BaseModel):
    include_hashtags: bool
    custom_hashtags: Optional[str] = None

class CaptionRequest(BaseModel):
    event_id: int
    keywords: Optional[List[str]] = None
    custom_context: Optional[str] = None

class ChatInitRequest(BaseModel):
    event_id: int
    custom_context: Optional[str] = None

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

@app.get("/api/preferences")
async def get_preferences(db: Session = Depends(get_db)):
    """Get user caption preferences"""
    from backend.database import UserPreference
    prefs = db.query(UserPreference).order_by(UserPreference.updated_at.desc()).first()
    
    if not prefs:
        # Return default preferences
        return {
            "include_hashtags": True,
            "custom_hashtags": ""
        }
    
    return {
        "include_hashtags": prefs.include_hashtags,
        "custom_hashtags": prefs.custom_hashtags or ""
    }

@app.post("/api/preferences")
async def update_preferences(request: PreferenceRequest, db: Session = Depends(get_db)):
    """Update user caption preferences"""
    from backend.database import UserPreference
    
    # For MVP, we use a single global preference record (or per user if we had auth)
    prefs = db.query(UserPreference).first()
    
    if not prefs:
        prefs = UserPreference(
            include_hashtags=request.include_hashtags,
            custom_hashtags=request.custom_hashtags
        )
        db.add(prefs)
    else:
        prefs.include_hashtags = request.include_hashtags
        prefs.custom_hashtags = request.custom_hashtags
    
    db.commit()
    return {"success": True}

@app.post("/api/generate-caption")
async def generate_caption_endpoint(request: CaptionRequest, db: Session = Depends(get_db)):
    """Generate AI caption for the event (Legacy one-shot)"""
    from backend.database import UserPreference
    
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
    
    # Fetch preferences
    prefs_record = db.query(UserPreference).order_by(UserPreference.updated_at.desc()).first()
    preferences = {
        "include_hashtags": prefs_record.include_hashtags if prefs_record else True,
        "custom_hashtags": prefs_record.custom_hashtags if prefs_record else ""
    }
    
    caption = caption_generator.generate_caption(
        event_name=event.name,
        num_photos=selected_count,
        keywords=request.keywords,
        custom_context=request.custom_context,
        preferences=preferences
    )
    
    return {"caption": caption}

@app.post("/api/chat/init")
async def init_chat(request: ChatInitRequest, db: Session = Depends(get_db)):
    """Initialize a chat session with event context"""
    event = db.query(Event).filter(Event.id == request.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get selected images count
    selected_pics = db.query(Image).filter(
        Image.event_id == request.event_id, 
        Image.is_selected == True
    ).count()
    
    context = f"Event Name: {event.name}\nPhotos Selected: {selected_pics}"
    if request.custom_context:
        context += f"\nUser Notes: {request.custom_context}"
        
    session_id = chatbot_manager.create_session(context)
    
    # Get the initial draft
    initial_message = "Hello! I've analyzed your event photos and context. Here is a high-impact draft for your LinkedIn post:"
    first_ai_response = chatbot_manager.get_response(session_id, "Please provide the initial draft now.")
    
    return {
        "session_id": session_id,
        "initial_message": initial_message,
        "first_draft": first_ai_response
    }

@app.post("/api/chat/message")
async def chat_message(request: ChatMessageRequest):
    """Send a message to the chatbot and get a response"""
    response = chatbot_manager.get_response(request.session_id, request.message)
    return {"response": response}


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
    """Get application statistics with user-specific data"""
    
    # Global stats
    total_events = db.query(Event).count()
    total_images = db.query(Image).count()
    total_posts = db.query(Post).filter(Post.status == "success").count()
    
    # User-specific stats (based on last authenticated LinkedIn user)
    last_token = db.query(LinkedInToken).order_by(LinkedInToken.created_at.desc()).first()
    user_email = last_token.user_email if last_token else None
    
    user_posts = 0
    user_images = 0
    
    if user_email:
        # Get events created by this user
        user_events = db.query(Event).filter(Event.user_email == user_email).all()
        user_event_ids = [e.id for e in user_events]
        
        if user_event_ids:
            user_posts = db.query(Post).filter(
                Post.event_id.in_(user_event_ids),
                Post.status == "success"
            ).count()
            
            user_images = db.query(Image).filter(
                Image.event_id.in_(user_event_ids),
                Image.is_posted == True
            ).count()
    
    return {
        "total_events": total_events,
        "total_images_processed": total_images,
        "total_posts": total_posts,
        "user_posts": user_posts,
        "user_images": user_images,
        "authenticated": last_token is not None,
        "user_email": user_email
    }

@app.get("/api/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Get aggregated analytics data for charts"""
    from sqlalchemy import func
    
    # 1. Events over time (last 30 days)
    events_by_date = db.query(
        func.date(Event.created_at).label('date'),
        func.count(Event.id).label('count')
    ).group_by(func.date(Event.created_at)).order_by(func.date(Event.created_at)).limit(30).all()
    
    # 2. Posts over time
    posts_by_date = db.query(
        func.date(Post.posted_at).label('date'),
        func.count(Post.id).label('count')
    ).filter(Post.status == "success").group_by(func.date(Post.posted_at)).order_by(func.date(Post.posted_at)).limit(30).all()
    
    # 3. Quality distribution
    quality_ranges = {
        "Low (<50%)": db.query(Image).filter(Image.quality_score < 0.5).count(),
        "Medium (50-80%)": db.query(Image).filter(Image.quality_score >= 0.5, Image.quality_score < 0.8).count(),
        "High (>80%)": db.query(Image).filter(Image.quality_score >= 0.8).count()
    }
    
    return {
        "events_timeline": [{"date": str(r.date), "count": r.count} for r in events_by_date],
        "posts_timeline": [{"date": str(r.date), "count": r.count} for r in posts_by_date],
        "quality_distribution": quality_ranges
    }

@app.get("/api/activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """Get recent activities for dashboard widget"""
    activities = []
    
    # Get last 5 successful posts
    posts = db.query(Post).filter(Post.status == "success").order_by(Post.posted_at.desc()).limit(5).all()
    for post in posts:
        event = db.query(Event).filter(Event.id == post.event_id).first()
        activities.append({
            "type": "post",
            "title": f"LinkedIn Post Shared",
            "subtitle": f"{post.num_images} photos from {event.name if event else 'Unknown Event'}",
            "time": post.posted_at.isoformat(),
            "status": "success",
            "id": post.id
        })
    
    # Get last 5 events
    events = db.query(Event).order_by(Event.created_at.desc()).limit(5).all()
    for event in events:
        activities.append({
            "type": "event",
            "title": f"New Event Created",
            "subtitle": f"{event.total_uploaded} photos uploaded",
            "time": event.created_at.isoformat(),
            "status": "info",
            "id": event.id
        })
    
    # Sort combined activities by time
    activities.sort(key=lambda x: x["time"], reverse=True)
    
    return {"activities": activities[:5]}

@app.get("/api/events")
async def get_events_history(db: Session = Depends(get_db)):
    """Get all events with their summary details"""
    events = db.query(Event).order_by(Event.created_at.desc()).all()
    
    results = []
    for event in events:
        # Check if this event has any successful posts
        post = db.query(Post).filter(Post.event_id == event.id, Post.status == "success").first()
        
        results.append({
            "id": event.id,
            "name": event.name,
            "created_at": event.created_at.isoformat(),
            "total_uploaded": event.total_uploaded,
            "total_selected": event.total_selected,
            "user_email": event.user_email,
            "status": "Posted" if post else "Draft",
            "post_id": post.id if post else None
        })
        
    return {"events": results}


# ============= Health Check =============

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
