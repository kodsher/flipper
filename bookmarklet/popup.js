document.addEventListener('DOMContentLoaded', function() {
    const statusDiv = document.getElementById('status');
    const toggleBtn = document.getElementById('toggleBtn');
    const openMarketplaceBtn = document.getElementById('openMarketplaceBtn');
    const bookmarkletBtn = document.getElementById('bookmarkletBtn');
    const autoScrapeBtn = document.getElementById('autoScrapeBtn');
    const marketplaceUrl = document.getElementById('marketplaceUrl');
    const cycleInfo = document.getElementById('cycleInfo');
    const cycleCount = document.getElementById('cycleCount');
    const statsText = document.getElementById('statsText');

    // Bookmarklet code
    const bookmarkletCode = `(function(){
        let rows=[['Price','Title','Location','Link']];
        let seen=new Set();
        let scrolls=0,maxScrolls=2,delay=1000;

        function abs(u){
            try{return new URL(u,location.origin).href}catch{return u}
        }

        function scrape(){
            document.querySelectorAll('div').forEach(e=>{
                let c=[...e.children];
                if(c.length===3&&c.every(x=>x.tagName==='DIV')){
                    let priceEl=c[0].querySelector('span[dir="auto"]');
                    let p=priceEl?priceEl.textContent.trim():'';
                    if(p.startsWith('$')){
                        let t=c[1].innerText.trim(),l=c[2].innerText.trim();
                        let a=e.closest('a');
                        let link=a?abs(a.getAttribute('href')||''):'';
                        let key=p+t+l+link;
                        if(!seen.has(key)){
                            seen.add(key);
                            rows.push([p,t,l,link]);
                        }
                    }
                }
            });
        }

        function dl(){
            let count=rows.length-1;
            let csv=rows.map(r=>r.map(x=>"`"+x.replace(/"/g,'""')+"`").join(',')).join('\\n');
            let a=document.createElement('a');
            a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
            a.download=\\`\\${count}_listings.csv\\`;
            a.click();
        }

        function step(){
            scrape();
            window.scrollBy(0,document.body.scrollHeight);
            scrolls++;
            if(scrolls<maxScrolls){
                setTimeout(step,delay);
            }else{
                scrape();
                dl();
                setTimeout(() => {
                    console.log('🔄 Refreshing page to continue scraping...');
                    location.reload();
                }, 5000);
            }
        }

        console.log('🚀 Starting Facebook Marketplace scraper...');
        step();
    })();`;

    // Get current tab status
    function updateStatus() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            const currentTab = tabs[0];

            if (currentTab.url && currentTab.url.includes('facebook.com/marketplace')) {
                chrome.tabs.sendMessage(currentTab.id, {action: 'getStatus'}, (response) => {
                    if (chrome.runtime.lastError) {
                        // Content script not loaded
                        statusDiv.textContent = 'Ready to scrape';
                        statusDiv.className = 'status stopped';
                        toggleBtn.textContent = '🚀 Start Scraping';
                        toggleBtn.className = 'main-btn start-btn';
                        statsText.textContent = 'Click Start Scraping to begin';
                        cycleInfo.style.display = 'none';
                        return;
                    }

                    if (response) {
                        if (response.isScraping) {
                            statusDiv.textContent = `Scraping in progress...`;
                            statusDiv.className = 'status scraping';
                            toggleBtn.textContent = '⏹️ Stop Scraping';
                            toggleBtn.className = 'main-btn stop-btn';
                            cycleCount.textContent = `Cycle ${response.scrapeCount + 1}/10`;
                            cycleInfo.style.display = 'block';
                            statsText.textContent = `Scraping cycle ${response.scrapeCount + 1} of 10`;
                        } else {
                            statusDiv.textContent = 'Ready to scrape';
                            statusDiv.className = 'status stopped';
                            toggleBtn.textContent = '🚀 Start Scraping';
                            toggleBtn.className = 'main-btn start-btn';
                            cycleInfo.style.display = 'none';
                            statsText.textContent = response.scrapeCount > 0
                                ? `Completed ${response.scrapeCount} scrape cycles`
                                : 'Ready to start';
                        }
                    } else {
                        statusDiv.textContent = 'Please refresh the page';
                        statusDiv.className = 'status stopped';
                        toggleBtn.textContent = '🚀 Start Scraping';
                        toggleBtn.className = 'main-btn start-btn';
                        statsText.textContent = 'Refresh the Marketplace page';
                    }
                });
            } else {
                statusDiv.textContent = 'Navigate to Facebook Marketplace';
                statusDiv.className = 'status stopped';
                toggleBtn.textContent = 'Not on Marketplace';
                toggleBtn.className = 'main-btn';
                toggleBtn.disabled = true;
                statsText.textContent = 'Go to Facebook Marketplace first';
                cycleInfo.style.display = 'none';
            }
        });
    }

    // Toggle scraping
    toggleBtn.addEventListener('click', function() {
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
                            // Try again after injection
                            setTimeout(() => {
                                chrome.tabs.sendMessage(currentTab.id, {action: 'startScraping'});
                            }, 500);
                        });
                        return;
                    }

                    if (response) {
                        if (response.isScraping) {
                            chrome.tabs.sendMessage(currentTab.id, {action: 'stopScraping'});
                        } else {
                            chrome.tabs.sendMessage(currentTab.id, {action: 'startScraping'});
                        }
                    }
                });
            }
        });
    });

    // Open Marketplace button
    openMarketplaceBtn.addEventListener('click', function() {
        chrome.tabs.create({
            url: 'https://www.facebook.com/marketplace'
        });
    });

    // Bookmarklet button
    bookmarkletBtn.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            const currentTab = tabs[0];

            if (currentTab.url && currentTab.url.includes('facebook.com/marketplace')) {
                chrome.scripting.executeScript({
                    target: { tabId: currentTab.id },
                    func: () => eval(`(${bookmarkletCode})`)
                });
            } else {
                alert('Please navigate to Facebook Marketplace first');
            }
        });
    });

    // Make bookmarklet draggable
    bookmarkletBtn.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/uri-list', `javascript:${bookmarkletCode}`);
        e.dataTransfer.setData('text/plain', `javascript:${bookmarkletCode}`);
    });

    // Auto-scrape button
    autoScrapeBtn.addEventListener('click', function() {
        const url = marketplaceUrl.value.trim();

        if (url && url.includes('facebook.com/marketplace')) {
            const autoScrapeUrl = url.includes('?')
                ? url + '&autoscrape=true'
                : url + '?autoscrape=true';

            chrome.tabs.create({ url: autoScrapeUrl });
        } else {
            alert('Please enter a valid Facebook Marketplace URL');
        }
    });

    // Update status on popup open
    updateStatus();

    // Update status every 2 seconds
    setInterval(updateStatus, 2000);
});