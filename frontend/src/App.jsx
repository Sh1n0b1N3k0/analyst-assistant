import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Projects from './pages/Projects'
import Requirements from './pages/Requirements'
import KnowledgeBase from './pages/KnowledgeBase'
import Specifications from './pages/Specifications'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/requirements" element={<Requirements />} />
          <Route path="/knowledge" element={<KnowledgeBase />} />
          <Route path="/specifications" element={<Specifications />} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App

