import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Button,
  Paper,
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Code,
} from '@mui/material'
import { Article, Generate } from '@mui/icons-material'
import { specificationsAPI, requirementsAPI } from '../services/api'

const Specifications = () => {
  const [requirements, setRequirements] = useState([])
  const [templates, setTemplates] = useState({})
  const [open, setOpen] = useState(false)
  const [spec, setSpec] = useState(null)
  const [formData, setFormData] = useState({
    requirement_id: '',
    spec_type: 'user_story',
  })

  useEffect(() => {
    loadRequirements()
    loadTemplates()
  }, [])

  const loadRequirements = async () => {
    try {
      const response = await requirementsAPI.list()
      setRequirements(response.data)
    } catch (error) {
      console.error('Error loading requirements:', error)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await specificationsAPI.listTemplates()
      setTemplates(response.data)
    } catch (error) {
      console.error('Error loading templates:', error)
    }
  }

  const handleGenerate = async () => {
    try {
      const response = await specificationsAPI.generate(formData)
      setSpec(response.data)
      setOpen(true)
    } catch (error) {
      console.error('Error generating specification:', error)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Генератор спецификаций
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Автоматическая генерация различных типов спецификаций
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel>Требование</InputLabel>
            <Select
              value={formData.requirement_id}
              onChange={(e) => setFormData({ ...formData, requirement_id: e.target.value })}
            >
              {requirements.map((req) => (
                <MenuItem key={req.id} value={req.id}>
                  {req.identifier} - {req.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Тип спецификации</InputLabel>
            <Select
              value={formData.spec_type}
              onChange={(e) => setFormData({ ...formData, spec_type: e.target.value })}
            >
              {Object.entries(templates).map(([key, value]) => (
                <MenuItem key={key} value={key}>
                  {value.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={<Generate />}
            onClick={handleGenerate}
            disabled={!formData.requirement_id}
          >
            Сгенерировать спецификацию
          </Button>
        </Box>
      </Paper>

      {/* Dialog для отображения спецификации */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Article sx={{ mr: 1, verticalAlign: 'middle' }} />
          Сгенерированная спецификация
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Тип: {spec?.spec_type}
            </Typography>
            <Code
              component="pre"
              sx={{
                p: 2,
                bgcolor: 'grey.100',
                borderRadius: 1,
                overflow: 'auto',
                maxHeight: 400,
              }}
            >
              {spec?.content}
            </Code>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Закрыть</Button>
          <Button variant="contained">Сохранить</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Specifications

