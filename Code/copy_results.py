import os
import shutil

def copy_resultats(dossier_source, dossier_destination):
    """
    Cherche tous les fichiers CSV et PNG dans le dossier source et les copie dans le dossier de destination.

    :param dossier_source: Dossier source où chercher les fichiers CSV et PNG
    :param dossier_destination: Dossier de destination où les fichiers seront copiés
    :return: Liste des fichiers copiés
    """
    # Vérifie si le dossier de destination existe sinon le crée
    os.makedirs(dossier_destination, exist_ok=True)

    # Liste pour garder la trace des fichiers copiés
    fichiers_copiers = []

    # Recherche tous les fichiers dans le dossier source
    for fichier in os.listdir(dossier_source):
        chemin_fichier = os.path.join(dossier_source, fichier)

        # Vérifie si c'est un fichier et s'il se termine par .csv ou .png
        if os.path.isfile(chemin_fichier) and (fichier.endswith(".csv") or fichier.endswith(".png")):
            # Copie le fichier dans le dossier de destination
            shutil.copy(chemin_fichier, os.path.join(dossier_destination, fichier))
            fichiers_copiers.append(os.path.join(dossier_destination, fichier))
            print(f"Fichier copié: {fichier}")

    # Retourne la liste des fichiers copiés
    return fichiers_copiers

if __name__ == "__main__":
# Exemple d'utilisation
    copy_resultats("D:\\mon_dossier\\source", "D:\\mon_dossier\\destination")
