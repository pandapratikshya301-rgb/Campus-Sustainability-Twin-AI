// Campus Sustainability Twin AI - Dashboard JavaScript

// Global variables
let categoryChart = null;
let trendChart = null;
window.allComplaints = [];  // Make it globally accessible for features.js

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    initializeDashboard();
    setupEventListeners();
});

// Check authentication
async function checkAuthentication() {
    const token = localStorage.getItem('session_token');
    
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await fetch('/api/auth/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            localStorage.removeItem('session_token');
            window.location.href = '/login';
        } else {
            // Display user info
            displayUserInfo(data.user);
        }
    } catch (error) {
        console.error('Error verifying session:', error);
        localStorage.removeItem('session_token');
        window.location.href = '/login';
    }
}

// Display user info
function displayUserInfo(user) {
    const userInfoDiv = document.getElementById('user-info');
    if (userInfoDiv) {
        userInfoDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="me-3">Welcome, <strong>${user.name}</strong></span>
                <button class="btn btn-sm btn-outline-danger" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </button>
            </div>
        `;
    }
}

// Logout function
async function logout() {
    const token = localStorage.getItem('session_token');
    
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });
    } catch (error) {
        console.error('Error logging out:', error);
    }
    
    localStorage.removeItem('session_token');
    window.location.href = '/login';
}

// Initialize dashboard
async function initializeDashboard() {
    try {
        await loadDashboardData();
        await loadHighPriorityComplaints();
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            navigateToSection(target);
        });
    });

    // Complaint form
    const complaintForm = document.getElementById('complaint-form');
    if (complaintForm) {
        complaintForm.addEventListener('submit', handleComplaintSubmit);
    }

    // Classify button
    const classifyBtn = document.getElementById('classify-btn');
    if (classifyBtn) {
        classifyBtn.addEventListener('click', classifyComplaint);
    }
    
    // Image upload functionality
    const imageInput = document.getElementById('complaint-image');
    if (imageInput) {
        imageInput.addEventListener('change', handleImageSelect);
    }
    
    // Camera capture button
    const captureBtn = document.getElementById('capture-btn');
    if (captureBtn) {
        captureBtn.addEventListener('click', openCamera);
    }
    
    // Refresh complaints button
    const refreshBtn = document.getElementById('refresh-complaints-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
            this.innerHTML = '<i class="fas fa-sync fa-spin"></i>';
            await loadHighPriorityComplaints();
            this.innerHTML = '<i class="fas fa-sync"></i>';
        });
    }
    
    // Filter controls
    const searchInput = document.getElementById('search-complaints');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounceFilter);
    }
    
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyComplaintFilters);
    }
}

// Debounce function for search
let filterTimeout;
function debounceFilter() {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(applyComplaintFilters, 300);
}

// Apply complaint filters
function applyComplaintFilters() {
    const searchTerm = document.getElementById('search-complaints')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('filter-category')?.value || '';
    const priorityFilter = document.getElementById('filter-priority')?.value || '';
    const statusFilter = document.getElementById('filter-status')?.value || '';
    
    let filtered = allComplaints.filter(complaint => {
        // Handle both uppercase and lowercase keys
        const complaintText = (complaint.Complaint || complaint.complaint || '').toLowerCase();
        const location = (complaint.Location || complaint.location || '').toLowerCase();
        const category = complaint.Category || complaint.category || '';
        const priority = complaint.Priority || complaint.priority || 'Medium';
        const status = complaint.Status || complaint.status || 'Open';
        
        const matchesSearch = !searchTerm ||
            complaintText.includes(searchTerm) ||
            location.includes(searchTerm);
        
        const matchesCategory = !categoryFilter || category === categoryFilter;
        const matchesPriority = !priorityFilter || priority === priorityFilter;
        const matchesStatus = !statusFilter || status === statusFilter;
        
        return matchesSearch && matchesCategory && matchesPriority && matchesStatus;
    });
    
    displayHighPriorityComplaints(filtered);
}

// Navigate to section
function navigateToSection(section) {
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`a[href="#${section}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Handle special case for dashboard (scroll to top)
    if (section === 'dashboard') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
    }

    // Handle submit section (show form and scroll)
    if (section === 'submit') {
        const submitSection = document.getElementById('submit-complaint-section');
        if (submitSection) {
            submitSection.style.display = 'block';
            submitSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        return;
    }

    // For other sections, use the ID directly
    const targetElement = document.getElementById(section);
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
    }
    
    // Scroll to target element
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Add offset for fixed header if needed
        window.scrollBy(0, -80);
    }
    
    // Show/hide submit complaint section
    const submitSection = document.getElementById('submit-complaint-section');
    if (submitSection) {
        if (section === 'submit') {
            submitSection.style.display = 'block';
            submitSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            submitSection.style.display = 'none';
        }
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        if (data.success) {
            updateStatistics(data.data);
            await loadTrends();
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update statistics
function updateStatistics(stats) {
    // Update total complaints
    document.getElementById('total-complaints').textContent = stats.total_complaints || 0;

    // Update category counts
    const categoryDist = stats.category_distribution || {};
    document.getElementById('water-issues').textContent = categoryDist.Water || 0;
    document.getElementById('electricity-issues').textContent = categoryDist.Electricity || 0;
    document.getElementById('transport-issues').textContent = categoryDist.Transportation || 0;

    // Update percentages
    const categoryPercent = stats.category_percentages || {};
    document.getElementById('water-percent').textContent = (categoryPercent.Water || 0) + '%';
    document.getElementById('electricity-percent').textContent = (categoryPercent.Electricity || 0) + '%';
    document.getElementById('transport-percent').textContent = (categoryPercent.Transportation || 0) + '%';

    // Update category chart
    updateCategoryChart(categoryDist);
}

// Update category chart
function updateCategoryChart(categoryDist) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    if (categoryChart) {
        categoryChart.destroy();
    }

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Water', 'Electricity', 'Transportation'],
            datasets: [{
                data: [
                    categoryDist.Water || 0,
                    categoryDist.Electricity || 0,
                    categoryDist.Transportation || 0
                ],
                backgroundColor: [
                    '#2196F3',
                    '#FFC107',
                    '#4CAF50'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load trends
async function loadTrends() {
    try {
        const response = await fetch('/api/dashboard/trends');
        const data = await response.json();

        if (data.success) {
            updateTrendChart(data.data);
            updateTrendIndicator(data.data.trend_direction);
        }
    } catch (error) {
        console.error('Error loading trends:', error);
    }
}

// Update trend chart
function updateTrendChart(trends) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    if (trendChart) {
        trendChart.destroy();
    }

    // Get last 7 days data
    const last7Days = trends.last_7_days || {};
    const categoryTrends = trends.category_trends || {};

    // Prepare data for last 7 days
    const dates = Object.keys(trends.daily_complaints || {}).slice(-7);
    const counts = dates.map(date => trends.daily_complaints[date] || 0);

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates.map(d => new Date(d).toLocaleDateString('en-US', { weekday: 'short' })),
            datasets: [{
                label: 'Total Complaints',
                data: counts,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Update trend indicator
function updateTrendIndicator(direction) {
    const indicator = document.getElementById('trend-indicator');
    if (!indicator) return;

    if (direction === 'increasing') {
        indicator.innerHTML = '<span class="text-danger">↑ Increasing</span>';
    } else if (direction === 'decreasing') {
        indicator.innerHTML = '<span class="text-success">↓ Decreasing</span>';
    } else {
        indicator.innerHTML = '<span class="text-info">→ Stable</span>';
    }
}

// Load high priority complaints
async function loadHighPriorityComplaints() {
    try {
        const response = await fetch('/api/complaints');
        const data = await response.json();

        if (data.success) {
            allComplaints = data.data;
            const highPriority = data.data.filter(c => c.Priority === 'High');
            displayHighPriorityComplaints(highPriority);
        }
    } catch (error) {
        console.error('Error loading complaints:', error);
    }
}

// Display high priority complaints
function displayHighPriorityComplaints(complaints) {
    const tbody = document.getElementById('high-priority-body');
    if (!tbody) return;

    if (complaints.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No high priority complaints</td></tr>';
        return;
    }

    tbody.innerHTML = complaints.slice(0, 10).map(complaint => {
        // Handle both uppercase and lowercase keys
        const id = complaint.Complaint_ID || complaint.id || 'N/A';
        const complaintText = complaint.Complaint || complaint.complaint || 'No description';
        const category = complaint.Category || complaint.category || 'Other';
        const priority = complaint.Priority || complaint.priority || 'Medium';
        const location = complaint.Location || complaint.location || 'Unknown';
        const usersAffected = complaint.Users_Affected || complaint.users_affected || 0;
        const status = complaint.Status || complaint.status || 'Open';
        
        return `
        <tr>
            <td><input type="checkbox" class="complaint-checkbox" data-id="${id}"></td>
            <td><strong>${id}</strong></td>
            <td>${complaintText.substring(0, 50)}${complaintText.length > 50 ? '...' : ''}</td>
            <td>
                <span class="badge bg-${getCategoryColor(category)}">
                    ${category}
                </span>
            </td>
            <td><span class="badge bg-${getPriorityColor(priority)}">${priority}</span></td>
            <td>${location}</td>
            <td>${usersAffected}</td>
            <td>
                <span class="badge bg-${getStatusColor(status)}">
                    ${status}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary view-complaint" data-id="${id}">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-success update-status" data-id="${id}" data-status="Resolved">
                    <i class="fas fa-check"></i>
                </button>
            </td>
        </tr>
        `;
    }).join('');
    
    // Reattach event listeners
    attachComplaintEventListeners();
}

function getPriorityColor(priority) {
    const colors = { 'High': 'danger', 'Medium': 'warning', 'Low': 'success' };
    return colors[priority] || 'secondary';
}

function getStatusColor(status) {
    const colors = { 'Open': 'warning', 'In Progress': 'info', 'Resolved': 'success' };
    return colors[status] || 'secondary';
}

function attachComplaintEventListeners() {
    document.querySelectorAll('.view-complaint').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const complaintId = this.dataset.id;
            viewComplaintDetails(complaintId);
        });
    });
}

// Get category color
function getCategoryColor(category) {
    const colors = {
        'Water': 'info',
        'Electricity': 'warning',
        'Transportation': 'success'
    };
    return colors[category] || 'secondary';
}

// View complaint details
async function viewComplaintDetails(complaintId) {
    try {
        const response = await fetch(`/api/complaint/${complaintId}`);
        const data = await response.json();

        if (data.success) {
            displayComplaintModal(data.data);
        }
    } catch (error) {
        console.error('Error loading complaint details:', error);
        showError('Failed to load complaint details');
    }
}

// Display complaint modal
function displayComplaintModal(complaint) {
    const modalBody = document.getElementById('modal-body-content');
    if (!modalBody) return;

    const recommendations = complaint.recommendations || {};
    const immediateActions = recommendations.immediate_actions || [];
    const preventiveMeasures = recommendations.preventive_measures || [];

    modalBody.innerHTML = `
        <div class="complaint-details">
            <h6><strong>Complaint ID:</strong> ${complaint.Complaint_ID}</h6>
            <p><strong>Category:</strong> <span class="badge bg-${getCategoryColor(complaint.Category)}">${complaint.Category}</span></p>
            <p><strong>Priority:</strong> <span class="badge badge-${complaint.Priority.toLowerCase()}">${complaint.Priority}</span></p>
            <p><strong>Status:</strong> <span class="badge badge-${complaint.Status.toLowerCase().replace(' ', '-')}">${complaint.Status}</span></p>
            <p><strong>Location:</strong> ${complaint.Location}</p>
            <p><strong>Users Affected:</strong> ${complaint.Users_Affected}</p>
            <p><strong>Date:</strong> ${complaint.Date}</p>
            
            <hr>
            
            <h6><strong>Complaint Description:</strong></h6>
            <p>${complaint.Complaint}</p>
            
            <hr>
            
            <h6><i class="fas fa-robot"></i> AI-Generated Recommendations:</h6>
            
            ${immediateActions.length > 0 ? `
                <div class="recommendation-card">
                    <h6>Immediate Actions:</h6>
                    <ul>
                        ${immediateActions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${preventiveMeasures.length > 0 ? `
                <div class="recommendation-card">
                    <h6>Preventive Measures:</h6>
                    <ul>
                        ${preventiveMeasures.map(measure => `<li>${measure}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${recommendations.resolution_time ? `
                <p><strong>Estimated Resolution Time:</strong> ${recommendations.resolution_time}</p>
            ` : ''}
            
            ${recommendations.responsible_department ? `
                <p><strong>Responsible Department:</strong> ${recommendations.responsible_department.name}</p>
            ` : ''}
        </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('complaintModal'));
    modal.show();
}

// Handle complaint submission
async function handleComplaintSubmit(e) {
    e.preventDefault();

    const complaintText = document.getElementById('complaint-text').value;
    const location = document.getElementById('location').value;
    const usersAffected = document.getElementById('users-affected').value;
    const token = localStorage.getItem('session_token');

    // Validate inputs
    if (!complaintText || !location || !usersAffected) {
        showError('Please fill in all required fields');
        return;
    }

    if (!token) {
        showError('You must be logged in to submit a complaint');
        window.location.href = '/login';
        return;
    }

    // Show loading state
    const submitBtn = document.querySelector('#complaint-form button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('complaint', complaintText);
        formData.append('location', location);
        formData.append('users_affected', parseInt(usersAffected));
        formData.append('date', new Date().toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '-'));
        
        // Add images if any
        selectedImages.forEach((file, index) => {
            formData.append('images', file);
        });

        const response = await fetch('/api/complaint/submit', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showSuccess('Complaint submitted successfully! ID: ' + data.complaint_id);
            document.getElementById('complaint-form').reset();
            
            // Clear images
            selectedImages = [];
            document.getElementById('image-preview').innerHTML = '';
            document.getElementById('image-preview-container').style.display = 'none';
            
            // Show classification result
            displayClassificationResult(data);
            
            // Reload dashboard
            await loadDashboardData();
            await loadHighPriorityComplaints();
        } else {
            // Handle specific error cases
            if (response.status === 401) {
                showError('Session expired. Please login again.');
                localStorage.removeItem('session_token');
                setTimeout(() => window.location.href = '/login', 2000);
            } else {
                showError('Failed to submit complaint: ' + (data.message || data.error || 'Unknown error'));
            }
        }
    } catch (error) {
        console.error('Error submitting complaint:', error);
        showError('Network error: Failed to submit complaint. Please check your connection.');
    } finally {
        // Restore button state
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// Classify complaint
async function classifyComplaint() {
    const complaintText = document.getElementById('complaint-text').value;
    
    if (!complaintText) {
        showError('Please enter a complaint description first');
        return;
    }

    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: complaintText })
        });

        const data = await response.json();

        if (data.success) {
            const classification = data.classification;
            const resultDiv = document.getElementById('ai-classification');
            const resultText = document.getElementById('classification-result');
            
            resultText.innerHTML = `
                <strong>Category:</strong> ${classification.category}<br>
                <strong>Urgency:</strong> ${classification.urgency}<br>
                <strong>Affected Area:</strong> ${classification.affected_area}<br>
                <strong>Recommended Action:</strong> ${classification.recommended_action}
            `;
            
            resultDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Error classifying complaint:', error);
        showError('Failed to classify complaint');
    }
}

// Display classification result
function displayClassificationResult(data) {
    const resultDiv = document.getElementById('ai-classification');
    const resultText = document.getElementById('classification-result');
    
    resultText.innerHTML = `
        <strong>Complaint ID:</strong> ${data.complaint_id}<br>
        <strong>Category:</strong> ${data.classification.category}<br>
        <strong>Priority:</strong> ${data.priority}<br>
        <strong>Top Recommendation:</strong> ${data.recommendations.immediate_actions[0] || 'Processing...'}
    `;
    
    resultDiv.style.display = 'block';
    resultDiv.classList.add('alert-success');
    resultDiv.classList.remove('alert-info');
}

// Show success message
function showSuccess(message) {
    alert(message); // In production, use a better notification system
}

// Show error message
function showError(message) {
    alert('Error: ' + message); // In production, use a better notification system
}

// Refresh dashboard every 30 seconds
setInterval(() => {
    loadDashboardData();
    loadHighPriorityComplaints();
}, 30000);

// Made with Bob

// Global variable for storing selected images
let selectedImages = [];

// Handle image selection
function handleImageSelect(event) {
    const files = Array.from(event.target.files);
    
    // Validate file count
    if (selectedImages.length + files.length > 5) {
        showError('Maximum 5 images allowed');
        return;
    }
    
    // Validate and process each file
    files.forEach(file => {
        // Check file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            showError(`File ${file.name} is too large. Max 5MB per image.`);
            return;
        }
        
        // Check file type
        if (!file.type.startsWith('image/')) {
            showError(`File ${file.name} is not an image.`);
            return;
        }
        
        // Add to selected images
        selectedImages.push(file);
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            displayImagePreview(e.target.result, selectedImages.length - 1);
        };
        reader.readAsDataURL(file);
    });
    
    // Clear input
    event.target.value = '';
}

