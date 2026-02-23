# 🧪 Testing Checklist

## Pre-Testing Setup

### ✅ Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with LinkedIn credentials
- [ ] LinkedIn Developer app created
- [ ] Redirect URI added: `http://localhost:8000/auth/linkedin/callback`
- [ ] "Share on LinkedIn" and "Sign In with LinkedIn" products approved

---

## 🔍 Test Cases

### 1. Application Startup
- [ ] Run `python main.py`
- [ ] No error messages displayed
- [ ] Server starts on port 8000
- [ ] Console shows "Server ready at http://localhost:8000"
- [ ] Open http://localhost:8000 in browser
- [ ] Page loads correctly
- [ ] No console errors in browser DevTools

### 2. Initial Page Load
- [ ] Header displays correctly
- [ ] Logo and title visible
- [ ] Auth status shows "Not Connected"
- [ ] "Connect LinkedIn" button present
- [ ] Hero section displays
- [ ] Statistics show "0" for all metrics
- [ ] Upload area is visible and clickable
- [ ] Footer displays

### 3. LinkedIn Authentication
- [ ] Click "Connect LinkedIn" button
- [ ] LinkedIn OAuth page opens in new window/tab
- [ ] Login to LinkedIn (if not already logged in)
- [ ] Authorization page displays app name and permissions
- [ ] Click "Allow" to authorize
- [ ] Redirected back to application
- [ ] Auth status badge changes to "Connected" (green)
- [ ] Button text changes to "Reconnect LinkedIn"
- [ ] Toast notification shows success message

### 4. File Upload - Valid Files
**Test with 10 JPEG/PNG images**

- [ ] Click upload area
- [ ] File picker opens
- [ ] Select 10 valid image files
- [ ] Upload starts immediately
- [ ] Progress bar appears
- [ ] Progress bar animates from 0% to 100%
- [ ] Progress text updates ("Uploading...", "Processing...", "Complete!")
- [ ] No error messages

### 5. AI Processing Results
- [ ] Processing completes in reasonable time (~10-20 seconds)
- [ ] Summary section appears
- [ ] Summary shows correct counts:
  - [ ] Total uploaded = 10
  - [ ] High quality count shown
  - [ ] Blurry count shown
  - [ ] Duplicates count shown
  - [ ] Selected count shown (should be ≤10)
- [ ] Gallery section appears
- [ ] All images displayed in grid
- [ ] Each image card shows:
  - [ ] Image thumbnail
  - [ ] Quality metrics (quality, sharpness, brightness)
  - [ ] Quality bar (colored)
  - [ ] Badges if applicable (blur, duplicate, selected)
  - [ ] Checkbox indicator

### 6. Image Quality Assessment
**Verify AI is working correctly**

Upload test images:
- [ ] Sharp, well-lit image → High quality score (>70%)
- [ ] Blurry image → Marked as "Blurry" badge
- [ ] Dark image → Lower brightness score
- [ ] Two identical images → One marked as "Duplicate"
- [ ] High quality images auto-selected

### 7. Manual Selection Override
- [ ] Click on a selected image
- [ ] Image becomes deselected (blue border removed)
- [ ] "Selected" badge disappears
- [ ] Selected count decreases
- [ ] Click again to reselect
- [ ] Image becomes selected (blue border appears)
- [ ] "Selected" badge reappears
- [ ] Selected count increases
- [ ] Changes reflected in summary section

### 8. Gallery Filters
- [ ] Click "Show Selected Only" button
- [ ] Only selected images remain visible
- [ ] Button changes style to indicate active
- [ ] Click "Show All" button
- [ ] All images become visible again
- [ ] Button changes style to indicate active

### 9. Post to LinkedIn - Unauthenticated
- [ ] Clear LinkedIn authentication (or start fresh)
- [ ] Upload and process images
- [ ] "Post to LinkedIn" button is disabled
- [ ] Clicking does nothing

### 10. Post to LinkedIn - Authenticated
**Prerequisites: LinkedIn connected, images selected**

- [ ] At least 1 image selected
- [ ] "Post to LinkedIn" button is enabled (blue)
- [ ] Enter optional caption in text area
- [ ] Click "Post to LinkedIn" button
- [ ] Loading overlay appears with spinner
- [ ] "Posting to LinkedIn..." text shown
- [ ] Wait for completion (5-15 seconds)
- [ ] Loading overlay disappears
- [ ] Success toast notification appears
- [ ] Check LinkedIn profile - post should be visible
- [ ] Post contains selected images
- [ ] Caption (if entered) is displayed

### 11. Multiple Image Post
- [ ] Select 5-9 images
- [ ] Post to LinkedIn
- [ ] All selected images included in post
- [ ] Images display correctly on LinkedIn

### 12. Statistics Update
- [ ] After first upload, stats should update:
  - [ ] Total Events = 1
  - [ ] Total Images > 0
- [ ] After first post, stats should update:
  - [ ] Total Posts = 1

### 13. Error Handling - Invalid Files
- [ ] Try to upload non-image files (PDF, TXT, etc.)
- [ ] Error toast appears
- [ ] No processing occurs

### 14. Error Handling - Too Many Files
- [ ] Try to upload 21+ files
- [ ] Error toast appears: "Maximum 20 files allowed"
- [ ] Upload rejected

### 15. Error Handling - No Files
- [ ] Click upload without selecting files
- [ ] Error toast appears
- [ ] No processing occurs

### 16. Error Handling - Network Issues
- [ ] Disconnect from internet
- [ ] Try to post to LinkedIn
- [ ] Error message displayed
- [ ] Loading overlay closes

