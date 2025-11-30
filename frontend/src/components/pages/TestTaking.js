"use client"

import { useState, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import "../styles/Pages.css"

function TestTaking() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [timeLeft, setTimeLeft] = useState(600) // 10 minutes
  const [score, setScore] = useState(0)
  const navigate = useNavigate()
  const location = useLocation()
  const cin = location.state?.cin || ""
  const version = location.state?.version || ""

  const questions = [
    {
      id: 1,
      text: "Question 1 : texte de la question ici.",
      image: null,
      correctAnswer: "yes",
    },
    {
      id: 2,
      text: "Question 2 : exemple de question HSE.",
      image: null,
      correctAnswer: "no",
    },
    {
      id: 3,
      text: "Question 3 : une autre question.",
      image: null,
      correctAnswer: "yes",
    },
    // ... 21 questions total
  ]

  // Timer effect
  useEffect(() => {
    if (timeLeft <= 0) {
      handleFinishTest()
      return
    }
    const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
    return () => clearTimeout(timer)
  }, [timeLeft])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const handleAnswer = (answer) => {
    const newAnswers = { ...answers, [currentQuestion]: answer }
    setAnswers(newAnswers)

    // Calculate score
    if (answer === questions[currentQuestion].correctAnswer) {
      setScore(score + 1)
    }
  }

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleFinishTest = () => {
    navigate("/test-success", {
      state: { score, totalQuestions: questions.length, cin },
    })
  }

  const question = questions[currentQuestion]

  return (
    <div className="page-container">
      <div className="test-header">
        <h1>Test HSE</h1>
        <div className="timer">{formatTime(timeLeft)}</div>
      </div>

      <div className="test-card">
        <div className="question-counter">
          Question {currentQuestion + 1} / {questions.length}
        </div>

        {question.image && <div className="image-placeholder">Image ici (à remplacer)</div>}

        <div className="question-text">{question.text}</div>

        <div className="answer-buttons">
          <button className="btn btn-success" onClick={() => handleAnswer("yes")}>
            ✓ Oui
          </button>
          <button className="btn btn-danger" onClick={() => handleAnswer("no")}>
            ✕ Non
          </button>
        </div>

        <div className="navigation-buttons">
          <button className="btn btn-secondary" onClick={handlePrevious} disabled={currentQuestion === 0}>
            Suivant
          </button>
          <button className="btn btn-primary" onClick={handleNext} disabled={currentQuestion === questions.length - 1}>
            Terminer le test
          </button>
        </div>
      </div>
    </div>
  )
}

export default TestTaking
