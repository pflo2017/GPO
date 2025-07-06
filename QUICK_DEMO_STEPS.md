# GPO Quick Demo Steps

## Pre-Demo Setup

1. **Start the demo environment**:
   ```bash
   ./run_demo.sh
   ```
   This will:
   - Stop any existing GPO processes
   - Set up necessary directories
   - Run the comprehensive test to populate the database
   - Start the main application and local brain
   - Provide login credentials

2. **Verify the environment**:
   - Open http://localhost:5001 in your browser
   - Log in with admin@test.com / password
   - Confirm you can see the dashboard

## Live Demo with Client

### 1. Introduction & System Overview
- Explain that GPO consists of two components:
  - Cloud Dashboard (web interface)
  - Local Brain (secure AI engine that runs on-premises)
- Emphasize that sensitive documents never leave the client's network

### 2. Create a New Project
- Click "New Project Request"
- Fill in the form:
  - Project Name: "Client Demo - Legal Contract"
  - Source Language: English
  - Target Language: German
  - Content Type: Legal
  - Deadline: (choose a date 2 weeks from now)
- Click "Create Project"
- Note the project ID that appears in the URL (you'll need this later)

### 3. Simulate Document Upload
- Open a new terminal window
- Copy a sample document to the local brain's monitored folder:
  ```bash
  cp dummy_docs/sample_legal_contract.txt gpo_local_brain/documents/
  ```
- Explain that in a real scenario, this would be done by placing documents in a secure folder on the client's network

### 4. Run AI Analysis
- In your terminal, run:
  ```bash
  ./analyze_project.sh <project_id>
  ```
  Replace `<project_id>` with the ID from step 2
- Show the terminal output as the AI analyzes the document

### 5. View Analysis Results
- Refresh the project page in the browser
- Click on the project to see the detailed analysis
- Walk through the "God PM Blueprint":
  - Risk Assessment
  - Key Challenges
  - Sensitive Data Alerts
  - Strategic Recommendations
  - Linguist Matching

### 6. Demonstrate Additional Features
- Show how to upload linguists
- Demonstrate the analytics dashboard
- Show user management features

## Post-Demo Cleanup
- Press Ctrl+C in the terminal running run_demo.sh to stop all processes
- Or manually stop the processes:
  ```bash
  pkill -f "python app.py"
  pkill -f "python gpo_local_brain/main.py"
  ```

## Additional Demo Scenarios
- Medical document analysis: Use sample_medical_report.txt
- Technical document analysis: Use sample_technical_manual.txt 