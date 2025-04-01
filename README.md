# 🌍 GOLFO - Manuel d'Utilisation 🚀

## ✨ Qu'est-ce que GOLFO ?
GOLFO est une application web permettant d'extraire automatiquement le trait de côte à partir d'images obliques. Elle utilise des techniques avancées de vision par ordinateur et de géomatique pour fournir des résultats précis et exploitables dans un SIG.

## ✅ Prérequis
Avant de commencer, assurez-vous d'avoir les éléments suivants :

- 🛠️ Un environnement Anaconda installé sur votre machine.
- 📦 Les dépendances nécessaires pour exécuter l'application (stockées dans `requirements.yaml`).

##  Clonage du dépôt
Avant toute installation, commencez par cloner le dépôt GitHub :

```bash
    git clone https://github.com/SamyKr/Golfo_Project.git
    cd GOLFO
```

## 💅 Installation

1. ** Téléchargez et extrayez** l'application sur votre ordinateur si cela n'est pas encore fait.
2. ** Ouvrez un terminal ou une invite de commande** dans le dossier contenant le fichier `app.py`.
3. ** Installez les dépendances** en exécutant :
   ```bash
   conda env create -f requirements.yaml
   conda activate golfo
   ```
4. **▶ Lancez** l'application avec la commande suivante :
   ```bash
   python app.py
   ```
5.  Une fois l'application démarrée, une invite de commande affichera un lien.
6. ⏳ **Patientez** quelques secondes et la page web s'ouvrira automatiquement.
7. *(💡 Optionnel)* Vous pouvez reconfigurer le fichier `application.bat` à l'aide d'un éditeur de texte pour rediriger vers votre `python.exe` et le chemin d'accès à `app.py` afin de lancer en un seul clic.

## 🛠️ Modules Principaux

L'application GOLFO repose sur plusieurs bibliothèques essentielles :

- 🖥️ **Flask** : Utilisé pour créer l'interface web et gérer les interactions avec l'utilisateur.
- 🌍 **OpenCV** : Utilisé pour le traitement d'image, notamment la détection et l'alignement des images.
- 📸 **Scikit-Image** : Fournit des outils avancés pour l'analyse et la transformation des images. Utilisé pour les algorithmes de détection du trait de côte.
- 📊 **GDAL** : Utilisé pour manipuler les fichiers géospatiaux, notamment pour lire et écrire des fichiers raster et vecteur.
- 🔍 **PyASIFT** : Implémentation de l'algorithme ASIFT pour la détection robuste des points d'intérêt dans les images. Code disponible ici : [PyASIFT](https://github.com/Mars-Rover-Localization/PyASIFT.git). L'algorithme ASIFT a été développé par **Zhou, Lang, Zhang, Zhitai et Wang, Hongliang**.

## 🌟 Configuration des données utilisateur

Avant de lancer le traitement, vous devez fournir trois informations essentielles :

1. 📷 **Insertion des images**
   - Les images doivent contenir des coordonnées dans leurs métadonnées (EXIF).
   - Ces coordonnées doivent être au format WGS84, qui est la norme attendue.

2. 🗂️ **Chemin vers le dossier des dalles**
   - L'application est optimisée pour les dalles Pléiades fournies.
   - Si vous utilisez vos propres dalles, assurez-vous que le chemin n'est pas trop long et ne contient pas de caractères spéciaux.
   - En cas de doute, placez vos dalles à la racine du logiciel en renommant le dossier `dalles`.

3. 💽 **Chemin vers le dossier de sortie**

## 🚀 Lancement du Traitement

Une fois ces étapes complétées, chargez vos données. Si aucune erreur n'est détectée, vos images apparaîtront.

Pour chaque image, vous pouvez choisir entre deux options de traitement :

- 🦟 **Roche** : Algorithme plus long (environ 30 minutes par image). Utilise la segmentation SLIC couplée à une classification colorimétrique.
- 🏖️ **Sable** : Algorithme plus rapide (environ 40 secondes par image). Utilise l'algorithme K-means pour la classification des pixels.

## 📊 Résultats en Sortie

À la fin du traitement, plusieurs fichiers seront générés dans le dossier de sortie :

- 🌏 `crop.png` : Portion de dalle Pléiades correspondant à l'image traitée.
- 🔄 `transformed_image.png` : Superposition entre la photo oblique et l'image aérienne.
- 🔴 `trait_de_cote.png` : Image avec le trait de côte identifié en rouge.
- 📌 `keypoints.txt` : Points d'intérêt entre les images (utilisable pour d'autres analyses).
- 🌍 **Dossier shapefile** : Contient un fichier shapefile utilisable dans un SIG.
- 📷 **Nom_Image_Classif** : Image oblique avec le trait de côte identifié.

## 🎨 Édition d'Image

L'éditeur d'images est accessible via le bouton **"Éditeur d'images"** dans la barre de navigation.

🎨 **Fonctionnalités disponibles** :

-  Modifier la luminosité
-  Modifier la transparence
-  Modifier l'inclinaison horizontale et verticale
-  Déplacer l'image
-  Agrandir ou réduire la taille de l'image
-  Modifier le calque de l'image

## 🔍 Outil de Vérification de la Qualité

Un outil `tools.py` permet de vérifier la qualité des superpositions.

- ✅ **Si la qualité est suffisante**, cliquez sur **Save**.
- ❌ **Si la qualité est insatisfaisante**, cliquez sur **Pass**.

Un nouveau dossier contenant les images filtrées sera alors généré.

## 📧 Contact et Support

Si vous rencontrez des problèmes ou avez des suggestions, contactez-nous : samy.kerri@icloud.com, sar.for@hotmail.fr, abigaelle.lagneaux@gmail.com, coline.roy13@gmail.com

Bonne navigation et bon traitement de vos images obliques ! 🚀✨

