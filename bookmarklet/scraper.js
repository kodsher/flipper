// Facebook Marketplace Auto Scraper Extension
let isScraping = false;
let scrapeCount = 0;
let maxScrapes = 999; // No limit for continuous scraping

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

  scrapeAndRefresh();
}

function stopAutoScraping() {
  console.log("🛑 Stopping auto-scraping");
  isScraping = false;
}

function scrapeAndRefresh() {
  if (!isScraping) return;

  console.log(`📱 Scrape cycle ${scrapeCount + 1}`);

  // Scrape current page (will handle refresh internally)
  scrapePage();
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
        // Break long lines at 15 characters
        let csv = rows.map(r => r.map(x => {
          let cell = `"${x.replace(/"/g, '""')}"`;
          // Break long cells at 15 characters
          if (cell.length > 20) {
            let parts = [];
            for (let i = 0; i < cell.length; i += 15) {
              parts.push(cell.substring(i, i + 15));
            }
            cell = parts.join('" \n"');
          }
          return cell;
        }).join(","));

        // Direct download in content script
        let blob = new Blob([csv], { type: "text/csv" });
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = `scrape_${scrapeCount + 1}_${count}_listings.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log(`✅ Downloaded CSV with ${count} listings`);
      } else {
        console.log("❌ No listings found");
      }

      scrapeCount++;

      // Schedule refresh after giving time for download to complete
      setTimeout(() => {
        if (isScraping) {
          console.log("🔄 Refreshing page for next scrape cycle...");
          location.reload();
        }
      }, 2000); // 2 seconds after download
    }, 500);
  }, 500);
}

// Auto-start if URL contains scrape parameter
if (window.location.search.includes('autoscrape=true')) {
  setTimeout(startAutoScraping, 2000);
}