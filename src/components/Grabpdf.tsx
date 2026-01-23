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
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        style={{
          border: dragging ? "2px dashed rgb(242, 0, 255)" : "2px dashed #9d9d9d",
          padding: "100px",
          textAlign: "center",
          marginBottom: "20px",
          borderRadius: "100px",
          cursor: "pointer",
        }}
      >
        {dragging ? "Déposez le PDF ici !" : "Glissez-déposez votre PDF"}
        <input
          type="file"
          accept="application/pdf"
          onChange={handleChange}
          style={{ display: "none" }}
          id="fileInput"
        />
      </div>
      <label htmlFor="fileInput" style={{ cursor: "pointer", color: "blue" }}>
        Ou cliquez ici pour sélectionner un PDF
      </label>
    </div>
  );
}

export default PdfUploaderDragDrop;