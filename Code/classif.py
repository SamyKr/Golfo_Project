import os
import cv2
import os
import cv2
import numpy as np
import time
from skimage.io import imread, imsave, imshow, show
from skimage.measure import find_contours
from skimage.morphology import binary_erosion
from skimage.color import label2rgb, rgb2hsv
from skimage.segmentation import slic


def convert_arrays_to_tuples(contours):
    return [(int(x), int(y)) for x, y in map(tuple, contours)]



def appel_process_image(image_path, outpout_folder, image_type):
    if image_type == 'roche':
        return convert_arrays_to_tuples(process_image_roche(image_path, outpout_folder, n_segments=650000, compactness=10, window_size=3))
    elif image_type == 'sable':
        return convert_arrays_to_tuples(process_image_sable(image_path, outpout_folder, n_segments=15000, compactness=10, window_size=3))
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

def process_image_sable(image_path, outpout_folder, n_segments=15000, compactness=10, window_size=3, blue_area_threshold=300):
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

    boundary = (blue_mask.astype(int) - brown_mask.astype(int)) + (brown_mask.astype(int) - other_mask)

    print("Recherche des contours...")
    contours = find_contours(boundary, level=0)
    contours = remove_closed_contours(contours)
    
    print(f"{len(contours)} contours trouvés.")
    
    blue_contours = []
    
    # Trouver les grandes zones bleues basées sur l'aire des contours
    for contour in contours:
        # Convertir les coordonnées des contours en int32 (pour OpenCV)
        contour_int = np.array(contour, dtype=np.int32)
        
        # Vérifier si l'aire du contour dépasse le seuil
        area = cv2.contourArea(contour_int)
        if area > blue_area_threshold:  # Seuil de l'aire pour considérer une zone comme grande
            blue_contours.append(contour_int)
    
    if blue_contours:
        print(f"{len(blue_contours)} grandes zones bleues détectées.")
        
        # Sélectionner le contour le plus bas
        lowest_contour = None
        lowest_y = -1

        for contour in blue_contours:
            # Trouver le point le plus bas du contour
            min_y = np.min(contour[:, 0])  # Récupère le minimum des y pour chaque contour
            if min_y > lowest_y:
                lowest_y = min_y
                lowest_contour = contour

        # Dessiner le contour le plus bas
        image_with_contours = image.copy()
        
        # Inverser l'ordre des coordonnées (ligne, colonne) -> (x, y)
        contour_swapped = lowest_contour[:, [1, 0]]  # Inverse (colonne, ligne) -> (x, y)
        
        # Dessiner le contour dans l'ordre normal en tant que segment ouvert
        cv2.polylines(image_with_contours, [contour_swapped], isClosed=False, color=(255, 0, 0), thickness=3)
        # Dessiner le contour dans l'ordre inversé pour l'effet aller-retour
        cv2.polylines(image_with_contours, [contour_swapped[::-1]], isClosed=False, color=(255, 0, 0), thickness=3)
        
        output_image = os.path.join(outpout_folder, os.path.basename(image_path))
        output_image = os.path.basename(image_path)
        outpout_image= os.path.join(outpout_folder, output_image)

        imsave(outpout_image, image_with_contours)
    
    else:
        print("Aucune grande zone bleue détectée.")
    
    end_time = time.time()
    execution_time = (end_time - start_time) / 60
    print(f"Temps d'exécution du traitement: {execution_time:.4f} minutes.")
    
    return contour_swapped

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




if __name__== "__main__":

   

    a=appel_process_image("test_basse_def.jpg", 'test', 'sable')
    print(a)

