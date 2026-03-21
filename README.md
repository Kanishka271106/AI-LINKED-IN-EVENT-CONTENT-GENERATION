# AI-Driven LinkedIn Event Content Generation

An intelligent web application that automatically curates, enhances, and posts event photos to LinkedIn, saving professionals hours of manual work.

## 🎯 Problem Statement

Professionals spend 2-3 hours per event manually selecting, editing, and posting photos to LinkedIn. This application automates the entire process using AI-powered quality assessment, resulting in consistent, professional content sharing.

## ✨ Key Features

- **AI Quality Assessment**: Automatically evaluates images based on sharpness, composition, and lighting
- **Duplicate & Blur Removal**: Filters out low-quality and redundant images
- **Smart Selection**: Curates the top 10 shareable images from your event photos
- **Manual Override Controls**: Review and adjust AI selections before posting
- **LinkedIn Integration**: Direct posting to your personal LinkedIn profile
- **Audit Logging**: Tracks all activities for accountability

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- LinkedIn Developer Account (for API access)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Kanishka271106/AI-LINKED-IN-EVENT-CONTENT-GENERATION.git
cd AI-LINKED-IN-EVENT-CONTENT-GENERATION
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env with your LinkedIn API credentials
```

### LinkedIn API Setup

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click **"Create app"**
3. Fill in your application details:
   - App name: "Event Photo Curator"
   - LinkedIn Page: Select or create a page
   - App logo: Upload a logo (optional)
4. In the **"Auth"** tab:
   - Add Redirect URL: `http://localhost:8000/auth/linkedin/callback`
5. In the **"Products"** tab:
   - Request access to **"Share on LinkedIn"** and **"Sign In with LinkedIn"**
6. Copy your **Client ID** and **Client Secret** to `.env` file

### Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. The application will be ready to use!

## 📖 How to Use

1. **Upload Photos**: Click the upload area and select 10-15 event photos
2. **AI Processing**: The system automatically:
   - Analyzes image quality (sharpness, lighting, composition)
   - Removes blurry and duplicate images
   - Selects the top 10 images
3. **Review & Override**: Manually deselect/reselect images if needed
4. **Connect LinkedIn**: Authorize the app to post on your behalf
5. **Post**: Click "Post to LinkedIn" to share selected images

## 🏗️ Project Structure

```
AI-Driven-LinkedIn-Event-Content-Generation/
├── backend/
│   ├── database.py          # Database setup and models
│   ├── image_processor.py   # AI quality assessment & processing
│   ├── linkedin_api.py      # LinkedIn OAuth and posting
│   └── models.py            # SQLAlchemy models
├── static/
│   ├── css/
│   │   └── styles.css       # Frontend styling
│   └── js/
│       └── app.js           # Frontend logic
├── templates/
│   └── index.html           # Main web interface
├── uploads/                 # Uploaded images (auto-created)
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## 🔧 Configuration

Edit `.env` file to customize:

- `QUALITY_THRESHOLD`: Minimum quality score (0-1, default: 0.6)
- `MAX_SELECTED_IMAGES`: Number of images to select (default: 10)
- `BLUR_THRESHOLD`: Blur detection sensitivity (lower = stricter)
- `DUPLICATE_THRESHOLD`: Similarity threshold for duplicates

## 📊 Technical Details

### Image Quality Metrics

- **Sharpness**: Laplacian variance (detects blur)
- **Brightness**: Mean luminance analysis
- **Contrast**: Standard deviation of pixel values
- **Composition**: Face detection and rule-of-thirds
- **Duplicate Detection**: Perceptual hashing (imagehash)

### Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Image Processing**: OpenCV, Pillow, scikit-image
- **Database**: SQLite with SQLAlchemy ORM
- **API Integration**: LinkedIn OAuth 2.0

## 🎨 Design Philosophy

Super-polished corporate aesthetic with:
- Professional color scheme
- Clean, intuitive interface
- Responsive design
- Accessibility considerations

## 📝 API Endpoints

- `POST /upload` - Upload event photos
- `GET /images` - Retrieve processed images
- `POST /process` - Trigger AI processing
- `POST /select` - Update image selection
- `GET /auth/linkedin` - Initiate LinkedIn OAuth
- `GET /auth/linkedin/callback` - Handle OAuth callback
- `POST /post/linkedin` - Post selected images to LinkedIn
- `GET /logs` - Retrieve audit logs

## 🔒 Privacy & Security

- Images processed locally on your machine
- No data sent to external services (except LinkedIn API)
- Audit logs stored in local database
- OAuth tokens securely managed

## 🐛 Troubleshooting

**LinkedIn authentication fails:**
- Verify redirect URI matches exactly in LinkedIn Developer portal
- Check client ID and secret in `.env`

**Images not processing:**
- Ensure images are JPEG/PNG format
- Check file size limits (50MB total recommended)

**Poor quality results:**
- Adjust `QUALITY_THRESHOLD` in `.env`
- Try with higher resolution images

## 📈 Success Metrics

- **Time Saved**: Reduces photo selection time from 2-3 hours to minutes
- **Quality**: Ensures only professional-grade images are posted
- **Consistency**: Standardized selection criteria

## 🤝 Contributing

This is a personal project for friends and staff. Feel free to suggest improvements!

## 📄 License

Free to use for personal and internal purposes.

## 👤 Author

**Kanishka**  
GitHub: https://github.com/Kanishka271106

---

Built with ❤️ to save time and boost professional presence on LinkedIn
