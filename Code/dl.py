import os
import cv2
import json
import torch
from torchvision import transforms, datasets
from torch.utils.data import DataLoader, Dataset
from PIL import Image

# Chemins vers vos données
data_dir = 'D:/train'
output_dir = 'D:/image_basse_def_annotée'
annotations_file = os.path.join(output_dir, 'annotations.json')

# Créer le répertoire de sortie s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

# Transformations pour la data augmentation
data_transforms = {
    'train': transforms.Compose([   
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
    ]),
}

# Classe personnalisée pour le dataset
class CoastlineDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = os.path.join(self.image_dir, self.image_files[idx])
        image = cv2.imread(img_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)  # Convertir en objet PIL

        if self.transform:
            image = self.transform(image)

        return image, img_name

# Fonction pour dessiner le trait de côte
def draw_coastline(image, points):
    for point in points:
        cv2.circle(image, tuple(point), 2, (0, 255, 0), -1)
    return image

# Charger les annotations existantes
def load_annotations():
    if os.path.exists(annotations_file):
        with open(annotations_file, 'r') as f:
            return json.load(f)
    return []

# Sauvegarder les annotations dans un fichier JSON
def save_annotations(annotations):
    with open(annotations_file, 'w') as f:
        json.dump(annotations, f)

# Charger les annotations existantes
annotations = load_annotations()

# Créer un dictionnaire pour un accès rapide aux annotations par image
existing_annotations = {annotation['image']: annotation for annotation in annotations}

# Charger le dataset
dataset = CoastlineDataset(data_dir, transform=data_transforms['train'])
dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

# Boucle pour dessiner le trait de côte sur chaque image
for images, img_names in dataloader:
    image_name = os.path.basename(img_names[0])

    # Si l'image a déjà été annotée, continuez avec ses annotations
    points = existing_annotations.get(image_name, {}).get('points', [])

    image = images[0].permute(1, 2, 0).numpy()  # Convertir le tenseur en tableau numpy
    image = (image * 255).astype('uint8')  # Convertir en uint8
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convertir en BGR pour OpenCV

    # Dessiner les points existants si l'image a déjà des annotations
    image = draw_coastline(image, points)

    # Créer une fenêtre redimensionnable
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.imshow('Image', image)

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append([x, y])
            cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
            cv2.imshow('Image', image)

    cv2.setMouseCallback('Image', click_event)

    # Attendre que l'utilisateur ferme la fenêtre (lorsque 'ESC' est pressé ou la fenêtre est fermée)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # 27 est la touche 'ESC' pour fermer la fenêtre
            break

    cv2.destroyAllWindows()

    # Sauvegarder les annotations
    annotation = {
        'image': image_name,
        'points': points
    }

    # Si l'image a déjà des annotations, les mettre à jour
    if image_name in existing_annotations:
        existing_annotations[image_name]['points'] = points
    else:
        existing_annotations[image_name] = annotation

    # Sauvegarder l'image annotée
    output_image_path = os.path.join(output_dir, image_name)
    cv2.imwrite(output_image_path, image)

    # Sauvegarder les annotations à chaque image
    save_annotations(list(existing_annotations.values()))

print('Annotations sauvegardées avec succès.')
