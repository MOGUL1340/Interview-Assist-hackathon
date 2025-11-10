# AI Interview Assistant - Technical Architecture Documentation

## Project Overview

**Purpose:** Automated interview preparation assistant that analyzes candidate resumes, processes client requirements, and generates comprehensive interview plans with questions, evaluation rubrics, and Excel exports.

**Target Users:** Recruiters, HR professionals, and technical interviewers who need to quickly prepare structured interviews.

**Tech Stack:**
- **Backend:** Python 3.x + Flask
- **Frontend:** React.js (Create React App)
- **AI:** OpenAI API (GPT-4, GPT-4o-mini, Whisper)
- **Excel Generation:** OpenPyXL
- **Document Parsing:** PyPDF2, python-docx, docx2txt

---

## System Architecture

```
┌─────────────────┐
│   React UI      │ (Port 3000)
│  (Frontend)     │
└────────┬────────┘
         │ HTTP POST /generate_interview_plan
         │
         ▼
┌─────────────────┐
│   Flask API     │ (Port 5000)
│   (Backend)     │
└────────┬────────┘
         │
         ├─► Resume Analyzer (GPT-4)
         ├─► Audio Transcriber (Whisper)
         ├─► Interview Plan Generator (GPT-4)
         ├─► Code Challenge Generator (GPT-4o-mini)
         └─► Excel Generator (OpenPyXL)
              │
              ▼
         Excel File (.xlsx)
```

---

## Backend Components

### 1. **app.py** - Main Flask Application

**Port:** 5000
**CORS:** Enabled for cross-origin requests from React frontend

#### Key Endpoint:

**`POST /generate_interview_plan`**

Expected JSON payload:
```json
{
  "candidate_cv": {
    "name": "resume.pdf",
    "content": "base64_encoded_content"
  },
  "meeting_recording": {  // Optional
    "name": "meeting.mp3",
    "content": "base64_encoded_content"
  },
  "meeting_transcript": "text transcript...",  // Alternative to recording
  "job_title": "QA Engineer",
  "job_position": "Senior Manual QA Engineer",  // Displayed in plan
  "job_requirements": "Job description...",
  "interview_duration_minutes": 30
}
```

Response:
```json
{
  "status": "success",
  "interview_plan": { /* structured plan */ },
  "code_challenges": { /* coding challenges */ },
  "excel_file": {
    "name": "interview_plan_CandidateName_20251110_143022.xlsx",
    "content": "base64_encoded_xlsx"
  }
}
```

#### Processing Pipeline:

1. **Extract Resume Text** (`extract_text_from_file()`)
   - Supports: PDF, DOCX, DOC, TXT
   - Uses PyPDF2, python-docx, docx2txt
   - Returns plain text

2. **Analyze Resume** (`resume_analyzer.py`)
   - GPT-4 extracts structured data
   - Schema: name, skills, experience, education, etc.

3. **Process Meeting Info** (Optional)
   - If transcript provided → extract insights directly
   - If recording provided → Whisper transcription → extract insights
   - Fallback: Use job_requirements from form

4. **Generate Interview Plan** (`interview_plan_generator.py`)
   - GPT-4 creates complete plan
   - Calls helper functions for topics prioritization and rubric

5. **Generate Code Challenges** (`code_challenge_generator.py`)
   - GPT-4o-mini generates coding problems
   - Only if technical position

6. **Create Excel File** (`excel_generator.py`)
   - OpenPyXL generates multi-sheet workbook
   - Returns path to .xlsx file

7. **Send Response**
   - Base64-encode Excel file
   - Return JSON with plan + Excel

---

### 2. **resume_analyzer.py** - Resume Processing Module

**Purpose:** Extract structured data from resume text using GPT-4.

**Key Function:** `process_resume(resume_text, job_details=None)`

**Process:**
1. Creates system prompt for GPT-4
2. Defines JSON schema for structured output
3. Calls GPT-4 with resume text
4. Returns parsed JSON with candidate info

