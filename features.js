// Campus Sustainability Twin AI - Advanced Features JavaScript

// ============================================
// 1. SIDEBAR TOGGLE
// ============================================
function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('main');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('sidebar-collapsed');
            
            // Save state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Restore sidebar state
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        }
    }
}

// ============================================
// 2. DARK MODE TOGGLE
// ============================================
function initDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            const icon = this.querySelector('i');
            
            if (body.classList.contains('dark-mode')) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
                localStorage.setItem('darkMode', 'enabled');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
                localStorage.setItem('darkMode', 'disabled');
            }
        });
        
        // Restore dark mode state
        const savedMode = localStorage.getItem('darkMode');
        if (savedMode === 'enabled') {
            body.classList.add('dark-mode');
            const icon = darkModeToggle.querySelector('i');
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
}

// ============================================
// 3. SEARCH AND FILTER
// ============================================
let filteredComplaints = [];

function initSearchAndFilter() {
    const searchInput = document.getElementById('search-complaints');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
    
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    // Initial display of all complaints
    setTimeout(() => {
        if (window.allComplaints && window.allComplaints.length > 0) {
            filteredComplaints = window.allComplaints;
            displayFilteredComplaints();
        }
    }, 1000);
}

function applyFilters() {
    const searchTerm = document.getElementById('search-complaints')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('filter-category')?.value || '';
    const priorityFilter = document.getElementById('filter-priority')?.value || '';
    const statusFilter = document.getElementById('filter-status')?.value || '';
    
    // Use window.allComplaints to access the global variable
    const complaints = window.allComplaints || [];
    
    filteredComplaints = complaints.filter(complaint => {
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
    
    displayFilteredComplaints();
}

function displayFilteredComplaints() {
    const tbody = document.getElementById('high-priority-body');
    if (!tbody) return;
    
    if (!filteredComplaints || filteredComplaints.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No complaints found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredComplaints.map(complaint => {
        // Handle both uppercase and lowercase keys
        const id = complaint.Complaint_ID || complaint.id || 'N/A';
        const complaintText = complaint.Complaint || complaint.complaint || 'No description';
        const category = complaint.Category || complaint.category || 'Other';
        const priority = complaint.Priority || complaint.priority || 'Medium';
        const location = complaint.Location || complaint.location || 'Unknown';
        const usersAffected = complaint.Users_Affected || complaint.users_affected || 0;
        const status = complaint.Status || complaint.status || 'Pending';
        
        return `
        <tr>
            <td><input type="checkbox" class="complaint-checkbox" data-id="${id}"></td>
            <td>${id}</td>
            <td>${complaintText.substring(0, 50)}${complaintText.length > 50 ? '...' : ''}</td>
            <td><span class="badge bg-info">${category}</span></td>
            <td><span class="badge bg-${getPriorityColor(priority)}">${priority}</span></td>
            <td>${location}</td>
            <td>${usersAffected}</td>
            <td><span class="badge bg-${getStatusColor(status)}">${status}</span></td>
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

// ============================================
// 4. EXPORT DATA (CSV/Excel)
// ============================================
function initExportFunctionality() {
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const exportExcelBtn = document.getElementById('export-excel-btn');
    
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => exportData('csv'));
    }
    
    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', () => exportData('excel'));
    }
}

function exportData(format) {
    const dataToExport = filteredComplaints.length > 0 ? filteredComplaints : allComplaints;
    
    if (format === 'csv') {
        exportToCSV(dataToExport);
    } else if (format === 'excel') {
        exportToExcel(dataToExport);
    }
}

function exportToCSV(data) {
    const headers = ['ID', 'Complaint', 'Category', 'Priority', 'Location', 'Users Affected', 'Status', 'Date'];
    const csvContent = [
        headers.join(','),
        ...data.map(row => [
            row.id,
            `"${row.complaint.replace(/"/g, '""')}"`,
            row.category,
            row.priority,
            row.location,
            row.users_affected,
            row.status || 'Pending',
            new Date().toISOString().split('T')[0]
        ].join(','))
    ].join('\n');
    
    downloadFile(csvContent, 'complaints.csv', 'text/csv');
}

