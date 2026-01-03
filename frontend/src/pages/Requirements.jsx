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
  Tabs,
  Tab,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import { Add, Upload } from '@mui/icons-material'
import { requirementsAPI, projectsAPI } from '../services/api'

const Requirements = () => {
  const [requirements, setRequirements] = useState([])
  const [projects, setProjects] = useState([])
  const [open, setOpen] = useState(false)
  const [processOpen, setProcessOpen] = useState(false)
  const [tab, setTab] = useState(0)
  const [processingStatus, setProcessingStatus] = useState(null)
  const [formData, setFormData] = useState({
    project_id: '',
    informal_text: '',
  })

  useEffect(() => {
    loadRequirements()
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

  const loadRequirements = async () => {
    try {
      const response = await requirementsAPI.list()
      setRequirements(response.data)
    } catch (error) {
      console.error('Error loading requirements:', error)
    }
  }

  const handleProcess = async () => {
    try {
      const response = await requirementsAPI.process({
        project_id: formData.project_id,
        informal_text: formData.informal_text,
      })
      setProcessingStatus(response.data)
      setProcessOpen(false)
      
      // Проверка статуса обработки
      const checkStatus = async () => {
        const statusResponse = await requirementsAPI.getProcessingStatus(
          response.data.processing_id
        )
        if (statusResponse.data.status === 'completed') {
          setProcessingStatus(statusResponse.data)
          loadRequirements()
        } else if (statusResponse.data.status === 'processing') {
          setTimeout(checkStatus, 2000)
        }
      }
      setTimeout(checkStatus, 2000)
    } catch (error) {
      console.error('Error processing requirement:', error)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Требования
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Upload />}
            onClick={() => setProcessOpen(true)}
            sx={{ mr: 1 }}
          >
            Обработать требование
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpen(true)}
          >
            Создать требование
          </Button>
        </Box>
      </Box>

      {processingStatus && processingStatus.status === 'completed' && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Требование успешно обработано!
        </Alert>
      )}

      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Все требования" />
        <Tab label="В обработке" />
        <Tab label="Утвержденные" />
      </Tabs>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Идентификатор</TableCell>
              <TableCell>Название</TableCell>
              <TableCell>Категория</TableCell>
              <TableCell>Приоритет</TableCell>
              <TableCell>Статус</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {requirements.map((req) => (
              <TableRow key={req.id}>
                <TableCell>{req.identifier}</TableCell>
                <TableCell>{req.name}</TableCell>
                <TableCell>{req.category || '-'}</TableCell>
                <TableCell>{req.priority || '-'}</TableCell>
                <TableCell>{req.status || 'draft'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog для обработки требования */}
      <Dialog open={processOpen} onClose={() => setProcessOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Обработать входящее требование</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Проект</InputLabel>
            <Select
              value={formData.project_id}
              onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
              label="Проект"
            >
              <MenuItem value="">Выберите проект</MenuItem>
              {projects.map((p) => (
                <MenuItem key={p.id} value={p.id}>
                  {p.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Неформализованное требование"
            margin="normal"
            multiline
            rows={6}
            value={formData.informal_text}
            onChange={(e) => setFormData({ ...formData, informal_text: e.target.value })}
            placeholder="Введите требование в свободной форме..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProcessOpen(false)}>Отмена</Button>
          <Button onClick={handleProcess} variant="contained">
            Обработать
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Requirements

