import os
import cv2
import numpy as np
import time
from skimage.io import imread, imsave
from sklearn.cluster import DBSCAN
from skimage.measure import find_contours
from skimage.morphology import binary_erosion
from skimage.color import label2rgb, rgb2hsv
from skimage.segmentation import slic

def appel_process_image(image_path, outpout_folder, image_type) :
    if image_type == 'roche' :
        return process_image(image_path, outpout_folder, n_segments=650000, compactness=10, window_size=3)
    elif image_type == 'sable' :
        return process_image(image_path, outpout_folder, n_segments=15000, compactness=10, window_size=3)
    else :
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

def process_image(image_path, outpout_folder, n_segments=650000, compactness=10, window_size=3):
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

        imsave(output_image, image_with_contour)
    
    if image_with_contour is None:
        print("Aucun contour trouvé, retourner une image vide ou l'originale.")

    end_time = time.time()
    execution_time = (end_time - start_time) / 60
    print(f"Temps d'exécution du traitement: {execution_time:.4f} minutes.")
    
    return image_with_contour, contours