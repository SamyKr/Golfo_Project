import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent

def enregistrer_points(image_path):
    # Charger l'image
    img = plt.imread(image_path)

    # Liste des points cliqués
    points = []

    # Fonction pour capturer les clics de souris
    def on_click(event: MouseEvent):
        # Vérifier que le clic est dans les limites de l'image
        if event.xdata is not None and event.ydata is not None:
            # Enregistrer le point cliqué
            points.append((event.xdata, event.ydata))
            print(f"Point ajouté: ({event.xdata}, {event.ydata})")
            # Afficher le point sur l'image
            ax.plot(event.xdata, event.ydata, 'ro')  # Marqueur rouge
            plt.draw()

    # Créer la figure et les axes
    fig, ax = plt.subplots()
    ax.imshow(img)
    ax.set_title('Cliquez pour enregistrer les points')

    # Connecter la fonction de clic à l'événement de la souris
    cid = fig.canvas.mpl_connect('button_press_event', on_click)

    # Afficher l'image et attendre les clics
    plt.show()

    # Retourner les points enregistrés
    return points


if __name__ == "__main__":
    # Exemple d'appel à la fonction avec le nom de l'image
    image_path = 'output_flask/test_basse_def.png'  # Remplacer par le chemin de votre image
    points = enregistrer_points(image_path)


