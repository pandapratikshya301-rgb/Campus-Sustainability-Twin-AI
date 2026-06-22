"""
Test Notification System
Run this to create test notifications in the database
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.database import Database
import time

def test_notifications():
    """Create test notifications"""
    db = Database()
    
    print("=" * 60)
    print("NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    
    # Get or create a test user
    print("\n1. Setting up test user...")
    result = db.register_user(
        email='test@campus.edu',
        password='test123',
        full_name='Test User',
        user_type='student'
    )
    
    if result.get('success'):
        print("✅ Test user created")
    else:
        print("ℹ️  Test user already exists")
    
    # Login to get user ID
    login_result = db.login_user(
        email_or_phone='test@campus.edu',
        password='test123',
        ip_address='127.0.0.1',
        user_agent='Test'
    )
    
    if not login_result.get('success'):
        print("❌ Failed to login test user")
        return
    
    user_id = login_result['user']['id']
    print(f"✅ Logged in as user ID: {user_id}")
    
    # Create test notifications
    print("\n2. Creating test notifications...")
    
    # Notification 1: New Complaint
    success1 = db.create_notification(
        user_id=user_id,
        complaint_id='TEST-001',
        notification_type='new_complaint',
        title='Complaint Registered',
        message='Your complaint #TEST-001 about broken fan has been registered successfully. Category: Electricity, Priority: Medium'
    )
    print(f"{'✅' if success1 else '❌'} Created 'new_complaint' notification")
    time.sleep(0.1)
    
    # Notification 2: Status Update
    success2 = db.create_notification(
        user_id=user_id,
        complaint_id='TEST-001',
        notification_type='status_update',
        title='Complaint Status Updated',
        message='Your complaint #TEST-001 status changed to: In Progress. Our team is working on it.'
    )
    print(f"{'✅' if success2 else '❌'} Created 'status_update' notification")
    time.sleep(0.1)
    
    # Notification 3: Resolved
    success3 = db.create_notification(
        user_id=user_id,
        complaint_id='TEST-001',
        notification_type='resolved',
        title='Complaint Resolved',
        message='Your complaint #TEST-001 has been resolved! The fan has been repaired. Thank you for your patience.'
    )
    print(f"{'✅' if success3 else '❌'} Created 'resolved' notification")
    
    # Get notifications
    print("\n3. Retrieving notifications...")
    notifications = db.get_user_notifications(user_id)
    unread_count = db.get_unread_count(user_id)
    
    print(f"✅ Found {len(notifications)} notifications")
    print(f"✅ Unread count: {unread_count}")
    
    # Display notifications
    print("\n4. Notification Details:")
    print("-" * 60)
    for notif in notifications:
        status = "🔴 UNREAD" if not notif['is_read'] else "✅ READ"
        icon = {'new_complaint': '🔵', 'status_update': '🟡', 'resolved': '🟢'}.get(notif['type'], '⚪')
        print(f"\n{icon} {status}")
        print(f"   ID: {notif['id']}")
        print(f"   Type: {notif['type']}")
        print(f"   Title: {notif['title']}")
        print(f"   Message: {notif['message']}")
        print(f"   Time: {notif['created_at']}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nTo test in browser:")
    print("1. Run: python app.py")
    print("2. Login with: test@campus.edu / test123")
    print("3. Click the bell icon in navbar")
    print("4. You should see 3 notifications with sounds!")
    print("\nSession Token:", login_result.get('session_token'))
    print("=" * 60)

if __name__ == '__main__':
    test_notifications()

# Made with Bob
