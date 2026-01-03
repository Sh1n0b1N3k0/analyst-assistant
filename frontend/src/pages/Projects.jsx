import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Chip,
} from '@mui/material'
import { Add, Psychology } from '@mui/icons-material'
import { projectsAPI } from '../services/api'

const Projects = () => {
  const [projects, setProjects] = useState([])
  const [open, setOpen] = useState(false)
  const [analyzeOpen, setAnalyzeOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    methodology: '',
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.list()
      setProjects(response.data)
    } catch (error) {
      console.error('Error loading projects:', error)
    }
  }

  const handleCreate = async () => {
    try {
      await projectsAPI.create(formData)
      setOpen(false)
      setFormData({ name: '', description: '', methodology: '' })
      loadProjects()
    } catch (error) {
      console.error('Error creating project:', error)
    }
  }

  const handleAnalyze = async (project) => {
    setSelectedProject(project)
    try {
      const response = await projectsAPI.analyze(project.id, {
        include_structure: true,
        include_risks: true,
      })
      setAnalysis(response.data)
      setAnalyzeOpen(true)
    } catch (error) {
      console.error('Error analyzing project:', error)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Проекты
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpen(true)}
        >
          Создать проект
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Название</TableCell>
              <TableCell>Описание</TableCell>
              <TableCell>Методология</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {projects.map((project) => (
              <TableRow key={project.id}>
                <TableCell>{project.name}</TableCell>
                <TableCell>{project.description || '-'}</TableCell>
                <TableCell>{project.methodology || '-'}</TableCell>
                <TableCell>
                  <Chip label={project.status || 'planning'} size="small" />
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<Psychology />}
                    onClick={() => handleAnalyze(project)}
                  >
                    Анализ ИИ
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog для создания проекта */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Создать новый проект</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Название"
            margin="normal"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <TextField
            fullWidth
            label="Описание"
            margin="normal"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <TextField
            fullWidth
            label="Методология"
            margin="normal"
            value={formData.methodology}
            onChange={(e) => setFormData({ ...formData, methodology: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Отмена</Button>
          <Button onClick={handleCreate} variant="contained">
            Создать
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog для анализа проекта */}
      <Dialog
        open={analyzeOpen}
        onClose={() => setAnalyzeOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>ИИ анализ проекта: {selectedProject?.name}</DialogTitle>
        <DialogContent>
          {analysis && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Рекомендации
              </Typography>
              <ul>
                {analysis.recommendations?.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Риски
              </Typography>
              <ul>
                {analysis.risks?.map((risk, idx) => (
                  <li key={idx}>{risk}</li>
                ))}
              </ul>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalyzeOpen(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Projects

