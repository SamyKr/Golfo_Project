from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, url_for
from flask_socketio import SocketIO, emit
import os
import glob
from traitement import traitement, supprimer_contenu_dossier
from pathlib import Path
from wsl import launch_program
from preparation_wsl import creer_fichier_bat
from convert_jpgtopng import convert_jpgtopng
from copy_results import copy_resultats
from georef import apply_homography, extract_match_points
from gps_image import extract_gps_from_image
import base64

chemin_app_build_linux = "/mnt/d/Golfo_Project/wsl/build"
chemin_app_build_windows = "wsl/build"

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('image_ready')
def handle_image_ready(data):
    image_url = url_for('static', filename='output_flask/crop.png')
    socketio.emit('image_ready', {'image_url': image_url})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'images' not in request.files or 'folder' not in request.form or 'output_folder' not in request.form:
        return jsonify({'error': 'Veuillez sélectionner une ou plusieurs images, un dossier et un dossier de sortie'}), 400

    images = request.files.getlist('images')  # Récupérer plusieurs fichiers
    folder_path = request.form['folder']
    output_folder = request.form['output_folder']
    
    results = []

    for image in images:
        image_raw = image.filename
        image_path = os.path.join(os.getcwd(), "uploads", image.filename)
        image.save(image_path)

        data_gps = extract_gps_from_image(image_path)
        
        try:
            X_Lambert = data_gps['X_Lambert']
            Y_Lambert = data_gps['Y_Lambert']
        except KeyError:
            results.append({
                'image': image.filename,
                'error': 'Les coordonnées GPS ne sont pas disponibles dans l\'image.',
                'message': 'Veuillez vérifier les coordonnées...',
                'input_required': True
            })
            continue  # Passer à l'image suivante

        results.append({
            'message': 'Image chargée avec succès',
            'image': image.filename,
            'image_path': f"/serve_image?path={image_path}",
            'folder': folder_path,
            'output_folder': output_folder,
            'Coord_X': X_Lambert,
            'Coord_Y': Y_Lambert
        })

    return jsonify({'results': results})





        
@app.route('/serve_image')
def serve_image():
    image_path = request.args.get('path')
    if os.path.exists(image_path):
        return send_file(image_path)
    return jsonify({'error': 'Fichier introuvable'}), 404


