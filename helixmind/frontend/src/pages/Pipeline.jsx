// frontend/src/pages/Pipeline.jsx
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { pipelineAPI } from '../api'

const STEP_LABELS = {
  fastqc: '🔬 Contrôle Qualité',
  alignment: '🧬 Alignement',
  variant_calling: '🔍 Variant Calling',
  annotation: '📚 Annotation',
  interpretation: '🤖 Interprétation IA',
  report: '📄 Rapport PDF',
}

export default function Pipeline() {
  const [job, setJob] = useState(null)
  const [status, setStatus] = useState(null)
  const [polling, setPolling] = useState(false)
  const [error, setError] = useState(null)

  const onDrop = useCallback(async (files) => {
    const file = files[0]
    if (!file) return
    setError(null)
    setStatus(null)
    try {
      const res = await pipelineAPI.upload(file)
      const jobId = res.data.job_id
      setJob(jobId)
      setPolling(true)
      pollStatus(jobId)
    } catch (err) {
      setError("Erreur lors de l'upload. Vérifiez que le backend est lancé.")
    }
  }, [])

  const pollStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const res = await pipelineAPI.status(jobId)
        setStatus(res.data)
        if (['completed', 'failed'].includes(res.data.status)) {
          clearInterval(interval)
          setPolling(false)
        }
      } catch (err) {
        clearInterval(interval)
        setPolling(false)
      }
    }, 1000)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/plain': ['.fastq', '.fq', '.txt'] },
    maxFiles: 1,
  })

  const getStepColor = (stepStatus) => {
    if (stepStatus === 'done') return '#00FF88'
    if (stepStatus === 'running') return '#00D4FF'
    return 'var(--text-muted)'
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem' }}>
      <h2 style={{
        fontFamily: 'Orbitron',
        color: 'var(--green)',
        marginBottom: '0.5rem',
        fontSize: '1rem',
        letterSpacing: '2px',
      }}>
        🧬 PIPELINE D'ANALYSE ADN
      </h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', fontSize: '0.9rem' }}>
        Uploadez un fichier FASTQ pour lancer l'analyse complète
      </p>

      {/* Dropzone */}
      <div {...getRootProps()} style={{
        border: `2px dashed ${isDragActive ? '#00FF88' : 'var(--border)'}`,
        borderRadius: '12px',
        padding: '3rem',
        textAlign: 'center',
        cursor: 'pointer',
        background: isDragActive ? '#00FF8811' : 'var(--bg-card)',
        transition: 'all 0.3s ease',
        marginBottom: '2rem',
      }}>
        <input {...getInputProps()} />
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🧬</div>
        <p style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          {isDragActive ? 'Déposez le fichier ici...' : 'Glissez votre fichier FASTQ ici'}
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          Formats acceptés : .fastq, .fq, .txt
        </p>
      </div>

      {error && (
        <div style={{
          background: '#FF444422',
          border: '1px solid #FF4444',
          borderRadius: '8px',
          padding: '1rem',
          color: '#FF4444',
          marginBottom: '1.5rem',
        }}>
          ❌ {error}
        </div>
      )}

      {status && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '1.5rem',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem',
          }}>
            <span style={{ fontFamily: 'Orbitron', fontSize: '0.85rem', color: 'var(--cyan)' }}>
              JOB #{job}
            </span>
            <span style={{
              padding: '0.3rem 1rem',
              borderRadius: '20px',
              fontSize: '0.75rem',
              fontWeight: '700',
              background: status.status === 'completed' ? '#00FF8833'
                : status.status === 'failed' ? '#FF444433' : '#00D4FF33',
              color: status.status === 'completed' ? '#00FF88'
                : status.status === 'failed' ? '#FF4444' : '#00D4FF',
            }}>
              {status.status.toUpperCase()}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            {Object.entries(STEP_LABELS).map(([key, label]) => {
              const step = status.steps?.[key]
              const stepStatus = step?.status || 'pending'
              return (
                <div key={key} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '0.7rem 1rem',
                  borderRadius: '8px',
                  background: stepStatus === 'running' ? '#00D4FF11' : 'transparent',
                  border: `1px solid ${stepStatus !== 'pending' ? getStepColor(stepStatus) + '44' : 'transparent'}`,
                }}>
                  <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: getStepColor(stepStatus),
                    boxShadow: stepStatus === 'running' ? '0 0 10px #00D4FF' : 'none',
                  }} />
                  <span style={{
                    fontSize: '0.9rem',
                    color: stepStatus === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)',
                  }}>
                    {label}
                  </span>
                  {stepStatus === 'running' && (
                    <span style={{ color: 'var(--cyan)', fontSize: '0.8rem', marginLeft: 'auto' }}>
                      En cours...
                    </span>
                  )}
                  {stepStatus === 'done' && (
                    <span style={{ color: 'var(--green)', fontSize: '0.8rem', marginLeft: 'auto' }}>
                      ✓ Terminé
                    </span>
                  )}
                </div>
              )
            })}
          </div>

          {status.status === 'completed' && (
            <a
              href={pipelineAPI.reportUrl(job)}
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'block',
                marginTop: '1.5rem',
                padding: '1rem',
                textAlign: 'center',
                borderRadius: '8px',
                background: 'linear-gradient(90deg, #00D4FF, #00FF88)',
                color: '#050A14',
                fontWeight: '700',
                fontFamily: 'Orbitron',
                letterSpacing: '1px',
                textDecoration: 'none',
                fontSize: '0.9rem',
              }}
            >
              📄 TÉLÉCHARGER LE RAPPORT PDF
            </a>
          )}

          {status.status === 'failed' && (
            <div style={{
              marginTop: '1rem',
              padding: '1rem',
              background: '#FF444422',
              border: '1px solid #FF4444',
              borderRadius: '8px',
              color: '#FF4444',
              fontSize: '0.85rem',
            }}>
              ❌ Erreur : {status.error}
            </div>
          )}
        </div>
      )}
    </div>
  )
}