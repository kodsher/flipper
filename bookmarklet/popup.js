document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const statusDiv = document.querySelector('.status');

    // Update status display
    function updateStatus() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            const currentTab = tabs[0];

            if (currentTab.url && currentTab.url.includes('facebook.com/marketplace')) {
                chrome.tabs.sendMessage(currentTab.id, {action: 'getStatus'}, (response) => {
                    if (chrome.runtime.lastError) {
                        // Content script not loaded, inject it first
                        chrome.scripting.executeScript({
                            target: { tabId: currentTab.id },
                            files: ['scraper.js']
                        }, () => {
                            // After injection, try again
                            setTimeout(() => {
                                chrome.tabs.sendMessage(currentTab.id, {action: 'startScraping'});
                            }, 500);
                        });
                        return;
                    }

                    if (response) {
                        if (response.isScraping) {
                            statusDiv.textContent = `Scraping... Cycle ${response.scrapeCount}`;
                            startBtn.textContent = '⏹️ Stop Scraping';
                            startBtn.style.background = 'linear-gradient(135deg, #f44336 0%, #da190b 100%)';
                        } else {
                            statusDiv.textContent = response.scrapeCount > 0
                                ? `Completed ${response.scrapeCount} cycles`
                                : 'Click Start to begin scraping';
                            startBtn.textContent = '🚀 Start Scraping';
                            startBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                        }
                    }
                });
            } else {
                statusDiv.textContent = 'Please go to Facebook Marketplace first';
                statusDiv.style.background = '#ffebee';
                statusDiv.style.color = '#c62828';
                startBtn.textContent = '🚀 Go to Marketplace';
                startBtn.style.background = 'linear-gradient(135deg, #1877f2 0%, #0c5bcc 100%)';
            }
        });
    }

    // Toggle scraping
    function toggleScraping() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            const currentTab = tabs[0];

            if (currentTab.url && currentTab.url.includes('facebook.com/marketplace')) {
                chrome.tabs.sendMessage(currentTab.id, {action: 'getStatus'}, (response) => {
                    if (chrome.runtime.lastError) {
                        // Content script not loaded, inject and start
                        chrome.scripting.executeScript({
                            target: { tabId: currentTab.id },
                            files: ['scraper.js']
                        }, () => {
                            setTimeout(() => {
                                chrome.tabs.sendMessage(currentTab.id, {action: 'startScraping'});
                                updateStatus();
                            }, 1000);
                        });
                        return;
                    }

                    if (response) {
                        if (response.isScraping) {
                            chrome.tabs.sendMessage(currentTab.id, {action: 'stopScraping'});
                        } else {
                            chrome.tabs.sendMessage(currentTab.id, {action: 'startScraping'});
                        }
                        updateStatus();
                    }
                });
            } else {
                // Open Marketplace
                chrome.tabs.create({
                    url: 'https://www.facebook.com/marketplace?autoscrape=true'
                });
            }
        });
    }

    // Start button click
    startBtn.addEventListener('click', toggleScraping);

    // Update status on popup open
    updateStatus();

    // Update status every 2 seconds
    setInterval(updateStatus, 2000);
});