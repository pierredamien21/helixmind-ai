// frontend/src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Pipeline from './pages/Pipeline'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ position: 'relative', zIndex: 1 }}>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/pipeline" element={<Pipeline />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}