// Facebook Marketplace Auto Scraper Extension
let isScraping = false;
let scrapeCount = 0;
let maxScrapes = 10; // Maximum number of scrapes before stopping

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startScraping') {
    startAutoScraping();
    sendResponse({ status: 'started' });
  } else if (request.action === 'stopScraping') {
    stopAutoScraping();
    sendResponse({ status: 'stopped' });
  } else if (request.action === 'getStatus') {
    sendResponse({
      isScraping: isScraping,
      scrapeCount: scrapeCount
    });
  }
});

function startAutoScraping() {
  if (isScraping) return;

  console.log("🚀 Starting auto-scraping...");
  isScraping = true;
  scrapeCount = 0;

  scrapeAndRefresh();
}

function stopAutoScraping() {
  console.log("🛑 Stopping auto-scraping");
  isScraping = false;
}

function scrapeAndRefresh() {
  if (!isScraping || scrapeCount >= maxScrapes) {
    console.log("🏁 Scraping complete or limit reached");
    stopAutoScraping();
    return;
  }

  console.log(`📱 Scrape cycle ${scrapeCount + 1}/${maxScrapes}`);

  // Scrape current page
  scrapePage();

  // Wait 5 seconds then refresh
  setTimeout(() => {
    if (isScraping) {
      console.log("🔄 Refreshing page for next scrape cycle...");
      window.location.reload();
    }
  }, 5000);
}

function scrapePage() {
  let rows = [["Price", "Title", "Location", "Link"]];
  let seen = new Set();

  function abs(u) {
    try {
      return new URL(u, location.origin).href;
    } catch {
      return u;
    }
  }

  // Scroll to load more content
  function scrollToBottom() {
    window.scrollBy(0, document.body.scrollHeight);
  }

  // Scrape listings
  function scrapeListings() {
    document.querySelectorAll("div").forEach(e => {
      let c = [...e.children];
      if (c.length === 3 && c.every(x => x.tagName === "DIV")) {
        let priceEl = c[0].querySelector('span[dir="auto"]');
        let p = priceEl ? priceEl.textContent.trim() : "";

        if (p.startsWith("$")) {
          let t = c[1].innerText.trim();
          let l = c[2].innerText.trim();
          let a = e.closest("a");
          let link = a ? abs(a.getAttribute("href") || "") : "";
          let key = p + t + l + link;

          if (!seen.has(key)) {
            seen.add(key);
            rows.push([p, t, l, link]);
          }
        }
      }
    });
  }

  // Perform scraping
  scrollToBottom();
  setTimeout(() => {
    scrollToBottom();
    setTimeout(() => {
      scrapeListings();

      // Create and download CSV
      let count = rows.length - 1;
      if (count > 0) {
        let csv = rows.map(r => r.map(x => `"${x.replace(/"/g, '""')}"`).join(",")).join("\n");
        let blob = new Blob([csv], { type: "text/csv" });
        let url = URL.createObjectURL(blob);

        // Send blob to background script for download
        chrome.runtime.sendMessage({
          action: 'downloadCSV',
          blob: Array.from(new Uint8Array(blob)),
          filename: `scrape_${scrapeCount + 1}_${count}_listings.csv`
        });

        console.log(`✅ Scraped ${count} listings`);
      } else {
        console.log("❌ No listings found");
      }

      scrapeCount++;
    }, 1000);
  }, 1000);
}

// Auto-start if URL contains scrape parameter
if (window.location.search.includes('autoscrape=true')) {
  setTimeout(startAutoScraping, 2000);
}