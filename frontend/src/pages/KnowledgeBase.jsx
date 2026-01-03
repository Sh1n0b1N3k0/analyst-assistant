import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Button,
  Paper,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material'
import { Psychology, CheckCircle, Warning } from '@mui/icons-material'
import { knowledgeAPI, requirementsAPI } from '../services/api'

const KnowledgeBase = () => {
  const [selectedRequirement, setSelectedRequirement] = useState(null)
  const [duplicates, setDuplicates] = useState([])
  const [conflicts, setConflicts] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [requirements, setRequirements] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadRequirements()
  }, [])

  const loadRequirements = async () => {
    try {
      const response = await requirementsAPI.list()
      setRequirements(response.data)
    } catch (error) {
      console.error('Error loading requirements:', error)
    }
  }

  const handleAnalyze = async (requirementId) => {
    setLoading(true)
    setSelectedRequirement(requirementId)
    
    try {
      const [dupRes, confRes, recRes] = await Promise.all([
        knowledgeAPI.checkDuplicates(requirementId),
        knowledgeAPI.checkConflicts(requirementId),
        knowledgeAPI.getRecommendations(requirementId),
      ])
      
      setDuplicates(dupRes.data)
      setConflicts(confRes.data)
      setRecommendations(recRes.data)
    } catch (error) {
      console.error('Error analyzing requirement:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        База знаний требований
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Анализ требований на дубликаты, противоречия и получение рекомендаций
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            Требования
          </Typography>
          <List>
            {requirements.map((req) => (
              <ListItem
                key={req.id}
                button
                onClick={() => handleAnalyze(req.identifier)}
                selected={selectedRequirement === req.identifier}
              >
                <ListItemText
                  primary={req.identifier}
                  secondary={req.name}
                />
              </ListItem>
            ))}
          </List>
        </Paper>

        <Paper sx={{ p: 2, flex: 2 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : selectedRequirement ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                Анализ требования: {selectedRequirement}
              </Typography>

              {duplicates.is_duplicate && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Найдены дубликаты! Похожесть: {duplicates.similarity_score}
                </Alert>
              )}

              {conflicts.has_conflicts && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  Обнаружены противоречия!
                </Alert>
              )}

              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Рекомендации
                </Typography>
                <List>
                  {recommendations.recommendations?.map((rec, idx) => (
                    <ListItem key={idx}>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Psychology sx={{ fontSize: 64, color: 'text.secondary' }} />
              <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                Выберите требование для анализа
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  )
}

export default KnowledgeBase

