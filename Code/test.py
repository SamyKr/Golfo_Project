import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt

# Chemins des données
data_dir = 'D:/image_basse_def'
annotations_file = 'D:/image_basse_def_annotée/annotations.json'
model_path = 'coastline_model_epoch10.pth'  # Chemin vers le modèle entraîné
image_path = 'test_basse_def.jpg'  # Chemin vers l'image de test

# Charger les annotations (si nécessaire pour la visualisation)
with open(annotations_file, 'r') as f:
    annotations = json.load(f)

# Vérifier si le JSON est une liste et le convertir en dictionnaire
if isinstance(annotations, list):
    annotations = {item["image"]: {"points": item["points"]} for item in annotations}

# Dataset personnalisé
class CoastlineDataset(Dataset):
    def __init__(self, image_dir, annotations, transform=None, max_points=200):
        self.image_dir = image_dir
        self.transform = transform
        self.annotations = annotations
        self.max_points = max_points  # Nombre max de points pour le padding
        self.image_files = list(self.annotations.keys())

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = os.path.join(self.image_dir, self.image_files[idx])
        image = cv2.imread(img_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)  # Convertir en objet PIL

        if self.transform:
            image = self.transform(image)

        # Récupérer les points d'annotation
        points = np.array(self.annotations[self.image_files[idx]]['points'], dtype=np.float32)

        # Normaliser les coordonnées (optionnel : diviser par la taille de l'image)
        w, h = image.size
        points = points / [w, h]

        # Padding pour uniformiser la taille
        if len(points) < self.max_points:
            pad_size = self.max_points - len(points)
            points = np.pad(points, ((0, pad_size), (0, 0)), mode='constant', constant_values=-1)
        else:
            points = points[:self.max_points]  # Tronquer si trop de points

        return image, torch.tensor(points)

# Transformations pour garder la résolution d'origine
data_transforms = transforms.Compose([
    transforms.ToTensor(),  # Convertir en tenseur PyTorch
])

# Modèle de régression basé sur ResNet18
class CoastlineRegressor(nn.Module):
    def __init__(self, num_points=200):
        super(CoastlineRegressor, self).__init__()
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.resnet.fc = nn.Linear(512, num_points * 2)  # Prédit (x,y) pour chaque point

    def forward(self, x):
        return self.resnet(x)

# Initialiser le modèle
model = CoastlineRegressor()
device = torch.device("cpu")
model.to(device)

# Charger les poids du modèle entraîné
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

# Préparer l'image de test
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image = Image.fromarray(image)  # Convertir en objet PIL
image_tensor = data_transforms(image).unsqueeze(0)  # Ajouter une dimension batch

# Passer l'image à travers le modèle
with torch.no_grad():
    outputs = model(image_tensor)

# Post-traitement des sorties
outputs = outputs.view(-1, 2)  # Résultats de forme (num_points, 2)
w, h = image.size  # Taille de l'image d'origine
outputs = outputs * torch.tensor([w, h])  # Dénormaliser les coordonnées

# Vérifier que les points sont dans les limites de l'image
outputs[:, 0] = torch.clamp(outputs[:, 0], 0, w)
outputs[:, 1] = torch.clamp(outputs[:, 1], 0, h)

# Afficher l'image avec les points prédits
plt.imshow(image)
valid_points = outputs[torch.all(outputs != -1, dim=1)]  # Ignorer les points pad
plt.scatter(valid_points[:, 0], valid_points[:, 1], c='red', s=20, label='Points Prédits')

plt.show()