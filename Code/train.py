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

# Chemins des données
data_dir = 'D:/train'
annotations_file = 'D:/image_basse_def_annotée/annotations.json'

# Charger les annotations
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

        # Debugging: Check the type of image and its size attribute
        print(f"Image type: {type(image)}")
        size = image.size
        print(f"Image size: {size}")

        if self.transform:
            image = self.transform(image)

        # Récupérer les points d'annotation
        points = np.array(self.annotations[self.image_files[idx]]['points'], dtype=np.float32)

        # Normaliser les coordonnées (optionnel : diviser par la taille de l'image)
        w, h = size  # Utiliser la variable size
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

# Créer le dataset et le dataloader
dataset = CoastlineDataset(data_dir, annotations, transform=data_transforms)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=0)  # Ajuste batch_size si nécessaire

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

# Configuration de l'entraînement
criterion = nn.SmoothL1Loss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
num_epochs = 10

# Entraînement
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, points in dataloader:
        images, points = images.to(device), points.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, points.view(outputs.shape))  # Ajuster la forme des tensors
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(dataloader)}")

    # Sauvegarde du modèle
    torch.save(model.state_dict(), f'coastline_model_epoch{epoch+1}.pth')

print("Entraînement terminé !")
