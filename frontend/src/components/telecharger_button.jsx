import axios from "axios";

function DownloadCertificateButton({ userId, testId }) {
  const handleDownload = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/authentication/download-certificate/${userId}/${testId}/`,
        {
          responseType: 'blob' // important pour télécharger le fichier
        }
      );

      // Créer un lien pour télécharger le fichier
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificat_${userId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

    } catch (error) {
      console.error("Erreur téléchargement certificat:", error);
    }
  };

  return <button onClick={handleDownload}>Télécharger Certificat</button>;
}

export default DownloadCertificateButton;
