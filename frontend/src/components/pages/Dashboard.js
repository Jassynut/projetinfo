import { Link } from "react-router-dom"
import "../styles/stats.css"

const stats = () => {
  const features = [
    {
      title: "Base de données",
      description: "Gérer et organiser les données",
      icon: "🗄️",
      link: "/gestion-donnees",
    },
    {
      title: "Tableau de bord",
      description: "Visualiser les statistiques et rapports",
      icon: "📊",
      link: "/tableau-bord",
    },
    {
      title: "Gestion des questionnaires",
      description: "Ajouter, modifier ou supprimer des questions",
      icon: "❓",
      link: "/gestion-questionnaires",
    },
    {
      title: "Commencer le test",
      description: "Lancer une formation HSE",
      icon: "📋",
      link: "/versions-test",
    },
    {
      title: "Générer un certificat",
      description: "Créer et télécharger les certificats",
      icon: "📜",
      link: "/certificats",
    },
  ]

  return (
    <div className="stats-container">
      <div className="stats-intro">
        <p>
          Ce portail vous permet de gérer les <strong>formations HSE</strong>, les <strong>tests</strong>, et les{" "}
          <strong>certificats</strong> de vos collaborateurs en toute simplicité.
        </p>
      </div>

      <div className="stats-grid">
        {features.map((feature, index) => (
          <Link key={index} to={feature.link} className="feature-card">
            <div className="feature-icon">{feature.icon}</div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default stats
