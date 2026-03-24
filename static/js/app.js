// ==================== Application State ====================
let currentEventId = null;
let allImages = [];
let selectedImageCount = 0;
let isAuthenticated = false;

// ==================== DOM Elements ====================
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFilesBtn = document.getElementById('selectFilesBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const summarySection = document.getElementById('summarySection');
const gallerySection = document.getElementById('gallerySection');
const imageGrid = document.getElementById('imageGrid');
const postSection = document.getElementById('postSection');
const linkedinAuthBtn = document.getElementById('linkedinAuthBtn');
const authStatusBadge = document.getElementById('authStatusBadge');
const authStatusText = document.getElementById('authStatusText');
const postToLinkedInBtn = document.getElementById('postToLinkedInBtn');
const postCaption = document.getElementById('postCaption');
const selectedCount = document.getElementById('selectedCount');
const showAllBtn = document.getElementById('showAllBtn');
const showSelectedBtn = document.getElementById('showSelectedBtn');
const toastContainer = document.getElementById('toastContainer');
const loadingOverlay = document.getElementById('loadingOverlay');
const generateCaptionBtn = document.getElementById('generateCaptionBtn');
// const postCaption = document.getElementById('postCaption'); // This was the duplicate
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const themeToggleText = document.getElementById('themeToggleText');
const navOverview = document.getElementById('navOverview');
const navEvents = document.getElementById('navEvents');
const navAnalytics = document.getElementById('navAnalytics');
const viewOverview = document.getElementById('viewOverview');
const viewEvents = document.getElementById('viewEvents');
const viewAnalytics = document.getElementById('viewAnalytics');
const eventsHistoryTable = document.getElementById('eventsHistoryTable');
const historySearch = document.getElementById('historySearch');
const includeHashtags = document.getElementById('includeHashtags');
const customHashtags = document.getElementById('customHashtags');
const customHashtagsContainer = document.getElementById('customHashtagsContainer');
const eventType = document.getElementById('eventType');
const postVibe = document.getElementById('postVibe');

const detailsModal = document.getElementById('detailsModal');
const detailsGallery = document.getElementById('detailsGallery');
const closeDetailsBtn = document.getElementById('closeDetailsBtn');
const backToHistoryBtn = document.getElementById('backToHistoryBtn');

const editorModal = document.getElementById('editorModal');
const editorImage = document.getElementById('editorImage');
const eraseCanvas = document.getElementById('eraseCanvas');
const closeEditorBtn = document.getElementById('closeEditorBtn');
const cancelEditBtn = document.getElementById('cancelEditBtn');
const saveEditBtn = document.getElementById('saveEditBtn');
const toolCrop = document.getElementById('toolCrop');
const toolErase = document.getElementById('toolErase');
const toolAutoEnhance = document.getElementById('toolAutoEnhance');
const brightnessRange = document.getElementById('brightnessRange');
const contrastRange = document.getElementById('contrastRange');
const saturationRange = document.getElementById('saturationRange');

// ==================== Editor State ====================
let cropper = null;
let currentEditIndex = null;
let isErasing = false;
let ctx = null;
let lastX = 0;
let lastY = 0;

// ==================== Initialize Application ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    console.log('Initializing Dashboard...');

    // Attach listeners FIRST so UI is interactive immediately
    try {
        setupEventListeners();
        console.log('Event listeners attached.');
    } catch (e) {
        console.error('CRITICAL: Event listeners failed:', e);
    }

    // Load data in parallel without blocking UI
    Promise.all([
        checkAuthStatus().catch(e => console.error('Auth check failed:', e)),
        loadStats().catch(e => console.error('Stats load failed:', e)),
        loadRecentActivity().catch(e => console.error('Activity load failed:', e))
    ]).then(() => {
        try { checkAuthQueryParam(); } catch (e) { console.error('Auth query check failed:', e); }
        updateUploadUI();
    });

    console.log('Dashboard base initialization complete.');
}

