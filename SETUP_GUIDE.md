# Complete Setup Guide - Campus Sustainability Twin AI

This guide will help you set up all components including IBM Granite, Google Sheets, and ChromaDB.

## 📋 Prerequisites

- Python 3.8+
- IBM Cloud account (for Granite)
- Google Cloud account (for Sheets API)
- Internet connection

## 🚀 Step 1: Install All Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS (Web framework)
- Pandas (Data processing)
- IBM watsonx.ai (Granite LLM)
- Google Sheets API libraries
- ChromaDB (Vector database)
- Sentence Transformers (Embeddings)
- And more...

## 🔧 Step 2: Configure IBM Granite (watsonx.ai)

### 2.1 Create IBM Cloud Account

1. Go to [IBM Cloud](https://cloud.ibm.com/)
2. Sign up for a free account
3. Verify your email

### 2.2 Create watsonx.ai Instance

1. Log in to IBM Cloud
2. Go to **Catalog** → Search for "watsonx.ai"
3. Click **Create** (Free tier available)
4. Wait for provisioning (2-3 minutes)

### 2.3 Get API Credentials

1. Go to your watsonx.ai instance
2. Click **Manage** → **Access (IAM)**
3. Create an **API Key**:
   - Click "Create an IBM Cloud API key"
   - Name it: "Campus-AI-Key"
   - Copy and save the API key (shown only once!)

### 2.4 Get Project ID

1. In watsonx.ai, go to **Projects**
2. Create a new project: "Campus Sustainability AI"
3. Click on the project
4. Copy the **Project ID** from the URL or project settings

### 2.5 Add to .env File

```bash
IBM_WATSONX_API_KEY=your_api_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

## 📊 Step 3: Configure Google Sheets

### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Campus-Sustainability-AI"
3. Wait for project creation

### 3.2 Enable Google Sheets API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Sheets API"
3. Click **Enable**
4. Also enable "Google Drive API"

### 3.3 Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Name: "campus-ai-service"
4. Click **Create and Continue**
5. Grant role: **Editor**
6. Click **Done**

### 3.4 Generate Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create New Key**
4. Choose **JSON** format
5. Click **Create**
6. Save the downloaded file as `credentials.json` in your project root

### 3.5 Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it: "Campus Complaints"
4. Add headers in first row:
   ```
   Complaint_ID | Category | Location | Complaint | Priority | Status | Users_Affected | Date
   ```

### 3.6 Share Sheet with Service Account

1. Open your Google Sheet
2. Click **Share** button
3. Add the service account email (from credentials.json)
   - Format: `campus-ai-service@project-id.iam.gserviceaccount.com`
4. Give **Editor** permission
5. Click **Send**

### 3.7 Add to .env File

```bash
GOOGLE_SHEETS_CREDENTIALS=credentials.json
GOOGLE_SHEET_NAME=Campus Complaints
```

## 🗄️ Step 4: Configure ChromaDB (RAG Knowledge Base)

ChromaDB is automatically configured! It will:
- Create a local database in `./chroma_db/` folder
- Initialize with campus policies on first run
- Store embeddings for semantic search

No additional configuration needed!

## ✅ Step 5: Verify Setup

Run the test script:

```bash
python test_basic.py
```

Expected output:
```
[OK] Python version is compatible
[OK] All files present
[OK] pandas, flask, flask-cors, python-dotenv
[OK] IBM watsonx.ai (if configured)
[OK] Google Sheets (if configured)
[OK] Priority Detector working
[OK] Classifier working
[OK] CSV data loaded
[OK] Dashboard data provider working
```

## 🚀 Step 6: Run the Application

```bash
python app.py
```

You should see:
```
IBM watsonx.ai not installed. Using rule-based classification.
OR
[OK] IBM Granite model initialized

Connected to Google Sheets
OR
Using local CSV fallback

Initializing RAG Knowledge Base...
[OK] Loaded existing knowledge base
OR
[OK] Created new knowledge base

Knowledge base initialized with 500 complaints

 * Running on http://0.0.0.0:5000
```

## 🌐 Step 7: Access Dashboard

Open your browser:
```
http://localhost:5000
```

## 🧪 Step 8: Test the System

### Test 1: Submit a Complaint

1. Click "Submit Complaint" in sidebar
2. Enter:
   ```
   Complaint: No water supply in Hostel B since morning
   Location: Hostel B
   Users Affected: 100
   ```
3. Click "Classify with AI"
4. Should show:
   ```
   Category: Water
   Urgency: High
   Affected Area: Hostel B
   ```
5. Click "Submit Complaint"

### Test 2: View AI Recommendations

1. Click on the submitted complaint
2. Should see:
   - Immediate Actions (3-5 items)
   - Preventive Measures
   - Resolution Time Estimate
   - Responsible Department
   - Sustainability Impact

### Test 3: Check Dashboard Analytics

1. Go to Dashboard
2. Verify:
   - Total complaints count
   - Category distribution chart
   - Trend chart
   - High priority table

## 🔍 Troubleshooting

### Issue: IBM Granite not working

**Check:**
```bash
# Verify API key
echo $IBM_WATSONX_API_KEY

# Test connection
python -c "from ibm_watsonx_ai import Credentials; print('OK')"
```

**Solution:**
- Verify API key is correct
- Check project ID
- Ensure watsonx.ai instance is active
- System will use rule-based fallback if unavailable

### Issue: Google Sheets not syncing

**Check:**
```bash
# Verify credentials file exists
ls credentials.json

# Test connection
python -c "import gspread; print('OK')"
```

**Solution:**
- Verify credentials.json is in root directory
- Check service account has access to sheet
- Verify sheet name matches .env
- System will use CSV fallback if unavailable

### Issue: ChromaDB errors

**Solution:**
```bash
# Delete and reinitialize
rm -rf chroma_db
python app.py
```

### Issue: Port already in use

**Solution:**
```bash
# Change port in .env
PORT=5001

# Or kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

## 📊 Monitoring

### Check System Status

```bash
# View logs
tail -f app.log

# Check ChromaDB
python -c "import chromadb; client = chromadb.Client(); print(client.list_collections())"

# Test IBM Granite
python -c "from modules.granite_classifier import GraniteClassifier; c = GraniteClassifier(); print(c.model)"
```

## 🔒 Security Best Practices

1. **Never commit credentials**
   ```bash
   # Already in .gitignore:
   .env
   credentials.json
   ```

2. **Rotate API keys regularly**
   - IBM: Every 90 days
   - Google: Every 180 days

3. **Use environment variables**
   - Never hardcode credentials
   - Use .env for local development
   - Use secrets manager in production

4. **Limit permissions**
   - Google: Only Editor access needed
   - IBM: Only watsonx.ai access needed

## 📈 Performance Tips

1. **ChromaDB Optimization**
   ```python
   # Increase batch size for large datasets
   collection.add(documents=docs, batch_size=100)
   ```

2. **Caching**
   ```python
   # Add Redis for production
   pip install redis flask-caching
   ```

3. **Database**
   ```python
   # Use PostgreSQL instead of CSV
   pip install psycopg2-binary sqlalchemy
   ```

## 🎓 Next Steps

1. **Customize Categories**
   - Edit `modules/granite_classifier.py`
   - Add your campus-specific categories

2. **Add More Policies**
   - Edit `modules/rag_knowledge_base.py`
   - Add campus-specific guidelines

3. **Customize Dashboard**
   - Edit `templates/index.html`
   - Modify `static/css/dashboard.css`

4. **Deploy to Production**
   - See `DEPLOYMENT.md` for details
   - Use gunicorn for production server
   - Set up HTTPS with SSL certificate

## 📞 Support

- **Documentation**: README.md, QUICKSTART.md, DEPLOYMENT.md
- **Issues**: Create GitHub issue
- **Email**: support@campus.edu

---

**Setup Complete! Your Campus Sustainability Twin AI is ready to use! 🎉**