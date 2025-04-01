// Navigation entre les pages
document.getElementById('uploadBtn').addEventListener('click', function() {
    // Affiche la page de téléchargement et cache l'éditeur
    document.getElementById('upload-page').style.display = 'block';
    document.getElementById('editor-page').style.display = 'none';
    // Active le bouton de téléchargement
    document.getElementById('uploadBtn').classList.add('active');
    document.getElementById('editorBtn').classList.remove('active');
});

document.getElementById('editorBtn').addEventListener('click', function() {
    // Affiche l'éditeur et cache la page de téléchargement
    document.getElementById('upload-page').style.display = 'none';
    document.getElementById('editor-page').style.display = 'block';
    // Active le bouton de l'éditeur
    document.getElementById('uploadBtn').classList.remove('active');
    document.getElementById('editorBtn').classList.add('active');
});

// Fonction pour faire défiler la page vers le bas pour voir les logs
function scrollToBottom() {
    const logElement = document.getElementById("log");
    logElement.scrollTop = logElement.scrollHeight;
}

// Traitement du formulaire de téléchargement des images
document.getElementById("uploadForm").onsubmit = async function(event) {
    event.preventDefault(); // Empêche la soumission classique du formulaire
    let formData = new FormData();

    // Récupère les fichiers d'image
    let imageFiles = document.getElementById("images").files;
    for (let i = 0; i < imageFiles.length; i++) {
        formData.append("images", imageFiles[i]);
    }

    // Récupère les autres informations du formulaire
    formData.append("folder", document.getElementById("folder").value);
    formData.append("output_folder", document.getElementById("output_folder").value);

    // Affiche un message de chargement
    document.getElementById("log").innerText = "Chargement des images en cours...";

    try {
        // Envoie les données vers le serveur
        let response = await fetch("/upload", { method: "POST", body: formData });
        let result = await response.json();

        // Affiche un message de succès
        document.getElementById("log").innerText = "Images chargées avec succès ! 🥳 \nPrêt à Traiter... 🖥️";
        scrollToBottom(); // Fait défiler la page pour voir le message

        if (result.results) {
            // Remplissage des images prévisualisées
            let previewContainer = document.getElementById("previewContainer");
            previewContainer.innerHTML = "";

            result.results.forEach((item, index) => {
                if (item.image_path) {
                    let imgContainer = document.createElement("div");
                    imgContainer.classList.add("image-container");

                    let img = document.createElement("img");
                    img.src = item.image_path;
                    img.alt = "Image prévisualisée";

                    let radioContainer = document.createElement("div");
                    radioContainer.classList.add("radio-options");

                    // Création des options de type d'image (Roche, Sable)
                    let rocheLabel = document.createElement("label");
                    rocheLabel.innerHTML = "Roche";
                    let rocheInput = document.createElement("input");
                    rocheInput.type = "radio";
                    rocheInput.name = "image_" + index;
                    rocheInput.value = "roche";

                    let sableLabel = document.createElement("label");
                    sableLabel.innerHTML = "Sable";
                    let sableInput = document.createElement("input");
                    sableInput.type = "radio";
                    sableInput.name = "image_" + index;
                    sableInput.value = "sable";

                    radioContainer.appendChild(rocheLabel);
                    radioContainer.appendChild(rocheInput);
                    radioContainer.appendChild(sableLabel);
                    radioContainer.appendChild(sableInput);

                    imgContainer.appendChild(img);
                    imgContainer.appendChild(radioContainer);

                    previewContainer.appendChild(imgContainer);
                }
            });

            // Affiche le bouton pour lancer le traitement
            document.getElementById("processBtn").style.display = "inline";
        }
    } catch (error) {
        // En cas d'erreur, affiche le message d'erreur
        document.getElementById("log").innerText = "Erreur lors du chargement des images: " + error.message;
        scrollToBottom();
    }
};

// Traitement des images après leur prévisualisation
document.getElementById("processBtn").onclick = async function() {
    let outputFolder = document.getElementById("output_folder").value;
    let imageElements = document.querySelectorAll("#previewContainer .image-container");

    // Récupère les données des images et leurs options
    let imagePaths = Array.from(imageElements).map((imgContainer, index) => {
        let img = imgContainer.querySelector("img");
        let path = img.src;
        let cleanedPath = path.split('=')[1];

        let selectedOption = imgContainer.querySelector('input[type="radio"]:checked')?.value || "non_specifié";

        return { path: cleanedPath, type: selectedOption };
    });

    document.getElementById("log").innerText += "\nTraitement des images en cours...";
    scrollToBottom();

    try {
        // Envoie la demande de traitement des images
        let response = await fetch("/process_image", {
            method: "POST",
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                image_data: JSON.stringify(imagePaths),
                output_folder: outputFolder,
                folder: document.getElementById("folder").value
            })
        });

        let result = await response.json();
        document.getElementById("log").innerText += "\n" + result.message;
        scrollToBottom();
    } catch (error) {
        document.getElementById("log").innerText += "\nErreur lors du traitement: " + error.message;
        scrollToBottom();
    }
};