// ==================== Event Listeners ====================
function setupEventListeners() {
    // Upload area interactions
    selectFilesBtn.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // LinkedIn authentication
    linkedinAuthBtn.addEventListener('click', initiateLinkedInAuth);

    // Post to LinkedIn


    // Gallery filters
    showAllBtn.addEventListener('click', () => filterImages('all'));
    showSelectedBtn.addEventListener('click', () => filterImages('selected'));

    // Generate Caption
    generateCaptionBtn.addEventListener('click', generateCaption);

    // Include Hashtags and Context settings
    includeHashtags.addEventListener('change', savePreferences);
    customHashtags.addEventListener('change', savePreferences);

    // Toggle custom hashtags visibility
    includeHashtags.addEventListener('change', () => {
        customHashtagsContainer.style.display = includeHashtags.checked ? 'block' : 'none';
    });

    // Editor actions
    closeEditorBtn.addEventListener('click', closeEditor);
    cancelEditBtn.addEventListener('click', closeEditor);
    saveEditBtn.addEventListener('click', saveEdits);

    // Tool buttons
    toolCrop.addEventListener('click', () => setTool('crop'));
    toolErase.addEventListener('click', () => setTool('erase'));
    toolAutoEnhance.addEventListener('click', toggleAutoEnhance);

    // Adjustment ranges
    [brightnessRange, contrastRange, saturationRange].forEach(range => {
        range.addEventListener('input', updateImageFilters);
    });

    // Erase canvas handlers
    eraseCanvas.addEventListener('mousedown', startErasing);
    eraseCanvas.addEventListener('mousemove', drawErase);
    eraseCanvas.addEventListener('mouseup', stopErasing);
    eraseCanvas.addEventListener('mouseout', stopErasing);

    // Sidebar Navigation
    console.log('Attaching sidebar listeners...', { navOverview, navEvents, navAnalytics });
    if (navOverview) navOverview.addEventListener('click', (e) => { console.log('Overview clicked'); e.preventDefault(); switchView('overview'); });
    if (navEvents) navEvents.addEventListener('click', (e) => { console.log('Events clicked'); e.preventDefault(); switchView('events'); });
    if (navAnalytics) navAnalytics.addEventListener('click', (e) => { e.preventDefault(); switchView('analytics'); });
    
    // Theme Toggle
    if (themeToggle) themeToggle.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
    });

    // Check for saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeUI(true);
    }

    // History Search
    if (historySearch) historySearch.addEventListener('input', debounce(filterHistory, 300));

    // Details Modal
    if (closeDetailsBtn) closeDetailsBtn.addEventListener('click', () => detailsModal.style.display = 'none');
    if (backToHistoryBtn) backToHistoryBtn.addEventListener('click', () => detailsModal.style.display = 'none');
}

// ==================== Preferences Handlers ====================
async function loadPreferences() {
    try {
        const response = await fetch('/api/preferences');
        const data = await response.json();

        includeHashtags.checked = data.include_hashtags;
        customHashtags.value = data.custom_hashtags || '';
        
        if (data.event_type && eventType) eventType.value = data.event_type;
        if (data.post_vibe && postVibe) postVibe.value = data.post_vibe;

        // Update visibility
        customHashtagsContainer.style.display = data.include_hashtags ? 'block' : 'none';
    } catch (error) {
        console.error('Failed to load preferences:', error);
    }
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeUI(isDark);
}

function updateThemeUI(isDark) {
    if (isDark) {
        themeToggleText.textContent = 'Light Mode';
        // Change to Sun icon
        themeIcon.innerHTML = `
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        `;
    } else {
        themeToggleText.textContent = 'Dark Mode';
        // Change to Moon icon
        themeIcon.innerHTML = `
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"></path>
        `;
    }
}

async function savePreferences() {
    try {
        const payload = {
            include_hashtags: includeHashtags.checked,
            custom_hashtags: customHashtags.value,
            event_type: eventType.value,
            post_vibe: postVibe.value
        };

        console.log('Saving preferences:', payload);

        const response = await fetch('/api/preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Failed to save preferences');
    } catch (error) {
        console.error('Save preferences error:', error);
        showToast('Failed to save settings', 'error');
    }
}

// ==================== File Upload Handlers ====================
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    processFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    processFiles(files);
}

async function processFiles(files) {
    if (!isAuthenticated) {
        showToast('Please connect to LinkedIn first!', 'warning');
        return;
    }

    if (!files || files.length === 0) {
        showToast('Please select at least one image', 'error');
        return;
    }

    if (files.length > 20) {
        showToast('Maximum 20 files allowed', 'error');
        return;
    }

    // Validate file types
    const validFiles = Array.from(files).filter(file =>
        file.type.startsWith('image/')
    );

    if (validFiles.length === 0) {
        showToast('Please select valid image files', 'error');
        return;
    }

    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading images (0%)...';

    // Create FormData
    const formData = new FormData();
    validFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        const xhr = new XMLHttpRequest();

        // Track REAL upload progress
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = `${percentComplete}%`;
                progressText.textContent = `Uploading images (${percentComplete}%)...`;

                if (percentComplete === 100) {
                    progressText.textContent = 'Processing with AI (Hang tight)...';
                    progressFill.classList.add('processing'); // Add a pulse effect via CSS if exists
                }
            }
        };

        const uploadPromise = new Promise((resolve, reject) => {
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        resolve(JSON.parse(xhr.responseText));
                    } catch (e) {
                        reject(new Error('Failed to parse response'));
                    }
                } else {
                    reject(new Error(`Upload failed with status ${xhr.status}`));
                }
            };
            xhr.onerror = () => reject(new Error('Network error during upload'));
            xhr.onabort = () => reject(new Error('Upload aborted'));
        });

        xhr.open('POST', '/api/upload');
        xhr.timeout = 120000; // 2 minute timeout for large batches
        
        xhr.ontimeout = () => {
            reject(new Error('Upload timed out. Try fewer images or check your connection.'));
        };

        xhr.send(formData);

        const data = await uploadPromise;

        progressText.textContent = 'Complete!';
        progressFill.style.width = '100%';
        progressFill.classList.remove('processing');

        // Store event data
        currentEventId = data.event_id;
        allImages = data.images;
        selectedImageCount = data.total_selected;

        // Display results
        displaySummary(data.summary);
        displayImages(allImages);
        updateSelectedCount();

        // Show sections
        setTimeout(() => {
            summarySection.style.display = 'block';
            gallerySection.style.display = 'block';
            progressContainer.style.display = 'none';

            // Scroll to summary
            summarySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 800);

        showToast('Images processed successfully!', 'success');

    } catch (error) {
        console.error('Upload error:', error);
        showToast(error.message || 'Failed to upload images. Please try again.', 'error');
        progressContainer.style.display = 'none';
        progressFill.classList.remove('processing');
    }
}

