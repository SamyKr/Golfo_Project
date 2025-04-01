from vrt_creation import create_vrt_from_folder
from decoupage import crop_vrt
import os
import shutil

def supprimer_contenu_dossier(dossier):
    """
    Supprime tout le contenu d'un dossier sans supprimer le dossier lui-même.

    Paramètres :
        dossier (str): Le chemin du dossier dont le contenu doit être supprimé.

    Retour :
        Aucun.
    """
    if os.path.exists(dossier):
        for fichier in os.listdir(dossier):
            chemin_fichier = os.path.join(dossier, fichier)
            if os.path.isfile(chemin_fichier) or os.path.islink(chemin_fichier):
                os.remove(chemin_fichier)
            elif os.path.isdir(chemin_fichier):
                shutil.rmtree(chemin_fichier)

def traitement(image_path, output_folder, dalles):
    """
    Effectue le traitement d'une image en supprimant le contenu du dossier de sortie, 
    créant un VRT à partir d'un dossier de dalles, puis découpant l'orthophoto 
    en fonction du VRT généré.

    Paramètres :
        image_path (str): Le chemin de l'image à traiter (orthophoto).
        output_folder (str): Le dossier où les fichiers résultants seront enregistrés.
        dalles (str): Le chemin du dossier contenant les dalles à utiliser pour créer le VRT.

    Retour :
        str: Le chemin vers le fichier PNG découpé résultant (link vers l'image).
    """
    # Création du VRT à partir du dossier de dalles
    output_vrt = os.path.join(output_folder, "dalle.vrt")
    create_vrt_from_folder(dalles, output_vrt)  # Assurer que cette fonction bloque jusqu'à la fin

    # Découper l'image en fonction du VRT généré
    output_crop_png = os.path.join(output_folder, "crop.png")
    output_crop_jpg = os.path.join(output_folder, "crop.jp2")
    png_link = crop_vrt(image_path, output_vrt, output_crop_jpg, output_crop_png)  # Idem ici, s'assurer que c'est bloquant

    return png_link

if __name__ == "__main__":
    # Exemple d'exécution de la fonction de traitement avec une image, un dossier de sortie et un dossier de dalles
    traitement("image_hd.jpg", "output", "D:\dalles_ensg\dalles")
