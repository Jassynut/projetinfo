// TestPage.jsx
import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Button, 
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import axios from 'axios';
import QuestionComponent from './QuestionComponent';
import Timer from './Timer';

const TestPage = ({ testId, attemptId }) => {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeLeft, setTimeLeft] = useState(null);
  const [submitDialog, setSubmitDialog] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Récupérer les questions
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await axios.get(`/api/hse/tests/version/${testId}/`);
        if (response.data.success) {
          setQuestions(response.data.test.questions);
          setTimeLeft(response.data.test.duration_minutes * 60); // en secondes
        }
      } catch (err) {
        setError('Erreur lors du chargement du test');
      } finally {
        setLoading(false);
      }
    };
    
    fetchQuestions();
  }, [testId]);

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const response = await axios.post(`/api/hse/test-attempts/${attemptId}/submit/`, {
        answers: answers
      });
      
      if (response.data.success) {
        // Rediriger vers la page de résultats
        window.location.href = `/test/results/${attemptId}/`;
      }
    } catch (err) {
      setError('Erreur lors de la soumission');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTimeUp = () => {
    handleSubmit();
  };

  if (loading) {
    return <LinearProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  const currentQuestionData = questions[currentQuestion];
  const answeredCount = Object.keys(answers).length;
  const progress = (answeredCount / questions.length) * 100;

  return (
    <Container maxWidth="md">
      {/* En-tête du test */}
      <Box sx={{ 
        position: 'sticky', 
        top: 0, 
        zIndex: 1000, 
        bgcolor: 'white', 
        py: 2, 
        borderBottom: '1px solid #ddd'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">
            Test HSE - Version {testId}
          </Typography>
          
          <Timer 
            initialTime={timeLeft} 
            onTimeUp={handleTimeUp}
          />
        </Box>
        
        <Box sx={{ mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2" sx={{ mt: 1 }}>
            {answeredCount} / {questions.length} questions répondues
          </Typography>
        </Box>
      </Box>

      {/* Navigation par étapes */}
      <Stepper activeStep={currentQuestion} alternativeLabel sx={{ mt: 3, mb: 3 }}>
        {questions.map((q, index) => (
          <Step key={q.id}>
            <StepLabel 
              onClick={() => setCurrentQuestion(index)}
              sx={{ cursor: 'pointer' }}
            >
              Q{index + 1}
              {answers[q.id] !== undefined && ' ✓'}
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Question courante */}
      {currentQuestionData && (
        <QuestionComponent
          question={currentQuestionData}
          questionNumber={currentQuestion + 1}
          onAnswer={handleAnswer}
          userAnswer={answers[currentQuestionData.id]}
        />
      )}

      {/* Navigation */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3, mb: 4 }}>
        <Button
          variant="outlined"
          onClick={handlePrev}
          disabled={currentQuestion === 0}
        >
          ← Précédent
        </Button>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            color="warning"
            onClick={() => setSubmitDialog(true)}
          >
            Soumettre le test
          </Button>
          
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={currentQuestion === questions.length - 1}
          >
            Suivant →
          </Button>
        </Box>
      </Box>

      {/* Dialog de confirmation */}
      <Dialog open={submitDialog} onClose={() => setSubmitDialog(false)}>
        <DialogTitle>Soumettre le test</DialogTitle>
        <DialogContent>
          <Typography>
            Vous avez répondu à {answeredCount} sur {questions.length} questions.
            {answeredCount < questions.length && (
              <strong> Certaines questions n'ont pas de réponse!</strong>
            )}
          </Typography>
          <Typography sx={{ mt: 2 }}>
            Êtes-vous sûr de vouloir soumettre vos réponses?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubmitDialog(false)}>Annuler</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary"
            disabled={submitting}
          >
            {submitting ? 'Soumission...' : 'Oui, soumettre'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Composant Timer */}
      {timeLeft && (
        <Timer 
          initialTime={timeLeft} 
          onTimeUp={handleTimeUp}
        />
      )}
    </Container>
  );
};

export default TestPage;