function animateProgress(from, to, duration) {
    const start = Date.now();
    const animate = () => {
        const now = Date.now();
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const currentProgress = from + (to - from) * progress;

        progressFill.style.width = `${currentProgress}%`;

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    animate();
}

// ==================== Display Functions ====================
function displaySummary(summary) {
    document.getElementById('summaryTotal').textContent = summary.total;
    document.getElementById('summaryHighQuality').textContent = summary.high_quality;
    document.getElementById('summaryDuplicates').textContent = summary.duplicates;
    document.getElementById('summarySelected').textContent = summary.selected;
}

function displayImages(images) {
    imageGrid.innerHTML = '';

    images.forEach((image, index) => {
        const imageCard = createImageCard(image, index);
        imageGrid.appendChild(imageCard);
    });
}

function createImageCard(image, index) {
    const card = document.createElement('div');
    card.className = `image-card ${image.is_selected ? 'selected' : ''} ${image.is_blur ? 'blurry' : ''} ${image.is_duplicate ? 'duplicate' : ''}`;
    card.dataset.imageIndex = index;

    // Build badges
    let badges = '';
    if (image.is_blur) {
        badges += '<span class="badge badge-blur">Blurry</span>';
    }
    if (image.is_duplicate) {
        badges += '<span class="badge badge-duplicate">Duplicate</span>';
    }
    if (image.is_selected) {
        badges += '<span class="badge badge-selected">Selected</span>';
    }

    card.innerHTML = `
        <div class="image-wrapper">
            <img src="${image.url}" alt="${image.filename}" loading="lazy">
            <div class="image-overlay"></div>
            ${badges ? `<div class="image-badges">${badges}</div>` : ''}
            <div class="select-checkbox">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </div>
            <button class="enhance-btn ${(image.url && (image.url.includes('_enhanced') || image.url.includes('_edited'))) ? 'enhanced' : ''}" 
                    title="${(image.url && (image.url.includes('_enhanced') || image.url.includes('_edited'))) ? 'Enhanced' : 'Enhance Image'}"
                    onclick="event.stopPropagation(); enhanceImage(${index}, this)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
                </svg>
            </button>
            <button class="edit-btn" title="Edit Photo" onclick="event.stopPropagation(); openEditor(${index})">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
            </button>
        </div>
        <div class="image-info">
            <div class="image-filename" title="${image.filename}">${image.filename}</div>
            <div class="image-metrics">
                <div class="metric">
                    <span class="metric-label">Quality</span>
                    <span class="metric-value">${Math.round(image.quality_score * 100)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Sharpness</span>
                    <span class="metric-value">${Math.round(image.sharpness_score * 100)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Brightness</span>
                    <span class="metric-value">${Math.round(image.brightness_score * 100)}%</span>
                </div>
            </div>
            <div class="quality-bar">
                <div class="quality-fill" style="width: ${image.quality_score * 100}%"></div>
            </div>
        </div>
    `;

    // Add click handler
    card.addEventListener('click', () => toggleImageSelection(index));

    return card;
}

async function toggleImageSelection(index) {
    const image = allImages[index];

    try {
        // Update on server - use the actual database ID
        const response = await fetch(`/api/images/${image.id}/toggle-select`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Failed to toggle selection');
        }

        const data = await response.json();

        // Update local state
        image.is_selected = data.is_selected;
        selectedImageCount = data.total_selected;

        // Update UI
        const card = document.querySelector(`[data-image-index="${index}"]`);
        if (data.is_selected) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }

        // Update badges
        const badges = card.querySelector('.image-badges');
        if (badges) {
            const selectedBadge = badges.querySelector('.badge-selected');
            if (data.is_selected && !selectedBadge) {
                badges.innerHTML += '<span class="badge badge-selected">Selected</span>';
            } else if (!data.is_selected && selectedBadge) {
                selectedBadge.remove();
            }
        } else if (data.is_selected) {
            const imageWrapper = card.querySelector('.image-wrapper');
            const badgesDiv = document.createElement('div');
            badgesDiv.className = 'image-badges';
            badgesDiv.innerHTML = '<span class="badge badge-selected">Selected</span>';
            imageWrapper.appendChild(badgesDiv);
        }

        updateSelectedCount();

    } catch (error) {
        console.error('Toggle error:', error);
        showToast('Failed to update selection', 'error');
    }
}

