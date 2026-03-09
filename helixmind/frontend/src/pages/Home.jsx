// frontend/src/pages/Home.jsx
import { Link } from 'react-router-dom'

export default function Home() {
  const features = [
    {
      icon: '🧠',
      title: 'Assistant RAG',
      desc: 'Posez des questions sur vos SOPs et protocoles. Réponses précises basées sur vos documents.',
      link: '/chat',
      color: '#00D4FF',
    },
    {
      icon: '🧬',
      title: 'Pipeline ADN',
      desc: 'Uploadez un fichier FASTQ et obtenez un rapport complet : QC, variants, interprétation IA.',
      link: '/pipeline',
      color: '#00FF88',
    },
  ]

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '4rem 2rem' }}>

      {/* Hero */}
      <div style={{ textAlign: 'center', marginBottom: '5rem' }}>
        <div style={{
          display: 'inline-block',
          padding: '0.3rem 1rem',
          border: '1px solid var(--cyan)',
          borderRadius: '20px',
          fontSize: '0.75rem',
          color: 'var(--cyan)',
          letterSpacing: '3px',
          marginBottom: '1.5rem',
          fontFamily: 'Orbitron',
        }}>
          GLOBAL BIOTEK — v1.0
        </div>

        <h1 style={{
          fontFamily: 'Orbitron, sans-serif',
          fontSize: 'clamp(2rem, 6vw, 4rem)',
          fontWeight: '900',
          lineHeight: 1.1,
          marginBottom: '1.5rem',
          background: 'linear-gradient(135deg, #00D4FF 0%, #00FF88 50%, #ffffff 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          INTELLIGENCE<br />GÉNOMIQUE IA
        </h1>

        <p style={{
          fontSize: '1.1rem',
          color: 'var(--text-muted)',
          maxWidth: '600px',
          margin: '0 auto 2.5rem',
          lineHeight: 1.7,
        }}>
          Plateforme combinant assistant conversationnel RAG et pipeline
          d'analyse ADN automatisé pour révolutionner l'interprétation
          des données biologiques en laboratoire.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/chat" style={{
            textDecoration: 'none',
            padding: '0.8rem 2rem',
            borderRadius: '8px',
            background: 'linear-gradient(90deg, #00D4FF, #00FF88)',
            color: '#050A14',
            fontWeight: '700',
            fontSize: '0.9rem',
            fontFamily: 'Orbitron',
            letterSpacing: '1px',
          }}>
            LANCER L'ASSISTANT
          </Link>
          <Link to="/pipeline" style={{
            textDecoration: 'none',
            padding: '0.8rem 2rem',
            borderRadius: '8px',
            border: '1px solid var(--cyan)',
            color: 'var(--cyan)',
            fontWeight: '600',
            fontSize: '0.9rem',
          }}>
            Analyser un fichier ADN
          </Link>
        </div>
      </div>

      {/* Feature Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem',
      }}>
        {features.map((f, i) => (
          <Link key={i} to={f.link} style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'var(--bg-card)',
              border: `1px solid ${f.color}33`,
              borderRadius: '12px',
              padding: '2rem',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              height: '100%',
            }}
              onMouseEnter={e => {
                e.currentTarget.style.border = `1px solid ${f.color}`
                e.currentTarget.style.boxShadow = `0 0 30px ${f.color}33`
              }}
              onMouseLeave={e => {
                e.currentTarget.style.border = `1px solid ${f.color}33`
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{f.icon}</div>
              <h3 style={{
                fontFamily: 'Orbitron',
                fontSize: '1rem',
                color: f.color,
                marginBottom: '0.8rem',
                letterSpacing: '1px',
              }}>
                {f.title}
              </h3>
              <p style={{ color: 'var(--text-muted)', lineHeight: 1.6, fontSize: '0.9rem' }}>
                {f.desc}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}