function exportToExcel(data) {
    // Simple Excel XML format
    const excelContent = `
        <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">
        <head><meta charset="UTF-8"></head>
        <body>
        <table>
            <tr>
                <th>ID</th><th>Complaint</th><th>Category</th><th>Priority</th>
                <th>Location</th><th>Users Affected</th><th>Status</th>
            </tr>
            ${data.map(row => `
                <tr>
                    <td>${row.id}</td>
                    <td>${row.complaint}</td>
                    <td>${row.category}</td>
                    <td>${row.priority}</td>
                    <td>${row.location}</td>
                    <td>${row.users_affected}</td>
                    <td>${row.status || 'Pending'}</td>
                </tr>
            `).join('')}
        </table>
        </body>
        </html>
    `;
    
    downloadFile(excelContent, 'complaints.xls', 'application/vnd.ms-excel');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ============================================
// 5. REAL-TIME NOTIFICATIONS
// ============================================
let notificationInterval;
let lastNotificationCheck = Date.now();

function initNotifications() {
    const notificationsBtn = document.getElementById('notifications-btn');
    
    if (notificationsBtn) {
        notificationsBtn.addEventListener('click', showNotificationsPanel);
    }
    
    // Check for new high-priority complaints every 30 seconds
    notificationInterval = setInterval(checkForNewNotifications, 30000);
    checkForNewNotifications();
}

async function checkForNewNotifications() {
    try {
        const response = await fetch('/api/complaints');
        const data = await response.json();
        
        if (data.success) {
            const highPriorityComplaints = data.complaints.filter(c => c.priority === 'High');
            const newComplaints = highPriorityComplaints.filter(c => {
                const complaintTime = new Date(c.timestamp || Date.now()).getTime();
                return complaintTime > lastNotificationCheck;
            });
            
            if (newComplaints.length > 0) {
                showNotificationBadge(newComplaints.length);
                addNotificationsToPanel(newComplaints);
            }
            
            lastNotificationCheck = Date.now();
        }
    } catch (error) {
        console.error('Error checking notifications:', error);
    }
}

function showNotificationBadge(count) {
    const badge = document.getElementById('notification-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = 'inline-block';
    }
}

function showNotificationsPanel() {
    const panel = new bootstrap.Offcanvas(document.getElementById('notificationsPanel'));
    panel.show();
    
    // Clear badge
    const badge = document.getElementById('notification-count');
    if (badge) {
        badge.style.display = 'none';
    }
}

function addNotificationsToPanel(complaints) {
    const list = document.getElementById('notifications-list');
    if (!list) return;
    
    const html = complaints.map(c => `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <strong>High Priority!</strong><br>
            ${c.complaint.substring(0, 100)}...<br>
            <small>Location: ${c.location}</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `).join('');
    
    list.innerHTML = html || '<p class="text-muted text-center">No new notifications</p>';
}

// ============================================
// 6. COMPLAINT STATUS UPDATE
// ============================================
function initStatusUpdate() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.update-status')) {
            const btn = e.target.closest('.update-status');
            const complaintId = btn.dataset.id;
            const status = btn.dataset.status;
            updateComplaintStatus(complaintId, status);
        }
    });
    
    // Modal buttons
    const resolveBtn = document.getElementById('modal-resolve-btn');
    const progressBtn = document.getElementById('modal-progress-btn');
    
    if (resolveBtn) {
        resolveBtn.addEventListener('click', () => updateCurrentComplaintStatus('Resolved'));
    }
    
    if (progressBtn) {
        progressBtn.addEventListener('click', () => updateCurrentComplaintStatus('In Progress'));
    }
}

async function updateComplaintStatus(complaintId, status) {
    try {
        const response = await fetch(`/api/complaint/${complaintId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('session_token')}`
            },
            body: JSON.stringify({ status })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Complaint status updated to ${status}`);
            await loadHighPriorityComplaints();
        } else {
            showError('Failed to update status');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showError('Error updating complaint status');
    }
}

function updateCurrentComplaintStatus(status) {
    const modal = document.getElementById('complaintModal');
    const complaintId = modal.dataset.currentComplaintId;
    if (complaintId) {
        updateComplaintStatus(complaintId, status);
        bootstrap.Modal.getInstance(modal).hide();
    }
}

// ============================================
// 7. USER PROFILE
// ============================================
function initUserProfile() {
    // Add profile link to user info
    const userInfo = document.getElementById('user-info');
    if (userInfo) {
        userInfo.addEventListener('click', function(e) {
            if (e.target.closest('.user-profile-link')) {
                showUserProfile();
            }
        });
    }
    
    const saveProfileBtn = document.getElementById('save-profile-btn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', saveUserProfile);
    }
}

async function showUserProfile() {
    try {
        const response = await fetch('/api/user/profile', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('session_token')}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('profile-username').value = data.user.username;
            document.getElementById('profile-email').value = data.user.email || '';
            document.getElementById('profile-phone').value = data.user.phone || '';
            document.getElementById('profile-complaints-count').value = data.user.complaints_count || 0;
            document.getElementById('profile-member-since').value = new Date(data.user.created_at).toLocaleDateString();
            
            const modal = new bootstrap.Modal(document.getElementById('profileModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function saveUserProfile() {
    const email = document.getElementById('profile-email').value;
    const phone = document.getElementById('profile-phone').value;
    
    try {
        const response = await fetch('/api/user/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('session_token')}`
            },
            body: JSON.stringify({ email, phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Profile updated successfully');
            bootstrap.Modal.getInstance(document.getElementById('profileModal')).hide();
        } else {
            showError('Failed to update profile');
        }
    } catch (error) {
        console.error('Error saving profile:', error);
        showError('Error updating profile');
    }
}

// ============================================
// 8. ADVANCED ANALYTICS
// ============================================
let priorityChart, statusChart;

async function initAdvancedAnalytics() {
    await loadAdvancedAnalytics();
}

