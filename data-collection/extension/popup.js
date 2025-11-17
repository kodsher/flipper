document.addEventListener('DOMContentLoaded', function() {
    const googleBtn = document.getElementById('googleBtn');

    googleBtn.addEventListener('click', function() {
        // Open Google in a new tab
        chrome.tabs.create({ url: 'https://www.google.com' });

        // Close the popup after a short delay
        setTimeout(() => {
            window.close();
        }, 100);
    });
});