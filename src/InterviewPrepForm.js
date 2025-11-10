import React, { useState } from 'react';
import './InterviewPrepForm.css';

function InterviewPrepForm({ onSubmit, setIsLoading }) {
  const [formData, setFormData] = useState({
    candidateName: '',
    candidateResume: null,
    meetingRecording: null,
    meetingTranscript: '',
    jobTitle: '',
    jobPosition: '',
    jobGrade: 'Senior',
    jobRequirements: '',
    interviewDuration: 30,
    useTranscript: false,
    includeCodeChallenges: false
  });

  const [errors, setErrors] = useState({});

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFileUpload = (event, fieldName) => {
    const file = event.target.files[0];
    if (file) {
      setFormData(prevData => ({ ...prevData, [fieldName]: file }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.candidateName.trim()) {
      newErrors.candidateName = 'Candidate name is required';
    }

    if (!formData.candidateResume) {
      newErrors.candidateResume = 'Candidate resume is required';
    }

    if (!formData.useTranscript && !formData.meetingRecording) {
      newErrors.meetingData = 'Please upload meeting recording or provide transcript';
    }

    if (formData.useTranscript && !formData.meetingTranscript.trim()) {
      newErrors.meetingTranscript = 'Meeting transcript is required';
    }

    if (!formData.jobTitle.trim()) {
      newErrors.jobTitle = 'Job title is required';
    }

    if (!formData.jobPosition.trim()) {
      newErrors.jobPosition = 'Position name is required';
    }

    if (!formData.jobRequirements.trim()) {
      newErrors.jobData = 'Job requirements are required';
    }

    if (formData.interviewDuration < 10 || formData.interviewDuration > 120) {
      newErrors.interviewDuration = 'Duration must be between 10 and 120 minutes';
    }

    return newErrors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const newErrors = validateForm();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setIsLoading(true);

      // Read resume file
      const resumeContent = await readFileAsBase64(formData.candidateResume);

      // Read meeting recording if provided
      let meetingRecordingContent = null;
      if (!formData.useTranscript && formData.meetingRecording) {
        meetingRecordingContent = await readFileAsBase64(formData.meetingRecording);
      }

      // Prepare payload
      const payload = {
        candidate_cv: {
          name: formData.candidateResume.name,
          content: resumeContent
        },
        job_title: formData.jobTitle,
        job_position: formData.jobPosition,
        job_requirements: formData.jobRequirements,
        interview_duration_minutes: parseInt(formData.interviewDuration)
      };

      if (formData.useTranscript) {
        payload.meeting_transcript = formData.meetingTranscript;
      } else if (meetingRecordingContent) {
        payload.meeting_recording = {
          name: formData.meetingRecording.name,
          content: meetingRecordingContent
        };
      }

      // Send to backend
      const response = await fetch('http://localhost:5000/generate_interview_plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.status === 'success') {
        onSubmit(result);
      } else {
        throw new Error(result.message || 'Failed to generate interview plan');
      }

    } catch (error) {
      console.error('Error generating interview plan:', error);
      setErrors({ submit: error.message || 'Failed to generate interview plan. Please try again.' });
      setIsLoading(false);
    }
  };

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

  return (
    <div className="interview-prep-form-container">
      <h1>Interview Preparation Assistant</h1>
      <p className="subtitle">Generate a comprehensive interview plan</p>

      <form className="interview-prep-form" onSubmit={handleSubmit}>
        <section className="form-section">
          <h2>Candidate Information</h2>

          <div className="form-group">
            <label htmlFor="candidateName">Candidate Name:</label>
            <input
              type="text"
              id="candidateName"
              name="candidateName"
              value={formData.candidateName}
              onChange={handleInputChange}
              placeholder="John Doe"
              required
            />
            {errors.candidateName && <div className="error">{errors.candidateName}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="candidateResume">Candidate Resume (PDF, DOC, TXT):</label>
            <input
              type="file"
              id="candidateResume"
              name="candidateResume"
              accept=".pdf,.doc,.docx,.txt"
              onChange={(e) => handleFileUpload(e, 'candidateResume')}
              required
            />
            {formData.candidateResume && (
              <div className="file-info">Selected: {formData.candidateResume.name}</div>
            )}
            {errors.candidateResume && <div className="error">{errors.candidateResume}</div>}
          </div>
        </section>

        <section className="form-section">
          <h2>Client Meeting Information</h2>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                name="useTranscript"
                checked={formData.useTranscript}
                onChange={handleInputChange}
              />
              I have a text transcript instead of recording
            </label>
          </div>

          {!formData.useTranscript ? (
            <div className="form-group">
              <label htmlFor="meetingRecording">Meeting Recording (MP3, WAV, M4A):</label>
              <input
                type="file"
                id="meetingRecording"
                name="meetingRecording"
                accept=".mp3,.wav,.m4a,.mp4"
                onChange={(e) => handleFileUpload(e, 'meetingRecording')}
              />
              {formData.meetingRecording && (
                <div className="file-info">Selected: {formData.meetingRecording.name}</div>
              )}
            </div>
          ) : (
            <div className="form-group">
              <label htmlFor="meetingTranscript">Meeting Transcript:</label>
              <textarea
                id="meetingTranscript"
                name="meetingTranscript"
                value={formData.meetingTranscript}
                onChange={handleInputChange}
                rows="6"
                placeholder="Paste the transcript of your meeting with the client here..."
              />
              {errors.meetingTranscript && <div className="error">{errors.meetingTranscript}</div>}
            </div>
          )}

          {errors.meetingData && <div className="error">{errors.meetingData}</div>}
        </section>

        <section className="form-section">
          <h2>Job Information</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="jobTitle">Job Title:</label>
              <input
                type="text"
                id="jobTitle"
                name="jobTitle"
                value={formData.jobTitle}
                onChange={handleInputChange}
                placeholder="QA Engineer"
                required
              />
              {errors.jobTitle && <div className="error">{errors.jobTitle}</div>}
            </div>

            <div className="form-group">
              <label htmlFor="jobGrade">Grade/Level:</label>
              <select
                id="jobGrade"
                name="jobGrade"
                value={formData.jobGrade}
                onChange={handleInputChange}
                required
              >
                <option value="Junior">Junior</option>
                <option value="Middle">Middle</option>
                <option value="Senior">Senior</option>
                <option value="Lead">Lead</option>
                <option value="Principal">Principal</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="jobPosition">Position Name (displayed in interview plan):</label>
            <input
              type="text"
              id="jobPosition"
              name="jobPosition"
              value={formData.jobPosition}
              onChange={handleInputChange}
              placeholder="Senior Manual QA Engineer"
              required
            />
            {errors.jobPosition && <div className="error">{errors.jobPosition}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="jobRequirements">Job Requirements and Responsibilities:</label>
            <textarea
              id="jobRequirements"
              name="jobRequirements"
              value={formData.jobRequirements}
              onChange={handleInputChange}
              rows="6"
              placeholder="Describe the job requirements, responsibilities, and key qualifications...&#10;&#10;Example:&#10;- 5+ years of experience in software development&#10;- Strong knowledge of React and TypeScript&#10;- Experience with REST APIs and microservices&#10;- Leadership and team management skills"
              required
            />
            {errors.jobData && <div className="error">{errors.jobData}</div>}
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="includeCodeChallenges"
                checked={formData.includeCodeChallenges}
                onChange={handleInputChange}
              />
              <span>Include Code Challenges (for technical/developer positions)</span>
            </label>
          </div>
        </section>

        <section className="form-section">
          <h2>Interview Settings</h2>

          <div className="form-group">
            <label htmlFor="interviewDuration">Interview Duration (minutes):</label>
            <input
              type="number"
              id="interviewDuration"
              name="interviewDuration"
              value={formData.interviewDuration}
              onChange={handleInputChange}
              min="10"
              max="120"
              step="5"
            />
            {errors.interviewDuration && <div className="error">{errors.interviewDuration}</div>}
          </div>
        </section>

        {errors.submit && <div className="error submit-error">{errors.submit}</div>}

        <button type="submit" className="submit-button">
          Generate Interview Plan
        </button>
      </form>
    </div>
  );
}

export default InterviewPrepForm;
