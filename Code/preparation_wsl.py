import os

def windows_to_wsl_path(chemin):
    """
    Convertit un chemin Windows en chemin compatible WSL.
    Exemple : "D:\\mon_dossier\\fichier.png" -> "/mnt/d/mon_dossier/fichier.png"
    """
    chemin = chemin.replace("\\", "/")  # Remplace les \ par /
    if ":" in chemin:  # Vérifie si c'est un chemin Windows avec une lettre de disque
        disque, reste = chemin.split(":", 1)
        chemin = f"/mnt/{disque.lower()}{reste}"  # Convertit en chemin Linux pour WSL
    return chemin

def creer_fichier_bat(dossier_destination, image_file, image_vrt, dossier_build):
    """
    Crée un fichier .bat dans le dossier spécifié pour exécuter une commande WSL.

    :param dossier_destination: Dossier où enregistrer le fichier .bat (Windows)
    :param image_file: Chemin du fichier image utilisé (Windows ou Linux)
    :param image_vrt: Chemin du fichier VRT utilisé (Windows ou Linux)
    :param dossier_build: Chemin du dossier build sous WSL (Windows ou Linux)
    """

    # Convertir les chemins Windows en chemins Linux pour WSL
    dossier_build_wsl = windows_to_wsl_path(dossier_build)
    image_file_wsl = windows_to_wsl_path(image_file)
    image_vrt_wsl = windows_to_wsl_path(image_vrt)

    # Vérifie et crée le dossier de destination sous Windows
    os.makedirs(dossier_destination, exist_ok=True)

    # Chemin du fichier .bat sous Windows
    chemin_fichier_bat = os.path.join(dossier_destination, "run_wsl.bat")

    # Création du fichier .bat avec la commande WSL corrigée
    with open(chemin_fichier_bat, "w") as fichier_bat:
        fichier_bat.write("@echo off\n")
        ########################## IL FAUT ADAPTER L'ENTETE DES IMAGES /mnt/d/Golfo_Project/ EST VALABLE QUE SUR MON ORDI ############################
        fichier_bat.write(f'wsl bash -c "cd {dossier_build_wsl} && pwd && ./main -im1 /mnt/d/Golfo_Project/{image_file_wsl} -im2 /mnt/d/Golfo_Project/{image_vrt_wsl} -desc 11 -applyfilter 4  -filter_precision 5 -covering 1.7  "\n')

    print(f"Le fichier .bat a été créé à cet emplacement : {chemin_fichier_bat}")
    return chemin_fichier_bat  # Retourne le chemin du fichier créé


if __name__ == "__main__":
    # Exemple d'utilisation avec des chemins Windows
    chemin_bat = creer_fichier_bat("D:\\mon_dossier", "D:\\images\\oblique.PNG", "D:\\data\\dalle.vrt", "D:\\Golfo_Project\\wsl\\build")
