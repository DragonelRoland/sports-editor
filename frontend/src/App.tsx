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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
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
      
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !prompt.trim()) {
      alert('Please select a video file and enter a prompt');
      return;
    }

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('prompt', prompt.trim());

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
    setSelectedFile(null);
    setPrompt('');
    setCurrentJob(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getVideoUrl = (filename: string) => {
    return `/jobs/${filename}`;
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎬 Sports Editor</h1>
          <p>Transform your videos with AI-powered animation</p>
        </header>

        <div className="upload-section">
          <div className="file-input-wrapper">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="file-input"
              id="video-input"
            />
            <label htmlFor="video-input" className="file-input-label">
              {selectedFile ? selectedFile.name : 'Choose video file'}
            </label>
          </div>

          <div className="prompt-input-wrapper">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your animation idea... (e.g., 'change colors to neon, add sparkle effects')"
              className="prompt-input"
              rows={3}
            />
          </div>

          <button
            onClick={handleUpload}
            disabled={!selectedFile || !prompt.trim() || isUploading}
            className="upload-button"
          >
            {isUploading ? 'Uploading...' : 'Transform Video'}
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
            
            <p><strong>Prompt:</strong> {currentJob.prompt}</p>
            
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