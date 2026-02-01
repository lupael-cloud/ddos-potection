import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Navbar({ onLogout }) {
  const [showTrafficMenu, setShowTrafficMenu] = useState(false);

  return (
    <div className="navbar">
      <h1>🛡️ DDoS Protection Platform</h1>
      <nav>
        <Link to="/">Dashboard</Link>
        <Link to="/traffic">Traffic</Link>
        
        {/* Traffic Collection & Detection Dropdown */}
        <div 
          style={{ position: 'relative', display: 'inline-block' }}
          onMouseEnter={() => setShowTrafficMenu(true)}
          onMouseLeave={() => setShowTrafficMenu(false)}
        >
          <span style={{ cursor: 'pointer', padding: '0.5rem 1rem' }}>
            Collection & Detection ▼
          </span>
          {showTrafficMenu && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              background: 'white',
              boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
              borderRadius: '4px',
              minWidth: '200px',
              zIndex: 1000,
              marginTop: '0.5rem'
            }}>
              <Link 
                to="/traffic-collection" 
                style={{
                  display: 'block',
                  padding: '0.75rem 1rem',
                  color: '#333',
                  textDecoration: 'none',
                  borderBottom: '1px solid #eee'
                }}
                onMouseEnter={(e) => e.target.style.background = '#f8f9fa'}
                onMouseLeave={(e) => e.target.style.background = 'white'}
              >
                Traffic Collection
              </Link>
              <Link 
                to="/anomaly-detection" 
                style={{
                  display: 'block',
                  padding: '0.75rem 1rem',
                  color: '#333',
                  textDecoration: 'none',
                  borderBottom: '1px solid #eee'
                }}
                onMouseEnter={(e) => e.target.style.background = '#f8f9fa'}
                onMouseLeave={(e) => e.target.style.background = 'white'}
              >
                Anomaly Detection
              </Link>
              <Link 
                to="/entropy-analysis" 
                style={{
                  display: 'block',
                  padding: '0.75rem 1rem',
                  color: '#333',
                  textDecoration: 'none'
                }}
                onMouseEnter={(e) => e.target.style.background = '#f8f9fa'}
                onMouseLeave={(e) => e.target.style.background = 'white'}
              >
                Entropy Analysis
              </Link>
            </div>
          )}
        </div>
        
        <Link to="/alerts">Alerts</Link>
        <Link to="/rules">Rules</Link>
        <Link to="/capture">Capture</Link>
        <Link to="/hostgroups">Hostgroups</Link>
        <Link to="/bgp-blackholing">BGP/RTBH</Link>
        <Link to="/reports">Reports</Link>
        <Link to="/settings">Settings</Link>
        <button 
          onClick={onLogout} 
          style={{
            background: 'rgba(255,255,255,0.2)',
            border: 'none',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </nav>
    </div>
  );
}

export default Navbar;
