import os
from osgeo import gdal

def create_vrt_from_folder(folder_path, output_vrt="D:/Golfo_Project/output_trql/fichier.vrt"):
    """
    Crée un fichier VRT à partir de toutes les images raster dans un dossier donné.

    :param folder_path: Chemin du dossier contenant les images.
    :param output_vrt: Nom ou chemin du fichier VRT de sortie.
    """
    # Vérifier si le dossier existe
    if not os.path.exists(folder_path):
        print("Le dossier spécifié n'existe pas.")
        return
    
    # Rechercher les fichiers raster (tif, tiff, jp2)
    raster_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith((".tif", ".tiff", ".jp2"))]

    if not raster_files:
        print("Aucune image raster trouvée dans le dossier.")
        return
    
    # Vérifier si le dossier de sortie existe
    output_folder = os.path.dirname(output_vrt)
    if not os.path.exists(output_folder):
        print(f"Le dossier de sortie {output_folder} n'existe pas, création...")
        os.makedirs(output_folder)

    # Créer le fichier VRT
    try:
        vrt_options = gdal.BuildVRTOptions(resolution='highest')  # Ajuster les options selon les besoins
        gdal.BuildVRT(output_vrt, raster_files, options=vrt_options)
        print(f"Fichier VRT créé : {output_vrt}")
    except Exception as e:
        print(f"Erreur lors de la création du fichier VRT : {str(e)}")


if __name__=="__main__":
    create_vrt_from_folder("dalles_pleiades\8bits\ORT_2019090439472760_LA93", "D:/Golfo_Project/output_trql/2019098bit.vrt")