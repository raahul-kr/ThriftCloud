import React, { useState } from 'react';
import axios from 'axios';
import ProviderSelector from './ProviderSelector';
import ModeSelector from './ModeSelector';
import FileUpload from './FileUpload';
import ResultsPanel from './ResultsPanel';
import Sidebar from './Sidebar';
import { Loader2 } from 'lucide-react';

export default function Dashboard() {
  const [provider, setProvider] = useState('aws');
  const [mode, setMode] = useState('sample');
  const [file, setFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let response;
      const baseUrl = '/api'; // Handled by Vite proxy in dev, Nginx in prod
      
      if (mode === 'upload') {
        if (!file) {
          throw new Error('Please select a file to upload first.');
        }
        const formData = new FormData();
        formData.append('provider', provider);
        formData.append('file', file);
        
        response = await axios.post(`${baseUrl}/analyze/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        response = await axios.post(`${baseUrl}/analyze`, { provider });
      }
      
      setResults(response.data);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || 'An unexpected error occurred connecting to the backend.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Sidebar />
      <div style={{ flex: 1, padding: '40px', overflowY: 'auto', height: '100vh' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          
          <div style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '1.875rem', marginBottom: '8px', color: 'var(--text-primary)' }}>Cost Dashboard</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Analyze your cloud spending and find optimization opportunities.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 400px) 1fr', gap: '40px', alignItems: 'start' }}>
            
            <div className="glass-panel animate-fade-in" style={{ padding: '24px' }}>
              <ProviderSelector provider={provider} onChange={setProvider} />
              
              <div style={{ height: '1px', background: 'var(--border-color-light)', margin: '24px 0' }} />
              
              <ModeSelector mode={mode} onChange={setMode} />
              
              {mode === 'upload' && (
                <div className="animate-fade-in">
                  <FileUpload file={file} setFile={setFile} />
                </div>
              )}

              <button 
                onClick={handleAnalyze}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: 'none',
                  background: 'var(--accent-primary)',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '1rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  marginTop: '16px',
                  transition: 'background 0.2s',
                  boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
                }}
              >
                {loading && <Loader2 size={20} className="animate-pulse" style={{ animation: 'spin 1s linear infinite' }} />}
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </button>
              
              {error && (
                <div className="animate-fade-in" style={{ 
                  marginTop: '16px', padding: '12px', borderRadius: '8px', 
                  background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)',
                  border: '1px solid rgba(239, 68, 68, 0.2)', fontSize: '0.875rem'
                }}>
                  {error}
                </div>
              )}
            </div>

            <div>
              {loading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px', color: 'var(--text-muted)' }}>
                  <Loader2 size={48} color="var(--accent-primary)" style={{ animation: 'spin 1s linear infinite', marginBottom: '16px' }} />
                  <p>Processing your billing data...</p>
                </div>
              ) : results ? (
                <ResultsPanel data={results} provider={provider} />
              ) : (
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px', color: 'var(--text-muted)' }}>
                  <BarChart2 size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
                  <p>Select your provider and run an analysis to see insights.</p>
                </div>
              )}
            </div>
            
          </div>
        </div>
      </div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}

// Just importing the icon for the empty state
import { BarChart2 } from 'lucide-react';
