########################################################################################################################
##################################################### Importations #####################################################
########################################################################################################################

from osgeo import gdal
import os
import gps_image as gi

gdal.UseExceptions()

def crop_vrt(image_path, vrt_path, output_jp2, output_png, width=2000, height=2000, offset_x=200):
    # Vérification si le fichier image existe
    if not os.path.exists(image_path):
        print(f"❌ L'image spécifiée n'existe pas : {image_path}")
        return  # Arrêt de la fonction si l'image n'existe pas
    
    # Vérification si le fichier VRT existe
    if not os.path.exists(vrt_path):
        print(f"❌ Le fichier VRT spécifié n'existe pas : {vrt_path}")
        return  # Arrêt de la fonction si le fichier VRT n'existe pas
    
    try:
        # Extraction des données GPS de l'image
        gps_data = gi.extract_gps_from_image(image_path)
        
        # Vérification si les données GPS ont été extraites avec succès
        if not gps_data:
            print("❌ Aucune donnée GPS trouvée dans l'image.")
            return  # Arrêt si aucune donnée GPS n'est trouvée
        
        # Calcul des coordonnées GPS avec un décalage en longitude (offset)
        center_lon = gps_data['X_Lambert'] - offset_x
        center_lat = gps_data['Y_Lambert']

        # Affichage des coordonnées GPS après application du décalage
        print(f"📍 Coordonnées GPS extraites (après offset) : Latitude {center_lat}, Longitude {center_lon}")

        # Définition des limites de la zone à rognée (crop)
        xmin = center_lon - width
        xmax = center_lon
        ymin = center_lat - (height / 2)
        ymax = center_lat + (height / 2)

        # Définition des options pour le format JP2 (compression)
        warp_options_jp2 = gdal.WarpOptions(
            format="JP2OpenJPEG",  # Format de sortie JP2
            outputBounds=[xmin, ymin, xmax, ymax],  # Limites de la zone à rognée
            outputType=gdal.GDT_Byte,  # Type de données de sortie
            xRes=1,  # Résolution en x
            yRes=1,  # Résolution en y
            warpMemoryLimit=500,  # Limite de mémoire pour le warp
            creationOptions=[  # Options spécifiques à la création du fichier JP2
                "QUALITY=90",  # Qualité de compression
                "REVERSIBLE=YES",  # Compression réversible
                "BlockXSIZE=512", 
                "BlockYSIZE=512"   
            ]
        )

        # Définition des options pour le format PNG
        warp_options_png = gdal.WarpOptions(
            format="PNG",  # Format de sortie PNG
            outputBounds=[xmin, ymin, xmax, ymax],  # Limites de la zone à rognée
            outputType=gdal.GDT_Byte,  # Type de données de sortie
            xRes=1,  # Résolution en x
            yRes=1   # Résolution en y
        )

        # Création du dossier de sortie si nécessaire
        output_dir = os.path.dirname(output_jp2)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # Création du dossier si inexistant

        # Application de la fonction GDAL pour créer le fichier JP2
        gdal.Warp(destNameOrDestDS=output_jp2, srcDSOrSrcDSTab=vrt_path, options=warp_options_jp2)
        print(f"✅ Fichier JP2 compressé créé avec succès : {output_jp2}")

        # Application de la fonction GDAL pour créer le fichier PNG
        gdal.Warp(destNameOrDestDS=output_png, srcDSOrSrcDSTab=vrt_path, options=warp_options_png)
        print(f"✅ Fichier PNG créé avec succès : {output_png}")

    except Exception as e:
        # Gestion des erreurs
        print(f"❌ Erreur lors du traitement : {str(e)}")
    
    # Retourne le chemin du fichier PNG créé
    return output_png


# exemple
if __name__ == "__main__":
    image_file = "test.jpg"
    vrt_file = "output/fichier_vrt3.vrt"
    output_jp2 = "output/sortie344.jp2"
    output_png = "output/sortie344pn.png"

    crop_vrt(image_file, vrt_file, output_jp2, output_png)