**Output Schema:**
```python
{
  "key_info": {
    "name": str,
    "email": str,
    "phone": str,
    "location": str,
    "linkedin": str
  },
  "summary": str,
  "skills": {
    "technical": [str],
    "soft": [str]
  },
  "experience": [
    {
      "company": str,
      "title": str,
      "duration": str,
      "responsibilities": [str]
    }
  ],
  "education": [
    {
      "degree": str,
      "institution": str,
      "year": str
    }
  ],
  "certifications": [str],
  "achievements": [str]
}
```

**IMPORTANT:** Line 230 previously had a NameError bug (using `result` before definition). This has been fixed.

---

### 3. **interview_plan_generator.py** - Core Planning Logic

**Purpose:** Generate comprehensive interview plans with questions, topics, and evaluation criteria.

#### Key Functions:

**`generate_interview_plan(resume_analysis, meeting_insights, job_details, time_limit_minutes)`**
- Main function that calls GPT-4
- **Model:** GPT-4 (higher quality than mini)
- **Temperature:** 0.3 (consistent output)
- **Response Format:** JSON

**CRITICAL PROMPT REQUIREMENTS:**
- "Generate 3-5 DIVERSE questions per topic to give the interviewer options!"
- "Each topic in 'prioritized_topics' MUST have 3-5 questions in its 'questions' array!"
- Questions should vary in difficulty and focus area

**`prioritize_topics(resume_analysis, meeting_insights, time_limit_minutes)`**
- Creates prioritized list of interview topics
- Allocates time based on priority and total duration
- Returns topics with priority scores (1-5)

**`generate_evaluation_rubric(topics)`**
- Creates scoring rubric for each topic
- Scoring scale 1-5 with descriptions
- Decision framework thresholds:
  - **≥70% = Hire** (green)
  - **50-69% = Maybe** (orange - needs review)
  - **<50% = No Hire** (red)

**`create_complete_interview_plan(...)`**
- Orchestrates all generation functions
- Normalizes data structure for frontend
- Distributes questions across topics
- Combines everything into final plan

**Output Structure:**
```python
{
  "metadata": {
    "generated_at": "2025-11-10T14:30:22",
    "time_limit_minutes": 30,
    "candidate_name": "John Doe",
    "job_title": "Senior QA Engineer"
  },
  "interview_overview": {
    "objectives": [str]
  },
  "prioritized_topics": [
    {
      "topic_name": str,
      "priority": int (1-5),
      "allocated_time_minutes": int,
      "rationale": str,
      "questions": [
        {
          "question": str,
          "what_to_look_for": str,
          "follow_up": str,
          "scoring_criteria": str
        }
      ]
    }
  ],
  "topics_to_cover": [...],  // Alias for compatibility
  "evaluation_rubric": {
    "decision_framework": {
      "hire_threshold": 70,
      "no_hire_threshold": 50
    },
    "overall_evaluation_guidelines": {...},
    "topics": [...]
  },
  "red_flags": [str],
  "candidate_questions": [str]
}
```

**IMPORTANT BUG FIX (line 113):** Previously used `os.popen('date')` which failed on Windows. Changed to `datetime.now().isoformat()`.

---

### 4. **audio_transcriber.py** - Audio Processing Module

**Purpose:** Transcribe meeting recordings and extract interview requirements.

**Key Functions:**

**`process_meeting_recording(audio_data, is_base64=True, file_extension='mp3')`**
- Decodes base64 audio
- Saves to temp file
- Calls Whisper API for transcription
- Extracts insights using GPT
- Cleans up temp file

**`extract_meeting_insights(transcript_text)`**
- Uses GPT-4o-mini to analyze transcript
- Extracts: job requirements, duration, topics, code challenge needs
- Returns structured JSON

**NOTE:** Audio transcription is currently marked as secondary priority and not fully tested.

---

### 5. **code_challenge_generator.py** - Coding Problem Generator

**Purpose:** Generate technical coding challenges for developer positions.

**Key Function:** `create_challenge_suite(job_details, resume_analysis, meeting_insights)`

**Process:**
1. Checks if code challenges needed (technical position check)
2. Calls GPT-4o-mini to generate:
   - Coding challenges (1-2 problems)
   - System design challenges (optional)
   - Debugging challenges (optional)
