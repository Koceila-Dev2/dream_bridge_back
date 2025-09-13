// dream_bridge_app/static/dream_bridge_app/js/recorder.js (Version de débogage)

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM chargé. Script recorder.js initialisé."); // Log de base

    const recorderUI = document.getElementById('recorder-ui');
    if (!recorderUI) {
        console.error("Erreur critique : L'élément avec l'ID 'recorder-ui' est introuvable.");
        return;
    }

    const uploadUrl = recorderUI.dataset.uploadUrl;
    const csrfToken = getCookie('csrftoken');
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const statusDisplay = document.getElementById('status-display');

    if (!startButton || !stopButton || !statusDisplay) {
        console.error("Un ou plusieurs éléments de l'interface (boutons, statut) sont introuvables. Vérifiez les IDs dans home.html.");
        return;
    }
    
    console.log("Tous les éléments de l'interface ont été trouvés avec succès.");

    let mediaRecorder;
    let audioChunks = [];

    // --- On attache les écouteurs d'événements ---

    startButton.addEventListener('click', () => {
        console.log("✅ Bouton 'Démarrer' cliqué. Appel de la fonction startRecording()."); // ESPION 1
        startRecording();
    });

    stopButton.addEventListener('click', () => {
        console.log("✅ Bouton 'Arrêter' cliqué. Appel de la fonction stopRecording().");
        stopRecording();
    });

    // --- Fonctions principales ---

    async function startRecording() {
        console.log("▶️  Fonction startRecording() exécutée."); // ESPION 2
        audioChunks = []; // Vider les anciens morceaux
        
        try {
            console.log("🎙️  Demande d'accès au micro..."); // ESPION 3
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log("👍 Accès au micro obtenu avec succès !"); // ESPION 4

            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                console.log("⏹️  Événement onstop déclenché. Création du Blob audio.");
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                uploadAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop()); // Bonne pratique pour couper le micro
            };
            
            mediaRecorder.start();
            console.log("🔴 Enregistrement démarré.");
            
            // Mise à jour de l'interface
            startButton.disabled = true;
            stopButton.disabled = false;
            statusDisplay.textContent = "Enregistrement en cours...";

        } catch (err) {
            console.error("❌ ERREUR lors de la demande d'accès au micro :", err); // ESPION 5 (Le plus important)
            statusDisplay.innerHTML = `<span class="text-danger">Erreur micro : ${err.name}.</span><br><small>Vérifiez les permissions et que la page est bien sur localhost.</small>`;
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            console.log("🎬 Arrêt de l'enregistrement demandé.");
            statusDisplay.textContent = "Enregistrement terminé. Envoi en cours...";
        }
    }

    function uploadAudio(audioBlob) {
        console.log(`📤 Envoi du fichier audio (${(audioBlob.size / 1024).toFixed(2)} Ko) vers ${uploadUrl}`);
        const formData = new FormData();
        formData.append('audio', audioBlob, 'dream-recording.webm'); 

        fetch(uploadUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData,
        })
        .then(response => {
            console.log("Réponse du serveur reçue.", response);
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                console.error("Le serveur n'a pas renvoyé de redirection. Réponse :", response);
                statusDisplay.textContent = "Erreur du serveur lors du traitement.";
            }
        })
        .catch(error => {
            console.error("❌ ERREUR lors de l'envoi du fichier :", error);
            statusDisplay.textContent = "Erreur réseau lors de l'envoi.";
            startButton.disabled = false;
            stopButton.disabled = true;
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}