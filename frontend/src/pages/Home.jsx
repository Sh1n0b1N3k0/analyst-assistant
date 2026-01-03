import React from 'react'
import { Container, Typography, Grid, Card, CardContent, CardActions, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import {
  Folder,
  Description,
  Psychology,
  Article,
} from '@mui/icons-material'

const Home = () => {
  const navigate = useNavigate()

  const components = [
    {
      title: 'Администратор проекта',
      description: 'Управление проектами разработки систем',
      icon: <Folder sx={{ fontSize: 48 }} />,
      path: '/projects',
      color: '#1976d2',
    },
    {
      title: 'Обработчик требований',
      description: 'Автоматизированный анализ и формализация требований',
      icon: <Description sx={{ fontSize: 48 }} />,
      path: '/requirements',
      color: '#dc004e',
    },
    {
      title: 'База знаний',
      description: 'Граф данных требований и их отношений',
      icon: <Psychology sx={{ fontSize: 48 }} />,
      path: '/knowledge',
      color: '#2e7d32',
    },
    {
      title: 'Генератор спецификаций',
      description: 'Автоматическая генерация различных типов спецификаций',
      icon: <Article sx={{ fontSize: 48 }} />,
      path: '/specifications',
      color: '#ed6c02',
    },
  ]

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Система управления требованиями
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        Комплексная система для управления требованиями к программному обеспечению
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {components.map((component) => (
          <Grid item xs={12} sm={6} md={3} key={component.title}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <div style={{ color: component.color, marginBottom: 16 }}>
                  {component.icon}
                </div>
                <Typography variant="h6" component="h2" gutterBottom>
                  {component.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {component.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  fullWidth
                  onClick={() => navigate(component.path)}
                >
                  Открыть
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}

export default Home

