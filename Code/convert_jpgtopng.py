from PIL import Image
import os

def convert_jpgtopng(image_jpg, dossier_sortie, compression_level=9):
    """convertir_jpg_en_png_avec_compression
    Convertit une image JPG en PNG avec compression et l'enregistre dans le dossier de sortie.

    :param image_jpg: Chemin du fichier JPG en entrée
    :param dossier_sortie: Dossier où enregistrer le fichier PNG
    :param compression_level: Niveau de compression pour l'image PNG (0 = aucun, 9 = maximum)
    :return: Chemin du fichier PNG créé
    """
    print("⏳ Conversion en attente... ⏳")
    # Vérifie et crée le dossier de sortie si besoin
    os.makedirs(dossier_sortie, exist_ok=True)

    # Ouvre l'image JPG
    img = Image.open(image_jpg)

    # Construit le nom du fichier de sortie en remplaçant .jpg par .png
    nom_fichier_png = os.path.splitext(os.path.basename(image_jpg))[0] + ".png"
    chemin_png = os.path.join(dossier_sortie, nom_fichier_png)

    # Sauvegarde l'image PNG avec compression
    img.save(chemin_png, "PNG", optimize=False, compress_level=compression_level)

    print(f"✅ Conversion terminée : {chemin_png}")
    return chemin_png


if __name__ =="__main__":
    convert_jpgtopng("test_basse_def_3.jpg", "output/")
