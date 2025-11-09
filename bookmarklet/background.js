// Background script for handling downloads
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'downloadCSV') {
    // Convert blob back to Blob object
    let uint8Array = new Uint8Array(request.blob);
    let blob = new Blob([uint8Array], { type: 'text/csv' });

    // Create download URL
    let url = URL.createObjectURL(blob);

    // Use Chrome downloads API
    chrome.downloads.download({
      url: url,
      filename: request.filename,
      saveAs: false
    }, (downloadId) => {
      // Clean up the URL
      URL.revokeObjectURL(url);
      sendResponse({ downloadId: downloadId });
    });

    return true; // Keep message channel open for async response
  }
});

// Extension icon click handler
chrome.action.onClicked.addListener((tab) => {
  // Open popup or toggle scraping
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    let currentTab = tabs[0];

    // Check if we're on a Facebook Marketplace page
    if (currentTab.url && currentTab.url.includes('facebook.com/marketplace')) {
      // Send message to content script
      chrome.tabs.sendMessage(currentTab.id, {action: 'getStatus'}, (response) => {
        if (response && response.isScraping) {
          // Stop scraping
          chrome.tabs.sendMessage(currentTab.id, {action: 'stopScraping'});
        } else {
          // Start scraping
          chrome.tabs.sendMessage(currentTab.id, {action: 'startScraping'});
        }
      });
    } else {
      // Show notification that they need to be on Marketplace
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon48.svg',
        title: 'FB Scraper',
        message: 'Please navigate to Facebook Marketplace to use this extension.'
      });
    }
  });
});