// Socket.io pour recevoir les messages en temps réel
try {
    const socket = io();
    // Affiche les logs en temps réel
    socket.on('log', function(data) {
        document.getElementById("log").innerText += "\n" + data.message;
        scrollToBottom();
    });

    // Affiche l'image traitée lorsque prête
    socket.on('image_ready', function(data) {
        const imageUrl = data.image_url;
        const imgElement = document.getElementById("preview");
        imgElement.src = imageUrl;
        imgElement.style.display = "block";
    });
} catch (error) {
    console.error("Erreur avec Socket.io:", error);
}

// Code pour l'éditeur d'images sans sauvegarde
const fileInput = document.getElementById('file-input');
const canvasContainer = document.getElementById('canvas-container');
let activeImage = null;

fileInput.addEventListener('change', (event) => {
    const files = event.target.files;
    for (let file of files) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        const div = document.createElement('div');
        div.classList.add('image-container-editor');
        div.style.left = '50px';
        div.style.top = '50px';
        div.style.width = '200px';
        div.style.height = '200px';
        img.style.width = '100%';
        img.style.height = '100%';

        // Création du redimensionneur
        const resizer = document.createElement('div');
        resizer.classList.add('resizer', 'bottom-right');
        div.appendChild(img);
        div.appendChild(resizer);

        // Création du bouton de suppression
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('delete-btn');
        deleteBtn.innerText = 'X';
        div.appendChild(deleteBtn);

        // Création du bouton pour changer l'ordre
        const orderBtn = document.createElement('button');
        orderBtn.classList.add('order-btn');
        orderBtn.innerText = '↑↓';
        div.appendChild(orderBtn);

        // Ajoute l'image à la zone d'édition
        canvasContainer.appendChild(div);
        makeDraggableResizable(div, resizer, img);

        // Active l'image au clic
        div.addEventListener('mousedown', () => { activeImage = img; });

        // Fonctionnalité du bouton de suppression
        deleteBtn.addEventListener('click', () => {
            div.remove();
        });

        // Fonctionnalité du bouton d'ordre (changer la superposition)
        orderBtn.addEventListener('click', () => {
            const zIndex = div.style.zIndex === '1' ? '0' : '1';
            div.style.zIndex = zIndex;
        });
    }
});

// Fonction pour rendre l'image redimensionnable et déplaçable
function makeDraggableResizable(element, resizer, img) {
    let offsetX, offsetY, isDragging = false;
    let isResizing = false;
    let startWidth, startHeight, startX, startY;

    // Fonction pour déplacer l'image
    element.addEventListener('mousedown', (event) => {
        if (event.target === resizer) return;
        isDragging = true;
        offsetX = event.clientX - element.offsetLeft;
        offsetY = event.clientY - element.offsetTop;
        document.addEventListener('mousemove', drag);
    });

    function drag(event) {
        if (isDragging) {
            element.style.left = `${event.clientX - offsetX}px`;
            element.style.top = `${event.clientY - offsetY}px`;
        }
    }

    document.addEventListener('mouseup', () => {
        isDragging = false;
        isResizing = false;
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mousemove', resize);
    });

    // Fonction pour redimensionner l'image
    resizer.addEventListener('mousedown', (event) => {
        event.preventDefault();
        isResizing = true;
        startX = event.clientX;
        startY = event.clientY;
        startWidth = element.offsetWidth;
        startHeight = element.offsetHeight;
        document.addEventListener('mousemove', resize);
    });

    function resize(event) {
        if (isResizing) {
            const newWidth = startWidth + (event.clientX - startX);
            const newHeight = startHeight + (event.clientY - startY);

            element.style.width = `${newWidth}px`;
            element.style.height = `${newHeight}px`;
            img.style.width = `${newWidth}px`;
            img.style.height = `${newHeight}px`;
        }
    }
}

// Événements pour ajuster la luminosité, l'opacité et la rotation de l'image
document.getElementById('brightness').addEventListener('input', (event) => {
    if (activeImage) {
        activeImage.style.filter = `brightness(${event.target.value}%)`;
    }
});

document.getElementById('opacity').addEventListener('input', (event) => {
    if (activeImage) {
        activeImage.style.opacity = event.target.value / 100;
    }
});

document.getElementById('vertical-straighten').addEventListener('input', (event) => {
    if (activeImage) {
        const horizontalValue = document.getElementById('horizontal-straighten').value;
        const verticalValue = event.target.value;
        applyRotation(activeImage, horizontalValue, verticalValue);
    }
});

document.getElementById('horizontal-straighten').addEventListener('input', (event) => {
    if (activeImage) {
        const verticalValue = document.getElementById('vertical-straighten').value;
        const horizontalValue = event.target.value;
        applyRotation(activeImage, horizontalValue, verticalValue);
    }
});

// Applique la rotation à l'image
function applyRotation(img, horizontalValue, verticalValue) {
    const rotateX = `rotateX(${verticalValue}deg)`;
    const rotateY = `rotateY(${horizontalValue}deg)`;
    const rotate = `rotate(${horizontalValue / 2}deg)`;

    img.style.transform = `${rotateX} ${rotateY} ${rotate}`;
}
