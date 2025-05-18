document.addEventListener('DOMContentLoaded', () => {
    const youtubeUrlInput = document.getElementById('youtube-url');
    const targetLanguageSelect = document.getElementById('target-language');
    const translateButton = document.getElementById('translate-btn');
    const resultContainer = document.getElementById('result-container');
    const translationResult = document.getElementById('translation-result');

    // Add loading state to button
    function setLoading(isLoading) {
        if (isLoading) {
            translateButton.disabled = true;
            translateButton.innerHTML = 'Traduction en cours...';
            translateButton.classList.add('opacity-75');
        } else {
            translateButton.disabled = false;
            translateButton.innerHTML = 'Traduire';
            translateButton.classList.remove('opacity-75');
        }
    }

    // Validate YouTube URL
    function isValidYouTubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
    }

    translateButton.addEventListener('click', async () => {
        const youtubeUrl = youtubeUrlInput.value.trim();
        const targetLanguage = targetLanguageSelect.value;

        // Basic validation
        if (!youtubeUrl) {
            alert('Veuillez entrer un lien YouTube');
            return;
        }

        if (!isValidYouTubeUrl(youtubeUrl)) {
            alert('Veuillez entrer un lien YouTube valide');
            return;
        }

        setLoading(true);

        try {
            // Simulate API call with a delay
            await new Promise(resolve => setTimeout(resolve, 2000));

            /* TODO: Actual API calls would go here
            1. Call API to extract video ID from URL
            2. Call API to get video transcript
            3. Call API to translate transcript
            Example:
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    youtubeUrl,
                    targetLanguage
                })
            });
            const data = await response.json();
            */

            // Simulate a response
            const mockTranslation = `Ceci est une simulation de traduction pour la vidéo : ${youtubeUrl}\n\n` +
                `Langue cible : ${targetLanguage}\n\n` +
                `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.`;

            // Show result
            resultContainer.classList.remove('hidden');
            resultContainer.classList.add('fade-in');
            translationResult.value = mockTranslation;

        } catch (error) {
            console.error('Error:', error);
            alert('Une erreur est survenue lors de la traduction. Veuillez réessayer.');
        } finally {
            setLoading(false);
        }
    });

    // Add input validation feedback
    youtubeUrlInput.addEventListener('input', () => {
        const isValid = isValidYouTubeUrl(youtubeUrlInput.value.trim());
        youtubeUrlInput.style.borderColor = youtubeUrlInput.value.trim() ? (isValid ? '#10B981' : '#EF4444') : '#E5E7EB';
    });
}); 