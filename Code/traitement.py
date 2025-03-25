from vrt_creation import create_vrt_from_folder
from decoupage import crop_vrt
import os
import shutil

def supprimer_contenu_dossier(dossier):
    """ Supprime tout le contenu d'un dossier sans supprimer le dossier lui-même """
    if os.path.exists(dossier):
        for fichier in os.listdir(dossier):
            chemin_fichier = os.path.join(dossier, fichier)
            if os.path.isfile(chemin_fichier) or os.path.islink(chemin_fichier):
                os.remove(chemin_fichier)
            elif os.path.isdir(chemin_fichier):
                shutil.rmtree(chemin_fichier)

def traitement(image_path, output_folder, dalles):
    """ Effectue le traitement en supprimant le contenu du dossier de sortie avant de commencer """
    
    # Suppression du contenu du dossier de sortie
    #supprimer_contenu_dossier(output_folder)
    #print(f"Le dossier {output_folder} a été vidé.")

    # Création du VRT à partir du dossier de dalles
    output_vrt = os.path.join(output_folder, "dalle.vrt")
    create_vrt_from_folder(dalles, output_vrt)  # Assurer que cette fonction bloque jusqu'à la fin

    # Découper l'image en fonction du VRT généré
    output_crop_png = os.path.join(output_folder, "crop.png")
    output_crop_jpg = os.path.join(output_folder, "crop.jp2")
    png_link=crop_vrt(image_path, output_vrt, output_crop_jpg, output_crop_png)  # Idem ici, s'assurer que c'est bloquant

    return png_link

if __name__ == "__main__":
    traitement("test.jpg", "output_vrai", "dalles_pleiades/ORT_2019090439472760_LA93")
