import cv2
import numpy as np
import os
import shutil
import geopandas as gpd
from classif import appel_process_image
from osgeo import gdal
from shapely.geometry import LineString
import pandas as pd

def extract_match_points(file):
    """
    Lit un fichier CSV et extrait les colonnes x1, y1 pour pts_target et x2, y2 pour pts_query.
    
    :param file: Fichier CSV sous forme de chemin ou d'objet fichier
    :return: Tuple (pts_target, pts_query)
    """
    df = pd.read_csv(file)
    
    # Vérifier que les colonnes existent en ignorant les espaces ou caractères cachés
    df.columns = df.columns.str.strip()
    
    required_columns = {'x1', 'y1', 'x2', 'y2'}
    missing_columns = required_columns - set(df.columns)
    
    if missing_columns:
        raise KeyError(f"Colonnes manquantes dans le fichier CSV : {missing_columns}")
    
    pts_target = df[['x1', 'y1']].values.astype(np.float32)
    pts_query = df[['x2', 'y2']].values.astype(np.float32)
    
    return pts_target, pts_query


def pixel_to_geo(x, y, geo_transform):
    """Convertit des coordonnées en pixels vers des coordonnées géographiques (terrain)."""
    x_geo = geo_transform[0] + x * geo_transform[1] + y * geo_transform[2]
    y_geo = geo_transform[3] + x * geo_transform[4] + y * geo_transform[5]
    return x_geo, y_geo

def apply_homography(pts_target, pts_query, query_img_path, target_img_path, output_path,type):
    """Applique une transformation homographique et génère une image et un shapefile géoréférencé."""
    
    # Calcul de la matrice d'homographie
    H, _ = cv2.findHomography(pts_query, pts_target)
    print("Matrice d'homographie:", H)

    # Charger les images
    query_img = cv2.imread(query_img_path)
    target_img = cv2.imread(target_img_path)
    height, width, _ = target_img.shape
    warped_query = cv2.warpPerspective(query_img, H, (width, height))

    points =appel_process_image(query_img_path,output_path,type)
    # Points sélectionnés par l'utilisateur
    # points = [
    # (7.564516129032057, 413.0483870967739),
    # (136.59677419354838, 396.91935483870975),
    # (251.11290322580643, 372.7258064516129),
    # (355.95161290322574, 364.6612903225804),
    # (454.3387096774194, 325.95161290322585),
    # (504.3387096774193, 329.1774193548388),
    # (507.5645161290322, 380.7903225806451),
    # (499.4999999999999, 429.17741935483866),
    # (470.4677419354838, 464.66129032258067),
    # (449.5, 517.8870967741937),
    # (510.7903225806451, 532.4032258064517),
    # (589.8225806451612, 537.241935483871),
    # (586.5967741935483, 638.8548387096774),
    # (597.8870967741935, 701.758064516129),
    # (694.6612903225806, 679.1774193548385),
    # (784.983870967742, 638.8548387096774),
    # (834.9838709677418, 559.8225806451612),
    # (833.3709677419355, 517.8870967741937),
    # (888.2096774193548, 500.14516129032233),
    # (962.4032258064516, 537.241935483871),
    # (962.4032258064516, 537.241935483871),
    # (1033.3709677419356, 540.4677419354839),
    # (1068.8548387096776, 466.27419354838685),
    # (1054.3387096774195, 425.95161290322585),
    # (1096.274193548387, 366.2741935483871),
    # (1147.8870967741934, 374.33870967741905),
    # (1172.08064516129, 382.4032258064516)
#]
    #points = enregistrer_points(query_img_path)
    points_array = np.array(points, dtype=np.float32)
    points_transformed = cv2.perspectiveTransform(points_array[None, :, :], H)[0]

    # Fusionner les images
    output_img = cv2.addWeighted(target_img, 1, warped_query, 1, 0)
    
    
    
    # Sauvegarde de l'image transformée
    output_img_path = os.path.join(output_path, "output_transformed_image.png")
    cv2.imwrite(output_img_path, output_img)
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

    pts_target,pts_query=extract_match_points("output_flask\data_matches.csv")

    query_img_path = "output_flask/test_basse_def.png"
    target_img_path = "output_flask/crop.png"
    output_path = "output_flask"

    apply_homography(pts_target, pts_query, query_img_path, target_img_path, output_path)