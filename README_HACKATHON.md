# AI Interview Preparation Assistant - Hackathon Submission

## Overview

This tool helps interviewers **prepare** for conducting interviews with senior candidates by automatically generating comprehensive interview plans based on:

- Candidate's CV/Resume
- Client meeting recording or transcript
- Job requirements
- Available interview time

**Key Output:** Excel file with structured interview plan, questions, evaluation rubric, and code challenges.

---

## Problem Statement

When interviewing senior candidates, interviewers face:
- Long, exhausting preparation time
- Need to ask numerous varied questions
- Manual planning of topics and questions
- Creating unbiased evaluation criteria

**Solution:** AI-powered tool that generates complete interview plans in minutes, saving time and ensuring comprehensive, unbiased interviews.

---

## Features

### Input
- ✅ Candidate Resume (PDF, DOC, TXT)
- ✅ Meeting Recording (MP3, WAV, M4A) **with automatic transcription via OpenAI Whisper**
- ✅ OR Meeting Transcript (text)
- ✅ Job Requirements (select from predefined or custom)
- ✅ Interview Duration (10-120 minutes)

### Processing (AI-Powered)
- Resume Analysis (GPT-4o-mini)
- Meeting Insights Extraction
- Interview Plan Generation (GPT-4o)
- Code Challenge Generation
- Evaluation Rubric Creation

### Output
- ✅ **Excel File** with:
  - Overview sheet (metadata, objectives, time allocation)
  - Questions sheet (categorized by topic with scoring guidance)
  - Evaluation sheet (rubric with scoring table)
  - Code Challenges sheet
  - Notes sheet (red flags, free-form notes)
- ✅ Interactive Web View
- ✅ Downloadable structured plan

---

## Tech Stack

**Backend:**
- Python 3.8+
- Flask (API server)
- OpenAI API (GPT-4o, GPT-4o-mini, Whisper)
- openpyxl (Excel generation)

**Frontend:**
- React 18
- Modern CSS
- Base64 file handling

---

## Installation & Setup

### Prerequisites
1. Python 3.8 or higher
2. Node.js 14 or higher
3. OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Node Dependencies

```bash
npm install
```

### Step 3: Configure Environment Variables

Edit `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

**Important:** Replace `sk-your-actual-openai-key-here` with your real OpenAI API key!

---

## Running the Application

### Terminal 1: Start Backend (Flask)

```bash
cd src
python app.py
```

Backend will run on `http://localhost:5000`

### Terminal 2: Start Frontend (React)

```bash
npm start
```

Frontend will run on `http://localhost:3000`

---

## Usage Guide

### Step 1: Open Application
Navigate to `http://localhost:3000` in your browser

### Step 2: Fill Interview Preparation Form

**Candidate Information:**
- Enter candidate name
- Upload candidate resume (PDF, DOC, or TXT)

**Client Meeting Information:**
- Option A: Upload meeting recording (MP3, WAV, M4A) - will be auto-transcribed
- Option B: Paste meeting transcript text

**Job Information:**
- Select job from dropdown (predefined positions from `.store/manifesto.md`)
- OR enter custom job requirements

**Interview Settings:**
- Set interview duration (default: 30 minutes)

### Step 3: Generate Plan

Click "Generate Interview Plan" button. Processing takes 20-60 seconds depending on:
- Resume length
- Meeting recording duration (if transcribing)
- Interview complexity

### Step 4: Review Plan

View generated plan in 4 tabs:
- **Overview:** Summary, objectives, time allocation
- **Questions:** Detailed questions by topic with scoring guidance
- **Code Challenges:** Programming tasks (if applicable)
- **Evaluation:** Rubric and scoring framework

### Step 5: Download Excel

Click "Download Excel Plan" to get complete interview plan as `.xlsx` file

---

## Project Structure

```
ai-interview-assistant/
├── src/
│   ├── app.py                      # Flask backend (main API)
│   ├── resume_analyzer.py          # Resume analysis using GPT
│   ├── audio_transcriber.py        # Whisper API for audio→text
│   ├── interview_plan_generator.py # Plan generation with GPT-4
│   ├── code_challenge_generator.py # Code challenge creation
│   ├── excel_generator.py          # Excel file creation
│   ├── manifesto_tools.py          # Job description parser
│   ├── App.js                      # React main component
│   ├── InterviewPrepForm.js        # Input form component
│   ├── InterviewPlanView.js        # Results display component
│   └── [other React components]
├── .store/
│   └── manifesto.md                # Job descriptions database
├── .env                            # Environment variables (API keys)
├── requirements.txt                # Python dependencies
├── package.json                    # Node dependencies
└── README_HACKATHON.md             # This file
```

---

## API Endpoints

### `GET /get_job_titles`
Returns list of available job titles from manifesto

### `POST /generate_interview_plan`
Main endpoint for generating interview plan

**Request:**
```json
{
  "candidate_cv": {
    "name": "resume.pdf",
    "content": "base64_encoded_content"
  },
  "meeting_transcript": "text of meeting...",
  "job_title": "Senior .NET Developer",
  "interview_duration_minutes": 30
}
```

**Response:**
```json
{
  "status": "success",
  "interview_plan": { /* structured plan */ },
  "code_challenges": { /* challenges */ },
  "excel_file": {
    "name": "interview_plan.xlsx",
    "content": "base64_encoded_excel"
  }
}
```

---

## Sample Data for Testing

### Test Resume
Create a simple text file `test_resume.txt`:
```
John Doe
Senior Software Engineer

Experience:
2018-Present: Senior .NET Developer at Tech Corp
- Built microservices with .NET Core
- Led team of 5 developers
- Implemented CI/CD pipelines

2015-2018: .NET Developer at StartUp Inc
- Developed web applications with C# and SQL Server

Education:
2011-2015: BS Computer Science, University

Skills: C#, .NET Core, SQL Server, Azure, Microservices
```

### Test Meeting Transcript
```
Client: We need a senior .NET developer for our fintech project.
The candidate should have strong C# skills and experience with microservices.
We also need someone who can work with Azure cloud services.
The interview should be about 30 minutes and include a coding challenge.
We're looking for someone with at least 5 years of experience.
```

---

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Make sure you ran `pip install -r requirements.txt` and `npm install`

### Issue: "OPENAI_API_KEY not defined"
**Solution:** Check `.env` file and ensure you added your actual OpenAI API key

### Issue: Backend not starting
**Solution:** Make sure you're running `python app.py` from the `src/` directory

### Issue: "Failed to generate interview plan"
**Solution:**
- Check your OpenAI API key is valid
- Ensure you have credits in your OpenAI account
- Check console logs for detailed error messages

### Issue: Excel file won't download
**Solution:** Check browser console for errors, ensure backend is running

---

## Cost Estimation

Approximate OpenAI API costs per interview plan:
- Resume analysis: ~$0.01
- Meeting transcription (5 min audio): ~$0.05
- Interview plan generation: ~$0.10-0.20
- Code challenges: ~$0.05

**Total per plan:** ~$0.21-0.31 USD

---

## Future Enhancements

- Multi-language support (Russian, Ukrainian)
- Integration with ATS systems
- Video recording analysis
- Post-interview evaluation comparison
- Interview recording and AI-assisted scoring
- Team collaboration features
- Historical interview data analysis

---

## Demo Video

[Link to demo video showing complete flow from input to Excel download]

---

## Credits

Created for Internal Hackathon - Task 6: Intelligent Interview Assistant

**Author:** [Your Name]
**Date:** November 2024
**Technologies:** React, Python Flask, OpenAI GPT-4, Whisper API, openpyxl

---

## License

MIT License - Internal Use Only
