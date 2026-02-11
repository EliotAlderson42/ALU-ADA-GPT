import os
 


def create_dc1(body = dict):
    data = {}
    for key, value in body.items():
        if key == "moduleA":
            for cle, valeur in value.items():
                data[cle] = valeur
        elif key == "moduleB":
            for cle, valeur in value.items():
                data[cle] = valeur
        elif key == "moduleC":
            for cle, valeur in value.items():
                data[cle] = valeur
        elif key == "moduleD":
            for cle, valeur in value.items():
                data[cle] = valeur
        elif key == "moduleE":
            for cle, valeur in value.items():
                data[cle] = valeur
        elif key == "moduleF":
            for cle, valeur in value.items():
                data[cle] = valeur
        elif key == "moduleG":
            for cle, valeur in value.items():
                data[cle] = valeur
        else:
            print(f"Clé invalide: {key}")
    
    print(data)
        
    