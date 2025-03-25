import json
from PIL import Image
from PIL.ExifTags import TAGS
import pyproj


# Fonction pour convertir DMS (degrés, minutes, secondes) en décimal
def dms_to_decimal(dms):
    return dms[0] + (dms[1] / 60.0) + (dms[2] / 3600.0)

# Fonction pour extraire les données GPS EXIF
def get_gps_info(exif_data):
    gps_info = {}
    
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == "GPSInfo":
            gps_info = value  # Récupère les données GPS sans modification
    
    return gps_info

# Fonction pour obtenir les coordonnées GPS et l'altitude depuis une image
def extract_gps_from_image(image_path):
    # Charger l'image
    img = Image.open(image_path)

    # Extraire les données EXIF
    exif_data = img._getexif()

    # Dictionnaire pour stocker les coordonnées et l'altitude
    gps_dict = {}

    # Vérifier si des données EXIF existent
    if exif_data:
        gps_data = get_gps_info(exif_data)
        if gps_data:
            # Extraire latitude, longitude et altitude
            lat_dms = gps_data.get(2)
            lon_dms = gps_data.get(4)
            altitude = gps_data.get(6)  # Altitude est généralement sous la clé 6

            if lat_dms and lon_dms and altitude:
                # Convertir DMS en décimal
                latitude = dms_to_decimal(lat_dms)
                longitude = dms_to_decimal(lon_dms)

                # Ajuster le signe en fonction de la direction N/S ou E/O
                if gps_data.get(3) == 'S':  # Si latitude est sud, on inverse le signe
                    latitude = -latitude
                if gps_data.get(3) == 'W':  # Si longitude est ouest, on inverse le signe
                    longitude = -longitude


                wgs84 = pyproj.CRS("EPSG:4326")  # WGS 84
                lambert93 = pyproj.CRS("EPSG:2154")  # Lambert 93

                # Convertir en coordonnées Lambert 93
                transformer = pyproj.Transformer.from_crs(wgs84, lambert93, always_xy=True)
                x, y = transformer.transform(longitude, latitude)

                # Ajouter les données dans le dictionnaire
                gps_dict['Longitude'] = longitude
                gps_dict['Latitude'] = latitude
                gps_dict['Altitude'] = altitude
                gps_dict['X_Lambert'] = x
                gps_dict['Y_Lambert'] = y

                return gps_dict  # Renvoie le dictionnaire avec les données GPS

            else:
                return {"error": "Données GPS ou altitude incomplètes."}
        else:
            return {"error": "Pas de données GPS dans l'image."}
    else:
        return {"error": "Pas de métadonnées EXIF dans l'image."}
    

if __name__ == "__main__":
    # Exemple d'utilisation
    image_path = "Photos_HD/028-de-123_PNM-Golfe-du-Lion_261019.jpg"
    gps_data = extract_gps_from_image(image_path)
    print(gps_data)