import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material'
import {
  Home,
  Folder,
  Description,
  Psychology,
  Article,
} from '@mui/icons-material'

const Navbar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Главная', icon: <Home /> },
    { path: '/projects', label: 'Проекты', icon: <Folder /> },
    { path: '/requirements', label: 'Требования', icon: <Description /> },
    { path: '/knowledge', label: 'База знаний', icon: <Psychology /> },
    { path: '/specifications', label: 'Спецификации', icon: <Article /> },
  ]

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Система управления требованиями
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              component={Link}
              to={item.path}
              color="inherit"
              startIcon={item.icon}
              variant={location.pathname === item.path ? 'outlined' : 'text'}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar

