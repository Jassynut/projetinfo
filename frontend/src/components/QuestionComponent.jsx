// QuestionComponent.jsx
import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography,
  Paper
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const QuestionComponent = ({ question, questionNumber, onAnswer, userAnswer }) => {
  const handleAnswer = (answer) => {
    onAnswer(question.id, answer);
  };

  return (
    <Card sx={{ mb: 3, border: userAnswer !== null ? '2px solid #1976d2' : 'none' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Question {questionNumber} {question.is_mandatory && '(Obligatoire)'}
        </Typography>
        
        <Typography variant="body1" paragraph>
          {question.enonce}
        </Typography>
        
        {question.has_image && question.image_url && (
          <Box sx={{ my: 2, textAlign: 'center' }}>
            <img 
              src={question.image_url} 
              alt="Question illustration"
              style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }}
            />
          </Box>
        )}
        
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant={userAnswer === true ? "contained" : "outlined"}
            color={userAnswer === true ? "success" : "inherit"}
            size="large"
            startIcon={<CheckCircleIcon />}
            onClick={() => handleAnswer(true)}
            sx={{
              minWidth: '150px',
              height: '60px',
              fontSize: '18px',
              backgroundColor: userAnswer === true ? '#4caf50' : 'transparent',
              borderColor: '#4caf50',
              color: userAnswer === true ? 'white' : '#4caf50',
              '&:hover': {
                backgroundColor: userAnswer === true ? '#45a049' : 'rgba(76, 175, 80, 0.1)',
              }
            }}
          >
            VRAI
          </Button>
          
          <Button
            variant={userAnswer === false ? "contained" : "outlined"}
            color={userAnswer === false ? "error" : "inherit"}
            size="large"
            startIcon={<CancelIcon />}
            onClick={() => handleAnswer(false)}
            sx={{
              minWidth: '150px',
              height: '60px',
              fontSize: '18px',
              backgroundColor: userAnswer === false ? '#f44336' : 'transparent',
              borderColor: '#f44336',
              color: userAnswer === false ? 'white' : '#f44336',
              '&:hover': {
                backgroundColor: userAnswer === false ? '#d32f2f' : 'rgba(244, 67, 54, 0.1)',
              }
            }}
          >
            FAUX
          </Button>
        </Box>
        
        {userAnswer !== null && (
          <Paper sx={{ 
            mt: 2, 
            p: 1, 
            bgcolor: 'grey.50',
            display: 'flex', 
            alignItems: 'center',
            gap: 1
          }}>
            <Typography variant="body2" color="text.secondary">
              Votre réponse: <strong>{userAnswer ? 'VRAI' : 'FAUX'}</strong>
            </Typography>
            <Button 
              size="small" 
              onClick={() => handleAnswer(null)}
              sx={{ ml: 'auto' }}
            >
              Changer
            </Button>
          </Paper>
        )}
      </CardContent>
    </Card>
  );
};

export default QuestionComponent;