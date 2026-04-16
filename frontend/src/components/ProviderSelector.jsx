import React from 'react';

export default function ProviderSelector({ provider, onChange }) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <h3 style={{ fontSize: '1rem', marginBottom: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>Select Cloud Provider</h3>
      <div style={{ display: 'flex', gap: '16px' }}>
        <ProviderCard 
          id="aws"
          name="Amazon Web Services"
          shortName="AWS"
          active={provider === 'aws'}
          onClick={() => onChange('aws')}
          accentColor="var(--accent-aws)"
        />
        <ProviderCard 
          id="azure"
          name="Microsoft Azure"
          shortName="Azure"
          active={provider === 'azure'}
          onClick={() => onChange('azure')}
          accentColor="var(--accent-azure)"
        />
      </div>
    </div>
  );
}

function ProviderCard({ name, shortName, active, onClick, accentColor }) {
  return (
    <div 
      className="glass-panel glass-panel-hover"
      onClick={onClick}
      style={{
        padding: '16px 20px',
        flex: 1,
        cursor: 'pointer',
        border: active ? `2px solid ${accentColor}` : '2px solid transparent',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {active && (
        <div style={{
          position: 'absolute',
          top: 0, right: 0, bottom: 0, width: '4px',
          background: accentColor
        }} />
      )}
      
      <div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>{shortName}</div>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{name}</div>
      </div>
      
      <div style={{
        width: '24px', height: '24px', borderRadius: '50%',
        border: `2px solid ${active ? accentColor : 'var(--border-color)'}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: active ? accentColor : 'transparent'
      }}>
        {active && <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'white' }} />}
      </div>
    </div>
  );
}
