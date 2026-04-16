import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileText, UploadCloud, X } from 'lucide-react';

export default function FileUpload({ file, setFile }) {
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles?.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, [setFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'text/plain': ['.txt'],
      'application/json': ['.json']
    },
    maxFiles: 1
  });

  if (file) {
    return (
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '12px', borderRadius: '8px' }}>
          <FileText size={24} color="var(--accent-primary)" />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{file.name}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{(file.size / 1024).toFixed(1)} KB</div>
        </div>
        <button 
          onClick={() => setFile(null)}
          style={{ 
            background: 'transparent', border: 'none', cursor: 'pointer', 
            color: 'var(--text-muted)', padding: '8px', borderRadius: '50%' 
          }}
          className="glass-panel-hover"
        >
          <X size={20} />
        </button>
      </div>
    );
  }

  return (
    <div style={{ marginBottom: '24px' }}>
      <div 
        {...getRootProps()} 
        style={{
          border: `2px dashed ${isDragActive ? 'var(--accent-primary)' : 'var(--border-color)'}`,
          borderRadius: '16px',
          padding: '40px 20px',
          textAlign: 'center',
          cursor: 'pointer',
          background: isDragActive ? 'rgba(59, 130, 246, 0.05)' : 'var(--bg-card)',
          transition: 'all 0.2s ease-in-out'
        }}
        className="glass-panel-hover"
      >
        <input {...getInputProps()} />
        <div style={{ 
          width: '48px', height: '48px', margin: '0 auto 16px', 
          background: 'rgba(59, 130, 246, 0.1)', borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <UploadCloud size={24} color="var(--accent-primary)" />
        </div>
        <h4 style={{ fontSize: '1.125rem', marginBottom: '4px', color: 'var(--text-primary)', fontWeight: 600 }}>
          {isDragActive ? 'Drop file here' : 'Click or drop file to upload'}
        </h4>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Supported formats: .csv, .txt, .json
        </p>
      </div>
    </div>
  );
}