3. Each challenge includes:
   - Problem description
   - Difficulty level
   - Duration
   - Technology stack
   - Evaluation criteria

**Output Structure:**
```python
{
  "coding_challenges": [
    {
      "problem_description": str,
      "metadata": {
        "difficulty": "Medium",
        "duration_minutes": 30,
        "technology_stack": [str]
      },
      "evaluation_criteria": [str]
    }
  ],
  "system_design": {...},
  "debugging_challenge": {...}
}
```

---

### 6. **excel_generator.py** - Excel Export Module

**Purpose:** Create multi-sheet Excel workbook for interview execution.

**Key Function:** `create_interview_excel(interview_plan, code_challenges, output_path=None)`

**Excel Structure:** 5 sheets

#### Sheet 1: **Overview**
- Candidate metadata (name, position, duration)
- Interview objectives
- Time allocation by topic

#### Sheet 2: **Questions**
- Questions grouped by topic
- Columns: #, Question, What to Look For, Follow-up, Score (1-5)
- Blue headers for topic sections
- Score column is empty for interviewer to fill

#### Sheet 3: **Evaluation**
- Topic-wise scoring table
- **Columns:**
  - Topic (name)
  - Weight % (auto-calculated from priority)
  - Score (1-5) - **AUTO-POPULATED via AVERAGE formula**
  - Notes (free text)
  - Weighted Score (%) - **Formula: `=C{row}/5*B{row}`**
- **Total Score:** Sum of weighted scores (0-100%)
- **Recommendation:** Checkboxes for Hire/Maybe/No Hire

**CRITICAL FORMULAS:**

1. **Score Column (C):**
   ```excel
   =AVERAGE(Questions!E{start_row}:E{end_row})
   ```
   Automatically calculates average score from Questions sheet for each topic.

2. **Weighted Score Column (E):**
   ```excel
   =C{row}/5*B{row}
   ```
   Converts score to percentage and multiplies by weight.
   - Example: Score=3, Weight=17.2% → 3/5 * 17.2% = 10.32%

3. **Total Score:**
   ```excel
   =SUM(E4:E{last_row})
   ```
   Sum of all weighted scores (result is 0-100%).

**IMPORTANT:** `topic_score_ranges` dictionary is passed from `create_questions_sheet()` to `create_evaluation_sheet()` to link the formulas correctly.

#### Sheet 4: **Code Challenges**
- Coding problems with descriptions
- Duration and evaluation criteria
- Empty state message if no challenges

#### Sheet 5: **Notes**
- Red flags section
- Free-form notes area

**Color Scheme:**
- Headers: `#1F4E78` (dark blue)
- Topic headers: `#4472C4` (medium blue)
- Highlights: `#70AD47` (green), `#FFC000` (orange)

---

## Frontend Components

### 1. **App.js** - Main Application Component

**State Management:**
```javascript
const [planData, setPlanData] = useState(null);
const [isLoading, setIsLoading] = useState(false);
```

**Flow:**
1. Shows `InterviewPrepForm` initially
2. On form submit → sets `isLoading=true`
3. Backend processes request
4. On success → sets `planData` and shows `InterviewPlanView`
5. "Start Over" button → clears `planData` and returns to form

---

### 2. **InterviewPrepForm.js** - Data Input Form

**Form Fields:**
- **Candidate Information:**
  - Name (text)
  - Resume (file: PDF, DOC, DOCX, TXT)

- **Client Meeting Information:**
  - Checkbox: "I have a text transcript instead of recording"
  - Meeting Recording (file: MP3, WAV, M4A) OR
  - Meeting Transcript (textarea)

- **Job Information:**
  - Job Title (text) - used for categorization
  - Job Grade (select: Junior/Middle/Senior/Lead/Principal)
  - Position Name (text) - **displayed in interview plan**
  - Job Requirements (textarea) - **detailed description**
  - Checkbox: "Include Code Challenges"

- **Interview Settings:**
  - Duration (number: 10-120 minutes, step 5)

