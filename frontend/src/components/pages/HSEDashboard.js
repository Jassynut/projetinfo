"use client"

import { useState } from "react"
import "../styles/Dashboard.css"

const HSEDashboard = () => {
  const [selectedDate, setSelectedDate] = useState({
    day: "",
    month: "",
    year: "",
  })

  const handleDateChange = (e) => {
    const { name, value } = e.target
    setSelectedDate((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="page-container">
      <div className="dashboard-controls">
        <h2>Tableau de bord HSE</h2>
        <div className="date-controls">
          <label>Sélectionner la date :</label>
          <input type="text" name="day" placeholder="JJ" value={selectedDate.day} onChange={handleDateChange} />
          <input type="text" name="month" placeholder="MM" value={selectedDate.month} onChange={handleDateChange} />
          <input type="text" name="year" placeholder="AAAA" value={selectedDate.year} onChange={handleDateChange} />
          <button className="btn-primary">Voir</button>
        </div>
      </div>

      <div className="dashboard-charts">
        <div className="chart-card">
          <h3>Pourcentage de présences</h3>
          <div className="chart-display">
            <div className="percentage">82%</div>
            <p>Taux de participation global</p>
          </div>
        </div>

        <div className="chart-card">
          <h3>Comparaison test initial et test final</h3>
          <div className="comparison-chart">
            <div className="chart-item">
              <label>Test initial</label>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: "64%" }}>
                  64%
                </div>
              </div>
            </div>
            <div className="chart-item">
              <label>Test final</label>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: "89%" }}>
                  89%
                </div>
              </div>
            </div>
            <p>Amélioration globale de 25 points</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HSEDashboard
