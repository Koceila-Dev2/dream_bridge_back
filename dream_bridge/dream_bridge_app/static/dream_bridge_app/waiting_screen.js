// static/dream_bridge_app/waiting_screen.js

document.addEventListener('DOMContentLoaded', () => {
    const loadingScreen = document.getElementById('loading-screen');
    if (!loadingScreen) return;

    const checkUrl = loadingScreen.dataset.checkUrl;
    const MIN_WAIT_TIME_MS = 8000; // 8 secondes
    const POLLING_INTERVAL_MS = 3000; // 3 secondes

    const startTime = Date.now();
    let pollingInterval;

    const checkStatus = async () => {
        try {
            const response = await fetch(checkUrl);
            if (!response.ok) {
                console.error('Erreur serveur lors de la vérification du statut.');
                clearInterval(pollingInterval); // Arrête en cas d'erreur serveur
                return;
            }

            const data = await response.json();

            if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                clearInterval(pollingInterval); 
                
                const elapsedTime = Date.now() - startTime;
                const remainingTime = MIN_WAIT_TIME_MS - elapsedTime;

                if (remainingTime > 0) {
                    // Si moins de 8 secondes se sont écoulées, attendre le reste du temps
                    setTimeout(() => {
                        window.location.href = data.status_url;
                    }, remainingTime);
                } else {
                    // Si 8 secondes ou plus se sont déjà écoulées, rediriger immédiatement
                    window.location.href = data.status_url;
                }
            }
            // Si PENDING ou PROCESSING, ne rien faire et laisser l'intervalle continuer
            
        } catch (error) {
            console.error('Erreur de connexion lors de la vérification du statut :', error);
            clearInterval(pollingInterval);
        }
    };

    // Démarrer la vérification à intervalles réguliers
    pollingInterval = setInterval(checkStatus, POLLING_INTERVAL_MS);
    
    // Lancer une première vérification immédiate pour plus de réactivité
    checkStatus(); 
});