import React from 'react';
import { Cloud, BarChart2, Settings, HelpCircle, User } from 'lucide-react';

export default function Sidebar() {
  return (
    <div style={{
      width: '260px',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      padding: '24px 16px',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      position: 'sticky',
      top: 0
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px', paddingLeft: '8px' }}>
        <div style={{ 
          background: 'var(--accent-primary)',
          borderRadius: '8px',
          width: '36px',
          height: '36px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Cloud size={20} color="white" />
        </div>
        <h1 style={{ fontSize: '1.25rem', margin: 0, fontWeight: 700 }} className="text-gradient">ThriftCloud</h1>
      </div>
      
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
        <NavItem icon={<BarChart2 size={20} />} label="Cost Analysis" active />
        <NavItem icon={<Cloud size={20} />} label="Resources" />
        <NavItem icon={<Settings size={20} />} label="Settings" />
      </nav>
      
      <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
        <NavItem icon={<HelpCircle size={20} />} label="Help & Support" />
        <NavItem icon={<User size={20} />} label="Account" />
      </div>
    </div>
  );
}

function NavItem({ icon, label, active }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '12px 16px',
      borderRadius: '8px',
      color: active ? 'white' : 'var(--text-secondary)',
      backgroundColor: active ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
      cursor: 'pointer',
      transition: 'all 0.2s'
    }} className={!active ? "glass-panel-hover" : ""}>
      {icon}
      <span style={{ fontWeight: active ? 600 : 500 }}>{label}</span>
      {active && (
        <div style={{ marginLeft: 'auto', width: '4px', height: '16px', borderRadius: '2px', background: 'var(--accent-primary)' }} />
      )}
    </div>
  );
}
