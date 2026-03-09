// frontend/src/components/Navbar.jsx
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()

  const links = [
    { path: '/', label: 'Accueil' },
    { path: '/chat', label: '🧠 Assistant IA' },
    { path: '/pipeline', label: '🧬 Pipeline ADN' },
  ]

  return (
    <nav style={{
      background: 'rgba(10, 22, 40, 0.95)',
      borderBottom: '1px solid var(--border)',
      backdropFilter: 'blur(10px)',
      padding: '0 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
      }}>
        {/* Logo */}
        <Link to="/" style={{ textDecoration: 'none' }}>
          <span style={{
            fontFamily: 'Orbitron, sans-serif',
            fontSize: '1.4rem',
            fontWeight: '900',
            background: 'linear-gradient(90deg, #00D4FF, #00FF88)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '2px',
          }}>
            HELIX<span style={{ color: '#00FF88' }}>MIND</span>
          </span>
        </Link>

        {/* Links */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {links.map(link => (
            <Link
              key={link.path}
              to={link.path}
              style={{
                textDecoration: 'none',
                padding: '0.5rem 1.2rem',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: '500',
                color: location.pathname === link.path ? '#050A14' : 'var(--text-primary)',
                background: location.pathname === link.path
                  ? 'linear-gradient(90deg, #00D4FF, #00FF88)'
                  : 'transparent',
                border: location.pathname === link.path
                  ? 'none'
                  : '1px solid var(--border)',
                transition: 'all 0.2s ease',
              }}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}