**Validation:**
- Candidate name required
- Resume file required
- Meeting recording OR transcript required
- Job title required
- **Position name required** (added in latest version)
- Job requirements required
- Duration 10-120 minutes

**File Handling:**
```javascript
const readFileAsBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result.split(',')[1];
      resolve(base64String);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};
```

**API Call:**
```javascript
const response = await fetch('http://localhost:5000/generate_interview_plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});
```

---

### 3. **InterviewPlanView.js** - Results Display Component

**Props:**
- `planData` - Object with `interview_plan`, `code_challenges`, `excel_file`
- `onStartOver` - Callback to reset form

**Tabs:**
1. **Overview** - Metadata, objectives, time allocation
2. **Questions** - All interview questions grouped by topic
3. **Code Challenges** - Coding problems (or empty state)
4. **Evaluation** - Rubric and decision framework

#### Key Features:

**Question Numbering:**
```javascript
let globalQuestionNumber = 0;
// Inside topic map:
globalQuestionNumber++;
<div className="question-number">Q{globalQuestionNumber}</div>
```
Questions are numbered globally (Q1, Q2, Q3...) across all topics.

**Empty States:**
- Topics without questions are filtered out: `if (!topic.questions || topic.questions.length === 0) return null;`
- Code challenges page shows helpful message when empty

**Excel Download:**
```javascript
const downloadExcel = () => {
  const byteCharacters = atob(excel_file.content);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = excel_file.name || 'interview_plan.xlsx';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
```

**Decision Framework Display:**
- Color-coded cards: Green (Hire), Orange (Maybe), Red (No Hire)
- Thresholds displayed clearly with visual hierarchy

**Workflow Instructions:**
Compact horizontal layout (3 columns):
1. BEFORE Interview: Review, Download Excel, Study Questions
2. DURING Interview: Ask questions, Compare answers, Record scores
3. AFTER Interview: Check total %, See Decision Framework, Decide

---

### 4. **CSS Styling** - InterviewPlanView.css

**Color Palette:**
- Primary: `#1F4E78` (dark blue)
- Secondary: `#4472C4` (medium blue)
- Success: `#70AD47` (green)
- Warning: `#FFA500` (orange)
- Danger: `#DC3545` (red)
- Background: `#f5f5f5` (light gray)

**Key Style Classes:**

**Topic Headers:**
```css
.topic-header {
  background-color: #4472C4;
  color: white !important;  /* !important fixes empty header bug */
  padding: 15px;
  margin: -25px -25px 15px -25px;
  border-radius: 8px 8px 0 0;
  font-size: 18px;
  font-weight: 600;
}
```

**Decision Framework Cards:**
```css
.decision-framework {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}
.threshold-hire {
  border-left-color: #70AD47;
  background-color: #f0f8f0;
}
```

**Workflow Grid (Compact Layout):**
```css
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}
.workflow-step {
  background-color: white;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #4472C4;
}
```

**Responsive Design:**
- Breakpoint: 768px
- Mobile: Stacked layout, smaller fonts, adjusted grid

---

## Data Flow Diagram

```
User Input (Form)
    ↓
Base64 Encode Files
    ↓
POST /generate_interview_plan
    ↓
┌─────────────────────────────────┐
│  BACKEND PROCESSING PIPELINE    │
├─────────────────────────────────┤
│ 1. Extract Resume Text          │
│    (PDF/DOCX/DOC/TXT → String)  │
│         ↓                        │
│ 2. Analyze Resume (GPT-4)       │
│    (String → Structured JSON)   │
│         ↓                        │
│ 3. Process Meeting Info         │
│    (Audio/Text → Requirements)  │
│         ↓                        │
│ 4. Generate Interview Plan      │
│    ├─ Main Plan (GPT-4)         │
│    ├─ Prioritize Topics         │
│    └─ Generate Rubric           │
│         ↓                        │
│ 5. Generate Code Challenges     │
│    (GPT-4o-mini)                │
│         ↓                        │
│ 6. Create Excel File            │
│    ├─ Overview Sheet            │
│    ├─ Questions Sheet           │
│    ├─ Evaluation Sheet          │
│    │   (with AVERAGE formulas)  │
│    ├─ Code Challenges Sheet     │
│    └─ Notes Sheet               │
│         ↓                        │
│ 7. Base64 Encode Excel          │
└─────────────────────────────────┘
    ↓
JSON Response
    ↓
Frontend Updates State
    ↓
Display Interview Plan View
```

