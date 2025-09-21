// static/dream_bridge_app/waiting_screen.js

document.addEventListener('DOMContentLoaded', () => {
    const loadingScreen = document.getElementById('loading-screen');
    if (!loadingScreen) return;

    // --- Configuration ---
    const checkUrl = loadingScreen.dataset.checkUrl;
    const MIN_WAIT_TIME_MS = 10000; // 10 secondes (modifiable)
    const POLLING_INTERVAL_MS = 3000; // 3 secondes

    // --- Gestion des messages de chargement dynamiques ---
    const loadingMessage = document.getElementById('loading-message');
    const messages = [
        "Analyse de la sémantique…",
        "Interprétation des symboles…",
        "Connexion au subconscient…",
        "Construction du pont onirique…",
        "Coloration des émotions…",
        "Finalisation de la vision…"
    ];
    let messageIndex = 0;
    
    const messageInterval = setInterval(() => {
        loadingMessage.style.opacity = 0;
        setTimeout(() => {
            messageIndex = (messageIndex + 1) % messages.length;
            loadingMessage.textContent = messages[messageIndex];
            loadingMessage.style.opacity = 1;
        }, 500); // Temps pour l'effet de fondu
    }, 4000); // Changer de message toutes les 4 secondes

    // --- Logique de vérification du statut (Polling) ---
    const startTime = Date.now();
    let pollingInterval;

    const checkStatus = async () => {
        try {
            const response = await fetch(checkUrl);
            if (!response.ok) {
                throw new Error('La réponse du serveur n\'est pas valide.');
            }

            const data = await response.json();

            // Si le rêve est terminé ou a échoué
            if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                clearInterval(pollingInterval); // Arrête de vérifier
                clearInterval(messageInterval); // Arrête de changer les messages

                const elapsedTime = Date.now() - startTime;
                const remainingTime = MIN_WAIT_TIME_MS - elapsedTime;

                // Rediriger après avoir attendu le temps restant (si nécessaire)
                setTimeout(() => {
                    window.location.href = data.status_url;
                }, Math.max(0, remainingTime)); // Assure que le délai n'est pas négatif
            }
            // Si le statut est 'PENDING' ou 'PROCESSING', on ne fait rien et on attend la prochaine vérification.

        } catch (error) {
            console.error('Erreur lors de la vérification du statut :', error);
            clearInterval(pollingInterval);
            clearInterval(messageInterval);
            loadingMessage.textContent = 'Erreur de connexion. Veuillez rafraîchir la page.';
        }
    };

    // --- Démarrage du processus ---
    pollingInterval = setInterval(checkStatus, POLLING_INTERVAL_MS);
    checkStatus(); // Lancer une première vérification immédiatement
});