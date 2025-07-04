# ⚡ GPO Quick Start

**Get GPO running in 10 minutes.**

## 🚀 Deploy Cloud Dashboard

1. **Fork this repo** to your GitHub
2. **Go to [render.com](https://render.com)** → Sign up with GitHub
3. **New Web Service** → Connect your repo → **Deploy**
4. **Set environment variables** in Render dashboard:
   ```
   SUPABASE_HOST=your_supabase_host
   SUPABASE_DB=postgres
   SUPABASE_USER=postgres
   SUPABASE_PASSWORD=your_supabase_password
   ```
5. **Access app**: `https://your-app.onrender.com`
6. **Login**: `admin@gpo.com` / `admin123`

## 🧠 Setup Local Brain

1. **Install Docker** from docker.com
2. **Download setup**:
   ```bash
   curl -O https://raw.githubusercontent.com/yourusername/gpo-product/main/gpo_local_brain/setup.sh
   chmod +x setup.sh
   ./setup.sh
   ```
3. **Edit `.env`** with your Cloud GPO URL and API key
4. **Start**:
   ```bash
   ./start_local_brain.sh
   ```

## 🔑 Get API Key

1. **Login to Cloud GPO**
2. **Settings → API Keys → Generate**
3. **Copy to Local Brain `.env` file**

## ✅ Test

1. **Create project** in Cloud GPO
2. **Drop document** in Local Brain `./documents/` folder
3. **View AI analysis** in dashboard

---

**That's it! See [GPO_ONBOARDING_GUIDE.md](GPO_ONBOARDING_GUIDE.md) for complete setup.** 