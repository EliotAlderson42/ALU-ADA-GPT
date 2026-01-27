import { useState, DragEvent } from "react";

type PdfUploaderProps = {
  onFileSelected: (file: File) => void;
};

function PdfUploaderDragDrop({ onFileSelected }: PdfUploaderProps) {
  const [dragging, setDragging] = useState(false);

  // Quand on dépose le fichier
  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);

    if (!e.dataTransfer.files || e.dataTransfer.files.length === 0) return;

    const file = e.dataTransfer.files[0];

    if (file.type !== "application/pdf") {
      alert("Veuillez sélectionner un PDF");
      return;
    }

    onFileSelected(file);
  };

  // Quand on commence à drag
  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  // Quand on quitte la zone de drop
  const handleDragLeave = () => {
    setDragging(false);
  };

  // Upload classique en cliquant
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const file = e.target.files[0];
    if (file.type !== "application/pdf") {
      alert("Veuillez sélectionner un PDF");
      return;
    }

    onFileSelected(file);
  };

  return (
    <div className="uploader">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`dropzone ${dragging ? "dropzone--active" : ""}`}
      >
        <p className="dropzone-title">
          {dragging ? "Déposez le PDF ici !" : "Glissez-déposez votre PDF"}
        </p>
        <p className="dropzone-subtitle">
          Le fichier reste sur ton ordinateur, seul le contenu est analysé.
        </p>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleChange}
          className="dropzone-input"
          id="fileInput"
        />
        <label htmlFor="fileInput" className="dropzone-button">
          Ou cliquez pour choisir un PDF
        </label>
      </div>
    </div>
  );
}

export default PdfUploaderDragDrop;