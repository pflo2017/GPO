# 🧠 GPO Local Brain Setup

The Local Brain processes sensitive documents on your local network - **documents never leave your premises**.

## Quick Setup (Docker)

### 1. **Install Docker**
- Download from: https://docs.docker.com/get-docker/
- Start Docker Desktop after installation

### 2. **Download Setup Script**
```bash
curl -O https://raw.githubusercontent.com/yourusername/gpo-product/main/gpo_local_brain/setup.sh
chmod +x setup.sh
./setup.sh
```

### 3. **Configure Connection**
Edit the `.env` file created by setup:
```bash
# Get these from your Cloud GPO dashboard
CLOUD_GPO_URL=https://your-app-name.onrender.com
API_KEY=your_api_key_here
ORGANIZATION_ID=your_org_id

# Local settings
POLL_INTERVAL=30
DEBUG=True
```

### 4. **Start Local Brain**
```bash
./start_local_brain.sh
```

## Manual Setup (Python)

If you prefer to run without Docker:

### 1. **Install Python 3.8+**
```bash
python3 --version  # Should be 3.8 or higher
```

### 2. **Clone and Setup**
```bash
git clone https://github.com/yourusername/gpo-product.git
cd gpo-product/gpo_local_brain
pip install -r requirements.txt
```

### 3. **Configure Environment**
Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. **Run Local Brain**
```bash
python main.py
```

## Getting API Keys

### 1. **Login to Cloud GPO**
- Go to your deployed Cloud GPO URL
- Login with: `admin@gpo.com` / `admin123`

### 2. **Generate API Key**
- Go to: Settings → API Keys
- Click "Generate New Key"
- Copy the key to your `.env` file

### 3. **Get Organization ID**
- Go to: Settings → Organization
- Copy the Organization ID to your `.env` file

## Usage

### 1. **Place Documents**
- Put files in: `./documents/` folder
- Supported: `.txt`, `.docx`, `.pdf`

### 2. **Monitor Processing**
- Check status in Cloud GPO dashboard
- View logs: `docker logs gpo-local-brain`

### 3. **Review Results**
- AI analysis appears in Cloud GPO
- Documents are moved to `./processed/` after completion

## Security

✅ **Your documents never leave your network**  
✅ **Only analysis results are sent to Cloud GPO**  
✅ **All communication is encrypted (HTTPS)**  
✅ **No document content is stored in cloud**  

## Troubleshooting

### Local Brain won't start
```bash
# Check Docker
docker --version

# Check logs
docker logs gpo-local-brain

# Restart
docker restart gpo-local-brain
```

### Can't connect to Cloud GPO
- Check `CLOUD_GPO_URL` in `.env`
- Verify API key is correct
- Check internet connection
- Verify Cloud GPO is running

### Documents not processing
- Check `./documents/` folder permissions
- Verify file formats (txt, docx, pdf only)
- Check Local Brain logs for errors

## Support

For help:
1. Check logs: `docker logs gpo-local-brain`
2. Verify `.env` settings
3. Ensure Cloud GPO is accessible
4. Contact support with log output 