---

## Important Implementation Details

### 1. **Question-to-Evaluation Score Linking**

The scores entered in the Questions tab automatically populate the Evaluation tab.

**Implementation:**

In `excel_generator.py`:

```python
def create_questions_sheet(wb, interview_plan):
    topic_score_ranges = {}  # Store ranges

    for topic in topics:
        start_row = row
        # ... add questions ...
        end_row = row - 1

        # Store range for this topic
        topic_score_ranges[topic_name] = f"Questions!E{start_row}:E{end_row}"

    return topic_score_ranges

def create_evaluation_sheet(wb, interview_plan, topic_score_ranges):
    for topic in topics:
        topic_name = topic.get("topic_name", "N/A")

        # Link to Questions sheet
        if topic_name in topic_score_ranges:
            ws.cell(row=row, column=3,
                   value=f"=AVERAGE({topic_score_ranges[topic_name]})")
```

**User Workflow:**
1. Interviewer opens Excel → Questions tab
2. During interview, fills Score (1-5) column for each question
3. Switches to Evaluation tab → Score column auto-populated with averages
4. Weighted Score column auto-calculates percentages
5. Total Score shows final percentage (0-100%)
6. Compare with Decision Framework thresholds

### 2. **Weighted Score Calculation**

**Formula:** `=C{row}/5*B{row}`

**Logic:**
- C{row} = Score (1-5)
- B{row} = Weight (percentage as 17.2%)
- Division by 5 converts score to 0-1 scale
- Multiplication by weight gives percentage contribution

**Example:**
- Score = 3
- Weight = 17.2%
- Weighted Score = 3/5 * 17.2% = 0.6 * 17.2 = 10.32%

**Previous Bug:** Formula was `=C{row}*B{row}/100` which gave 0.00516 instead of 10.32%. **FIXED.**

### 3. **Resume File Format Support**

**Supported Formats:**
- **TXT:** Multiple encodings tried (utf-8, utf-8-sig, latin-1, windows-1252, cp1252)
- **PDF:** PyPDF2.PdfReader, extracts text from all pages
- **DOCX:** python-docx, extracts paragraphs and tables
- **DOC:** docx2txt (requires temp file)

**Error Handling:**
- Minimum 10 characters required
- Returns error message if extraction fails
- Logs all operations for debugging

### 4. **GPT Model Selection Strategy**

**GPT-4 (gpt-4o):**
- Resume analysis (high quality needed)
- Interview plan generation (complex reasoning)
- Temperature: 0.3 (consistent, focused)

**GPT-4o-mini:**
- Topic prioritization (simpler task)
- Evaluation rubric (structured output)
- Code challenge generation (cost optimization)
- Meeting insights extraction
- Temperature: 0.2-0.4

**Whisper:**
- Audio transcription only
- No alternative models

### 5. **Frontend State Management**

**No Redux/Context:** Simple useState hooks sufficient

**Key States:**
```javascript
// App.js
const [planData, setPlanData] = useState(null);
const [isLoading, setIsLoading] = useState(false);

// InterviewPrepForm.js
const [formData, setFormData] = useState({ /* 10+ fields */ });
const [errors, setErrors] = useState({});

// InterviewPlanView.js
const [activeTab, setActiveTab] = useState('overview');
```

**Data Persistence:** None (single session, no localStorage)

---

## Environment Variables

**Required in `.env`:**
```
OPENAI_API_KEY=sk-...
```

**Optional:**
- None currently (could add: MAX_FILE_SIZE, UPLOAD_DIR, etc.)

---

## File Structure

