import React, { useState, useRef } from 'react';
import './App.css';

interface Job {
  id: string;
  status: 'processing' | 'completed' | 'failed';
  prompt: string;
  input_file: string;
  output_file: string | null;
  error: string | null;
  created_at: string;
  completed_at: string | null;
}

function App() {
  const [characterFile, setCharacterFile] = useState<File | null>(null);
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const characterInputRef = useRef<HTMLInputElement>(null);
  const referenceInputRef = useRef<HTMLInputElement>(null);

  const handleCharacterSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('video/')) {
        alert('Please select a video file');
        return;
      }
      
      // Validate file size (16MB)
      if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
      }
      
      setCharacterFile(file);
    }
  };

  const handleReferenceSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('video/')) {
        alert('Please select a video file');
        return;
      }
      
      // Validate file size (16MB)
      if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
      }
      
      setReferenceFile(file);
    }
  };

  const handleUpload = async () => {
    if (!characterFile || !referenceFile) {
      alert('Please select both character and reference videos');
      return;
    }

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('character_file', characterFile);
      formData.append('reference_file', referenceFile);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      
      // Start polling for job status
      pollJobStatus(result.job_id);
      
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}`);
        if (response.ok) {
          const jobData: Job = await response.json();
          setCurrentJob(jobData);
          
          if (jobData.status === 'processing') {
            setTimeout(poll, 3000); // Poll every 3 seconds
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };
    
    poll();
  };

  const resetForm = () => {
    setCharacterFile(null);
    setReferenceFile(null);
    setCurrentJob(null);
    if (characterInputRef.current) {
      characterInputRef.current.value = '';
    }
    if (referenceInputRef.current) {
      referenceInputRef.current.value = '';
    }
  };

  const getVideoUrl = (filename: string) => {
    return `/jobs/${filename}`;
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎭 Performance Transfer Studio</h1>
          <p>Transfer performances between characters using AI</p>
        </header>

                <div className="upload-section">
          <div className="upload-grid">
            <div className="file-input-wrapper">
              <h3>Character Video</h3>
              <input
                ref={characterInputRef}
                type="file"
                accept="video/*"
                onChange={handleCharacterSelect}
                className="file-input"
                id="character-input"
              />
              <label htmlFor="character-input" className="file-input-label">
                {characterFile ? characterFile.name : 'Choose character video'}
              </label>
              <p className="file-description">
                Video of the person/character you want to animate
              </p>
            </div>

            <div className="file-input-wrapper">
              <h3>Reference Performance</h3>
              <input
                ref={referenceInputRef}
                type="file"
                accept="video/*"
                onChange={handleReferenceSelect}
                className="file-input"
                id="reference-input"
              />
              <label htmlFor="reference-input" className="file-input-label">
                {referenceFile ? referenceFile.name : 'Choose reference video'}
              </label>
              <p className="file-description">
                Video of the performance you want to transfer
              </p>
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!characterFile || !referenceFile || isUploading}
            className="upload-button"
          >
            {isUploading ? 'Processing...' : 'Transfer Performance'}
          </button>
        </div>

        {currentJob && (
          <div className="job-status">
            <h3>Processing Status</h3>
            <div className={`status-badge ${currentJob.status}`}>
              {currentJob.status === 'processing' && '⏳ Processing...'}
              {currentJob.status === 'completed' && '✅ Completed'}
              {currentJob.status === 'failed' && '❌ Failed'}
            </div>
            
            <p><strong>Performance Transfer:</strong> Character → Reference</p>
            
            {currentJob.status === 'processing' && (
              <div className="loading-spinner">
                <div className="spinner"></div>
                <p>This may take a few minutes...</p>
              </div>
            )}
            
            {currentJob.status === 'completed' && currentJob.output_file && (
              <div className="result-section">
                <h4>Your transformed video is ready!</h4>
                <video
                  controls
                  className="result-video"
                  src={getVideoUrl(currentJob.output_file)}
                >
                  Your browser does not support the video tag.
                </video>
                <div className="download-section">
                  <a
                    href={getVideoUrl(currentJob.output_file)}
                    download={currentJob.output_file}
                    className="download-button"
                  >
                    Download Video
                  </a>
                </div>
              </div>
            )}
            
            {currentJob.status === 'failed' && (
              <div className="error-section">
                <p><strong>Error:</strong> {currentJob.error}</p>
              </div>
            )}
            
            <button onClick={resetForm} className="reset-button">
              Start New Project
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 