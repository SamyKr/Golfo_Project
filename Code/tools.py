import os
import shutil
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np
import cv2
import sys
import tkinter as tk
from tkinter import filedialog

# Fonction pour ouvrir une boîte de dialogue et sélectionner un dossier
def select_folder(title):
    """Ouvre une boîte de dialogue pour sélectionner un dossier."""
    root = tk.Tk()  
    root.withdraw()  # Cache la fenêtre principale Tkinter
    folder = filedialog.askdirectory(title=title)  # Ouvre la boîte de dialogue pour sélectionner un dossier
    return folder  # Retourne le chemin du dossier sélectionné

# Fonction pour traiter les sous-dossiers dans le dossier d'entrée
def process_folders(input_dir, output_dir):
    # Liste les sous-dossiers dans le dossier d'entrée
    subdirs = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    for subdir in subdirs:
        subdir_path = os.path.join(input_dir, subdir)  # Chemin du sous-dossier
        crop_path = os.path.join(subdir_path, "crop.png")  # Chemin pour l'image de "crop"
        transformed_path = os.path.join(subdir_path, "output_transformed_image.png")  # Chemin pour l'image transformée
        
        # Si l'une des images n'existe pas, on passe au sous-dossier suivant
        if not os.path.exists(crop_path) or not os.path.exists(transformed_path):
            continue
        
        # Charger les images (crop et transformée)
        img1 = cv2.imread(crop_path, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(transformed_path, cv2.IMREAD_UNCHANGED)
        
        # Si l'une des images ne peut pas être chargée, on passe au sous-dossier suivant
        if img1 is None or img2 is None:
            continue
        
        # Conversion des images BGR (OpenCV) en RGB (pour matplotlib)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        
        # Création de la figure pour l'affichage des images avec matplotlib
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.canvas.manager.full_screen_toggle()  # Passe la fenêtre en plein écran
        plt.subplots_adjust(bottom=0.3)  # Ajuste l'espacement du bas
        ax.axis('off')  # Cache les axes de l'image
        
        # Affichage des images (avec alpha pour l'image transformée)
        im1 = ax.imshow(img1)
        im2 = ax.imshow(img2, alpha=0.5)  # L'image transformée est semi-transparente
        
        # Fonction pour mettre à jour l'opacité de l'image transformée
        def update_opacity(val):
            im2.set_alpha(val)  # Change l'alpha (opacité)
            fig.canvas.draw_idle()  # Redessine la figure avec la nouvelle opacité
        
        # Ajout d'un slider pour contrôler l'opacité de l'image transformée
        ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])  # Position du slider
        slider = widgets.Slider(ax_slider, 'Opacity', 0.0, 1.0, valinit=0.5)  # Slider de 0 à 1, valeur initiale à 0.5
        slider.on_changed(update_opacity)  # Met à jour l'opacité lorsque le slider est modifié
        
        # Fonction pour enregistrer les images et continuer
        def save_and_continue(event):
            shutil.copytree(subdir_path, os.path.join(output_dir, subdir), dirs_exist_ok=True)  # Copie le sous-dossier vers le dossier de sortie
            plt.close(fig)  # Ferme la fenêtre de la figure
        
        # Fonction pour ignorer ce sous-dossier et passer au suivant
        def pass_and_continue(event):
            plt.close(fig)  # Ferme simplement la fenêtre
        
        # Fonction pour quitter le programme
        def exit_program(event):
            plt.close(fig)  # Ferme la fenêtre
            sys.exit(0)  # Quitte le programme
        
        # Ajout des boutons pour sauvegarder, passer ou quitter
        ax_save = plt.axes([0.75, 0.02, 0.15, 0.075])  # Position du bouton "Save"
        btn_save = widgets.Button(ax_save, 'Save')  # Crée un bouton "Save"
        btn_save.on_clicked(save_and_continue)  # Enregistre et continue lorsque cliqué
        
        ax_pass = plt.axes([0.55, 0.02, 0.15, 0.075])  # Position du bouton "Pass"
        btn_pass = widgets.Button(ax_pass, 'Pass')  # Crée un bouton "Pass"
        btn_pass.on_clicked(pass_and_continue)  # Passe au sous-dossier suivant lorsque cliqué

        ax_exit = plt.axes([0.35, 0.02, 0.15, 0.075])  # Position du bouton "Exit"
        btn_exit = widgets.Button(ax_exit, 'Exit')  # Crée un bouton "Exit"
        btn_exit.on_clicked(exit_program)  # Quitte le programme lorsque cliqué

        plt.show()  # Affiche la fenêtre

# Fonction principale
if __name__ == "__main__":
    # Demande à l'utilisateur de choisir les dossiers d'entrée et de sortie
    input_directory = select_folder("Sélectionnez le dossier contenant les images")
    if not input_directory:
        print("Aucun dossier sélectionné, arrêt du programme.")
        sys.exit(0)
    
    output_directory = select_folder("Sélectionnez le dossier de sortie")
    if not output_directory:
        print("Aucun dossier de sortie sélectionné, arrêt du programme.")
        sys.exit(0)

    os.makedirs(output_directory, exist_ok=True)  # Crée le dossier de sortie s'il n'existe pas
    process_folders(input_directory, output_directory)  # Lance le traitement des dossiers
