#!/usr/bin/env node
/**
 * Opens Facebook Marketplace URLs in browser sequentially with delays
 * Prevents running in background - runs in foreground only
 */

const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// URLs to open (from command line args or default list)
const urls = process.argv.slice(2).filter(arg => arg.startsWith('http'));

// Default URLs if none provided
const defaultUrls = [
    'https://www.facebook.com/marketplace/103103056397247/search?minPrice=125&daysSinceListed=1&deliveryMethod=local_pick_up&query=iphone%2014&exact=false',
    'https://www.facebook.com/marketplace/austin/search?minPrice=125&daysSinceListed=1&deliveryMethod=local_pick_up&query=iphone%2017&exact=false',
    'https://www.facebook.com/marketplace/austin/search?minPrice=125&daysSinceListed=1&deliveryMethod=local_pick_up&query=iphone%2016&exact=false',
    'https://www.facebook.com/marketplace/austin/search?minPrice=125&daysSinceListed=1&deliveryMethod=local_pick_up&query=iphone%2014&exact=false'
];

const urlsToOpen = urls.length > 0 ? urls : defaultUrls;

function delay(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}

function randomDelay(min, max) {
    const delaySeconds = Math.random() * (max - min) + min;
    return delay(delaySeconds);
}

async function openUrl(url, index, total) {
    try {
        console.log(`\n[${index}/${total}] Opening: ${url}`);
        console.log(`   City: ${extractCity(url)}`);
        console.log(`   Query: ${extractQuery(url)}`);
        
        // Open URL in default browser (macOS)
        await execAsync(`open "${url}"`);
        console.log(`   ✅ Opened in browser`);
        
        return true;
    } catch (error) {
        console.error(`   ❌ Error opening URL: ${error.message}`);
        return false;
    }
}

function extractCity(url) {
    const match = url.match(/marketplace\/([^\/]+)/);
    if (match) {
        const cityId = match[1];
        if (cityId === '103103056397247') return 'Corpus Christi';
        return cityId.charAt(0).toUpperCase() + cityId.slice(1);
    }
    return 'Unknown';
}

function extractQuery(url) {
    const match = url.match(/query=([^&]+)/);
    if (match) {
        return decodeURIComponent(match[1]);
    }
    return 'Unknown';
}

async function main() {
    console.log('🌐 Facebook Marketplace URL Opener');
    console.log('=' .repeat(50));
    console.log(`📋 Total URLs: ${urlsToOpen.length}`);
    console.log('⚠️  Using delays to avoid Facebook blocking');
    console.log('🔄 Running in FOREGROUND (not background)');
    console.log('=' .repeat(50));
    
    // Initial delay before starting
    console.log('\n⏳ Waiting 3 seconds before starting...');
    await delay(3);
    
    for (let i = 0; i < urlsToOpen.length; i++) {
        const url = urlsToOpen[i];
        const success = await openUrl(url, i + 1, urlsToOpen.length);
        
        if (!success) {
            console.log(`   ⚠️  Skipping to next URL...`);
            continue;
        }
        
        // Wait before opening next URL (except for last one)
        if (i < urlsToOpen.length - 1) {
            // Random delay between 15-30 seconds to avoid detection
            const waitTime = Math.random() * 15 + 15;
            console.log(`   ⏸️  Waiting ${waitTime.toFixed(1)}s before next URL (anti-detection)...`);
            await delay(waitTime);
        }
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ Finished opening all URLs');
    console.log('💡 Tip: Use the bookmarklet on each page to scrape data');
    console.log('='.repeat(50));
    console.log('\n📝 Next steps:');
    console.log('   1. Wait for each page to load');
    console.log('   2. Click the bookmarklet on each page');
    console.log('   3. Wait for CSV download to complete');
    console.log('   4. Process the CSV files\n');
}

// Run the script
main().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});





