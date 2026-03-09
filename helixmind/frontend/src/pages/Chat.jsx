// frontend/src/pages/Chat.jsx
import { useState, useRef, useEffect } from 'react'
import { chatAPI } from '../api'

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Bonjour ! Je suis HelixMind, votre assistant scientifique. Posez-moi vos questions sur les protocoles, SOPs et procédures de laboratoire.',
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const res = await chatAPI.ask(question)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Erreur de connexion au serveur. Vérifiez que le backend est lancé.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '2rem',
      height: 'calc(100vh - 64px)',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <h2 style={{
        fontFamily: 'Orbitron',
        color: 'var(--cyan)',
        marginBottom: '1.5rem',
        fontSize: '1rem',
        letterSpacing: '2px',
      }}>
        🧠 ASSISTANT SCIENTIFIQUE RAG
      </h2>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        marginBottom: '1rem',
        paddingRight: '0.5rem',
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              maxWidth: '75%',
              padding: '1rem 1.2rem',
              borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
              background: msg.role === 'user'
                ? 'linear-gradient(135deg, #00D4FF22, #00FF8822)'
                : 'var(--bg-card)',
              border: msg.role === 'user'
                ? '1px solid var(--cyan)'
                : '1px solid var(--border)',
              fontSize: '0.9rem',
              lineHeight: 1.6,
              color: 'var(--text-primary)',
            }}>
              {msg.content}
              {msg.sources && msg.sources.length > 0 && (
                <div style={{
                  marginTop: '0.8rem',
                  paddingTop: '0.8rem',
                  borderTop: '1px solid var(--border)',
                  fontSize: '0.75rem',
                  color: 'var(--green)',
                }}>
                  📎 Sources : {msg.sources.join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{
              padding: '1rem 1.5rem',
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: '16px 16px 16px 4px',
              color: 'var(--cyan)',
              fontSize: '0.9rem',
            }}>
              ⏳ Analyse en cours...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        display: 'flex',
        gap: '0.8rem',
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '0.8rem',
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Posez votre question scientifique..."
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-primary)',
            fontSize: '0.9rem',
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            padding: '0.6rem 1.5rem',
            borderRadius: '8px',
            border: 'none',
            background: loading ? 'var(--border)' : 'linear-gradient(90deg, #00D4FF, #00FF88)',
            color: '#050A14',
            fontWeight: '700',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '0.85rem',
            fontFamily: 'Orbitron',
          }}
        >
          ENVOYER
        </button>
      </div>
    </div>
  )
}