async function enhanceImage(index, btn) {
    const image = allImages[index];
    const originalId = image.id;

    if (!originalId) {
        showToast('Image ID missing. Please refresh and try again.', 'error');
        return;
    }

    // Check if it's already being enhanced
    if (btn.classList.contains('loading')) return;

    btn.classList.add('loading');

    try {
        const response = await fetch(`/api/images/${originalId}/enhance`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Enhancement failed');
        }

        const data = await response.json();

        // Update local state
        image.url = data.url;
        image.filepath = data.filename; // Use for checking '_enhanced'

        // Update UI
        const card = document.querySelector(`[data-image-index="${index}"]`);
        const img = card.querySelector('img');

        // Add a small fade effect during reload
        img.style.opacity = '0.5';
        img.src = `${data.url}?t=${Date.now()}`; // Cache busting
 
        img.onload = () => {
            img.style.opacity = '1';
            btn.classList.remove('loading');
            btn.classList.add('enhanced');
            btn.title = 'Enhanced';
            showToast('Super-Premium Enhancement Applied!', 'success');
        };

    } catch (error) {
        console.error('Enhance error:', error);
        btn.classList.remove('loading');
        showToast('Failed to enhance image', 'error');
    }
}

function updateSelectedCount() {
    selectedCount.textContent = selectedImageCount;
    document.getElementById('summarySelected').textContent = selectedImageCount;

    // Enable post button if photos are selected (even if not connected yet)
    if (selectedImageCount > 0) {
        postToLinkedInBtn.disabled = false;
    } else {
        postToLinkedInBtn.disabled = true;
    }
}

function filterImages(filter) {
    const cards = document.querySelectorAll('.image-card');

    cards.forEach(card => {
        if (filter === 'all') {
            card.classList.remove('hidden');
        } else if (filter === 'selected') {
            if (card.classList.contains('selected')) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        }
    });

    // Update button states
    if (filter === 'all') {
        showAllBtn.classList.add('btn-primary');
        showAllBtn.classList.remove('btn-secondary');
        showSelectedBtn.classList.add('btn-secondary');
        showSelectedBtn.classList.remove('btn-primary');
    } else {
        showSelectedBtn.classList.add('btn-primary');
        showSelectedBtn.classList.remove('btn-secondary');
        showAllBtn.classList.add('btn-secondary');
        showAllBtn.classList.remove('btn-primary');
    }
}

// ==================== LinkedIn Authentication ====================
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        console.log("Auth status check complete. Authenticated:", data.authenticated);
        isAuthenticated = data.authenticated;

        if (isAuthenticated) {
            authStatusBadge.classList.remove('disconnected');
            authStatusBadge.classList.add('connected');
            authStatusText.textContent = `Connected as ${data.user_email || 'LinkedIn Member'}`;
            linkedinAuthBtn.textContent = 'Change Account';
            postToLinkedInBtn.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
                Post to LinkedIn
            `;
            // If they are connected, clicking the post button will only post
            postToLinkedInBtn.onclick = postToLinkedIn;
        } else {
            authStatusBadge.classList.remove('connected');
            authStatusBadge.classList.add('disconnected');
            authStatusText.textContent = 'Not Connected';
            linkedinAuthBtn.textContent = 'Connect LinkedIn';
            postToLinkedInBtn.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M24 12c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.248h3.328l-.532 3.47h-2.796v8.385C19.612 22.954 24 17.99 24 12z"/>
                </svg>
                Connect LinkedIn
            `;
            // If they are NOT connected, clicking the post button will only connect
            postToLinkedInBtn.onclick = initiateLinkedInAuth;
        }

        updateSelectedCount();
        updateUploadUI();

    } catch (error) {
        console.error('Auth check error:', error);
    }
}