async function loadAdvancedAnalytics() {
    try {
        const response = await fetch('/api/dashboard/advanced-stats', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('session_token')}`
            }
        });
        const data = await response.json();
        
        if (data.success) {
            createPriorityChart(data.priority_distribution);
            createStatusChart(data.status_distribution);
            updateResolutionTime(data.avg_resolution_time);
        } else {
            console.error('Failed to load advanced stats:', data.message);
        }
    } catch (error) {
        console.error('Error loading advanced analytics:', error);
        // Show default empty charts
        createPriorityChart({High: 0, Medium: 0, Low: 0});
        createStatusChart({Pending: 0, 'In Progress': 0, Resolved: 0});
        updateResolutionTime(0);
    }
}

function createPriorityChart(data) {
    const ctx = document.getElementById('priorityChart');
    if (!ctx) return;
    
    if (priorityChart) priorityChart.destroy();
    
    priorityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                data: [data.High || 0, data.Medium || 0, data.Low || 0],
                backgroundColor: ['#dc3545', '#ffc107', '#28a745']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function createStatusChart(data) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;
    
    if (statusChart) statusChart.destroy();
    
    statusChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Open', 'In Progress', 'Resolved'],
            datasets: [{
                data: [data.Open || 0, data['In Progress'] || 0, data.Resolved || 0],
                backgroundColor: ['#ffc107', '#17a2b8', '#28a745']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function updateResolutionTime(avgTime) {
    const timeElement = document.getElementById('avg-resolution-time');
    const progressBar = document.getElementById('resolution-progress');
    
    if (timeElement) {
        timeElement.textContent = avgTime ? avgTime.toFixed(1) : '--';
    }
    
    if (progressBar && avgTime) {
        const percentage = Math.min((avgTime / 24) * 100, 100);
        progressBar.style.width = `${percentage}%`;
        progressBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
        progressBar.classList.add(avgTime <= 24 ? 'bg-success' : avgTime <= 48 ? 'bg-warning' : 'bg-danger');
    }
}

// ============================================
// 9. BULK ACTIONS
// ============================================
let selectedComplaints = [];

function initBulkActions() {
    const selectAllCheckbox = document.getElementById('select-all-complaints');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.complaint-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
                updateSelectedComplaints(cb.dataset.id, this.checked);
            });
        });
    }
    
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('complaint-checkbox')) {
            updateSelectedComplaints(e.target.dataset.id, e.target.checked);
        }
    });
    
    // Bulk action buttons
    document.getElementById('bulk-resolve-btn')?.addEventListener('click', () => bulkUpdateStatus('Resolved'));
    document.getElementById('bulk-progress-btn')?.addEventListener('click', () => bulkUpdateStatus('In Progress'));
    document.getElementById('bulk-delete-btn')?.addEventListener('click', bulkDeleteComplaints);
}

function updateSelectedComplaints(id, isSelected) {
    if (isSelected) {
        if (!selectedComplaints.includes(id)) {
            selectedComplaints.push(id);
        }
    } else {
        selectedComplaints = selectedComplaints.filter(cid => cid !== id);
    }
    
    updateBulkActionsBar();
}

function updateBulkActionsBar() {
    const bar = document.getElementById('bulk-actions-bar');
    const countElement = document.getElementById('selected-count');
    
    if (bar && countElement) {
        if (selectedComplaints.length > 0) {
            bar.style.display = 'block';
            countElement.textContent = selectedComplaints.length;
        } else {
            bar.style.display = 'none';
        }
    }
}

async function bulkUpdateStatus(status) {
    if (selectedComplaints.length === 0) return;
    
    try {
        const promises = selectedComplaints.map(id => 
            updateComplaintStatus(id, status)
        );
        
        await Promise.all(promises);
        selectedComplaints = [];
        updateBulkActionsBar();
        showSuccess(`${promises.length} complaints updated to ${status}`);
    } catch (error) {
        console.error('Error in bulk update:', error);
        showError('Error updating complaints');
    }
}

async function bulkDeleteComplaints() {
    if (selectedComplaints.length === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedComplaints.length} complaints?`)) {
        return;
    }
    
    // Implement delete functionality
    showSuccess(`${selectedComplaints.length} complaints deleted`);
    selectedComplaints = [];
    updateBulkActionsBar();
}

// ============================================
// 10. COMPLAINT HISTORY TIMELINE
// ============================================
function showComplaintTimeline(complaintId) {
    // This would show a timeline of complaint updates
    // For now, we'll add it to the modal
    const timeline = `
        <div class="timeline mt-3">
            <h6>Complaint History</h6>
            <div class="timeline-item">
                <span class="badge bg-primary">Created</span>
                <span class="text-muted">Just now</span>
            </div>
        </div>
    `;
    
    return timeline;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
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

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'danger');
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function attachComplaintEventListeners() {
    document.querySelectorAll('.view-complaint').forEach(btn => {
        btn.addEventListener('click', function() {
            const complaintId = this.dataset.id;
            viewComplaintDetails(complaintId);
        });
    });
}

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    initSidebarToggle();
    initDarkMode();
    initSearchAndFilter();
    initExportFunctionality();
    initNotifications();
    initStatusUpdate();
    initUserProfile();
    initAdvancedAnalytics();
    initBulkActions();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (notificationInterval) {
        clearInterval(notificationInterval);
    }
});

// Made with Bob
