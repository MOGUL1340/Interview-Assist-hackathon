# Hackathon - Task: Intelligent Interview Assistant

## Task Information

**Task #6:** Internal Task 6: Intelligent interview assistant
**Author:** Pavlo Kud (.NET developer)
**Difficulty Level:** Medium
**Deadline:** November 10, 2025
**Evaluation Period:** November 10-20, 2025
**Results Announcement:** End of November 2025

---

## Problem Statement

When interviewing senior candidates, interviews become long and exhausting:
- Interviewer must ask an enormous number of questions
- Questions vary from basic to expert level ("zero to hero")
- Customer expectations about candidates can be expressed verbally (during kick-off meeting) or in written form
- Need to plan the interview: list of topics and questions for each topic
- Interview time is limited

**Current Situation:** Task is performed manually or with some help from Copilot.

**Goal:** Leverage Gen AI to automate interview preparation, especially when live coding is needed.

---

## Workflow (Sequence of Steps)

### INPUT:

1. **Customer Requirements** - collected from various sources:
   - Voice recording from kick-off meeting
   - Written text/document
   - Meeting script

2. **Candidate CV** - resume in various formats:
   - Unstructured text
   - May contain images
   - Different file formats

3. **Job Requirements** - position requirements:
   - Document prepared with customer
   - May be prepared with colleagues or recruitment office

4. **Additional Candidate Information**:
   - Pre-screening results
   - Other relevant data

5. **Time Constraints** - desired interview duration

### PROCESS:

**The tool should:**
1. Collect requirements from customer (voice, script, or written text - depending on available media)
2. Process requirements with Interview AI Assistant and get list of topics and questions
3. Fine-tune the list of topics and questions by prompting Intelligent Assistant
4. Obtain finalized list of questions in formalized protocol form, where interviewers might put their assessment, marks, and notes
5. Conduct the interview, fill in the form, and make final decision Go/No-go

### OUTPUT:

1. **Interview Plan** (PRIMARY OUTPUT - required):
   - List of topics
   - Questions for each topic
   - Formalized form (spreadsheet/table) where you can:
     - Put marks for each topic
     - Put marks for each question
     - Add notes
     - Get summary based on results

2. **Code for Coding Challenge** (OPTIONAL OUTPUT):
   - Tasks for live coding
   - Code that interviewer can approach candidate with during interview

---

## Business Value

**What it solves:**
- Better quality of candidates for customer review
- Shorter cycle between inception of selection process and candidate exposure to customer
- Less time for preparation
- More accurate and less biased scenario for the interview

**Why it matters:**
- Interviewers subconsciously pick topics they know best
- Tool will create unbiased interview plan
- Automation of routine work

---

## Technical Requirements

### AI Tools and Technologies:
- Must use LLM for voice recognition (if cannot get script and summary from kick-off meeting tool)
- May be any model or several models
- Models must be well-trained on programming topics and code
- Can use frontier or open-source models

### Possible Implementation:
- Add-on to Teams
- Standalone assistant
- Recommended to use internal tool: **AI Project Factory**
- If additional tools or infrastructure needed - fill out form for IT department

### Committee Comment:
"Covered by ATS system and Chat GPT"

---

## Evaluation Criteria

1. **Functionality and working demo**
2. **Customer fit use case depth**
3. **Scalability and production potential**

---

## Important Details from Discussion

### Target Audience:
- Primary: Developers (.NET domain)
- Ideal: Any roles in company (management, QA, etc.) if competence metrics available for each domain

### Priority Features:
1. **Interview Plan** (most important):
   - Not just sequence of questions
   - Form in Excel or similar format
   - Ability to put marks for each topic/question
   - Summary of marks considering topic weights

2. **Work Format**:
   - Tool works before interview
   - Generates form
   - Form is used during interview for marking
   - After interview - review marks and summary

3. **Automation Level**:
   - Minimum: semi-automated (acceptable for hackathon)
   - Ideal: maximum automation to reduce manual work
   - Ability to upload documents to tool (not only copy-paste)

### What is NOT Required:
- Assistant should NOT be present on screen during interview
- Resulting form is enough

---

## Current Project Status

### Implemented Modules (based on files):
- `resume_analyzer.py` - resume analysis
- `interview_plan_generator.py` - interview plan generation
- `audio_transcriber.py` - audio transcription
- `code_challenge_generator.py` - coding challenge generation
- `excel_generator.py` - Excel form generation
- React components: InterviewPlanView, InterviewPrepForm

### Architecture:
- Backend: Python (Flask)
- Frontend: React
- AI: LLM integration (likely Claude/OpenAI)

---

## Next Steps

1. Complete integration of all modules
2. Ensure correct upload/processing of documents
3. Test interview plan generation
4. Create final evaluation form (Excel)
5. Prepare demo
6. Submit project by **November 10, 2025**