async function initiateLinkedInAuth() {
    return new Promise(async (resolve, reject) => {
        try {
            console.log("Initiating LinkedIn Auth...");
            const response = await fetch('/api/auth/linkedin');
            const data = await response.json();

            if (!data.auth_url || data.auth_url.includes("client_id=None")) {
                showToast('Configuration Error: Missing LinkedIn Client ID', 'error');
                return reject(new Error('Missing Client ID'));
            }

            // Open LinkedIn OAuth in new window
            const width = 600;
            const height = 700;
            const left = (screen.width - width) / 2;
            const top = (screen.height - height) / 2;

            const authWindow = window.open(
                data.auth_url,
                'LinkedIn Authentication',
                `width=${width},height=${height},left=${left},top=${top}`
            );

            // Poll for authentication completion
            const pollInterval = setInterval(async () => {
                console.log("Polling for auth status...");
                await checkAuthStatus();
                if (isAuthenticated) {
                    console.log("Auth detected! Clearing poll...");
                    clearInterval(pollInterval);
                    showToast('Successfully connected to LinkedIn!', 'success');
                    resolve(true);
                }
                
                // If window is closed and we are NOT authenticated yet, keep polling for 5 more seconds 
                // just in case the server is slow to process the callback.
                if (authWindow.closed && !isAuthenticated) {
                    console.log("Auth window closed. Final check...");
                    setTimeout(async () => {
                        await checkAuthStatus();
                        if (isAuthenticated) {
                            clearInterval(pollInterval);
                            resolve(true);
                        } else {
                            clearInterval(pollInterval);
                            reject(new Error('Authentication window closed'));
                        }
                    }, 5000);
                    // Prevent further polling while waiting for the final check
                    clearInterval(pollInterval);
                }
            }, 2000);

            // Stop polling after 5 minutes
            setTimeout(() => {
                clearInterval(pollInterval);
                reject(new Error('Authentication timeout'));
            }, 300000);

        } catch (error) {
            console.error('LinkedIn auth error:', error);
            showToast('Failed to initiate LinkedIn authentication', 'error');
            reject(error);
        }
    });
}

