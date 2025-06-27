import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')

# Exemple d'utilisation
if __name__ == "__main__":
    chemin_image = "wtf-is-this-image-from-ive-seen-it-around-but-theres-never-v0-co23vp2uiw591.webp"  # Remplace avec le chemin de ton image
    base64_str = image_to_base64(chemin_image)
    
    # Affichage ou sauvegarde
    print(base64_str)

    # Sauvegarde dans un fichier texte (facultatif)
    with open("image_base64.txt", "w") as output_file:
        output_file.write(base64_str)
