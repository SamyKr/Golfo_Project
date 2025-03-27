import os
import cv2
import numpy as np
import time
from skimage.io import imread, imsave
from skimage.measure import find_contours
from skimage.morphology import binary_erosion, binary_closing, binary_opening, disk
from skimage.color import label2rgb, rgb2hsv
from skimage.segmentation import slic
from sklearn.cluster import KMeans
from shapely.geometry import LineString


def convert_arrays_to_tuples(contours):
    return [(int(x), int(y)) for x, y in map(tuple, contours)]



def appel_process_image(image_path, output_folder, image_type):
    if image_type == 'roche':
        return convert_arrays_to_tuples(process_image_roche(image_path, output_folder, n_segments=650000, compactness=10, window_size=3))
    elif image_type == 'sable':
        return convert_arrays_to_tuples(kmeans(image_path, output_folder, n_clusters=2, n_init=15, init='k-means++', max_iter=300, tol=1e-4, min_contour_length=1000))
    else:
        print("Le type de l'image a été mal renseigné")
        return None

def detect_blue(image):
    """Détecte uniquement les pixels de bleu et crée un masque binaire."""
    hsv = rgb2hsv(image)
    
    blue_mask = (hsv[:, :, 0] >= 0.5) & (hsv[:, :, 0] <= 0.7)
    blue_mask &= (hsv[:, :, 1] > 0.2)
    blue_mask &= (hsv[:, :, 2] > 0.2)
    
    return binary_erosion(blue_mask)

def detect_brown(image):
    """Détecte uniquement les pixels de couleur marron et crée un masque binaire."""
    hsv = rgb2hsv(image)
    
    brown_mask = (hsv[:, :, 0] >= 0.05) & (hsv[:, :, 0] <= 0.12)
    brown_mask &= (hsv[:, :, 1] < 0.4)
    brown_mask &= (hsv[:, :, 2] > 0.2) & (hsv[:, :, 2] < 0.6)
    
    return brown_mask

def remove_closed_contours(contours, threshold=5):
    filtered_contours = []
    for contour in contours:
        if np.linalg.norm(contour[0] - contour[-1]) > threshold:
            filtered_contours.append(contour)
    return filtered_contours

def process_image_roche(image_path, outpout_folder, n_segments=650000, compactness=10, window_size=3):
    print("Démarrage du processus de segmentation de l'image...")
    
    start_time = time.time()
    
    image = imread(image_path)
    print(f"Image chargée: {image_path}")
    
    print("Applique SLIC pour la segmentation des superpixels...")
    segments = slic(image, n_segments=n_segments, compactness=compactness, start_label=1)
    
    print("Segmentation effectuée, traitement de l'image...")
    segmented_image = label2rgb(segments, image, kind='avg')
    
    print("Détection des zones bleues et marron...")
    blue_mask = detect_blue(segmented_image)
    brown_mask = detect_brown(segmented_image)

    other_mask = ~(blue_mask | brown_mask)

    boundary = (blue_mask.astype(int) - brown_mask.astype(int)) + (brown_mask.astype(int) - other_mask.astype(int))

    print("Recherche des contours...")
    contours = find_contours(boundary, level=0)
    contours = remove_closed_contours(contours)
    
    print(f"{len(contours)} contours trouvés.")

    if contours:
        largest_contour = max(contours, key=len)
        print("Le plus grand contour trouvé, dessin de la polyligne...")

        # Sauvegarder l'image résultante avec les contours dessinés
        image_with_contour = image.copy()
        for contour in largest_contour:
            image_with_contour[int(contour[0]), int(contour[1])] = [255, 0, 0]  # Dessiner en rouge
            
        output_image = os.path.basename(image_path)
        outpout_image= os.path.join(outpout_folder, output_image)

        imsave(outpout_image, image_with_contour)
    
    if image_with_contour is None:
        print("Aucun contour trouvé, retourner une image vide ou l'originale.")

    end_time = time.time()
    execution_time = (end_time - start_time) / 60
    print(f"Temps d'exécution du traitement: {execution_time:.4f} minutes.")
    
    return contours

def polygon_to_open_linestring(polygon):
    coords = list(polygon.exterior.coords)
    return LineString(coords[:-1])  # Supprimer le dernier point pour ouvrir la ligne

def calculate_contour_length(contour):
    # Calculer la longueur d'un contour (distance entre les points successifs)
    length = 0
    for i in range(1, len(contour)):
        length += np.linalg.norm(contour[i] - contour[i - 1])
    return length

def kmeans(image_path, output_folder, n_clusters=2, n_init=15, init='k-means++', max_iter=300, tol=1e-4, min_contour_length=1000):
    # Charger l'image
    image = imread(image_path)

    # Redimensionner l'image pour l'algorithme de clustering
    pixels = image.reshape(-1, 3)

    # Appliquer K-Means avec les paramètres spécifiés
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=n_init, init=init, max_iter=max_iter, tol=tol)
    labels = kmeans.fit_predict(pixels).reshape(image.shape[:2])

    # Filtrer pour réduire le bruit
    filtered_labels = binary_closing(labels, disk(10))
    filtered_labels = binary_opening(filtered_labels, disk(3))

    # Seuil de taille pour les petites régions
    new_labels = filtered_labels.copy()

    # Détection des contours
    contours = find_contours(new_labels, level=0.5)

    # Appliquer le seuil de longueur (contours de longueur > 200 pixels)
    valid_contours = []
    for contour in contours:
        contour_length = calculate_contour_length(contour)
        if contour_length >= min_contour_length:
            valid_contours.append(contour)

    # Si plusieurs contours valides existent, garder le plus bas et le plus long
    if len(valid_contours) > 1:
        # Calculer la coordonnée verticale moyenne pour chaque contour (pour choisir le plus bas)
        contour_heights = [np.mean(contour[:, 0]) for contour in valid_contours]
        lowest_contour_index = np.argmax(contour_heights)  # Le contour avec la coordonnée moyenne la plus basse
        valid_contours = [valid_contours[lowest_contour_index]]  # Garde seulement ce contour

    # Affichage de l'image originale avec les contours tracés en rouge
    for contour in valid_contours:
        # Dessiner les contours en rouge
        cv2.drawContours(image, [contour], -1, (0, 0, 255), 2) 
    
    output_image = os.path.basename(image_path)
    outpout_image= os.path.join(output_folder, output_image)
    
    # Sauvegarde de l'image avec les contours dessinés
    imsave(outpout_image, image)

    return valid_contours

if __name__== "__main__":

    a=appel_process_image("test_basse_def.jpg", 'test', 'sable')
    print(a)

