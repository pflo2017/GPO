# Global Project Orchestrator (GPO)

GPO is a comprehensive project management system designed specifically for Language Service Providers (LSPs). It combines a web-based dashboard with an AI-powered local analysis engine to help project managers make better decisions.

## 🚀 Quick Start

For the fastest way to get up and running:

```bash
# Clone the repository
git clone <repository-url>
cd gpo-product

# Install dependencies
pip install -r requirements.txt

# Start the application
./start.sh
```

Then open your browser to: http://localhost:5001

Default login credentials:
- Email: admin@test.com
- Password: password

## 🏗️ System Architecture

GPO consists of two main components:

1. **GPO Cloud Dashboard** - A web application that provides the user interface for project management, linguist management, and analytics.

2. **GPO Local Brain** - A local AI engine that analyzes project documents to provide risk assessment, linguist recommendations, and strategic insights.

## 📋 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (a Supabase instance is configured by default)
- Operating System: macOS, Linux, or Windows

### Installation Steps

1. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

Create a `.env` file in the project root with the following variables:

```
# Database Configuration
SUPABASE_HOST=db.dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PORT=5432
SUPABASE_USER=postgres
SUPABASE_PASSWORD=UCOXZibz5OLgTofg
SUPABASE_DB=postgres

# Application Settings
SECRET_KEY=your-secret-key
FLASK_ENV=development
DEBUG=True

# Local Brain Configuration
GPO_CLOUD_API_URL=http://localhost:5001
GPO_ORGANIZATION_API_KEY=local-dev-key
```

4. **Start the application:**

```bash
./start.sh
```

This script will:
- Check for port conflicts
- Start the GPO web application
- Start the GPO Local Brain component
- Create necessary directories

## 🧪 Testing with Real Data

To test the system with real data and AI analysis:

```bash
cd gpo_product
python run_comprehensive_test.py
```

This script will:
1. Create a test organization and admin user
2. Create test linguist profiles
3. Create a test project with sample documents
4. Trigger the AI analysis process

## 📄 Document Processing

GPO supports the following document formats:
- PDF (.pdf)
- Microsoft Word (.docx)
- Text files (.txt)

To test with your own documents:
1. Place sample documents in the `dummy_docs` directory
2. Run the comprehensive test script
3. Or upload documents manually through the web interface

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in the `.env` file
   - Check if the database server is running

2. **Port Conflicts**
   - The application uses ports 5001 (web) and 5002 (local brain)
   - Use `lsof -i :5001` to check if the port is in use
   - Modify ports in the configuration if needed

3. **Missing Tables**
   - If you see "relation does not exist" errors, the database schema may need to be updated
   - Run `python gpo_product/fix_db.py` to repair the database schema

## 🔐 Security Considerations

For production testing:

1. **Change Default Credentials**
   - Update the default admin password after first login
   - Create separate user accounts for each tester

2. **API Keys**
   - The Local Brain uses an API key to communicate with the Cloud Dashboard
   - For production, generate a secure API key and update the configuration

3. **Data Privacy**
   - Be mindful of the documents you upload for testing
   - The system analyzes document content for risk assessment

## 📚 Additional Resources

- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Compliance Information](COMPLIANCE.md)
- [Local Brain Setup](LOCAL_BRAIN_SETUP.md)

## 📞 Support

For issues or questions, please contact:
- Email: support@gpo-product.com
- GitHub Issues: [Create a new issue](https://github.com/yourusername/gpo-product/issues)
