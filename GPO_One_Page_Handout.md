# GPO - AI-Powered Project Orchestrator

## What is GPO?
GPO is an intelligent project orchestration platform for Language Service Providers (LSPs). It uses advanced AI to proactively identify, assess, and mitigate risks in translation projects—helping you deliver on time, on budget, and in compliance.

---

## Key Benefits
- **AI-Powered Risk Assessment:** Instantly analyzes projects and documents for deadline, quality, and compliance risks.
- **Sensitive Data Detection:** Flags PHI, PII, legal, and financial content for secure handling.
- **Proactive Recommendations:** Actionable advice to prevent delays, rework, and compliance issues.
- **Resource Optimization:** Monitors linguist workloads and recommends optimal assignments.
- **Professional Dashboard:** Real-time visibility into all projects and risk levels.
- **API-Ready:** Designed for integration with your existing systems.

---

## How Does GPO Work?
1. **Upload Project & Document:** Enter project details and upload source files (DOCX, PDF, TXT).
2. **AI Analysis:** Google Gemini LLM analyzes content, deadlines, and resources for risks.
3. **Actionable Insights:** Dashboard displays risk status, reasons, and recommendations.
4. **Compliance & Logging:** All actions and AI decisions are logged for audit and compliance.

---

## Why Docker?
- **Fast Deployment:** GPO runs in a Docker container—a portable, self-contained box that works the same on any server or cloud.
- **No Setup Hassle:** No need to install dependencies or configure environments. Just run one command and it works.
- **Easy Updates:** Future upgrades are as simple as pulling a new image and restarting.

---

## How to Go Live
1. **Get a Server or Cloud VM** (with Docker installed)
2. **Set Up Environment Variables** (API keys, database info)
3. **Deploy with Docker:**
   - Build: `docker build -t gpo-product .`
   - Run: `docker run -d --restart unless-stopped --name gpo-app -p 80:5000 --env-file .env gpo-product`
4. **Access the Dashboard:** Open your browser to your server's address.
5. **Integrate:** Use the API for TMS/ERP integration (optional).

---

## Why Choose GPO?
- **Proactive, not reactive:** Prevents problems before they happen.
- **AI-powered:** Goes beyond rules—understands real content and context.
- **Compliance-focused:** Reduces risk of data breaches and regulatory fines.
- **Saves time and money:** Fewer delays, less rework, better resource use.
- **Ready for enterprise:** Secure, scalable, and API-first.

---

**Contact us to schedule a live demo or discuss your deployment needs!** 