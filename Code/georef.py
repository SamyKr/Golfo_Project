import cv2
import numpy as np
import os
import shutil
import geopandas as gpd
from classif import appel_process_image
from osgeo import gdal
from shapely.geometry import LineString
import pandas as pd
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'PyASIFT')))
from PyASIFT.asift import asift_main


def extract_match_points(df):
    """
    Lit un fichier CSV et extrait les colonnes x1, y1 pour pts_target et x2, y2 pour pts_query.
    
    :param file: Fichier CSV sous forme de chemin ou d'objet fichier
    :return: Tuple (pts_target, pts_query)
    """
    
    # Vérifier que les colonnes existent en ignorant les espaces ou caractères cachés
    df.columns = df.columns.str.strip()
    
    required_columns = {'x1', 'y1', 'x2', 'y2'}
    missing_columns = required_columns - set(df.columns)
    
    if missing_columns:
        raise KeyError(f"Colonnes manquantes dans le fichier CSV : {missing_columns}")
    
    pts_target = df[['x1', 'y1']].values.astype(np.float32)
    pts_query = df[['x2', 'y2']].values.astype(np.float32)

    print("Points cibles (target) :", pts_target)
    print("Points requête (query) :", pts_query)
    
    return pts_target, pts_query


def pixel_to_geo(x, y, geo_transform):
    """Convertit des coordonnées en pixels vers des coordonnées géographiques (terrain)."""
    x_geo = geo_transform[0] + x * geo_transform[1] + y * geo_transform[2]
    y_geo = geo_transform[3] + x * geo_transform[4] + y * geo_transform[5]
    return x_geo, y_geo


def apply_homography(pts_target, pts_query, query_img_path, target_img_path, output_path, type):
    """Applique une transformation homographique et génère une image et un shapefile géoréférencé."""
    
    # Calcul de la matrice d'homographie
    H, _ = cv2.findHomography(pts_query, pts_target)
    print("Matrice d'homographie:", H)

    # Charger les images
    query_img = cv2.imread(query_img_path, cv2.IMREAD_UNCHANGED)
    target_img = cv2.imread(target_img_path, cv2.IMREAD_UNCHANGED)
    height, width, _ = target_img.shape
    
    # Ajouter un canal alpha si absent
    if query_img.shape[2] == 3:
        query_img = cv2.cvtColor(query_img, cv2.COLOR_BGR2BGRA)
    
    # Créer une image vierge avec transparence
    transformed_image = np.zeros((height, width, 4), dtype=np.uint8)
    
    # Appliquer la transformation avec transparence
    warped_query = cv2.warpPerspective(query_img, H, (width, height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    
    # Copier les pixels non transparents de warped_query vers transformed_image
    mask = warped_query[:, :, 3] > 0
    transformed_image[mask] = warped_query[mask]
    
    # Sauvegarde de l'image transformée
    output_img_path = os.path.join(output_path, "output_transformed_image.png")
    cv2.imwrite(output_img_path, transformed_image)
    print(f"Image enregistrée sous : {output_img_path}")
    
    # Copier le fichier .aux.xml pour conserver le géoréférencement
    aux_file_path = target_img_path + ".aux.xml"
    output_aux_path = os.path.join(output_path, "output_transformed_image.png.aux.xml")
    if os.path.exists(aux_file_path):
        shutil.copy(aux_file_path, output_aux_path)
        print(f"Fichier de géoréférencement copié vers : {output_aux_path}")
    else:
        print("Aucun fichier .aux.xml trouvé pour l'image cible.")
    
    # Charger les infos géospatiales
    ds = gdal.Open(target_img_path)
    geo_transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    
    # Conversion des coordonnées en pixels vers coordonnées géographiques
    points = appel_process_image(query_img_path, output_path, type)
    points_array = np.array(points, dtype=np.float32)
    points_transformed = cv2.perspectiveTransform(points_array[None, :, :], H)[0]
    geo_points = [pixel_to_geo(pt[0], pt[1], geo_transform) for pt in points_transformed]
    
    # Création du GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=[LineString(geo_points) for x, y in geo_points], crs=projection)
    
    # Création du dossier pour le shapefile
    shapefile_directory = os.path.join(output_path, "shapefile")
    os.makedirs(shapefile_directory, exist_ok=True)
    shapefile_path = os.path.join(shapefile_directory, "points_transformed_geo.shp")
    gdf.to_file(shapefile_path)
    
    print("Coordonnées géographiques des points enregistrées :")
    print(gdf)
    print(f"Shapefile enregistré sous : {shapefile_path}")


if __name__ == "__main__":
    query_img_path = "output_flask/image_1/test_basse_def_2.png"
    target_img_path = "output_flask/image_1/crop.png"
    output_path = "output"
    
    points_match = asift_main(query_img_path, target_img_path, "sift-flann", output_path)
    pts_target, pts_query = extract_match_points(points_match)
    
    apply_homography(pts_target, pts_query, query_img_path, target_img_path, output_path, type="sable")
