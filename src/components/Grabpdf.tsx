import {useState} from "react";

function Grabpdf() {
    const [file, setFile] = useState<File | null>(null);

    //Pour 
    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0){
            setFile(e.dataTransfer.files[0])
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
    };

    const handleUpload = () => {
        if (!file) return;
        alert('Prèt à envoyer : ${file.name}');
    };

    return (
        <main>
            <h2>Importer un PDF</h2>
             <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        style={{
          border: "2px dashed #4ade80",
          padding: "40px",
          textAlign: "center",
          marginBottom: "20px",
          cursor: "pointer",
        }}
      >
        {file ? `Fichier sélectionné : ${file.name}` : "Glissez un PDF ici"}
      </div>

      <button onClick={handleUpload}>Envoyer</button>
    </main>
  );

}

export default Grabpdf