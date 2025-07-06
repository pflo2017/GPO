# GPO Demo Script: Real AI Analysis Showcase

## Setup (Do Before the Client Arrives)

1. **Start the GPO Application**:
   ```bash
   cd /Users/florinmacbook/Desktop/GPO\ product
   ./start.sh
   ```
   This will start both the main application and the local brain.

2. **Verify Services**:
   - Confirm the main application is running at http://localhost:5001
   - Confirm the local brain is running and monitoring for new documents

3. **Prepare Sample Documents**:
   - Ensure sample documents are available in the `dummy_docs` folder
   - Have them ready to copy to the `gpo_local_brain/documents` folder during the demo

## Demo Script

### 1. Introduction (2 minutes)

"Welcome to the Global Project Orchestrator (GPO) demo. Today I'll show you how our platform uses AI to analyze translation projects in real-time, providing valuable insights that help project managers make better decisions while maintaining data security."

### 2. System Architecture Overview (3 minutes)

"GPO consists of two main components:
- The **Cloud Dashboard** - A secure web interface where project managers track projects and view AI insights
- The **Local Brain** - A secure AI engine that runs on your premises, ensuring sensitive documents never leave your network"

*[Draw a simple diagram on a whiteboard showing data flow]*

### 3. Cloud Dashboard Tour (5 minutes)

"Let me show you the Cloud Dashboard first."

- Log in using the demo credentials:
  - Email: admin@test.com
  - Password: password

- Walk through key sections:
  - Project dashboard
  - Linguist management
  - Analytics
  - User management

### 4. Real-Time AI Analysis Demo (10 minutes)

"Now for the exciting part - let's see GPO in action with real AI analysis!"

#### Step 1: Create a New Project

- Click "New Project Request"
- Fill in the form:
  - Project Name: "Client Demo - Legal Contract"
  - Source Language: English
  - Target Language: German
  - Content Type: Legal
  - Deadline: (choose a date 2 weeks from now)
- Click "Create Project"

"Notice the project is created with 'Pending Analysis' status. Now, let's simulate a document being uploaded to your secure server."

#### Step 2: Document Processing

"In a real scenario, your team would place documents in a secure folder on your network. The Local Brain monitors this folder and processes new documents without sending them outside your network."

- Copy a sample document to the processing folder:
  ```bash
  cp dummy_docs/sample_legal_contract.txt gpo_local_brain/documents/
  ```

"Watch the Local Brain terminal - you can see it detecting the new document, extracting text, and performing AI analysis locally. This ensures your sensitive content never leaves your secure environment."

#### Step 3: View AI Analysis Results

"Now, let's check the Cloud Dashboard to see the AI insights."

- Refresh the project page
- Click on the project to view details

"Here's the 'God PM Blueprint' - the AI has analyzed the document and provided critical insights:

1. **Risk Assessment**: The AI identified this as a high-risk legal document with potential PII concerns
2. **Key Challenges**: Complex legal terminology, potential confidentiality clauses
3. **Sensitive Data Alert**: The AI detected potential personally identifiable information in sections 3 and 7
4. **Strategic Recommendations**: The AI recommends assigning a legal specialist with at least 5 years of experience
5. **Linguist Matching**: Based on the content analysis, the AI has suggested these specific linguists from your database"

### 5. Value Proposition (5 minutes)

"What you've just seen demonstrates how GPO:

1. **Enhances Security**: All document analysis happens on your premises
2. **Improves Efficiency**: PMs get instant insights without manual document review
3. **Reduces Risk**: Early identification of sensitive content and complexity
4. **Optimizes Resources**: Better linguist matching based on content analysis
5. **Increases Profitability**: Fewer surprises, better planning, happier clients"

### 6. Q&A (5 minutes)

"What aspects of this would you like to explore further?"

## Post-Demo Notes

- Be prepared to show the code for the AI analyzer if the client is technical
- Have additional sample documents ready for different content types
- Be ready to discuss customization options for specific client needs 