document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const statusDiv = document.querySelector('.status');

    // Simple scraping function
    function startScraping() {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            const currentTab = tabs[0];

            if (currentTab.url && currentTab.url.includes('facebook.com/marketplace')) {
                statusDiv.textContent = 'Scraping started!';
                startBtn.textContent = '✅ Scraping...';
                startBtn.disabled = true;

                // Execute the scraper
                chrome.scripting.executeScript({
                    target: { tabId: currentTab.id },
                    func: () => {
                        // The scraper code
                        (function(){
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
                                let csv=rows.map(r=>r.map(x=>`"${x.replace(/"/g,'""')}"`).join(',')).join('\n');
                                let a=document.createElement('a');
                                a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
                                a.download=`${count}_listings.csv`;
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
                                        console.log('🔄 Refreshing page...');
                                        location.reload();
                                    }, 5000);
                                }
                            }

                            console.log('🚀 Starting scraper...');
                            step();
                        })();
                    }
                }, () => {
                    // After 10 seconds, reset the button
                    setTimeout(() => {
                        statusDiv.textContent = 'Click Start to begin scraping';
                        startBtn.textContent = '🚀 Start Scraping';
                        startBtn.disabled = false;
                    }, 10000);
                });

            } else {
                statusDiv.textContent = 'Please go to Facebook Marketplace first';
                statusDiv.style.background = '#ffebee';
                statusDiv.style.color = '#c62828';
            }
        });
    }

    // Start button click
    startBtn.addEventListener('click', startScraping);
});