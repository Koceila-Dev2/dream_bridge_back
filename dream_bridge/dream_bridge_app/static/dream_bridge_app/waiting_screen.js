document.addEventListener('DOMContentLoaded', () => {
  const loadingScreen = document.getElementById('loading-screen');
  const dreamContent = document.getElementById('dream-content');
  if (!loadingScreen || !dreamContent) return;

  const checkUrl = loadingScreen.dataset.checkUrl;
  const loadingMessage = document.getElementById('loading-message');

  const messages = [
    "Analyse de la sémantique...",
    "Interprétation des symboles...",
    "Connexion au subconscient...",
    "Construction du pont onirique...",
    "Coloration des émotions...",
    "Finalisation de la vision..."
  ];
  let messageIndex = 0;

  const messageInterval = setInterval(() => {
    if (loadingMessage) {
      loadingMessage.style.opacity = 0;
      setTimeout(() => {
        messageIndex = (messageIndex + 1) % messages.length;
        loadingMessage.textContent = messages[messageIndex];
        loadingMessage.style.opacity = 1;
      }, 500);
    }
  }, 4000);

  // Durée minimum de l'écran d'attente (10 secondes)
  const MIN_WAIT = 10000;
  const startTime = Date.now();

  function showDreamAfterDelay() {
    const elapsed = Date.now() - startTime;
    const remaining = MIN_WAIT - elapsed;
    if (remaining > 0) {
      setTimeout(() => {
        loadingScreen.style.display = 'none';
        dreamContent.style.display = 'block';
        clearInterval(messageInterval);
      }, remaining);
    } else {
      loadingScreen.style.display = 'none';
      dreamContent.style.display = 'block';
      clearInterval(messageInterval);
    }
  }

  function checkStatus() {
    fetch(checkUrl)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'COMPLETED' || data.status === 'FAILED') {
          clearInterval(pollInterval);
          showDreamAfterDelay();
        }
      })
      .catch(error => {
        console.error("Erreur lors du polling :", error);
        clearInterval(pollInterval);
        clearInterval(messageInterval);
        if (loadingMessage) {
          loadingMessage.textContent = "Erreur de connexion. Veuillez rafraîchir la page.";
        }
      });
  }

  let pollInterval = setInterval(checkStatus, 3000);
  checkStatus();
});

