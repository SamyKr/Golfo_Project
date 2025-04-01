########################################################################################################################
##################################################### Importations #####################################################
########################################################################################################################
import os
import numpy as np
from skimage.io import imread, imsave
from skimage.measure import find_contours
from skimage.morphology import binary_erosion, binary_closing, binary_opening, disk
from skimage.color import label2rgb, rgb2hsv
from skimage.segmentation import slic
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


########################################################################################################################
####################################################### Fonctions ######################################################
########################################################################################################################

####################################################### Générales ######################################################
def convert_arrays_to_tuples(contours):
    '''
    Cette fonction convertie une liste de liste en une liste de tuple
    
    Entrée :
        - contours : list
    
    Sortie :
        - list
    '''
    
    return [(int(x), int(y)) for x, y in map(tuple, contours)]


def appel_process_image(image_path, output_folder, image_type):
    '''
    Cette fonction renvoie le bon algorithme de classification en fonction du type de littoral renseigné
    
    Entrée :
        - image path : string
        - output_folder : string
        - image_type : string
    
    Sortie :
        - list
    '''
    
    if image_type == 'roche':
        return convert_arrays_to_tuples(process_image_roche(image_path, output_folder, n_segments=50000, compactness=10, window_size=3))
    elif image_type == 'sable':
        return convert_arrays_to_tuples(kmeans(image_path, output_folder, n_clusters=2, n_init=15, init='k-means++', max_iter=300, tol=1e-4, min_contour_length=1000))
    else:
        print("Le type de l'image a été mal renseigné")
        return None
    
################################################### Littoral rocheux ###################################################

def detect_blue(image):
    '''
    Cette fonction detecte les zones bleues et forme un masque binaire
    
    Entrée :
        - image : ndarray
        
    Sortie :
        - ndarray
    '''
    
    hsv = rgb2hsv(image)
    
    blue_mask = (hsv[:, :, 0] >= 0.5) & (hsv[:, :, 0] <= 0.7)
    blue_mask &= (hsv[:, :, 1] > 0.2)
    blue_mask &= (hsv[:, :, 2] > 0.2)
    
    return binary_erosion(blue_mask)

def detect_brown(image):
    '''
    Cette fonction detecte les zones marron et forme un masque binaire
    
    Entrée :
        - image : ndarray
        
    Sortie :
        - ndarray
    '''
    
    hsv = rgb2hsv(image)
    
    brown_mask = (hsv[:, :, 0] >= 0.05) & (hsv[:, :, 0] <= 0.12)
    brown_mask &= (hsv[:, :, 1] < 0.4)
    brown_mask &= (hsv[:, :, 2] > 0.2) & (hsv[:, :, 2] < 0.6)
    
    return brown_mask

def remove_closed_contours(contours, threshold=5):
    '''
    Cette fonction permet de filtrer les contours fermés dans une liste de contours
    
    Entrée :
        - contours : list
        
    Sortie :
        - filtered_contours : list
    '''
    
    filtered_contours = []
    for contour in contours:
        if np.linalg.norm(contour[0] - contour[-1]) > threshold:
            filtered_contours.append(contour)
    return filtered_contours

def process_image_roche(image_path, output_folder, n_segments=5000, compactness=10, window_size=3):
    '''
    Cette fonction permet de trouver la ligne de côte pour un littoral rocheux
    
    Entrée :
        - image_path : string
        - output_folder : string
    
    Sortie :
        - valid_contours : list
    '''
    image = imread(image_path)
    
    # Applique SLIC pour la segmentation des superpixels
    segments = slic(image, n_segments=n_segments, compactness=compactness, start_label=1)
    
    # Traitement de l'image
    segmented_image = label2rgb(segments, image, kind='avg')
    
    # Détection des zones bleues et marron
    blue_mask = detect_blue(segmented_image)
    brown_mask = detect_brown(segmented_image)

    other_mask = ~(blue_mask | brown_mask)

    boundary = (blue_mask.astype(int) - brown_mask.astype(int)) + (brown_mask.astype(int) - other_mask.astype(int))

    # Recherche des contours
    contours = find_contours(boundary, level=0)
    contours = remove_closed_contours(contours)

    if contours:
        # On trouve le plus grand contour
        largest_contour = max(contours, key=len)

        # Sauvegarder l'image avec les contours dessinés
        image_with_contour = image.copy()
        for contour in largest_contour:
            image_with_contour[int(contour[0]), int(contour[1])] = [255, 0, 0]
        
        # Nom et chemin du fichier de sortie
        output_image = os.path.basename(image_path)
        outpout_image= os.path.join(output_folder, output_image)

        # Enregistrement de l'image
        imsave(outpout_image, image_with_contour)
    # On retourne la ligne de côte
    return contours[0]

################################################## Littoral sablonneux ##################################################

def calculate_contour_length(contour):
    '''
    Cette fonction calcule la longueur d'un contour

    Entrée :
        - contour : ndarray

    Sortie :
        - float
    '''
    return np.sum(np.sqrt(np.sum(np.diff(contour, axis=0) ** 2, axis=1)))

def kmeans(image_path, output_folder, n_clusters=2, n_init=15, init='k-means++', max_iter=300, tol=1e-4, min_contour_length=1000):
    '''
    Cette fonction permet de trouver la ligne de côte pour un littoral sablonneux.

    Entrée :
        - image_path : string (chemin de l'image)
        - output_folder : string (dossier où enregistrer l'image classifiée)

    Sortie :
        - valid_contours_pixels : liste de tuples (x, y) des pixels constituant le contour détecté
    '''
     
    # Charger l'image
    image = imread(image_path)

    # Appliquer K-Means (sans changer la taille de l’image)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=n_init, init=init, max_iter=max_iter, tol=tol)
    labels = kmeans.fit_predict(image.reshape((-1, 3))).reshape(image.shape[:2])

    # Filtrage du bruit
    filtered_labels = binary_closing(labels, disk(10))
    filtered_labels = binary_opening(filtered_labels, disk(3))

    # Détection des contours
    contours = find_contours(filtered_labels, level=0.5)

    # Filtrer les contours trop courts
    valid_contours = [contour for contour in contours if calculate_contour_length(contour) >= min_contour_length]

    # Garder seulement le contour le plus bas
    if len(valid_contours) > 1:
        contour_heights = [np.mean(contour[:, 0]) for contour in valid_contours]
        lowest_contour_index = np.argmax(contour_heights)
        valid_contours = [valid_contours[lowest_contour_index]]

    # Convertir en indices de pixels entiers (coordonnées x, y)
    valid_contours_pixels = [(int(point[1]), int(point[0])) for point in valid_contours[0]]

    # Affichage du résultat
    plt.imshow(image)  
    for contour in valid_contours:
        plt.plot(contour[:, 1], contour[:, 0], color='red', linewidth=2)  
    plt.axis('off')

    # Génération du nom du fichier de sortie
    name, ext = os.path.splitext(os.path.basename(image_path))  
    output_image_name = f"{name}_classif{ext}"  
    output_image_path = os.path.join(output_folder, output_image_name)

    # Enregistrement du résultat
    plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)  
    plt.close()

    return valid_contours_pixels  # Retourne la liste des pixels du contour détecté


if __name__== "__main__":

    appel_process_image("test_basse_def.jpg", 'test', 'sable')
  