function checkAuthQueryParam() {
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get('auth');

    if (authStatus === 'success') {
        showToast('Successfully connected to LinkedIn!', 'success');
        checkAuthStatus();
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authStatus === 'error') {
        const reason = urlParams.get('reason');
        const detail = urlParams.get('detail') || urlParams.get('desc');
        let msg = 'LinkedIn authentication failed';
        if (reason) msg += `: ${reason}`;
        if (detail) msg += ` (${detail})`;

        showToast(msg, 'error');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ==================== Caption Generation ====================
async function generateCaption(silent = false) {
    if (!currentEventId) {
        if (!silent) showToast('Please upload images first', 'error');
        return null;
    }

    const btn = generateCaptionBtn;
    const originalText = btn.innerHTML;
    const customContext = postCaption.value.trim();

    try {
        if (!silent) {
            btn.classList.add('btn-loading');
            btn.disabled = true;
        }

        const response = await fetch('/api/generate-caption', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_id: currentEventId,
                custom_context: customContext || null,
                event_type: eventType.value,
                post_vibe: postVibe.value
            })
        });

        if (!response.ok) throw new Error('Failed to generate caption');

        const data = await response.json();
        postCaption.value = data.caption;
        
        if (!silent) {
            postCaption.scrollIntoView({ behavior: 'smooth', block: 'center' });
            showToast('Caption generated successfully!', 'success');
        }
        return data.caption;

    } catch (error) {
        console.error('Caption error:', error);
        if (!silent) showToast('Failed to generate caption', 'error');
        return null;
    } finally {
        if (!silent) {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
}

// ==================== Post to LinkedIn ====================
async function postToLinkedIn() {
    if (!isAuthenticated) {
        showToast('Please connect to LinkedIn first', 'error');
        await initiateLinkedInAuth();
        return;
    }

    if (selectedImageCount === 0) {
        showToast('Please select at least one image', 'error');
        return;
    }

    // 2. One-Click: Auto-generate caption if empty
    let caption = postCaption.value.trim();
    if (!caption) {
        showToast('Generating AI caption...', 'info');
        caption = await generateCaption(true); // silent = true
        if (!caption) {
            showToast('Missing caption. Please enter one or click Generate.', 'error');
            return;
        }
    }

    try {
        loadingOverlay.style.display = 'flex';
        const loadingText = loadingOverlay.querySelector('.loading-text');
        if (loadingText) loadingText.textContent = 'Uploading to LinkedIn...';

        const response = await fetch(`/api/post/linkedin/${currentEventId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                caption: caption || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to post to LinkedIn');
        }

        const data = await response.json();

        loadingOverlay.style.display = 'none';
        showToast(`Successfully posted ${data.num_images} image(s) to LinkedIn!`, 'success');

        // Mark images as posted
        allImages.forEach(img => {
            if (img.is_selected) {
                img.is_posted = true;
            }
        });

        // Clear caption
        postCaption.value = '';

        // Reload stats
        await loadStats();

    } catch (error) {
        console.error('Post error:', error);
        loadingOverlay.style.display = 'none';
        showToast(error.message || 'Failed to post to LinkedIn', 'error');
    }
}

// ==================== Statistics ====================
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        // Global Stats
        const totalEventsGlobal = document.getElementById('totalEventsGlobal');
        const totalPostsGlobal = document.getElementById('totalPostsGlobal');
        if (totalEventsGlobal) totalEventsGlobal.textContent = data.total_events;
        if (totalPostsGlobal) totalPostsGlobal.textContent = data.total_posts;

        // Legacy IDs in Hero (if still present)
        const totalEventsHero = document.getElementById('totalEvents');
        const totalPostsHero = document.getElementById('totalPosts');
        if (totalEventsHero) totalEventsHero.textContent = data.total_events;
        if (totalPostsHero) totalPostsHero.textContent = data.total_posts;

        // User Impact
        const userPostsEl = document.getElementById('userPosts');
        const userImagesEl = document.getElementById('userImages');
        if (userPostsEl) userPostsEl.textContent = data.user_posts || 0;
        if (userImagesEl) userImagesEl.textContent = data.user_images || 0;

        // Welcome Message
        const welcomeMessage = document.getElementById('welcomeMessage');
        if (welcomeMessage && data.user_email) {
            welcomeMessage.textContent = `Welcome Back, ${data.user_email.split('@')[0]}!`;
        }

        // Connection status
        isAuthenticated = data.authenticated;
        updateAuthUI(data);

    } catch (error) {
        console.error('Stats error:', error);
    }
}

function updateAuthUI(data) {
    const authStatusBadge = document.getElementById('authStatusBadge');
    if (authStatusBadge) {
        if (data.authenticated) {
            authStatusBadge.classList.remove('disconnected');
            authStatusBadge.classList.add('connected');
            document.getElementById('authStatusText').textContent = 'Connected';
            linkedinAuthBtn.textContent = 'Reconnect LinkedIn';
        } else {
            authStatusBadge.classList.remove('connected');
            authStatusBadge.classList.add('disconnected');
            document.getElementById('authStatusText').textContent = 'Not Connected';
            linkedinAuthBtn.textContent = 'Connect LinkedIn';
        }
    }
    updateSelectedCount();
}

async function loadRecentActivity() {
    const activityList = document.getElementById('activityList');
    if (!activityList) return;

    try {
        const response = await fetch('/api/activity');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        activityList.innerHTML = '';

        if (!data.activities || data.activities.length === 0) {
            activityList.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--gray-400); font-size: 0.8rem;">No recent activity</div>';
            return;
        }

        data.activities.forEach((item, index) => {
            const activityItem = document.createElement('div');
            activityItem.className = `activity-item animate-delay-${index + 1}`;

            const icon = item.type === 'post' ?
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22.23 0H1.77C.8 0 0 .77 0 1.72v20.56C0 23.23.8 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.72V1.72C24 .77 23.2 0 22.23 0zM7.12 20.45H3.56V9h3.56v11.45zM5.34 7.43c-1.14 0-2.06-.92-2.06-2.06 0-1.14.92-2.06 2.06-2.06 1.14 0 2.06.92 2.06 2.06 0 1.14-.92 2.06-2.06 2.06zM20.45 20.45h-3.56v-5.6c0-1.34-.03-3.05-1.86-3.05-1.86 0-2.14 1.45-2.14 2.95v5.7h-3.56V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29z"/></svg>' :
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>';

            const timeStr = new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            activityItem.innerHTML = `
                <div class="activity-icon ${item.type}">
                    ${icon}
                </div>
                <div class="activity-content">
                    <div class="activity-title">${item.title}</div>
                    <div class="activity-subtitle">${item.subtitle}</div>
                    <div class="activity-time">${timeStr}</div>
                </div>
            `;
            activityList.appendChild(activityItem);
        });

    } catch (error) {
        console.error('Activity error:', error);
        activityList.innerHTML = '<div style="text-align: center; padding: 10px; color: var(--error-red); font-size: 0.75rem;">Failed to load activity</div>';
    }
}

// ==================== View Management ====================
function switchView(viewId) {
    console.log(`switchView called with: ${viewId}`);

    // Update Nav UI
    const navItems = [navOverview, navEvents, navAnalytics];
    navItems.forEach(item => {
        if (item) item.classList.remove('active');
    });

    // Update View UI
    const views = [viewOverview, viewEvents, viewAnalytics];
    views.forEach(view => {
        if (view) view.style.display = 'none';
    });

    // Active specific view
    if (viewId === 'overview') {
        navOverview.classList.add('active');
        viewOverview.style.display = 'block';
    } else if (viewId === 'events') {
        navEvents.classList.add('active');
        viewEvents.style.display = 'block';
        loadEventsHistory();
    } else if (viewId === 'analytics') {
        navAnalytics.classList.add('active');
        viewAnalytics.style.display = 'block';
        loadAnalytics();
    }
}

// ==================== Analytics Logic ====================
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        if (!response.ok) throw new Error('Failed to fetch analytics');
        const data = await response.json();

        renderTimeline('eventsTimelineChart', data.events_timeline, 'Events');
        renderTimeline('postsTimelineChart', data.posts_timeline, 'Posts');
        renderQualityDistribution(data.quality_distribution);

    } catch (error) {
        console.error('Analytics load error:', error);
        showToast('Failed to load performance metrics', 'error');
    }
}

function renderTimeline(containerId, timeline, label) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!timeline || timeline.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:10px; font-size:0.7rem; color:var(--gray-400);">No data</div>';
        return;
    }

    const maxCount = Math.max(...timeline.map(d => d.count), 1);
    container.innerHTML = '';

    timeline.forEach(day => {
        const bar = document.createElement('div');
        bar.className = 'bar';
        const height = (day.count / maxCount) * 100;
        bar.style.height = `${Math.max(height, 5)}%`;
        bar.title = `${day.date}: ${day.count} ${label}`;
        container.appendChild(bar);
    });
}

function renderQualityDistribution(dist) {
    const chart = document.getElementById('qualityDistChart');
    if (!chart) return;

    const total = Object.values(dist).reduce((a, b) => a + b, 0);
    if (total === 0) return;

    const highSeg = chart.querySelector('.dist-segment.high');
    const medSeg = chart.querySelector('.dist-segment.medium');
    const lowSeg = chart.querySelector('.dist-segment.low');

    highSeg.style.width = `${(dist["High (>80%)"] / total) * 100}%`;
    medSeg.style.width = `${(dist["Medium (50-80%)"] / total) * 100}%`;
    lowSeg.style.width = `${(dist["Low (<50%)"] / total) * 100}%`;
}

async function loadEventsHistory() {
    if (!eventsHistoryTable) return;

    try {
        const response = await fetch('/api/events');
        if (!response.ok) throw new Error('Failed to fetch events');
        const data = await response.json();

        eventsHistoryTable.innerHTML = '';

        if (!data.events || data.events.length === 0) {
            eventsHistoryTable.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px; color: var(--gray-400);">
                        No events found. Start by uploading some photos!
                    </td>
                </tr>
            `;
            return;
        }

        data.events.forEach(event => {
            const row = document.createElement('tr');
            const date = new Date(event.created_at).toLocaleDateString();
            const statusClass = event.status.toLowerCase();

            row.innerHTML = `
                <td><strong>${event.name || 'Unnamed Event'}</strong></td>
                <td>${date}</td>
                <td>${event.total_selected} / ${event.total_uploaded}</td>
                <td><span class="status-badge ${statusClass}">${event.status}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="showEventDetails(${event.id})">Details</button>
                </td>
            `;
            eventsHistoryTable.appendChild(row);
        });
    } catch (error) {
        console.error('History load error:', error);
        eventsHistoryTable.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: var(--error-red);">
                    Failed to load history. Please try again.
                </td>
            </tr>
        `;
    }
}

// Event Details Logic
window.showEventDetails = async (eventId) => {
    try {
        const response = await fetch(`/api/events/${eventId}/images`);
        if (!response.ok) throw new Error('Failed to fetch event details');
        const data = await response.json();

        // Update Modal Header/Stats
        document.getElementById('detailsEventName').textContent = data.event_name;
        document.getElementById('detailsEventDate').textContent = new Date(data.created_at).toLocaleDateString();
        document.getElementById('detailsTotal').textContent = data.total_images;
        document.getElementById('detailsSelected').textContent = data.total_selected;

        const statusEl = document.getElementById('detailsStatus');
        statusEl.textContent = data.images.some(img => img.is_posted) ? 'Posted' : 'Draft';
        statusEl.className = 'status-badge ' + statusEl.textContent.toLowerCase();

        // Render mini-gallery
        detailsGallery.innerHTML = '';
        data.images.forEach(image => {
            const card = document.createElement('div');
            card.className = `image-card ${image.is_selected ? 'selected' : ''}`;
            card.innerHTML = `
                <div class="image-wrapper">
                    <img src="${image.url}" alt="${image.filename}" loading="lazy">
                    ${image.is_posted ? '<div class="badge badge-selected" style="position:absolute; bottom:5px; right:5px;">Shared</div>' : ''}
                </div>
            `;
            detailsGallery.appendChild(card);
        });

        detailsModal.style.display = 'block';

    } catch (error) {
        console.error('Details load error:', error);
        showToast('Failed to load event details', 'error');
    }
};

// Utils
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== Toast Notifications ====================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        info: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };

    toast.innerHTML = `
        ${icons[type] || icons.info}
        <div class="toast-message">${message}</div>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ==================== Utility Functions ====================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// ==================== Image Editor Logic ====================
function openEditor(index) {
    const image = allImages[index];
    currentEditIndex = index;

    // Set image source
    editorImage.src = image.url;
    editorModal.style.display = 'block';

    // Reset sliders
    brightnessRange.value = 100;
    contrastRange.value = 100;
    saturationRange.value = 100;
    toolAutoEnhance.classList.remove('active');

    // Initialize Cropper after image loads
    editorImage.onload = () => {
        if (cropper) cropper.destroy();

        cropper = new Cropper(editorImage, {
            viewMode: 1,
            dragMode: 'none',
            autoCropArea: 0.8,
            restore: false,
            guides: true,
            center: true,
            highlight: false,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: false,
        });

        setupEraseCanvas();
        setTool('crop');
    };
}

function closeEditor() {
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    editorModal.style.display = 'none';
    currentEditIndex = null;
}

function setTool(tool) {
    // Reset visual states
    toolCrop.classList.remove('active');
    toolErase.classList.remove('active');

    if (tool === 'crop') {
        toolCrop.classList.add('active');
        isErasing = false;
        eraseCanvas.style.pointerEvents = 'none';
        if (cropper) cropper.setDragMode('crop');
    } else if (tool === 'erase') {
        toolErase.classList.add('active');
        isErasing = true;
        eraseCanvas.style.pointerEvents = 'auto';
        if (cropper) cropper.setDragMode('none');
    }
}

function toggleAutoEnhance() {
    toolAutoEnhance.classList.toggle('active');
}

function updateImageFilters() {
    const b = brightnessRange.value;
    const c = contrastRange.value;
    const s = saturationRange.value;

    // Apply visual filter to editor preview
    editorImage.style.filter = `brightness(${b}%) contrast(${c}%) saturate(${s}%)`;
}

// --- Erase Canvas logic ---
function setupEraseCanvas() {
    eraseCanvas.width = editorImage.naturalWidth;
    eraseCanvas.height = editorImage.naturalHeight;
    eraseCanvas.style.width = editorImage.width + 'px';
    eraseCanvas.style.height = editorImage.height + 'px';

    ctx = eraseCanvas.getContext('2d');
    ctx.strokeStyle = 'rgba(255, 0, 255, 0.5)'; // Magenta with 50% opacity for better visibility
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Clear canvas
    ctx.clearRect(0, 0, eraseCanvas.width, eraseCanvas.height);
}

function startErasing(e) {
    if (!isErasing) return;
    const pos = getCanvasPos(e);
    lastX = pos.x;
    lastY = pos.y;
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
}

function drawErase(e) {
    if (!isErasing || e.buttons !== 1) return;
    const pos = getCanvasPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
}

function stopErasing() {
    if (!isErasing) return;
    ctx.closePath();
}

function getCanvasPos(e) {
    const rect = eraseCanvas.getBoundingClientRect();
    const scaleX = eraseCanvas.width / rect.width;
    const scaleY = eraseCanvas.height / rect.height;
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

async function saveEdits() {
    if (currentEditIndex === null) return;

    const btn = saveEditBtn;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-sm"></span> Saving...';
    btn.disabled = true;

    try {
        const image = allImages[currentEditIndex];
        const cropData = cropper.getData();

        // Get erase data as base64 mask
        const maskData = eraseCanvas.toDataURL('image/png');

        const editData = {
            crop: {
                x: Math.round(cropData.x),
                y: Math.round(cropData.y),
                width: Math.round(cropData.width),
                height: Math.round(cropData.height)
            },
            adjustments: {
                brightness: parseInt(brightnessRange.value) / 100,
                contrast: parseInt(contrastRange.value) / 100,
                saturation: parseInt(saturationRange.value) / 100
            },
            auto_enhance: toolAutoEnhance.classList.contains('active'),
            mask: maskData
        };

        const response = await fetch(`/api/images/${image.id}/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(editData)
        });

        if (!response.ok) throw new Error('Save failed');

        const data = await response.json();

        // Update local state and UI
        image.url = data.url;
        const card = document.querySelector(`[data-image-index="${currentEditIndex}"]`);
        const img = card.querySelector('img');
        img.src = `${data.url}?t=${Date.now()}`;

        showToast('Image saved successfully!', 'success');
        closeEditor();

    } catch (error) {
        console.error('Save error:', error);
        showToast('Failed to save changes', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function updateUploadUI() {
    if (!uploadArea || !selectFilesBtn) return;

    if (isAuthenticated) {
        uploadArea.classList.remove('disabled');
        selectFilesBtn.disabled = false;
    } else {
        uploadArea.classList.add('disabled');
        selectFilesBtn.disabled = true;
    }
}
