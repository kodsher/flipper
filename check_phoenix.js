#!/usr/bin/env node

// Simple script to check for Phoenix listings in the Firebase database
// Run with: node check_phoenix.js

const https = require('https');
const firebaseConfig = {
    databaseURL: "https://phone-flipping-default-rtdb.firebaseio.com"
};

console.log('🔍 Checking Firebase database for Phoenix listings...\n');

// Fetch data from Firebase
const url = `${firebaseConfig.databaseURL}/phone_listings.json`;

https.get(url, (res) => {
    let data = '';

    res.on('data', (chunk) => {
        data += chunk;
    });

    res.on('end', () => {
        try {
            const listings = JSON.parse(data);
            const totalListings = Object.keys(listings).length;
            console.log(`📊 Total listings in database: ${totalListings}\n`);

            // Find Phoenix listings
            const phoenixListings = [];
            const cities = new Set();

            Object.values(listings).forEach(listing => {
                const city = listing.search_city;
                if (city) {
                    cities.add(city);
                    if (city === 'Phoenix') {
                        phoenixListings.push(listing);
                    }
                }
            });

            console.log(`🏙️ Cities found (${cities.size}):`);
            Array.from(cities).sort().forEach(city => {
                const count = Object.values(listings).filter(l => l.search_city === city).length;
                console.log(`   • ${city}: ${count} listings`);
            });

            console.log(`\n🌵 Phoenix listings found: ${phoenixListings.length}`);

            if (phoenixListings.length > 0) {
                console.log('\n📋 Phoenix listing details:');
                phoenixListings.forEach((listing, index) => {
                    console.log(`\n${index + 1}. ID: ${listing.id}`);
                    console.log(`   Title: ${listing.title}`);
                    console.log(`   Model: ${listing.model || 'Unknown'}`);
                    console.log(`   Price: $${listing.price || 'Unknown'}`);
                    console.log(`   Date: ${listing.date || 'Unknown'}`);
                    console.log(`   Variant: ${listing.variant || 'None'}`);
                });
            } else {
                console.log('❌ No Phoenix listings found in the database!');
                console.log('🤔 This means the Phoenix tag showing in the app is a bug.');
            }

        } catch (error) {
            console.error('❌ Error parsing data:', error.message);
        }
    });

}).on('error', (error) => {
    console.error('❌ Error fetching data:', error.message);
});