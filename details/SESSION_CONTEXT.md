# Session Context - AI Interview Assistant Debugging

**Last Updated:** 2025-11-10 16:46 (Session in progress)
**Status:** Testing fixes for question generation and time allocation

---

## Project Overview

**Project:** AI Interview Assistant (Hackathon Task #6)
**Deadline:** November 10, 2025 (TODAY!)
**Tech Stack:** React (frontend) + Flask (backend) + OpenAI GPT-4
**Repository Path:** `F:\AI\Claude-Projects\Interview_Assisstant\ai-interview-assistant`

### Key Files
- Backend: `src/app.py`, `src/interview_plan_generator.py`
- Frontend: `src/App.js`, `src/InterviewPlanView.js`, `src/InterviewPrepForm.js`
- Documentation: `details/ARCHITECTURE.md`, `details/HACKATHON_TASK_SUMMARY.md`

---

## Current Session Summary

### What Was Working
✅ Resume parsing (PDF, DOCX, DOC, TXT)
✅ Basic interview plan generation
✅ Excel file export with formulas
✅ React frontend with file upload
✅ Flask backend API

### Issues Found & Fixed

#### Issue #1: Questions Only Generated for First 2 Topics ✅ FIXED
**Problem:** Only first 2 topics had questions (3 each), remaining 5 topics had 0 questions.

**Root Cause:**
- GPT-4 in `generate_interview_plan()` generated 5 questions total in categories (manualQAExperience, testingComplexDigitalEcosystems, etc.)
- Code tried to "distribute" these 5 questions among 7 topics
- First 2 topics got 3+2 questions, remaining topics got nothing

**Solution Implemented:**
1. Modified `prioritize_topics()` function (line 226-327 in `interview_plan_generator.py`)
2. Updated prompt to generate 3-5 questions PER TOPIC (not total)
3. Changed model from `gpt-4o-mini` to `gpt-4o` for better quality
4. Added validation in prompt: "Check that EVERY topic has 3-5 questions"
5. Removed question distribution logic, questions now come directly from GPT

**Files Modified:**
- `src/interview_plan_generator.py` (lines 226-327)

#### Issue #2: Frontend Crash - objectives.map Error ✅ FIXED
**Problem:** `TypeError: _interview_plan$inter2.map is not a function`

**Root Cause:**
- GPT-4 sometimes returns `objectives` as a string instead of array
- Frontend tried to `.map()` over string → crash

**Solution Implemented:**
- Modified `InterviewPlanView.js` (lines 59-77)
- Added type checking: handles both string and array for objectives
- Uses IIFE to safely render objectives

**Files Modified:**
- `src/InterviewPlanView.js` (lines 59-77)

#### Issue #3: Time Allocation Mismatch ⚠️ IN PROGRESS
**Problem:**
- Interview duration: 60 minutes
- Topic times: 10+10+8+7+5+5 = 45 minutes
- Missing: 15 minutes
- Also: 5 minutes per topic too short for 3 questions

**Root Cause:**
- `prioritize_topics()` doesn't account for total interview time correctly
- No validation that sum of topic times equals available time
- No minimum time per topic enforced

**Solution Implemented (NEEDS TESTING):**
1. Updated `prioritize_topics()` signature to accept `job_details` parameter (line 226)
2. Calculate `available_time = time_limit_minutes - 10` (reserve for intro/outro)
3. Updated prompt with CRITICAL INSTRUCTIONS:
   - "Generate 5-8 topics based on importance"
   - "SUM of all allocated_time MUST equal {available_time}"
   - "Each topic: minimum 5 minutes, maximum 15 minutes"
   - "Validation: Check SUM equals {available_time} before responding"
4. Added post-GPT validation (lines 308-320):
   - Calculate total allocated time
   - If mismatch > 5 minutes, adjust proportionally
   - Log warnings

**Files Modified:**
- `src/interview_plan_generator.py` (lines 226-327)
- Modified call in `create_complete_interview_plan()` line 390

**Status:** ✅ FIXED - Fallback values added

#### Issue #4: Decision Framework Shows NaN% ✅ FIXED
**Problem:** Evaluation page shows "NaN%" instead of threshold values (70%, 50%)

**Root Cause:**
- `generate_evaluation_rubric()` doesn't enforce `decision_framework` structure
- GPT sometimes doesn't return `decision_framework` or returns invalid structure
- Frontend tries to access `rubric.decision_framework.hire_threshold` → undefined → NaN

**Solution Implemented:**
- Added validation after GPT response (lines 380-395)
- If `decision_framework` missing, add default: `{hire_threshold: 70, no_hire_threshold: 50}`
- If thresholds missing or invalid, set to defaults
- Log warnings when fallbacks are used

**Files Modified:**
- `src/interview_plan_generator.py` (lines 380-395)

**Status:** Code deployed, server restarted, READY FOR TESTING

---

## Current System State

### Backend Server Status
- **Running:** Yes
- **Port:** 5000
- **Debug Mode:** ON
- **Process ID:** 3dd2d6 (background bash)
- **Last Restart:** 16:27:35 (after time allocation fix)

### Frontend Server Status
- **Running:** Yes
- **Port:** 3000
- **Process ID:** b4bf80 (background bash)
- **URL:** http://localhost:3000

### Last Test Results (16:32:51 request)
**IMPORTANT:** This request was made BEFORE the time allocation fix was applied!
- Topics generated: 6
- Time allocation: 10+10+8+7+5+5 = 45 min (should be 50 for 60 min interview)
- Questions per topic: 3 ✅
- All topics have questions: ✅

### What's Still Being Tested
- Time allocation fix (user making new request now)
- Need to verify:
  - Total time equals interview duration - 10 min
  - Minimum 5 minutes per topic
  - Questions remain 3-5 per topic

---

## Technical Details

### Key Functions in interview_plan_generator.py

#### `prioritize_topics(resume_analysis, meeting_insights, time_limit_minutes, job_details=None)`
**Lines:** 226-327
**Purpose:** Generate topics WITH questions (3-5 per topic)
**Model:** GPT-4 (gpt-4o)
**Temperature:** 0.3
**Critical Changes:**
- Calculates `available_time = time_limit_minutes - 10`
- Passes available_time to GPT in prompt
- Validates total allocated time after GPT response
- Adjusts times proportionally if mismatch detected

#### `create_complete_interview_plan()`
**Line 390:** Now calls `prioritize_topics()` with `job_details` parameter

#### `generate_interview_plan()`
**Lines:** 114-224
**Purpose:** Generates overview and general structure (NOT used for questions anymore)
**Note:** Questions now come from `prioritize_topics()`, not this function

### Data Flow
```
User Submit Form
  ↓
POST /generate_interview_plan
  ↓
1. extract_text_from_file(resume)
2. process_resume(resume_text) → resume_analysis
3. extract_meeting_insights(transcript) → meeting_insights
4. create_complete_interview_plan()
   ├─ generate_interview_plan() → main_plan (overview)
   ├─ prioritize_topics() → prioritized_topics (WITH QUESTIONS)
   ├─ generate_evaluation_rubric() → rubric
   └─ Normalize and combine
5. create_challenge_suite() → code_challenges
6. create_interview_excel() → excel_file
7. Return JSON response
```

### Expected Output Structure
```json
{
  "status": "success",
  "interview_plan": {
    "metadata": {
      "generated_at": "ISO datetime",
      "time_limit_minutes": 60,
      "candidate_name": "Name",
      "job_title": "Position"
    },
    "interview_overview": {
      "objectives": "string or array"
    },
    "prioritized_topics": [
      {
        "topic_name": "string",
        "priority": 1-5,
        "allocated_time": "minutes",
        "allocated_time_minutes": "minutes",
        "rationale": "string",
        "questions": [
          {
            "question": "string",
            "what_to_look_for": "string",
            "follow_up": "string",
            "scoring_criteria": "string"
          }
        ]
      }
    ]
  },
  "excel_file": {
    "name": "interview_plan_Name_YYYYMMDD_HHMMSS.xlsx",
    "content": "base64 string"
  }
}
```

---

## Known Issues & Limitations

### Current Problems (Not Yet Fixed)
1. **Time Allocation** - Waiting for user test confirmation
2. **Minimum topic time** - 5 min may still be too short for 3 questions
3. **GPT consistency** - Sometimes generates 5 topics, sometimes 6-7
4. **No retry logic** - If GPT fails validation, no automatic regeneration

### Design Limitations
- No database - sessions are stateless
- No authentication
- No plan history
- Single user only
- Development servers (not production-ready)

### Not Implemented
- Audio transcription (marked as secondary priority)
- Real-time collaboration
- Plan templates
- Question bank

---

## Testing Instructions

### How to Test Current Fixes

1. **Open browser:** http://localhost:3000
2. **Click "Start Over"** to reset
3. **Fill form with test data:**
   - Candidate Name: Test Kandidat
   - Resume: Use `Test Kandidat_Resume.docx` (in uploads or test data)
   - Meeting Transcript: (any text about QA requirements)
   - Job Title: Manual QA Engineer
   - Job Grade: Senior
   - Position Name: Manual QA Engineer (Senior)
   - Job Requirements: (detailed QA job description)
   - Duration: **60 minutes** (important for testing)
4. **Submit and wait** (~2-3 minutes for generation)
5. **Check Results:**
   - Go to "Questions" tab
   - Count topics (should be 5-8)
   - Check each topic has 3-5 questions
   - Go to "Overview" tab
   - Check "Time Allocation" section
   - **SUM all topic times** → should equal ~50 minutes (60 - 10 for intro/outro)
   - Each topic should have at least 5 minutes

### Where to Look for Logs
```bash
# Backend logs (in background bash 3dd2d6)
# Look for these lines:
"Total time allocated: X minutes (expected: Y minutes)"
"Adjusted time allocation to match Y minutes"
"Prioritized N topics successfully"

# Check if topics have questions:
"Topic 'TopicName' has N questions from GPT"
```

### Test Data Location
- Resume files: `src/uploads/` or create test files
- Example transcript: See `details/HACKATHON_TASK_SUMMARY.md` for context

---

## Quick Commands for New Session

### Check Server Status
```bash
# See if servers are running
netstat -ano | findstr :5000  # Backend
netstat -ano | findstr :3000  # Frontend
```

### Start Servers (if not running)
```bash
# Terminal 1 - Backend
cd F:\AI\Claude-Projects\Interview_Assisstant\ai-interview-assistant\src
python app.py

# Terminal 2 - Frontend
cd F:\AI\Claude-Projects\Interview_Assisstant\ai-interview-assistant
npm start
```

### View Recent Code Changes
```bash
cd F:\AI\Claude-Projects\Interview_Assisstant\ai-interview-assistant
git diff HEAD~1 src/interview_plan_generator.py
git diff HEAD~1 src/InterviewPlanView.js
```

### Check Background Processes
```bash
# List background bash processes
ps aux | grep python  # Backend
ps aux | grep node    # Frontend
```

---

## Next Steps After Session Resume

### Immediate Actions
1. **Check test results** - User should have completed new test by now
2. **Verify time allocation:**
   - Check logs for "Total time allocated"
   - Confirm sum matches expected time
   - Verify no topics < 5 minutes
3. **If time still wrong:**
   - Increase `reserved_time` from 10 to 15 minutes
   - Add stricter validation in GPT prompt
   - Consider post-processing to enforce minimums

### Additional Improvements Needed
1. **Minimum time per topic:**
   - Current: 5 minutes (too short)
   - Recommended: 8-10 minutes for 3 questions
   - Update prompt: "Each topic: minimum 8 minutes, maximum 15 minutes"

2. **Better validation:**
   - Add check: if any topic < 8 minutes, regenerate
   - Add retry logic for GPT failures
   - Log warnings if proportional adjustment needed

3. **Frontend improvements:**
   - Show warning if topic time < 8 minutes
   - Display total time calculation on Overview page
   - Add time validation before Excel download

### Testing Checklist
- [ ] All topics have 3-5 questions
- [ ] No topics with 0 questions
- [ ] Total time allocation matches interview duration - 10 min
- [ ] No topics < 5 minutes (ideally < 8 minutes)
- [ ] Excel file downloads correctly
- [ ] Excel formulas work (Score column averages from Questions sheet)
- [ ] Frontend doesn't crash
- [ ] Objectives display correctly (string or array)

---

## Important Files to Check

### Backend
1. `src/interview_plan_generator.py` - Main logic (lines 226-327 critical)
2. `src/app.py` - API endpoint
3. `src/resume_analyzer.py` - Resume processing
4. `src/excel_generator.py` - Excel generation with formulas

### Frontend
1. `src/InterviewPlanView.js` - Results display (lines 59-77 critical)
2. `src/InterviewPrepForm.js` - Form inputs
3. `src/App.js` - Main component

### Documentation
1. `details/ARCHITECTURE.md` - Full technical documentation
2. `details/HACKATHON_TASK_SUMMARY.md` - Original requirements
3. `details/SESSION_CONTEXT.md` - This file

---

## OpenAI API Info

**API Key Location:** `.env` file (OPENAI_API_KEY)
**Models Used:**
- Resume analysis: GPT-4 (gpt-4o)
- Interview plan: GPT-4 (gpt-4o)
- Topic prioritization: GPT-4 (gpt-4o) - **CHANGED from gpt-4o-mini**
- Meeting insights: GPT-4o-mini
- Code challenges: GPT-4o-mini
- Audio transcription: Whisper (not tested)

**Rate Limits:** Watch for 429 errors if testing frequently

---

## Git Status (Session Start)

```
Current branch: master
Main branch: master

Modified files:
M package-lock.json
M requirements.txt
M src/App.js
M src/app.py
D src/manifesto_tools.py
M src/resume_analyzer.py

Untracked files:
?? .claude/
?? .env
?? README_HACKATHON.md
?? details/
?? src/InterviewPlanView.css
?? src/InterviewPlanView.js
?? src/InterviewPrepForm.css
?? src/InterviewPrepForm.js
?? src/audio_transcriber.py
?? src/code_challenge_generator.py
?? src/excel_generator.py
?? src/interview_plan_generator.py
```

**Files Modified This Session:**
- `src/interview_plan_generator.py` (lines 226-327, 390)
- `src/InterviewPlanView.js` (lines 59-77)

---

## Key Learnings from This Session

1. **Don't distribute questions** - Generate them per-topic from the start
2. **GPT-4 > GPT-4o-mini** for complex question generation
3. **Validation is critical** - GPT doesn't always follow instructions perfectly
4. **Type safety in frontend** - Handle both string and array types
5. **Time allocation needs constraints** - Min/max per topic, total must match
6. **Prompts need to be VERY specific** - Use "CRITICAL", "MUST", "VALIDATION" keywords
7. **Log everything** - Helps debug GPT responses
8. **Test with fresh data** - Cached responses can hide bugs

---

## Contact/Handoff Notes

**Language:** User speaks Russian, prefers Russian responses
**Deadline Pressure:** HIGH - hackathon deadline is TODAY (Nov 10, 2025)
**Priority:** Get working demo ready for submission
**User's Technical Level:** Understands programming, can read code, uses IDE

**Current Blocker:** Waiting for user to test time allocation fix
**Next Decision Point:** If time still wrong, need to adjust approach

**User Expectations:**
- Topics should cover full interview duration
- Each topic needs realistic time for 3 questions (8-10 minutes)
- All topics must have questions
- Excel export must work
- Demo ready for hackathon submission

---

**END OF CONTEXT DOCUMENT**

*To continue from this point: Review this document, check test results from user, adjust time allocation logic if needed, prepare for demo/submission.*