// Display image preview
function displayImagePreview(dataUrl, index) {
    const previewContainer = document.getElementById('image-preview-container');
    const previewDiv = document.getElementById('image-preview');
    
    previewContainer.style.display = 'block';
    
    const imageCard = document.createElement('div');
    imageCard.className = 'col-md-3';
    imageCard.innerHTML = `
        <div class="card">
            <img src="${dataUrl}" class="card-img-top" alt="Preview" style="height: 150px; object-fit: cover;">
            <div class="card-body p-2">
                <button type="button" class="btn btn-sm btn-danger w-100" onclick="removeImage(${index})">
                    <i class="fas fa-trash"></i> Remove
                </button>
            </div>
        </div>
    `;
    
    previewDiv.appendChild(imageCard);
}

// Remove image
function removeImage(index) {
    selectedImages.splice(index, 1);
    
    // Rebuild preview
    const previewDiv = document.getElementById('image-preview');
    previewDiv.innerHTML = '';
    
    selectedImages.forEach((file, idx) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            displayImagePreview(e.target.result, idx);
        };
        reader.readAsDataURL(file);
    });
    
    // Hide container if no images
    if (selectedImages.length === 0) {
        document.getElementById('image-preview-container').style.display = 'none';
    }
}

// Open camera for capture
function openCamera() {
    // Create camera modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'cameraModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-camera"></i> Capture Photo
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    <video id="camera-video" autoplay style="width: 100%; max-height: 400px; background: #000;"></video>
                    <canvas id="camera-canvas" style="display: none;"></canvas>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                    <button type="button" class="btn btn-primary" id="capture-photo-btn">
                        <i class="fas fa-camera"></i> Capture
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Start camera
    startCamera();
    
    // Capture button
    document.getElementById('capture-photo-btn').addEventListener('click', capturePhoto);
    
    // Cleanup on close
    modal.addEventListener('hidden.bs.modal', function() {
        stopCamera();
        modal.remove();
    });
}

let cameraStream = null;

// Start camera
async function startCamera() {
    try {
        const video = document.getElementById('camera-video');
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } // Use back camera on mobile
        });
        video.srcObject = cameraStream;
    } catch (error) {
        console.error('Error accessing camera:', error);
        showError('Could not access camera. Please check permissions.');
    }
}

// Stop camera
function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
}

// Capture photo
function capturePhoto() {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    const context = canvas.getContext('2d');
    
    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    context.drawImage(video, 0, 0);
    
    // Convert to blob
    canvas.toBlob(function(blob) {
        if (selectedImages.length >= 5) {
            showError('Maximum 5 images allowed');
            return;
        }
        
        // Create file from blob
        const file = new File([blob], `capture_${Date.now()}.jpg`, { type: 'image/jpeg' });
        selectedImages.push(file);
        
        // Display preview
        const dataUrl = canvas.toDataURL('image/jpeg');
        displayImagePreview(dataUrl, selectedImages.length - 1);
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('cameraModal')).hide();
        
        showSuccess('Photo captured successfully!');
    }, 'image/jpeg', 0.9);
}