### 17. Responsive Design
- [ ] Resize browser window to mobile size (375px width)
- [ ] Layout adjusts appropriately
- [ ] All elements still accessible
- [ ] Images stack in single column
- [ ] Buttons remain clickable

### 18. Database Persistence
- [ ] Upload and process images
- [ ] Note the event ID in console/network tab
- [ ] Restart the server
- [ ] Check database file exists (`linkedin_event_curator.db`)
- [ ] Data should persist between restarts

### 19. Multiple Sessions
- [ ] Complete first upload/post workflow
- [ ] Upload new set of images (don't refresh page)
- [ ] Process second set
- [ ] Both events should be tracked separately
- [ ] Statistics should reflect both events

### 20. Drag and Drop Upload
- [ ] Open file explorer
- [ ] Drag 10 images over upload area
- [ ] Upload area highlights (border change)
- [ ] Drop images
- [ ] Upload starts automatically
- [ ] Processing begins

---

## 🐛 Known Edge Cases to Test

### Edge Case 1: All Images Blurry
- [ ] Upload only blurry images
- [ ] All marked as blurry
- [ ] 0 images auto-selected
- [ ] User must manually select some
- [ ] Post button disabled if none selected

### Edge Case 2: All Images Duplicates
- [ ] Upload same image 10 times
- [ ] First one kept, others marked as duplicates
- [ ] Only 1 image auto-selected
- [ ] Can manually select duplicates if desired

### Edge Case 3: LinkedIn Token Expired
- [ ] Wait for token to expire (or manually delete from database)
- [ ] Try to post
- [ ] Error message: "LinkedIn token expired"
- [ ] Prompted to re-authenticate

### Edge Case 4: Very Large Images
- [ ] Upload high-resolution images (10+ MB each)
- [ ] Processing takes longer but completes
- [ ] Images display correctly (thumbnails generated)
- [ ] Posting works

### Edge Case 5: Special Characters in Filenames
- [ ] Upload images with special characters: `photo #1 (copy).jpg`
- [ ] Files upload successfully
- [ ] Filenames display correctly
- [ ] No errors

---

## 🔍 Code Quality Checks

### Backend
- [ ] Run application with DEBUG=True
- [ ] No deprecation warnings
- [ ] No unhandled exceptions
- [ ] All imports resolve correctly
- [ ] Database migrations work

### Frontend
- [ ] Open browser DevTools Console
- [ ] No JavaScript errors
- [ ] No CORS errors
- [ ] All API calls succeed
- [ ] Network tab shows 200 status codes

### Performance
- [ ] Page loads in < 2 seconds
- [ ] Image processing takes < 30 seconds for 15 images
- [ ] No memory leaks (check Task Manager during processing)
- [ ] UI remains responsive during processing

---

## 📊 Test Results Template

```
Test Date: _______________
Tester: __________________
Environment: _____________

✅ = Pass
❌ = Fail
⚠️ = Warning/Issue

| Test Case | Status | Notes |
|-----------|--------|-------|
| Application Startup | ✅ | |
| Initial Page Load | ✅ | |
| LinkedIn Auth | ✅ | |
| File Upload | ✅ | |
| AI Processing | ✅ | |
| Quality Assessment | ✅ | |
| Manual Selection | ✅ | |
| Gallery Filters | ✅ | |
| Post to LinkedIn | ✅ | |
| Error Handling | ✅ | |
| Responsive Design | ✅ | |
| Database Persistence | ✅ | |

Overall Status: ✅ PASS / ❌ FAIL
```

---

## 🎯 Acceptance Criteria

All tests must pass before considering the application ready for use:

### Critical Tests (Must Pass)
- ✅ Application starts without errors
- ✅ LinkedIn authentication works
- ✅ File upload and processing completes
- ✅ AI quality assessment produces results
- ✅ Images can be selected/deselected
- ✅ Posting to LinkedIn succeeds
- ✅ No data loss or corruption

### Important Tests (Should Pass)
- ✅ Error messages display correctly
- ✅ UI is responsive and intuitive
- ✅ Performance is acceptable
- ✅ Statistics update correctly

### Nice to Have (Optional)
- ⚠️ Handles all edge cases gracefully
- ⚠️ Perfect on all screen sizes
- ⚠️ Optimal performance

---

## 🚀 Quick Test Script

For rapid testing, follow this sequence:

1. **Start:** `python main.py`
2. **Open:** http://localhost:8000
3. **Auth:** Click "Connect LinkedIn" → Authorize
4. **Upload:** Drag 10 images to upload area
5. **Wait:** Processing completes (~20 sec)
6. **Review:** Check quality scores and selections
7. **Adjust:** Toggle 2-3 image selections
8. **Caption:** Add test caption: "Test post from Event Photo Curator"
9. **Post:** Click "Post to LinkedIn"
10. **Verify:** Check LinkedIn profile for post
11. **Success:** ✅

**Total test time: ~5 minutes**

---

## 📝 Test Data Recommendations

### Good Test Image Set (10 images)
- 3 high-quality, sharp, well-lit photos
- 2 slightly blurry photos
- 1 very blurry photo
- 2 similar/duplicate photos
- 1 dark/underexposed photo
- 1 overexposed photo

This gives good coverage of AI capabilities!

---

## ✅ Sign-Off

- [ ] All critical tests passed
- [ ] All important tests passed
- [ ] Edge cases handled appropriately
- [ ] Performance is acceptable
- [ ] Documentation is accurate
- [ ] Ready for production use

**Tested by:** _______________  
**Date:** _______________  
**Status:** ✅ APPROVED / ❌ NEEDS WORK
