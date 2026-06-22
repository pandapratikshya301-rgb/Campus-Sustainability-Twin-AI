/**
 * Notification System
 * Handles real-time notifications with sound alerts
 */

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.pollInterval = null;
        this.audioContext = null;
        this.isInitialized = false;
        
        // Initialize audio context on user interaction
        document.addEventListener('click', () => this.initAudio(), { once: true });
    }
    
    /**
     * Initialize audio context
     */
    initAudio() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
    }
    
    /**
     * Play notification sound
     * @param {string} type - Type of notification (new_complaint, status_update, resolved)
     */
    playSound(type) {
        if (!this.audioContext) {
            this.initAudio();
        }
        
        const ctx = this.audioContext;
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        
        // Different sounds for different notification types
        if (type === 'new_complaint') {
            // Pleasant notification sound (C-E-G chord)
            this.playChord(ctx, [523.25, 659.25, 783.99], 0.3, 0.4);
        } else if (type === 'resolved') {
            // Success sound (ascending notes)
            this.playSequence(ctx, [523.25, 659.25, 783.99, 1046.50], 0.15, 0.3);
        } else {
            // Status update sound (single pleasant tone)
            oscillator.frequency.setValueAtTime(659.25, ctx.currentTime); // E note
            gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
            
            oscillator.start(ctx.currentTime);
            oscillator.stop(ctx.currentTime + 0.5);
        }
    }
    
    /**
     * Play a chord
     */
    playChord(ctx, frequencies, duration, volume) {
        frequencies.forEach(freq => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            gain.gain.setValueAtTime(volume, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
            
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + duration);
        });
    }
    
    /**
     * Play a sequence of notes
     */
    playSequence(ctx, frequencies, noteDuration, volume) {
        frequencies.forEach((freq, index) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            const startTime = ctx.currentTime + (index * noteDuration);
            osc.frequency.setValueAtTime(freq, startTime);
            gain.gain.setValueAtTime(volume, startTime);
            gain.gain.exponentialRampToValueAtTime(0.01, startTime + noteDuration);
            
            osc.start(startTime);
            osc.stop(startTime + noteDuration);
        });
    }
    
    /**
     * Initialize notification system
     */
    async init() {
        if (this.isInitialized) return;
        
        // Create notification bell UI
        this.createNotificationBell();
        
        // Load initial notifications
        await this.loadNotifications();
        
        // Start polling for new notifications every 10 seconds
        this.startPolling();
        
        this.isInitialized = true;
        console.log('[Notifications] System initialized');
    }
    
    /**
     * Create notification bell icon in navbar
     */
    createNotificationBell() {
        const navbar = document.querySelector('.navbar-nav');
        if (!navbar) {
            console.error('[Notifications] Navbar not found');
            return;
        }
        
        const bellHTML = `
            <li class="nav-item dropdown" id="notification-dropdown">
                <a class="nav-link position-relative" href="#" id="notificationBell"
                   role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-bell fs-5 text-white"></i>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                          id="notification-badge" style="display: none;">
                        0
                    </span>
                </a>
                <div class="dropdown-menu dropdown-menu-end notification-dropdown"
                     aria-labelledby="notificationBell" style="width: 350px; max-height: 500px; overflow-y: auto;">
                    <div class="dropdown-header d-flex justify-content-between align-items-center">
                        <span class="fw-bold">Notifications</span>
                        <button class="btn btn-sm btn-link text-decoration-none"
                                id="mark-all-read" style="font-size: 0.85rem;">
                            Mark all as read
                        </button>
                    </div>
                    <div class="dropdown-divider"></div>
                    <div id="notification-list">
                        <div class="text-center py-3 text-muted">
                            <i class="fas fa-bell-slash fs-3"></i>
                            <p class="mb-0 mt-2">No notifications</p>
                        </div>
                    </div>
                </div>
            </li>
        `;
        
        // Insert before the user-info li element
        const userInfoLi = navbar.querySelector('li:has(#user-info)');
        if (userInfoLi) {
            userInfoLi.insertAdjacentHTML('beforebegin', bellHTML);
        } else {
            navbar.insertAdjacentHTML('beforeend', bellHTML);
        }
        
        console.log('[Notifications] Bell created');
        
        // Add event listeners
        const markAllBtn = document.getElementById('mark-all-read');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.markAllAsRead();
            });
        }
    }
    
    /**
     * Load notifications from server
     */
    async loadNotifications() {
        try {
            const token = localStorage.getItem('session_token');
            if (!token) {
                console.log('[Notifications] No session token found');
                return;
            }
            
            console.log('[Notifications] Loading notifications...');
            const response = await fetch('/api/notifications', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('[Notifications] Received data:', data);
                this.notifications = data.notifications || [];
                this.unreadCount = data.unread_count || 0;
                console.log(`[Notifications] Loaded ${this.notifications.length} notifications, ${this.unreadCount} unread`);
                this.updateUI();
            } else {
                console.error('[Notifications] Server returned error:', response.status);
            }
        } catch (error) {
            console.error('[Notifications] Error loading:', error);
        }
    }
    
    /**
     * Start polling for new notifications
     */
    startPolling() {
        // Poll every 10 seconds
        this.pollInterval = setInterval(() => this.checkForNewNotifications(), 10000);
    }
    
    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }
    
    /**
     * Check for new notifications
     */
    async checkForNewNotifications() {
        try {
            const token = localStorage.getItem('session_token');
            if (!token) return;
            
            const response = await fetch('/api/notifications/unread-count', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                const newCount = data.count || 0;
                
                // If there are new notifications, reload and play sound
                if (newCount > this.unreadCount) {
                    await this.loadNotifications();
                    
                    // Play sound for the newest notification
                    if (this.notifications.length > 0) {
                        const latestNotification = this.notifications[0];
                        this.playSound(latestNotification.type);
                        this.showBrowserNotification(latestNotification);
                    }
                }
            }
        } catch (error) {
            console.error('[Notifications] Error checking for new:', error);
        }
    }
    
    /**
     * Show browser notification
     */
    showBrowserNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico'
            });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification(notification.title, {
                        body: notification.message,
                        icon: '/static/favicon.ico'
                    });
                }
            });
        }
    }
    
    /**
     * Update UI with current notifications
     */
    updateUI() {
        console.log('[Notifications] Updating UI...');
        
        // Update badge
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.style.display = 'inline-block';
                console.log(`[Notifications] Badge updated: ${this.unreadCount}`);
            } else {
                badge.style.display = 'none';
            }
        } else {
            console.warn('[Notifications] Badge element not found');
        }
        
        // Update notification list
        const list = document.getElementById('notification-list');
        if (!list) {
            console.error('[Notifications] notification-list element not found!');
            return;
        }
        
        console.log(`[Notifications] Rendering ${this.notifications.length} notifications`);
        
        if (this.notifications.length === 0) {
            list.innerHTML = `
                <div class="text-center py-3 text-muted">
                    <i class="fas fa-bell-slash fs-3"></i>
                    <p class="mb-0 mt-2">No notifications</p>
                </div>
            `;
            return;
        }
        
        list.innerHTML = this.notifications.map(notif => this.createNotificationHTML(notif)).join('');
        console.log('[Notifications] HTML rendered');
        
        // Add click handlers
        this.notifications.forEach(notif => {
            const element = document.getElementById(`notif-${notif.id}`);
            if (element) {
                element.addEventListener('click', () => this.markAsRead(notif.id));
            }
        });
        console.log('[Notifications] Click handlers added');
    }
    
    /**
     * Create HTML for a single notification
     */
    createNotificationHTML(notification) {
        const isUnread = !notification.is_read;
        const icon = this.getNotificationIcon(notification.type);
        const bgClass = isUnread ? 'bg-light' : '';
        const time = this.formatTime(notification.created_at);
        
        return `
            <div class="dropdown-item ${bgClass}" id="notif-${notification.id}" 
                 style="cursor: pointer; border-left: 3px solid ${this.getNotificationColor(notification.type)};">
                <div class="d-flex align-items-start">
                    <div class="me-2">
                        <i class="${icon} text-${this.getNotificationColorClass(notification.type)}"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="fw-bold">${notification.title}</div>
                        <div class="small text-muted">${notification.message}</div>
                        <div class="small text-muted mt-1">
                            <i class="far fa-clock"></i> ${time}
                        </div>
                    </div>
                    ${isUnread ? '<div class="ms-2"><span class="badge bg-primary">New</span></div>' : ''}
                </div>
            </div>
            <div class="dropdown-divider"></div>
        `;
    }
    
    /**
     * Get icon for notification type
     */
    getNotificationIcon(type) {
        const icons = {
            'new_complaint': 'fas fa-exclamation-circle',
            'status_update': 'fas fa-info-circle',
            'resolved': 'fas fa-check-circle'
        };
        return icons[type] || 'fas fa-bell';
    }
    
    /**
     * Get color for notification type
     */
    getNotificationColor(type) {
        const colors = {
            'new_complaint': '#0d6efd',
            'status_update': '#ffc107',
            'resolved': '#198754'
        };
        return colors[type] || '#6c757d';
    }
    
    /**
     * Get Bootstrap color class for notification type
     */
    getNotificationColorClass(type) {
        const classes = {
            'new_complaint': 'primary',
            'status_update': 'warning',
            'resolved': 'success'
        };
        return classes[type] || 'secondary';
    }
    
    /**
     * Format timestamp
     */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        
        return date.toLocaleDateString();
    }
    
    /**
     * Mark notification as read
     */
    async markAsRead(notificationId) {
        try {
            const token = localStorage.getItem('session_token');
            if (!token) return;
            
            const response = await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                await this.loadNotifications();
            }
        } catch (error) {
            console.error('[Notifications] Error marking as read:', error);
        }
    }
    
    /**
     * Mark all notifications as read
     */
    async markAllAsRead() {
        try {
            const token = localStorage.getItem('session_token');
            if (!token) return;
            
            const response = await fetch('/api/notifications/read-all', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                await this.loadNotifications();
            }
        } catch (error) {
            console.error('[Notifications] Error marking all as read:', error);
        }
    }
    
    /**
     * Destroy notification system
     */
    destroy() {
        this.stopPolling();
        this.isInitialized = false;
    }
}

// Create global instance
window.notificationSystem = new NotificationSystem();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Check if user is logged in
        const token = localStorage.getItem('session_token');
        if (token) {
            window.notificationSystem.init();
        }
    });
} else {
    const token = localStorage.getItem('session_token');
    if (token) {
        window.notificationSystem.init();
    }
}

// Made with Bob
