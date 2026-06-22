# Campus Sustainability Twin AI

**Intelligent Complaint Analysis & Resource Management System**

A comprehensive AI-powered system for managing campus sustainability complaints, leveraging IBM Granite LLM, RAG knowledge base, and real-time analytics to support UN Sustainable Development Goals (SDGs) 6, 11, and 12.

![System Architecture](https://img.shields.io/badge/AI-IBM%20Granite-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)

## 🌟 Features

### 1. **User Authentication & Session Management** 🔐
- **Google OAuth Sign-In**: One-click login with Google account
- **Demo Login**: Quick access with pre-configured demo credentials
- **Secure Registration**: User accounts with email/phone and password
- **Session Persistence**: 7-day sessions - no need to sign in repeatedly
- **Protected Routes**: Secure complaint submission and user data
- **Animated Login Portal**: Modern design with cartoon bear character and smooth animations

### 2. **AI-Powered Complaint Classification** 🤖
- **IBM Granite LLM Integration**: Automatically classifies complaints into Water, Electricity, or Transportation categories
- **Enhanced Rule-Based Fallback**: Improved keyword matching for accurate classification (e.g., fan/AC → Electricity)
- **Intelligent Priority Detection**: Multi-factor analysis to determine urgency (High/Medium/Low)
- **Real-time Processing**: Instant classification and recommendation generation

### 3. **Intelligent Chatbot with RAG** 💬
- **35+ Sustainability Guidelines**: Comprehensive knowledge base covering all 17 SDGs
- **Natural Language Understanding**: Answers questions about reporting, resolution, and tracking
- **Voice Input**: Hands-free interaction with continuous speech recognition
- **Auto-Send**: Automatically submits voice input when you stop speaking
- **Suggested Questions**: Quick access to common queries
- **Visual Feedback**: Pulsing animations during voice recognition

### 4. **Real-Time Notification System** 🔔
- **Notification Bell**: Badge counter showing unread notifications
- **Sound Alerts**: Different sounds for status updates, assignments, and resolutions
- **Browser Notifications**: Desktop alerts for important updates
- **10-Second Polling**: Near real-time updates without page refresh
- **Notification History**: View all past notifications with timestamps

### 5. **Image Upload & Capture** 📸
- **Photo Upload**: Attach images to complaints for better documentation
- **Camera Capture**: Take photos directly from your device
- **File Validation**: Automatic format and size checking
- **Visual Preview**: See uploaded images before submission

### 6. **Smart Recommendations** 💡
- **Immediate Actions**: Context-aware action items based on complaint type
- **Preventive Measures**: Long-term solutions to prevent recurring issues
- **Department Routing**: Automatic assignment to responsible departments
- **Resolution Time Estimates**: Data-driven time predictions

### 7. **Modern Admin Dashboard** 📊
- **Vibrant UI**: Color-coded cards with gradients and animations
- **Real-time Statistics**: Live complaint tracking and analytics
- **Interactive Charts**: Category distribution, status overview, and resolution time trends
- **High Priority Alerts**: Immediate visibility of critical issues
- **Sustainability Metrics**: SDG alignment and impact assessment
- **User Complaints Tracking**: View complaints submitted by logged-in user
- **Animated Icons**: Bouncing, pulsing, and floating effects

### 8. **Google Sheets Integration** 📑
- **Seamless Data Sync**: Automatic synchronization with Google Sheets
- **CSV Fallback**: Works offline with local CSV files
- **Bulk Operations**: Efficient handling of large datasets

## 🏗️ System Architecture

```
Student Complaint
        ↓
Google Sheets Dataset
        ↓
IBM Granite (LLM)
        ↓
Complaint Classification & Prioritization
        ↓
RAG Knowledge Base
        ↓
AI Recommendations
        ↓
Dashboard
        ↓
Campus Administrator
```

## 📋 Prerequisites

- Python 3.8 or higher
- IBM watsonx.ai account (for Granite LLM)
- Google Cloud account (for Sheets API - optional)
- 4GB RAM minimum
- Modern web browser

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd IBM
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - IBM_WATSONX_API_KEY
# - IBM_WATSONX_PROJECT_ID
# Optional:
# - GOOGLE_SHEETS_CREDENTIALS (for Google Sheets integration)
```

### 5. Setup Google Sheets (Optional)

If using Google Sheets integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API
4. Create service account credentials
5. Download credentials as `credentials.json`
6. Place in project root directory
7. Share your Google Sheet with the service account email

### 6. Initialize the System

```bash
python app.py
```

The system will:
- Initialize the RAG knowledge base
- Load campus policies and guidelines
- Import historical complaints from CSV
- Start the Flask web server

## 📊 Usage

### First Time Setup - Quick Login Options

**Option 1: Google OAuth (Recommended)**
1. Open your browser and navigate to: `http://localhost:5000/login`
2. Click "Sign in with Google"
3. Select your Google account
4. You'll be automatically logged in and redirected to the dashboard

**Option 2: Demo Login (For Testing)**
1. Navigate to: `http://localhost:5000/login`
2. Click "Demo Login"
3. Instantly access the system with pre-configured credentials

**Option 3: Manual Registration**
1. Navigate to: `http://localhost:5000/login`
2. Click on the "Register" tab
3. Fill in your details (name, email, phone, password)
4. Click "Register"
5. You'll be automatically logged in

### Access the Dashboard

After logging in, you'll be redirected to:
```
http://localhost:5000
```

### Submit a Complaint

1. Click "Submit Complaint" in the sidebar
2. Enter complaint description
3. Specify location and users affected
4. **Optional**: Upload or capture an image
5. Click "Classify with AI" to preview classification
6. Submit the complaint (automatically linked to your account)

### Use the Chatbot

1. Click the chat icon in the bottom-right corner
2. **Type** your question or click a suggested question
3. **Or use voice**: Click the microphone icon and speak
4. Get instant answers about:
   - SDGs (all 17 goals)
   - How to report issues
   - Issue resolution process
   - Complaint tracking
   - Campus sustainability policies

### Receive Notifications

1. Watch the notification bell icon (top-right)
2. Badge shows unread notification count
3. Click bell to view notification history
4. Hear sound alerts for:
   - Status updates (ding)
   - Assignments (chime)
   - Resolutions (success)
5. Browser notifications appear automatically

### View Recommendations

1. Click on any complaint in the dashboard
2. View AI-generated recommendations:
   - Immediate actions
   - Preventive measures
   - Resolution time estimate
   - Responsible department

### Monitor Analytics

- **Dashboard**: Real-time statistics and trends
- **Category Distribution**: Pie chart showing complaint breakdown
- **Status Overview**: Track open, in-progress, and resolved complaints
- **Resolution Time**: Average time to resolve by category
- **High Priority**: Table of urgent complaints requiring attention

## 🔧 Configuration

### Customize Categories

Edit `modules/granite_classifier.py`:

```python
self.categories = ['Water', 'Electricity', 'Transportation', 'YourCategory']
```

### Adjust Priority Weights

Edit `modules/priority_detector.py`:

```python
self.priority_weights = {
    'urgency_keywords': 0.4,
    'users_affected': 0.3,
    'category_severity': 0.2,
    'time_sensitivity': 0.1
}
```

### Add Knowledge Base Content

Edit `modules/rag_knowledge_base.py` in the `_initialize_knowledge_base()` method to add custom guidelines.

## 📁 Project Structure

```
IBM/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git exclusions
├── README.md                       # This file
├── Campus_Sustainability_Twin_AI_500_Row_Dataset.csv
│
├── modules/                        # Core modules
│   ├── __init__.py
│   ├── chatbot.py                 # AI chatbot with RAG
│   ├── sheets_integration.py      # Google Sheets integration
│   ├── granite_classifier.py      # IBM Granite AI classifier
│   ├── priority_detector.py       # Priority detection logic
│   ├── rag_knowledge_base.py      # RAG knowledge base (35+ guidelines)
│   ├── recommendation_engine.py   # AI recommendation engine
│   ├── dashboard_data.py          # Dashboard data provider
│   └── database.py                # User authentication & notifications
│
├── templates/                      # HTML templates
│   ├── index.html                 # Main dashboard with chatbot
│   └── login.html                 # Animated login/register portal
│
├── static/                         # Static assets
│   ├── css/
│   │   ├── chatbot.css            # Chatbot styles
│   │   ├── dashboard.css          # Dashboard styles
│   │   ├── modern-dashboard.css   # Modern UI with animations
│   │   ├── notifications.css      # Notification bell styles
│   │   └── features.css           # Feature page styles
│   ├── js/
│   │   ├── chatbot.js             # Chatbot with voice input
│   │   ├── dashboard.js           # Dashboard JavaScript
│   │   ├── notifications.js       # Real-time notifications
│   │   └── features.js            # Feature interactions
│   ├── uploads/                   # User uploaded images
│   └── sounds/                    # Notification sound files
│
├── chroma_db/                      # Vector database (auto-generated)
└── campus_ai.db                    # SQLite database (auto-generated)
```

## 🔌 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/verify` - Verify session token
- `POST /api/auth/logout` - User logout

### Complaints

- `GET /api/complaints` - Get all complaints
- `POST /api/complaint/submit` - Submit new complaint (requires auth)
- `GET /api/complaint/<id>` - Get specific complaint
- `PUT /api/complaint/<id>/update` - Update complaint status
- `GET /api/user/complaints` - Get user's complaints (requires auth)

### Dashboard

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/trends` - Get complaint trends

### AI Services

- `POST /api/classify` - Classify complaint text
- `POST /api/knowledge-base/search` - Search knowledge base

## 🌍 Sustainability Impact

This system supports three UN Sustainable Development Goals:

### SDG 6: Clean Water and Sanitation
- Monitors water supply issues
- Tracks contamination reports
- Promotes water conservation

### SDG 11: Sustainable Cities and Communities
- Optimizes campus transportation
- Reduces traffic congestion
- Improves infrastructure management

### SDG 12: Responsible Consumption and Production
- Tracks energy efficiency
- Monitors resource wastage
- Promotes sustainable practices

## 🧪 Testing

Run the system with sample data:

```bash
python app.py
```

The system will automatically load the 500-row dataset and initialize the knowledge base.

## 🔒 Security Features

### Authentication & Authorization
- **User Registration**: Secure account creation with email/phone validation
- **Password Security**: SHA-256 hashing for password storage
- **Session Management**: 7-day persistent sessions with secure tokens
- **Protected Routes**: Authentication required for complaint submission
- **Token Validation**: Automatic session verification on every request

### Best Practices
- Store API keys in `.env` file (never commit to git)
- Use HTTPS in production
- Regularly update dependencies
- Sanitize user inputs
- Database file excluded from version control

### Authentication Documentation
For detailed authentication system documentation, see [AUTHENTICATION.md](AUTHENTICATION.md)

## 🐛 Troubleshooting

### Issue: IBM Granite not working
**Solution**: Check your API key and project ID in `.env` file. The system will fall back to rule-based classification if Granite is unavailable.

### Issue: Google Sheets not syncing
**Solution**: Verify `credentials.json` is in the root directory and the service account has access to your sheet. The system will use local CSV as fallback.

### Issue: ChromaDB errors
**Solution**: Delete the `chroma_db` folder and restart the application to reinitialize the database.

### Issue: Port already in use
**Solution**: Change the PORT in `.env` file or stop the process using port 5000.

## 📈 Performance Optimization

- **Caching**: Implement Redis for frequently accessed data
- **Database**: Use PostgreSQL for production instead of CSV
- **Load Balancing**: Deploy multiple instances behind a load balancer
- **CDN**: Serve static assets through a CDN

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **Development Team** - Campus Sustainability Initiative

## 🙏 Acknowledgments

- IBM watsonx.ai for Granite LLM
- Google Cloud for Sheets API
- ChromaDB for vector database
- Flask community for web framework
- UN for Sustainable Development Goals framework

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@campus.edu
- Documentation: [Link to docs]

## 🔄 Version History

### v2.0.0 (2026-06-22) - Major Feature Update
- ✅ **Intelligent Chatbot**: RAG-powered chatbot with 35+ sustainability guidelines
- ✅ **Voice Input**: Continuous speech recognition with auto-send
- ✅ **Real-Time Notifications**: Bell icon with sound alerts and browser notifications
- ✅ **Image Upload**: Photo attachment and camera capture for complaints
- ✅ **Google OAuth**: One-click sign-in with Google
- ✅ **Modern UI**: Vibrant colors, gradients, and smooth animations
- ✅ **Enhanced Classifier**: Improved accuracy with rule-based fallback
- ✅ **Animated Login**: Cartoon bear character with modern design

### v1.0.0 (2026-06-15) - Initial Release
- IBM Granite integration
- RAG knowledge base
- Admin dashboard
- Google Sheets sync
- User authentication

## 🗺️ Roadmap

- [x] Intelligent chatbot with voice input
- [x] Real-time notification system
- [x] Image upload for complaints
- [x] Google OAuth integration
- [x] Modern animated UI
- [ ] Mobile app for students
- [ ] SMS/Email notifications
- [ ] Multi-language support
- [ ] Advanced analytics with ML predictions
- [ ] Integration with campus IoT sensors
- [ ] Automated resolution workflows
- [ ] Student feedback system
- [ ] Performance benchmarking dashboard

---

**Built with ❤️ for a sustainable campus future**