import React, { useState } from 'react';
import InterviewPrepForm from './InterviewPrepForm';
import InterviewPlanView from './InterviewPlanView';
import LoadingSpinner from './LoadingSpinner';
import './App.css';

function App() {
  const [step, setStep] = useState('prepForm');
  const [planData, setPlanData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handlePrepFormSubmit = (data) => {
    setIsLoading(false);
    setPlanData(data);
    setStep('viewPlan');
  };

  const handleStartOver = () => {
    setPlanData(null);
    setStep('prepForm');
  };

  return (
    <div className="App">
      {isLoading && <LoadingSpinner />}
      {step === 'prepForm' && (
        <InterviewPrepForm
          onSubmit={handlePrepFormSubmit}
          setIsLoading={setIsLoading}
        />
      )}
      {step === 'viewPlan' && planData && (
        <InterviewPlanView
          planData={planData}
          onStartOver={handleStartOver}
        />
      )}
    </div>
  );
}

export default App;