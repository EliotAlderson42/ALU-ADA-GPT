import os
from docxtpl import DocxTemplate
 


def create_dc1(body = dict):
    data = {}
    for key, value in body.items():

        if key == "moduleA":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        elif key == "moduleB":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        elif key == "moduleC":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        elif key == "moduleD":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        elif key == "moduleE":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        elif key == "moduleF":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        elif key == "moduleG":
            for cle, valeur in value.items():
                if isinstance(valeur, dict):
                    for cle, valeur in valeur.items():
                        data[cle] = valeur
                else:
                    data[cle] = valeur
        else:
            print(f"Clé invalide: {key}")
    
    for key, value in data.items():
        print(f"{key}: {value}\n")
    return data

def fill_dc1(data = dict):
    base = os.path.dirname(__file__)
    template_path = os.path.join(base, "Documents", "DC1.docx")
    output_dir = os.path.join(base, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dc1.docx")
    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)
        
    