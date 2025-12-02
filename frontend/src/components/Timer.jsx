// Timer.jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, LinearProgress, Alert } from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

const Timer = ({ initialTime, onTimeUp }) => {
  const [timeLeft, setTimeLeft] = useState(initialTime);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          onTimeUp();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, onTimeUp]);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const progress = (timeLeft / initialTime) * 100;

  // Couleurs selon le temps restant
  let color = 'primary';
  if (timeLeft < 300) color = 'warning'; // 5 minutes
  if (timeLeft < 60) color = 'error';    // 1 minute

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <AccessTimeIcon color={color} />
        <Typography variant="h6" color={color}>
          {minutes}:{seconds < 10 ? '0' : ''}{seconds}
        </Typography>
      </Box>
      
      <LinearProgress 
        variant="determinate" 
        value={progress} 
        color={color}
        sx={{ height: 8, borderRadius: 4 }}
      />
      
      {timeLeft < 300 && (
        <Alert severity="warning" sx={{ mt: 1 }}>
          Temps restant: {minutes} minute{minutes > 1 ? 's' : ''}
        </Alert>
      )}
    </Box>
  );
};

export default Timer;