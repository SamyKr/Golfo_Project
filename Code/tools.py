import os
import shutil
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np
import cv2
import sys
import tkinter as tk
from tkinter import filedialog

def select_folder(title):
    """Ouvre une boîte de dialogue pour sélectionner un dossier."""
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale Tkinter
    folder = filedialog.askdirectory(title=title)
    return folder

def process_folders(input_dir, output_dir):
    subdirs = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]
    
    for subdir in subdirs:
        subdir_path = os.path.join(input_dir, subdir)
        crop_path = os.path.join(subdir_path, "crop.png")
        transformed_path = os.path.join(subdir_path, "output_transformed_image.png")
        
        if not os.path.exists(crop_path) or not os.path.exists(transformed_path):
            continue
        
        # Charger les images
        img1 = cv2.imread(crop_path, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(transformed_path, cv2.IMREAD_UNCHANGED)
        
        if img1 is None or img2 is None:
            continue
        
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.canvas.manager.full_screen_toggle()
        plt.subplots_adjust(bottom=0.3)
        ax.axis('off')
        
        im1 = ax.imshow(img1)
        im2 = ax.imshow(img2, alpha=0.5)
        
        def update_opacity(val):
            im2.set_alpha(val)
            fig.canvas.draw_idle()
        
        ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
        slider = widgets.Slider(ax_slider, 'Opacity', 0.0, 1.0, valinit=0.5)
        slider.on_changed(update_opacity)
        
        def save_and_continue(event):
            shutil.copytree(subdir_path, os.path.join(output_dir, subdir), dirs_exist_ok=True)
            plt.close(fig)
        
        def pass_and_continue(event):
            plt.close(fig)

        def exit_program(event):
            plt.close(fig)
            sys.exit(0)  # Quitte complètement le script
        
        ax_save = plt.axes([0.75, 0.02, 0.15, 0.075])
        btn_save = widgets.Button(ax_save, 'Save')
        btn_save.on_clicked(save_and_continue)
        
        ax_pass = plt.axes([0.55, 0.02, 0.15, 0.075])
        btn_pass = widgets.Button(ax_pass, 'Pass')
        btn_pass.on_clicked(pass_and_continue)

        ax_exit = plt.axes([0.35, 0.02, 0.15, 0.075])  
        btn_exit = widgets.Button(ax_exit, 'Exit')
        btn_exit.on_clicked(exit_program)

        plt.show()

if __name__ == "__main__":
    # Demande à l'utilisateur de choisir les dossiers
    input_directory = select_folder("Sélectionnez le dossier contenant les images")
    if not input_directory:
        print("Aucun dossier sélectionné, arrêt du programme.")
        sys.exit(0)
    
    output_directory = select_folder("Sélectionnez le dossier de sortie")
    if not output_directory:
        print("Aucun dossier de sortie sélectionné, arrêt du programme.")
        sys.exit(0)

    os.makedirs(output_directory, exist_ok=True)
    process_folders(input_directory, output_directory)
