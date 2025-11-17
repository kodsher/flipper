// Test variant detection on actual database titles
function detectiPhoneVariant(title) {
    if (!title) return null;

    const lowerTitle = title.toLowerCase();

    // iPhone 17 variants
    if (lowerTitle.includes('iphone 17')) {
        if (lowerTitle.includes('pro max') || lowerTitle.includes('17 pro max')) return '17_pro_max';
        if (lowerTitle.includes('pro') || lowerTitle.includes('17 pro')) return '17_pro';
        if (lowerTitle.includes('air') || lowerTitle.includes('17 air')) return '17_air';
    }

    // iPhone 16 variants
    if (lowerTitle.includes('iphone 16')) {
        if (lowerTitle.includes('pro max') || lowerTitle.includes('16 pro max')) return '16_pro_max';
        if (lowerTitle.includes('pro') || lowerTitle.includes('16 pro')) return '16_pro';
        if (lowerTitle.includes('plus') || lowerTitle.includes('16 plus')) return '16_plus';
        if (lowerTitle.includes('16e') || lowerTitle.includes('16 e')) return '16_16e';
    }

    // iPhone 15 variants
    if (lowerTitle.includes('iphone 15')) {
        if (lowerTitle.includes('pro max') || lowerTitle.includes('15 pro max')) return '15_pro_max';
        if (lowerTitle.includes('pro') || lowerTitle.includes('15 pro')) return '15_pro';
        if (lowerTitle.includes('plus') || lowerTitle.includes('15 plus')) return '15_plus';
    }

    // iPhone 14 variants
    if (lowerTitle.includes('iphone 14')) {
        if (lowerTitle.includes('pro max') || lowerTitle.includes('14 pro max')) return '14_pro_max';
        if (lowerTitle.includes('pro') || lowerTitle.includes('14 pro')) return '14_pro';
        if (lowerTitle.includes('plus') || lowerTitle.includes('14 plus')) return '14_plus';
    }

    return null;
}

// Test on actual titles from database
const testTitles = [
    "iPhone 16e",
    "iPhone 14 5G 128GB for T-Mobile and MetroPCS, Excellent Condition!",
    "iPhone 15 plus 128g Tmobile / Metro",
    "iPhone 15 Pro Max 256GB",
    "iPhone 16 Pro 128GB",
    "iPhone 14 Plus 256GB"
];

console.log("🧪 Testing Variant Detection on Real Database Titles:");
console.log("=" .repeat(60));

testTitles.forEach(title => {
    const variant = detectiPhoneVariant(title);
    console.log(`"${title}"`);
    console.log(`  → Variant: ${variant || 'None'}`);
    console.log("");
});