# 🚀 GPO Complete Onboarding Guide

Welcome to GPO - the secure, AI-powered solution for Language Service Providers (LSPs).

## 📋 What You'll Get

✅ **Cloud Dashboard** - Manage projects, linguists, and AI analysis  
✅ **Local Brain** - Process sensitive documents on your network  
✅ **AI Analysis** - Automatic document analysis and linguist matching  
✅ **Security** - Documents never leave your premises  

---

## 🎯 Phase 1: Deploy Cloud Dashboard (5 minutes)

### Step 1: Deploy to Render
1. **Fork this repository** to your GitHub account
2. **Go to [render.com](https://render.com)** and sign up with GitHub
3. **Click "New +"** → "Web Service"
4. **Connect your fork** of the GPO repository
5. **Click "Deploy"** - Render will auto-detect settings

### Step 2: Set Environment Variables
In Render dashboard → Environment, add:
```
SUPABASE_HOST=your_supabase_host
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your_supabase_password
SUPABASE_PORT=5432
```

### Step 3: Access Your Dashboard
- **URL**: `https://your-app-name.onrender.com`
- **Login**: `admin@gpo.com` / `admin123`
- **⚠️ Change password immediately after first login**

---

## 🧠 Phase 2: Setup Local Brain (10 minutes)

### Option A: Docker Setup (Recommended)

#### 1. Install Docker
- Download: https://docs.docker.com/get-docker/
- Start Docker Desktop

#### 2. Download and Run Setup
```bash
# Download setup script
curl -O https://raw.githubusercontent.com/yourusername/gpo-product/main/gpo_local_brain/setup.sh
chmod +x setup.sh
./setup.sh
```

#### 3. Configure Connection
Edit the `.env` file:
```bash
# Get these from your Cloud GPO dashboard
CLOUD_GPO_URL=https://your-app-name.onrender.com
API_KEY=your_api_key_here
ORGANIZATION_ID=your_org_id
```

#### 4. Start Local Brain
```bash
./start_local_brain.sh
```

### Option B: Python Setup (Advanced)
```bash
git clone https://github.com/yourusername/gpo-product.git
cd gpo-product/gpo_local_brain
pip install -r requirements.txt
# Edit .env file
python main.py
```

---

## 🔑 Phase 3: Get API Keys (5 minutes)

### 1. Generate API Key
- **Login to Cloud GPO** dashboard
- **Go to**: Settings → API Keys
- **Click**: "Generate New Key"
- **Copy** the key to Local Brain `.env` file

### 2. Get Organization ID
- **Go to**: Settings → Organization
- **Copy** the Organization ID to `.env` file

---

## 👥 Phase 4: Initial Setup (15 minutes)

### 1. Organization Settings
- **Login** to Cloud GPO dashboard
- **Go to**: Settings → Organization
- **Fill in**: Company name, contact info, preferences

### 2. Create Users
- **Go to**: Admin → User Management
- **Add** team members with appropriate roles:
  - **Admin**: Full access
  - **PM**: Project management
  - **Viewer**: Read-only access

### 3. Add Linguists
- **Go to**: Linguists → Add Linguist
- **Add** your linguist database:
  - Name, email, languages, specializations
  - Availability, rates, performance metrics

### 4. Upload Linguist Database (Optional)
- **Prepare CSV** with columns: name, email, source_lang, target_lang, specialization
- **Go to**: Linguists → Upload
- **Select** your CSV file

---

## 🧪 Phase 5: Test the System (10 minutes)

### 1. Create Test Project
- **Go to**: Dashboard → New Project
- **Fill in**: Client, source/target languages, deadline
- **Upload** a test document

### 2. Process Document
- **Place document** in Local Brain `./documents/` folder
- **Monitor** processing in dashboard
- **View** AI analysis results

### 3. Review AI Recommendations
- **Check**: Complexity analysis
- **Review**: Linguist recommendations
- **Verify**: Quality predictions

---

## 🔒 Security & Privacy

### ✅ Your Data is Safe
- **Documents stay local** - never uploaded to cloud
- **Only analysis results** sent to dashboard
- **Encrypted communication** (HTTPS)
- **No content stored** in cloud database

### 🛡️ Best Practices
- **Change default password** immediately
- **Use strong API keys** (auto-generated)
- **Regular backups** of local documents
- **Monitor access logs** in dashboard

---

## 📊 Daily Operations

### For Project Managers
1. **Create projects** in dashboard
2. **Upload documents** to Local Brain folder
3. **Review AI analysis** results
4. **Assign linguists** based on recommendations
5. **Monitor progress** and deadlines

### For Linguists
1. **Check assignments** in dashboard
2. **View document analysis** before starting
3. **Update availability** and preferences
4. **Track performance** metrics

### For Admins
1. **Monitor system health** (Local Brain logs)
2. **Manage users** and permissions
3. **Review audit logs** for security
4. **Update linguist database**

---

## 🆘 Troubleshooting

### Local Brain Issues
```bash
# Check status
docker logs gpo-local-brain

# Restart if needed
docker restart gpo-local-brain

# View configuration
cat .env
```

### Cloud Dashboard Issues
- **Check Render logs** in dashboard
- **Verify environment variables** are set
- **Test database connection** in logs

### Common Problems

| Problem | Solution |
|---------|----------|
| Local Brain can't connect | Check `CLOUD_GPO_URL` and `API_KEY` |
| Documents not processing | Verify file format (txt, docx, pdf) |
| Dashboard login fails | Reset password or check admin user |
| API key invalid | Generate new key in dashboard |

---

## 📞 Support & Next Steps

### Getting Help
1. **Check logs** first (Docker or application logs)
2. **Review troubleshooting** section above
3. **Contact support** with specific error messages

### Scaling Up
- **Production deployment**: Migrate to AWS/GCP if needed
- **Custom domain**: Set up in Render dashboard
- **Multiple Local Brains**: Deploy on different networks
- **Advanced features**: Custom AI models, integrations

### Training Your Team
- **Demo walkthrough**: Schedule with your team
- **User guides**: Share role-specific sections
- **Best practices**: Establish workflows
- **Regular reviews**: Monthly optimization

---

## 🎉 You're Ready!

Your GPO system is now fully operational:

✅ **Cloud Dashboard**: Live and accessible  
✅ **Local Brain**: Processing documents securely  
✅ **AI Analysis**: Providing insights  
✅ **Team Access**: Users can login and work  

**Start with a test project and gradually expand your usage.**

---

*This guide covers 95% of use cases. For advanced customization or enterprise features, contact support.* 