@app.route('/process_image', methods=['POST'])
def process_image():
    logs = []
    results = []

    images = request.form.getlist('image_path')  # Récupérer plusieurs chemins d'images
    output_folder = request.form.get('output_folder')
    dalles = request.form.get('folder')

    if not images or not output_folder or not dalles:
        logs.append("❌ Paramètres manquants pour le traitement")
        socketio.emit('log', {'message': "❌ Paramètres manquants pour le traitement"})
        return jsonify({'error': 'Paramètres manquants pour le traitement', 'logs': logs}), 400

    # Appel de `supprimer_contenu_dossier` avant de commencer le traitement des images
    #logs.append(f"🟡 Vidange du dossier de sortie ")
    #socketio.emit('log', {'message': f"🟡 Vidange du dossier de sortie "})
    #supprimer_contenu_dossier(output_folder)

    logs.append(f"🟡 Début du traitement de {len(images)} images")
    socketio.emit('log', {'message': f"🟡 Début du traitement de {len(images)} images"})
    
    for i, image_path in enumerate(images, start=1):
        image_path = image_path.split('path=', 1)[1]
        image_output_folder = os.path.join(output_folder, str(i))  # Dossier spécifique à chaque image
        os.makedirs(image_output_folder, exist_ok=True)

        logs.append(f"📸 Image {i} : {image_path}")
        socketio.emit('log', {'message': f"📸 Image {i} : {image_path}"})
        logs.append(f"📂 Dossier de sortie : {image_output_folder}")
        socketio.emit('log', {'message': f"📂 Dossier de sortie : {image_output_folder}"})

        try:
            logs.append(f"🟡 Traitement de l'image {i}")
            socketio.emit('log', {'message': f"🟡 Traitement de l'image {i}"})
            crop_png = traitement(image_path, image_output_folder, dalles)
            logs.append(f"✅ Image {i} traitée et rognée")
            socketio.emit('log', {'message': f"✅ Image {i} traitée et rognée"})

            logs.append(f"🟡 Conversion de l'image {i} en PNG")
            socketio.emit('log', {'message': f"🟡 Conversion de l'image {i} en PNG"})
            image_png = convert_jpgtopng(image_path, image_output_folder)
            logs.append(f"✅ Conversion de l'image {i} terminée")
            socketio.emit('log', {'message': f"✅ Conversion de l'image {i} terminée"})

            logs.append(f"🟡 Création du fichier batch pour l'image {i}")
            socketio.emit('log', {'message': f"🟡 Création du fichier batch pour l'image {i}"})
            chemin_bat = creer_fichier_bat(image_output_folder, crop_png, image_png, chemin_app_build_linux)
            logs.append(f"✅ Fichier batch créé : {chemin_bat}")
            socketio.emit('log', {'message': f"✅ Fichier batch créé : {chemin_bat}"})

            logs.append(f"🟡 Lancement du programme WSL pour l'image {i}")
            socketio.emit('log', {'message': f"🟡 Lancement du programme WSL pour l'image {i}"})
            launch_program(chemin_bat)
            logs.append(f"✅ Programme lancé pour l'image {i}")
            socketio.emit('log', {'message': f"✅ Programme lancé pour l'image {i}"})

            logs.append(f"🟡 Copie des résultats pour l'image {i}")
            socketio.emit('log', {'message': f"🟡 Copie des résultats pour l'image {i}"})
            copy_resultats(chemin_app_build_windows, image_output_folder)
            logs.append(f"✅ Copie des résultats pour l'image {i} terminée")
            socketio.emit('log', {'message': f"✅ Copie des résultats pour l'image {i} terminée"})

            # Vérification du fichier data_matches.csv
            match_csv = os.path.join(image_output_folder, "data_matches.csv")
            if not os.path.exists(match_csv):
                logs.append(f"❌ Erreur : data_matches.csv introuvable pour l'image {i}")
                socketio.emit('log', {'message': f"❌ Erreur : data_matches.csv introuvable pour l'image {i}"})
                results.append({'image': image_path, 'error': 'Fichier data_matches.csv introuvable'})
                continue  # Passe à l'image suivante

            with open(match_csv, 'r') as f:
                data = f.readlines()
            nombre_de_points = len(data) - 1
            if nombre_de_points < 1:
                logs.append(f"❌ Erreur : Pas assez de points de correspondance pour l'image {i}")
                socketio.emit('log', {'message': f"❌ Erreur : Pas assez de points de correspondance pour l'image {i}"})
                results.append({'image': image_path, 'error': 'Pas assez de points de correspondance'})
                continue  # Passe à l'image suivante

            logs.append(f"✅ {nombre_de_points} points de correspondance trouvés pour l'image {i}")
            socketio.emit('log', {'message': f"✅ {nombre_de_points} points de correspondance trouvés pour l'image {i}"})

            logs.append(f"🟡 Application de l'homographie pour l'image {i}")
            socketio.emit('log', {'message': f"🟡 Application de l'homographie pour l'image {i}"})
            apply_homography(*extract_match_points(match_csv), query_img_path=image_path, target_img_path=crop_png, output_path=image_output_folder)
            logs.append(f"✅ Homographie appliquée pour l'image {i}")
            socketio.emit('log', {'message': f"✅ Homographie appliquée pour l'image {i}"})

            processed_image_url = os.path.join(image_output_folder, "crop.png")
            logs.append(f"✅ Image {i} traitée avec succès, disponible à : {processed_image_url}")
            socketio.emit('log', {'message': f"✅ Image {i} traitée avec succès, disponible à : {processed_image_url}"})
            socketio.emit('image_ready', {'image_url': processed_image_url})

            results.append({
                'image': image_path,
                'success': True,
                'processed_image': processed_image_url
            })

        except Exception as e:
            logs.append(f"❌ Erreur sur l'image {i} : {str(e)}")
            socketio.emit('log', {'message': f"❌ Erreur sur l'image {i} : {str(e)}"})
            results.append({'image': image_path, 'error': str(e)})

    return jsonify({'success': True, 'results': results, 'logs': logs})



@app.route('/check_folder', methods=['POST'])
def check_folder():
    folder_path = request.form.get('folder')
    
    # Vérification que le dossier existe avant de le traiter
    if not os.path.exists(folder_path):
        return jsonify({'error': 'Le dossier n\'existe pas'}), 400
    
    valid_extensions = ['.tif', '.tiff', '.jp2', '.geotiff']
    image_files = []
    
    # Recherche des fichiers d'images dans le dossier
    for ext in valid_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, '*' + ext)))
    
    return jsonify({
        'message': f'Nombre d\'images trouvées : {len(image_files)}',
        'image_count': len(image_files)
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)