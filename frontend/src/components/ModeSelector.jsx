import React from 'react';
import { Database, UploadCloud } from 'lucide-react';

export default function ModeSelector({ mode, onChange }) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <h3 style={{ fontSize: '1rem', marginBottom: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>Analysis Mode</h3>
      <div style={{ display: 'flex', background: 'var(--bg-card)', padding: '4px', borderRadius: '12px', border: '1px solid var(--border-color-light)' }}>
        <ModeTab 
          icon={<Database size={18} />}
          label="Sample Data"
          active={mode === 'sample'}
          onClick={() => onChange('sample')}
        />
        <ModeTab 
          icon={<UploadCloud size={18} />}
          label="Upload Billing File"
          active={mode === 'upload'}
          onClick={() => onChange('upload')}
        />
      </div>
    </div>
  );
}

function ModeTab({ icon, label, active, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        padding: '12px',
        borderRadius: '8px',
        cursor: 'pointer',
        fontWeight: 500,
        color: active ? 'white' : 'var(--text-muted)',
        background: active ? 'var(--accent-primary)' : 'transparent',
        transition: 'all 0.2s',
        boxShadow: active ? '0 4px 12px rgba(59, 130, 246, 0.3)' : 'none'
      }}
    >
      {icon}
      <span>{label}</span>
    </div>
  );
}
