import React, { useState } from 'react';
import './InterviewPlanView.css';

function InterviewPlanView({ planData, onStartOver }) {
  const [activeTab, setActiveTab] = useState('overview');

  const { interview_plan, code_challenges, excel_file } = planData;

  const downloadExcel = () => {
    if (!excel_file || !excel_file.content) {
      alert('Excel file is not available');
      return;
    }

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

  const renderOverview = () => {
    const metadata = interview_plan?.metadata || {};
    const topics = interview_plan?.prioritized_topics || [];

    return (
      <div className="tab-content">
        <div className="overview-section">
          <h2>Interview Overview</h2>

          <div className="metadata-grid">
            <div className="metadata-item">
              <span className="label">Candidate:</span>
              <span className="value">{metadata.candidate_name || 'N/A'}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Position:</span>
              <span className="value">{metadata.job_title || 'N/A'}</span>
            </div>
            <div className="metadata-item">
              <span className="label">Duration:</span>
              <span className="value">{metadata.time_limit_minutes || 'N/A'} minutes</span>
            </div>
          </div>

          <h3>Objectives</h3>
          <div className="objectives-list">
            {(() => {
              const objectives = interview_plan?.interview_overview?.objectives;
              if (!objectives) {
                return <p>No objectives available</p>;
              }
              // Handle both string and array
              if (typeof objectives === 'string') {
                return <div className="objective-item">{objectives}</div>;
              }
              if (Array.isArray(objectives)) {
                return objectives.map((obj, idx) => (
                  <div key={idx} className="objective-item">{obj}</div>
                ));
              }
              return <p>No objectives available</p>;
            })()}
          </div>

          <h3>Time Allocation</h3>
          <div className="topics-timeline">
            {topics.map((topic, idx) => (
              <div key={idx} className="topic-timeline-item">
                <div className="topic-name">{topic.topic_name || 'Topic'}</div>
                <div className="topic-time">{topic.allocated_time_minutes || '0'} min</div>
                <div className="topic-priority">Priority: {topic.priority || 'N/A'}/5</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderQuestions = () => {
    const topics = interview_plan?.topics_to_cover || interview_plan?.prioritized_topics || [];

    // Calculate global question number across all topics
    let globalQuestionNumber = 0;

    return (
      <div className="tab-content">
        <h2>Interview Questions</h2>

        {topics.map((topic, topicIdx) => {
          // Skip topics without questions
          if (!topic.questions || topic.questions.length === 0) {
            return null;
          }

          return (
          <div key={topicIdx} className="topic-section">
            <h3 className="topic-header">{topic.topic_name || topic.topic || 'Topic'}</h3>
            {topic.rationale && <p className="topic-rationale">{topic.rationale}</p>}

            <div className="questions-list">
              {topic.questions?.map((question, qIdx) => {
                globalQuestionNumber++;
                return (
                <div key={qIdx} className="question-card">
                  <div className="question-number">Q{globalQuestionNumber}</div>
                  <div className="question-content">
                    <div className="question-text">{question.question || 'No question'}</div>
                    {question.what_to_look_for && (
                      <div className="question-detail">
                        <strong>What to look for:</strong> {question.what_to_look_for}
                      </div>
                    )}
                    {question.follow_up && (
                      <div className="question-detail">
                        <strong>Follow-up:</strong> {question.follow_up}
                      </div>
                    )}
                    {question.scoring_criteria && (
                      <div className="question-detail">
                        <strong>Scoring:</strong> {JSON.stringify(question.scoring_criteria)}
                      </div>
                    )}
                  </div>
                </div>
                );
              }) || <p>No questions available for this topic</p>}
            </div>
          </div>
        );
        })}
      </div>
    );
  };

  const renderCodeChallenges = () => {
    const challenges = code_challenges?.coding_challenges || [];
    const systemDesign = code_challenges?.system_design;
    const debugging = code_challenges?.debugging_challenge;

    return (
      <div className="tab-content">
        <h2>Code Challenges</h2>

        {challenges.length === 0 && !systemDesign && !debugging && (
          <div className="empty-state">
            <p className="empty-state-message">
              No code challenges were generated for this interview.
            </p>
            <p className="empty-state-hint">
              Code challenges are typically generated for technical positions that require coding skills.
              If you expected code challenges to be included, ensure the "Include Code Challenges"
              option was selected in the form.
            </p>
          </div>
        )}

        {challenges.map((challenge, idx) => (
          <div key={idx} className="challenge-card">
            <div className="challenge-header">
              <h3>Challenge {idx + 1}</h3>
              <span className="challenge-badge">
                {challenge.metadata?.difficulty || 'Medium'}
              </span>
            </div>

            <div className="challenge-content">
              <div className="challenge-section">
                <h4>Problem Description</h4>
                <p>{challenge.problem_description || 'No description'}</p>
              </div>

              <div className="challenge-meta">
                <span>Duration: {challenge.metadata?.duration_minutes || '30'} minutes</span>
                <span>Stack: {challenge.metadata?.technology_stack?.join(', ') || 'General'}</span>
              </div>

              {challenge.evaluation_criteria && (
                <div className="challenge-section">
                  <h4>Evaluation Criteria</h4>
                  <ul>
                    {Array.isArray(challenge.evaluation_criteria) ?
                      challenge.evaluation_criteria.map((criterion, i) => (
                        <li key={i}>{criterion}</li>
                      )) :
                      <li>{challenge.evaluation_criteria}</li>
                    }
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {systemDesign && (
          <div className="challenge-card system-design">
            <div className="challenge-header">
              <h3>System Design Challenge</h3>
              <span className="challenge-badge">Architecture</span>
            </div>
            <div className="challenge-content">
              <p>{systemDesign.problem_statement || 'No problem statement'}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderEvaluation = () => {
    const rubric = interview_plan?.evaluation_rubric || {};

    return (
      <div className="tab-content">
        <h2>Evaluation Rubric</h2>

        <div className="rubric-info">
          <div className="rubric-instructions-compact">
            <h4>🎯 Interview Workflow</h4>
            <div className="workflow-grid">
              <div className="workflow-step">
                <div className="workflow-number">1</div>
                <h5>BEFORE Interview</h5>
                <ul>
                  <li>Review this page</li>
                  <li>Download Excel file</li>
                  <li>Study Questions tab</li>
                </ul>
              </div>

              <div className="workflow-step">
                <div className="workflow-number">2</div>
                <h5>DURING Interview</h5>
                <ul>
                  <li>Ask questions</li>
                  <li>Open Excel file</li>
                  <li>Compare answers</li>
                  <li>Record scores (1-5)</li>
                </ul>
              </div>

              <div className="workflow-step">
                <div className="workflow-number">3</div>
                <h5>AFTER Interview</h5>
                <ul>
                  <li>Check total %</li>
                  <li>See Decision Framework</li>
                  <li>Decide: Hire/Maybe/No</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {rubric && Object.keys(rubric).length > 0 ? (
          <div className="rubric-display">
            {/* Decision Framework */}
            {rubric.decision_framework && (
              <div className="rubric-section">
                <h3>Decision Framework</h3>
                <p className="framework-explanation">
                  Use these thresholds to make hiring decisions based on the candidate's total score:
                </p>
                <div className="decision-framework">
                  <div className="threshold-item threshold-hire">
                    <div className="threshold-label">✓ Hire</div>
                    <div className="threshold-value">≥ {rubric.decision_framework.hire_threshold}%</div>
                    <div className="threshold-description">Strong candidate - recommend to hire</div>
                  </div>
                  <div className="threshold-item threshold-maybe">
                    <div className="threshold-label">? Maybe</div>
                    <div className="threshold-value">{rubric.decision_framework.no_hire_threshold}% - {rubric.decision_framework.hire_threshold - 1}%</div>
                    <div className="threshold-description">Consider additional interview or review</div>
                  </div>
                  <div className="threshold-item threshold-no-hire">
                    <div className="threshold-label">✗ No Hire</div>
                    <div className="threshold-value">&lt; {rubric.decision_framework.no_hire_threshold}%</div>
                    <div className="threshold-description">Does not meet requirements</div>
                  </div>
                </div>
              </div>
            )}

            {/* Evaluation Guidelines */}
            {rubric.overall_evaluation_guidelines && Object.keys(rubric.overall_evaluation_guidelines).length > 0 && (
              <div className="rubric-section">
                <h3>Overall Evaluation Guidelines</h3>
                {rubric.overall_evaluation_guidelines.recommendations && (
                  <div className="recommendations">
                    <h4>Recommendations</h4>
                    <ul>
                      <li><strong>High Score:</strong> {rubric.overall_evaluation_guidelines.recommendations.high}</li>
                      <li><strong>Low Score:</strong> {rubric.overall_evaluation_guidelines.recommendations.low}</li>
                      <li><strong>Medium Score:</strong> {rubric.overall_evaluation_guidelines.recommendations.medium}</li>
                    </ul>
                  </div>
                )}
                {rubric.overall_evaluation_guidelines.score_ranges && (
                  <div className="score-ranges">
                    <h4>Score Ranges</h4>
                    <ul>
                      <li><strong>High:</strong> {rubric.overall_evaluation_guidelines.score_ranges.high}</li>
                      <li><strong>Low:</strong> {rubric.overall_evaluation_guidelines.score_ranges.low}</li>
                      <li><strong>Medium:</strong> {rubric.overall_evaluation_guidelines.score_ranges.medium}</li>
                    </ul>
                  </div>
                )}
                {rubric.overall_evaluation_guidelines.total_score && (
                  <div className="total-score-info">
                    <strong>Total Score Calculation:</strong> {rubric.overall_evaluation_guidelines.total_score}
                  </div>
                )}
                {rubric.overall_evaluation_guidelines.special_considerations && (
                  <div className="special-considerations">
                    <h4>Special Considerations</h4>
                    <ul>
                      {rubric.overall_evaluation_guidelines.special_considerations.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Topics */}
            {rubric.topics && rubric.topics.length > 0 && (
              <div className="rubric-section">
                <h3>Topic Evaluation Criteria</h3>
                {rubric.topics.map((topic, idx) => (
                  <div key={idx} className="topic-rubric-card">
                    <h4 className="topic-rubric-header">
                      {topic.topic_name || topic.topic || `Topic ${idx + 1}`}
                    </h4>

                    {topic.description && (
                      <p className="topic-description">{topic.description}</p>
                    )}

                    <div className="topic-meta">
                      <span><strong>Time Allocated:</strong> {topic.allocated_time || topic.allocated_time_minutes || 'N/A'} minutes</span>
                      <span><strong>Priority:</strong> {topic.priority || 'N/A'}/5</span>
                    </div>

                    {topic.scoring_scale && (
                      <div className="scoring-scale">
                        <h5>Scoring Scale (1-5)</h5>
                        <div className="scale-items-vertical">
                          {Object.entries(topic.scoring_scale).map(([key, value]) => {
                            // Parse the value if it's an object with description and key_indicators
                            let description = '';
                            let indicators = [];

                            if (typeof value === 'object' && value !== null) {
                              description = value.description || '';
                              indicators = value.key_indicators || value.key_indicator || [];
                              if (typeof indicators === 'string') {
                                indicators = [indicators];
                              }
                            } else {
                              description = value;
                            }

                            return (
                              <div key={key} className="scale-item-detailed">
                                <div className="scale-score">{key}</div>
                                <div className="scale-content">
                                  <div className="scale-description">{description}</div>
                                  {indicators.length > 0 && (
                                    <ul className="scale-indicators">
                                      {indicators.map((indicator, idx) => (
                                        <li key={idx}>{indicator}</li>
                                      ))}
                                    </ul>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {topic.key_indicators && topic.key_indicators.length > 0 && (
                      <div className="key-indicators">
                        <h5>Key Indicators</h5>
                        <ul>
                          {topic.key_indicators.map((indicator, i) => (
                            <li key={i}>{indicator}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">
            <p className="empty-state-message">Evaluation rubric will be included in the Excel file</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="interview-plan-view">
      <header className="plan-header">
        <h1>Interview Plan Ready!</h1>
        <div className="header-actions">
          <button className="download-btn" onClick={downloadExcel}>
            Download Excel Plan
          </button>
          <button className="secondary-btn" onClick={onStartOver}>
            Start Over
          </button>
        </div>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          Questions
        </button>
        <button
          className={`tab ${activeTab === 'challenges' ? 'active' : ''}`}
          onClick={() => setActiveTab('challenges')}
        >
          Code Challenges
        </button>
        <button
          className={`tab ${activeTab === 'evaluation' ? 'active' : ''}`}
          onClick={() => setActiveTab('evaluation')}
        >
          Evaluation
        </button>
      </div>

      <div className="plan-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'questions' && renderQuestions()}
        {activeTab === 'challenges' && renderCodeChallenges()}
        {activeTab === 'evaluation' && renderEvaluation()}
      </div>
    </div>
  );
}

export default InterviewPlanView;
