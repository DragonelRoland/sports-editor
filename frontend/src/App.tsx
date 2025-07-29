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
            <h1>⚽ SportsVoice AI</h1>
            <p>Transform any athlete into your perfect sports interviewer using AI</p>
            <div className="subtitle">
              Upload your favorite player + reference interview → Get your custom sports content
            </div>
            <div className="demo-section">
              <p>🎯 <strong>Perfect for:</strong> Sports content creators, podcasters, social media managers</p>
              <p>🔥 <strong>Use cases:</strong> Custom interviews, sports commentary, social media content</p>
            </div>
          </header>

                <div className="upload-section">
                      <div className="upload-grid">
              <div className="file-input-wrapper">
                <h3>🏈 Your Athlete</h3>
                <input
                  ref={characterInputRef}
                  type="file"
                  accept="video/*"
                  onChange={handleCharacterSelect}
                  className="file-input"
                  id="character-input"
                />
                <label htmlFor="character-input" className="file-input-label">
                  {characterFile ? characterFile.name : 'Upload athlete video'}
                </label>
                <p className="file-description">
                  Video of your favorite player (clear face shot works best)
                </p>
                <div className="example-text">
                  💡 Example: Messi celebration, Ronaldo interview, LeBron press conference
                </div>
              </div>

              <div className="file-input-wrapper">
                <h3>🎤 Interview Style</h3>
                <input
                  ref={referenceInputRef}
                  type="file"
                  accept="video/*"
                  onChange={handleReferenceSelect}
                  className="file-input"
                  id="reference-input"
                />
                <label htmlFor="reference-input" className="file-input-label">
                  {referenceFile ? referenceFile.name : 'Upload interview reference'}
                </label>
                <p className="file-description">
                  Professional interviewer or presenter style to copy
                </p>
                <div className="example-text">
                  💡 Example: ESPN anchor, sports reporter, podcast host
                </div>
              </div>
            </div>

                      <button
              onClick={handleUpload}
              disabled={!characterFile || !referenceFile || isUploading}
              className="upload-button"
            >
              {isUploading ? 'Creating Sports Content...' : '🚀 Create Sports Interview'}
            </button>
        </div>

        {currentJob && (
          <div className="job-status">
            <h3>🎬 Production Status</h3>
            <div className={`status-badge ${currentJob.status}`}>
              {currentJob.status === 'processing' && '⏳ Creating Sports Interview...'}
              {currentJob.status === 'completed' && '✅ Sports Content Ready!'}
              {currentJob.status === 'failed' && '❌ Production Failed'}
            </div>
            
            <p><strong>AI Magic:</strong> Athlete + Interview Style = Custom Content</p>
            
            {/* Video Preview Section */}
            <div className="video-preview-section">
              <div className="video-preview-grid">
                <div className="video-preview">
                  <h4>🏈 Original Athlete</h4>
                  {characterFile && (
                    <video 
                      controls 
                      className="preview-video"
                      src={URL.createObjectURL(characterFile)}
                    />
                  )}
                </div>
                <div className="video-preview">
                  <h4>🎤 Interview Reference</h4>
                  {referenceFile && (
                    <video 
                      controls 
                      className="preview-video"
                      src={URL.createObjectURL(referenceFile)}
                    />
                  )}
                </div>
              </div>
            </div>
            
            {currentJob.status === 'processing' && (
              <div className="loading-spinner">
                <div className="spinner"></div>
                <p>🔥 AI is working its magic... This may take a few minutes.</p>
                <p>We're transferring the interview style to your athlete!</p>
              </div>
            )}
            
            {currentJob.status === 'completed' && currentJob.output_file && (
              <div className="result-section">
                <h4>🎯 Your Sports Interview</h4>
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
                    📥 Download Sports Interview
                  </a>
                </div>
              </div>
            )}
            
            {currentJob.status === 'failed' && (
              <div className="error-section">
                <h4>⚠️ Production Issue:</h4>
                <p className="error-message">{currentJob.error}</p>
                <div className="error-help">
                  <p><strong>💡 Tips for better results:</strong></p>
                  <ul>
                    <li>Use clear face shots of athletes</li>
                    <li>Choose professional interview videos</li>
                    <li>Ensure good lighting in both videos</li>
                  </ul>
                </div>
              </div>
            )}
            
            <button onClick={resetForm} className="reset-button">
              🎬 Create New Sports Content
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 