```
ai-interview-assistant/
├── src/
│   ├── app.py                      # Main Flask app
│   ├── resume_analyzer.py          # Resume processing
│   ├── audio_transcriber.py        # Audio → text + insights
│   ├── interview_plan_generator.py # Core planning logic
│   ├── code_challenge_generator.py # Coding problems
│   ├── excel_generator.py          # Excel creation
│   ├── App.js                      # React root component
│   ├── InterviewPrepForm.js        # Input form
│   ├── InterviewPrepForm.css       # Form styling
│   ├── InterviewPlanView.js        # Results display
│   └── InterviewPlanView.css       # Results styling
├── details/
│   ├── HACKATHON_TASK_SUMMARY.md   # Original requirements
│   └── ARCHITECTURE.md             # This file
├── uploads/                        # Temp file storage
├── .env                           # API keys
├── requirements.txt               # Python dependencies
├── package.json                   # Node dependencies
└── README_HACKATHON.md            # Project README
```

---

## Deployment Considerations

### Current Setup (Development):
- **Backend:** Flask dev server (port 5000)
- **Frontend:** React dev server (port 3000)
- **CORS:** Enabled for localhost

### Production Recommendations:

**Backend:**
- Use WSGI server (Gunicorn, uWSGI)
- Set `debug=False`
- Add rate limiting (Flask-Limiter)
- Implement file size limits
- Add request validation
- Use environment-based config

**Frontend:**
- Build for production: `npm run build`
- Serve static files via Nginx/Apache
- Update API endpoint to production URL
- Enable HTTPS
- Add error boundaries
- Implement loading states for all async ops

**Security:**
- Validate file uploads (size, type, content)
- Sanitize user inputs
- Add authentication/authorization
- Use secure headers
- Implement CSRF protection
- Store API keys securely (not in .env file)

**Performance:**
- Cache frequently accessed data
- Implement request queuing for GPT calls
- Add retry logic for API failures
- Optimize Excel generation (stream large files)
- Use CDN for static assets

---

## Common Issues & Solutions

### Issue 1: Empty Blue Topic Headers
**Symptom:** Topic headers appear as empty blue boxes
**Cause:** CSS inheritance/z-index issues
**Solution:** Added `color: white !important;` to `.topic-header`

### Issue 2: All Questions Numbered Q1
**Symptom:** Every question shows "Q1" instead of sequential numbers
**Cause:** Counter reset per topic instead of global
**Solution:** Moved `globalQuestionNumber` outside topic map loop

### Issue 3: Weighted Score Shows 0.00516 Instead of 10.32%
**Symptom:** Excel weighted scores in wrong decimal format
**Cause:** Incorrect formula `=C*B/100`
**Solution:** Changed to `=C/5*B` to properly convert score to percentage

### Issue 4: Questions Tab Scores Not Linked to Evaluation
**Symptom:** Manual entry required in both tabs
**Cause:** No formula linking the sheets
**Solution:** Implemented `topic_score_ranges` dictionary with AVERAGE formulas

### Issue 5: Only 1-2 Questions Generated Per Topic
**Symptom:** Insufficient question variety
**Cause:** GPT prompt not specific enough
**Solution:** Updated prompt: "CRITICAL: Generate 3-5 DIVERSE questions per topic"

### Issue 6: Backend Crashes on Windows
**Symptom:** `os.popen('date')` fails
**Cause:** Windows doesn't have `date` command
**Solution:** Changed to `datetime.now().isoformat()`

### Issue 7: NameError in resume_analyzer.py
**Symptom:** `result` used before definition (line 230)
**Cause:** Conditional block referenced variable before creation
**Solution:** Removed premature conditional, let function create `result` first

---

## Testing Guidelines

### Manual Testing Checklist:

**Form Validation:**
- [ ] Empty fields show errors
- [ ] Invalid file types rejected
- [ ] Large files handled gracefully
- [ ] Position field required and displays correctly

**Backend Processing:**
- [ ] PDF resume parsed correctly
- [ ] DOCX resume parsed correctly
- [ ] TXT resume parsed correctly
- [ ] Audio transcription works (if enabled)
- [ ] Text transcript processed
- [ ] Interview plan generated with 3-5 questions per topic

