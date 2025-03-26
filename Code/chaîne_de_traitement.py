from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, url_for
from flask_socketio import SocketIO, emit
import os
import glob
from traitement import traitement, supprimer_contenu_dossier
from pathlib import Path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'PyASIFT')))
from PyASIFT.asift import asift_main
from convert_jpgtopng import convert_jpgtopng
from georef import apply_homography, extract_match_points
from gps_image import extract_gps_from_image
import base64
import json 
import pandas as pd



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

    # Récupérer la liste des chemins d'images et leurs types
    image_paths = request.form.get('image_data')  # Supposons que tu envoies ces informations sous 'image_data'
    image_paths = json.loads(image_paths)  # Convertir le JSON en liste 

    output_folder = request.form.get('output_folder')
    dalles = request.form.get('folder')


    

    if not image_paths or not output_folder or not dalles:
        logs.append("❌ Paramètres manquants pour le traitement")
        socketio.emit('log', {'message': "❌ Paramètres manquants pour le traitement"})
        return jsonify({'error': 'Paramètres manquants pour le traitement', 'logs': logs}), 400
    


    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            logs.append(f"🟢 Dossier de sortie créé : {output_folder}")
            socketio.emit('log', {'message': f"🟢 Dossier de sortie créé : {output_folder}"})
        except Exception as e:
            logs.append(f"❌ Erreur lors de la création du dossier de sortie : {str(e)}")
            socketio.emit('log', {'message': f"❌ Erreur lors de la création du dossier de sortie : {str(e)}"})
            return jsonify({'error': 'Erreur lors de la création du dossier de sortie', 'logs': logs}), 500

    logs.append(f"🟡 Début du traitement de {len(image_paths)} images")
    socketio.emit('log', {'message': f"🟡 Début du traitement de {len(image_paths)} images"})

    for i, image_data in enumerate(image_paths, start=1):
        image_path = image_data['path']  # Chemin de l'image
        image_type = image_data['type']  # "roche" ou "sable"

        image_output_folder = os.path.join(output_folder, f"image_{i}")
        os.makedirs(image_output_folder, exist_ok=True)

        logs.append(f"📸 Image {i} : {image_path} - Type: {image_type} - Progression: {i}/{len(image_paths)} ({(i/len(image_paths)*100):.2f}%)")
        socketio.emit('log', {'message': f"📸 Image {i} : {image_path} - Type: {image_type} - Progression: {i}/{len(image_paths)} ({(i/len(image_paths)*100):.2f}%)"})

        try:
            logs.append(f"🟡 Traitement de l'image {i} de type {image_type}")
            socketio.emit('log', {'message': f"🟡 Traitement de l'image {i} de type {image_type}..."})
            crop_png = traitement(image_path, image_output_folder, dalles)
            logs.append(f"✅ Image {i} traitée et rognée")
            socketio.emit('log', {'message': f"✅ Image {i} traitée et rognée"})

            logs.append(f"🟡 Conversion de l'image {i} en PNG")
            socketio.emit('log', {'message': f"🟡 Conversion de l'image {i} en PNG..."})
            image_png = convert_jpgtopng(image_path, image_output_folder)
            logs.append(f"✅ Conversion de l'image {i} terminée")
            socketio.emit('log', {'message': f"✅ Conversion de l'image {i} terminée"})

         
#:param detector_name: (sift|surf|orb|akaze|brisk)[-flann] Detector type to use, default as SIFT. Add '-flann' to use FLANN matching.
            socketio.emit('log', {'message': f"🟡 Recherche points de correspondance ... "}) 
            points_match=asift_main(crop_png, image_path, "brisk",image_output_folder  )
            socketio.emit('log', {'message': f"✅ {points_match.shape[0]} points de correspondance trouvés ! "}) 
            
            pts_target,pts_query=extract_match_points(points_match)
            logs.append(f"🟡 Application de l'homographie pour l'image {i}")
            socketio.emit('log', {'message': f"🟡 Application de l'homographie pour l'image {i} ... (ETAPE LONGUE JUST WAIT)"})
            apply_homography(pts_target,pts_query, query_img_path=image_path, target_img_path=crop_png, output_path=image_output_folder,type=image_type)
            logs.append(f"✅ Homographie appliquée pour l'image {i}")
            socketio.emit('log', {'message': f"✅ Homographie appliquée pour l'image {i}"})

            processed_image_url = os.path.join(image_output_folder, "crop.png")
            logs.append(f"✅ Image {i} traitée avec succès, disponible à : {processed_image_url}")
            socketio.emit('log', {'message': f"✅ Image {i} traitée avec succès, disponible à : {processed_image_url}"})
            socketio.emit('image_ready', {'image_url': processed_image_url})

            results.append({
                'image': image_path,
                'type': image_type,  # Ajouter ici le type de l'image (roche ou sable)
                'success': True,
                'processed_image': processed_image_url
            })

        except Exception as e:
            logs.append(f"❌ Erreur sur l'image {i} : {str(e)}")
            socketio.emit('log', {'message': f"❌ Erreur sur l'image {i} : {str(e)}"})
            results.append({'image': image_path, 'type': image_type, 'error': str(e)})

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