**Frontend Display:**
- [ ] Overview tab shows metadata correctly
- [ ] Questions tab shows all questions with global numbering
- [ ] Topic headers visible (not empty blue boxes)
- [ ] Code Challenges shows empty state if none
- [ ] Evaluation tab shows decision framework
- [ ] Excel download works

**Excel Functionality:**
- [ ] All 5 sheets present
- [ ] Questions sheet has score column
- [ ] Evaluation sheet formulas work:
  - [ ] Score column averages from Questions tab
  - [ ] Weighted Score calculates percentages correctly
  - [ ] Total Score sums to 0-100%
- [ ] Decision Framework thresholds correct (70%, 50%)

**Edge Cases:**
- [ ] Very short resume (< 100 chars)
- [ ] Resume with special characters
- [ ] Non-technical position (no code challenges)
- [ ] 120-minute interview (max duration)
- [ ] 10-minute interview (min duration)

---

## Debugging Tips

### Backend Logs:
```bash
cd src && python app.py
# Watch for:
# - "Resume text extracted successfully. Length: XXX characters"
# - "Interview plan generated successfully"
# - "Excel file created successfully: path"
```

### Frontend Console:
```javascript
// Check network tab for:
// - POST /generate_interview_plan (200 OK)
// - Response JSON structure
// - Base64 Excel content present

// Check console for:
// - Form validation errors
// - State updates
// - Excel download triggers
```

### Common Debug Points:

1. **Resume not parsing:**
   - Check file format in `extract_text_from_file()`
   - Verify encoding detection
   - Log extracted text length

2. **No questions generated:**
   - Check GPT response in `interview_plan_generator.py`
   - Verify `prioritized_topics` has questions array
   - Check question distribution logic (line 385-408)

3. **Excel formulas broken:**
   - Verify `topic_score_ranges` dictionary populated
   - Check cell references match actual row numbers
   - Test formula syntax in Excel directly

4. **Frontend not updating:**
   - Check React DevTools for state changes
   - Verify API response structure matches expected
   - Check error boundaries for caught exceptions

---

## Future Enhancement Ideas

1. **User Authentication:** Save interview plans per user
2. **Plan Templates:** Pre-built templates for common positions
3. **Candidate Portal:** Let candidates see questions before interview
4. **Video Interviews:** Integrate with Zoom/Teams
5. **AI-Powered Scoring:** Auto-score candidate answers
6. **Analytics Dashboard:** Track interviewer performance
7. **Multi-Language Support:** Translate questions
8. **Collaborative Editing:** Multiple interviewers on same plan
9. **Question Bank:** Reusable question library
10. **Interview Scheduling:** Calendar integration

---

## Key Takeaways for New Session

**What Works Well:**
✅ Resume parsing (PDF, DOCX, DOC, TXT)
✅ GPT-4 interview plan generation
✅ Excel export with linked formulas
✅ React UI with tabs and file upload
✅ Automatic score calculation
✅ Decision framework thresholds

**What's Not Implemented:**
❌ Audio transcription (marked secondary priority)
❌ User authentication
❌ Plan persistence (no database)
❌ Real-time collaboration
❌ Advanced analytics

**What to Watch Out For:**
⚠️ OpenAI API rate limits
⚠️ Large file uploads (no size limit enforced)
⚠️ Excel formula cell references (must match sheet structure)
⚠️ Cross-origin requests (CORS must be enabled)
⚠️ GPT response format variations (handle gracefully)

**Most Important Files to Understand:**
1. `app.py` - Request flow and orchestration
2. `interview_plan_generator.py` - Core business logic
3. `excel_generator.py` - Formula linking magic
4. `InterviewPlanView.js` - UI rendering and data display

**Quick Start for Development:**
```bash
# Terminal 1 - Backend
cd src && python app.py

# Terminal 2 - Frontend
npm start

# Access at http://localhost:3000
# API at http://localhost:5000
```

---

*Last Updated: 2025-11-10*
*Version: 1.0*
*Author: AI Interview Assistant Development Team*
