// Phone Flipping Dashboard React App - Enhanced for Individual Listings with Table View
const { useState, useEffect, useCallback } = React;

// Function to truncate text every 15 characters with proper line breaks
const truncateText = (text, maxChars = 15) => {
    if (!text) return '';

    let result = '';
    for (let i = 0; i < text.length; i += maxChars) {
        if (i > 0) result += '\n';
        result += text.substring(i, i + maxChars);
    }
    return result;
};

// Main Dashboard Component
const Dashboard = () => {
    const [phoneListings, setPhoneListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(null);
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    const [error, setError] = useState(null);
    const [duplicateInfo, setDuplicateInfo] = useState({ total: 0, duplicates: 0, unique: 0 });

    // Filtering states
    const [selectedModels, setSelectedModels] = useState(['all']);
    const [selectedGenerations, setSelectedGenerations] = useState(['all']);
    const [selectedSearchCities, setSelectedSearchCities] = useState(['all']);  // Search city filter
    const [selectedTimeRanges, setSelectedTimeRanges] = useState(['all']);  // Time-based filter
    const [priceRange, setPriceRange] = useState({ min: 0, max: 10000 });
    const [sortBy, setSortBy] = useState('price');
    const [sortOrder, setSortOrder] = useState('asc');
    const [searchTerm, setSearchTerm] = useState('');
    const [showHidden, setShowHidden] = useState(false);
    const [showFavorites, setShowFavorites] = useState(false);

    // Price range editing states
    const [priceRangePopup, setPriceRangePopup] = useState({ show: false, generation: '' });
    const [editingPriceRange, setEditingPriceRange] = useState({ min: '', max: '' });
    const [generationPriceRanges, setGenerationPriceRanges] = useState({});

    // iPhone variant states
    const [selectedVariants, setSelectedVariants] = useState([]);
    const [variantPriceRanges, setVariantPriceRanges] = useState({});
    const [variantPopup, setVariantPopup] = useState({ show: false, variant: '' });
    const [editingVariantPriceRange, setEditingVariantPriceRange] = useState({ min: '', max: '' });

    // Always dark mode
    useEffect(() => {
        // Add dark mode class to both html and body
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');

        // Also set a fallback background color
        document.body.style.backgroundColor = '#0d1117';
        document.body.style.color = '#f0f6fc';
    }, []);

    // Swipe handlers - improved for iOS/iPad
    const handleTouchStart = (e, listingId) => {
        const touch = e.touches[0];
        const row = e.currentTarget;

        // Store initial touch data with page coordinates for better iOS support
        row.dataset.startX = touch.pageX.toString();
        row.dataset.startY = touch.pageY.toString();
        row.dataset.listingId = listingId;
        row.dataset.startTime = Date.now().toString();
        row.classList.add('swiping');

        // Reset any previous animations
        row.classList.remove('swiped-right');
        row.style.transform = 'translateX(0)';

        // Prevent default to avoid iOS scrolling issues during swipe
        e.preventDefault();
    };

    const handleTouchMove = (e) => {
        if (!e.currentTarget.dataset.startX) return;

        const touch = e.touches[0];
        const startX = parseFloat(e.currentTarget.dataset.startX);
        const startY = parseFloat(e.currentTarget.dataset.startY);
        const currentX = touch.pageX;
        const currentY = touch.pageY;
        const diffX = currentX - startX;
        const diffY = currentY - startY;

        // Check if it's a horizontal swipe (more horizontal than vertical)
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 15) {
            // Prevent vertical scroll during horizontal swipe
            e.preventDefault();

            // Only allow right swipe (positive diffX)
            if (diffX > 0) {
                // Limit the transform to prevent over-swiping
                const limitedX = Math.min(diffX, window.innerWidth);
                e.currentTarget.style.transform = `translateX(${limitedX}px)`;

                    } else {
                e.currentTarget.style.transform = 'translateX(0)';
            }
        }
    };

    const handleTouchEnd = (e) => {
        const row = e.currentTarget;
        const startX = parseFloat(row.dataset.startX);
        const startTime = parseFloat(row.dataset.startTime);
        const listingId = row.dataset.listingId;

        if (!startX || !startTime) return;

        const touch = e.changedTouches[0];
        const currentX = touch.pageX;
        const diffX = currentX - startX;
        const timeDiff = Date.now() - startTime;

        // Reset swiping state
        row.classList.remove('swiping');

        // Check if it's a significant right swipe (more than 80px or quick swipe)
        if ((diffX > 80) || (diffX > 40 && timeDiff < 300)) {
            // Provide haptic feedback if available (iOS)
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }

            // Hide the listing immediately and let React handle the animation
            toggleHideItem(listingId, false);

            // Keep the visual swipe animation smooth
            row.style.transform = 'translateX(100%)';
            row.style.opacity = '0';

            // Clean up immediately
            setTimeout(() => {
                row.style.transform = '';
                row.style.opacity = '';
            }, 50);
        } else {
            // Animate back to original position
            row.style.transform = 'translateX(0)';
        }

    
        // Clean up dataset
        delete row.dataset.startX;
        delete row.dataset.startY;
        delete row.dataset.listingId;
        delete row.dataset.startTime;
    };

    // Also handle mouse events for desktop testing
    const handleMouseDown = (e, listingId) => {
        const row = e.currentTarget;
        row.dataset.startX = e.clientX.toString();
        row.dataset.startY = e.clientY.toString();
        row.dataset.listingId = listingId;
        row.dataset.startTime = Date.now().toString();
        row.classList.add('swiping');
        row.style.transform = 'translateX(0)';

        // Add mouse move and up listeners
        const handleMouseMove = (e) => {
            if (!row.dataset.startX) return;

            const startX = parseFloat(row.dataset.startX);
            const startY = parseFloat(row.dataset.startY);
            const diffX = e.clientX - startX;
            const diffY = e.clientY - startY;

            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 15) {
                if (diffX > 0) {
                    row.style.transform = `translateX(${diffX}px)`;
                } else {
                    row.style.transform = 'translateX(0)';
                }
            }
        };

        const handleMouseUp = (e) => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);

            const startX = parseFloat(row.dataset.startX);
            const startTime = parseFloat(row.dataset.startTime);
            const listingId = row.dataset.listingId;
            const diffX = e.clientX - startX;
            const timeDiff = Date.now() - startTime;

            row.classList.remove('swiping');

            if ((diffX > 80) || (diffX > 40 && timeDiff < 300)) {
                // Hide immediately and animate smoothly
                toggleHideItem(listingId, false);
                row.style.transform = 'translateX(100%)';
                row.style.opacity = '0';

                // Clean up immediately
                setTimeout(() => {
                    row.style.transform = '';
                    row.style.opacity = '';
                }, 50);
            } else {
                row.style.transform = 'translateX(0)';
            }

            delete row.dataset.startX;
            delete row.dataset.startY;
            delete row.dataset.listingId;
            delete row.dataset.startTime;
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    };

    // Calculate statistics from phone listings
    const calculateStats = useCallback(() => {
        if (phoneListings.length === 0) {
            return {
                totalListings: 0,
                totalValue: 0,
                averagePrice: 0,
                uniqueModels: 0,
                topModel: { name: 'N/A', count: 0 },
                priceRange: { min: 0, max: 0 }
            };
        }

        const totalValue = phoneListings.reduce((sum, listing) => sum + (listing.price || 0), 0);
        const averagePrice = totalValue / phoneListings.length;
        const uniqueModels = new Set(phoneListings.map(l => l.model)).size;

        // Find top model
        const modelCounts = {};
        phoneListings.forEach(listing => {
            const model = listing.model || 'Unknown';
            modelCounts[model] = (modelCounts[model] || 0) + 1;
        });

        const topModel = Object.entries(modelCounts).reduce((max, [model, count]) =>
            count > max.count ? { name: model, count } : max, { name: 'N/A', count: 0 });

        const prices = phoneListings.map(l => l.price || 0);
        const priceRange = {
            min: Math.min(...prices),
            max: Math.max(...prices)
        };

        return {
            totalListings: phoneListings.length,
            totalValue,
            averagePrice,
            uniqueModels,
            topModel,
            priceRange
        };
    }, [phoneListings]);

    // Get unique models for filter dropdown
    const getUniqueModels = useCallback(() => {
        const models = new Set(phoneListings.map(l => l.model || 'Unknown'));
        return Array.from(models).sort();
    }, [phoneListings]);

    // Function to get count for each model category
    const getModelCounts = useCallback(() => {
        const counts = {
            all: phoneListings.length,
            iphone: 0,
            ipad: 0,
            macbook: 0,
            android: 0,
            android_tablet: 0,
            other_computers: 0,
            other: 0
        };

        phoneListings.forEach(listing => {
            const model = (listing.model || 'Unknown').toLowerCase();

            if (model.includes('iphone')) {
                counts.iphone++;
            } else if (model.includes('ipad')) {
                counts.ipad++;
            } else if (model.includes('macbook') || model.includes('mac book')) {
                counts.macbook++;
            } else if (model.includes('samsung') || model.includes('galaxy') || model.includes('pixel') || model.includes('oneplus') || model.includes('lg') || model.includes('sony') || model.includes('motorola') || model.includes('nokia') || model.includes('htc')) {
                counts.android++;
            } else if (model.includes('android tablet') || model.includes('galaxy tab') || model.includes('pixel tablet')) {
                counts.android_tablet++;
            } else if (model.includes('laptop') || model.includes('dell') || model.includes('hp') || model.includes('lenovo') || model.includes('asus') || model.includes('acer') || model.includes('microsoft') || model.includes('surface') || model.includes('pc')) {
                counts.other_computers++;
            } else {
                counts.other++;
            }
        });
        return counts;
    }, [phoneListings]);

    // Function to get count for each generation
    const getGenerationCounts = useCallback(() => {
        const counts = { all: 0, '17': 0, '16': 0, '15': 0, '14': 0, older: 0 };
        phoneListings.forEach(listing => {
            const model = listing.model || '';
            if (model.toLowerCase().includes('iphone')) {
                counts.all++;
                if (model.includes('17')) counts['17']++;
                else if (model.includes('16')) counts['16']++;
                else if (model.includes('15')) counts['15']++;
                else if (model.includes('14')) counts['14']++;
                else counts.older++; // 13 and older models
            }
        });
        return counts;
    }, [phoneListings]);

    // Function to toggle model selection
    const toggleModel = useCallback((model) => {
        setSelectedModels(prev => {
            if (model === 'all') {
                // Clear all variant selections when going to 'all'
                setSelectedVariants([]);
                return ['all'];
            }
            let newSelection = prev.includes(model)
                ? prev.filter(m => m !== model)
                : [...prev.filter(m => m !== 'all'), model];

            // If no models selected, default to 'all'
            if (newSelection.length === 0) {
                setSelectedVariants([]);
                return ['all'];
            }

            // Clear variant and generation selections if iPhone is no longer selected
            if (!newSelection.some(m => m.toLowerCase().includes('iphone'))) {
                setSelectedVariants([]);
                setSelectedGenerations(['all']);
            }

            return newSelection;
        });
    }, []);

    // Function to toggle generation selection
    const toggleGeneration = useCallback((generation) => {
        setSelectedGenerations(prev => {
            if (generation === 'all') {
                // Clear all variant selections when going to 'all'
                setSelectedVariants([]);
                return ['all'];
            }
            let newSelection = prev.includes(generation)
                ? prev.filter(g => g !== generation)
                : [...prev.filter(g => g !== 'all'), generation];

            // If no generations selected, default to 'all'
            if (newSelection.length === 0) {
                setSelectedVariants([]);
                return ['all'];
            }

            // Don't aggressively clear variants - let users manage their selections
            // Variants will be validated during filtering instead

            return newSelection;
        });
    }, []);

    // Price range editing functions
    const openPriceRangePopup = useCallback((generation) => {
        const currentRange = generationPriceRanges[generation] || { min: '', max: '' };
        setEditingPriceRange(currentRange);
        setPriceRangePopup({ show: true, generation });
    }, [generationPriceRanges]);

    const closePriceRangePopup = useCallback(() => {
        setPriceRangePopup({ show: false, generation: '' });
        setEditingPriceRange({ min: '', max: '' });
    }, []);

    const savePriceRange = useCallback(() => {
        const { generation } = priceRangePopup;
        if (generation) {
            setGenerationPriceRanges(prev => ({
                ...prev,
                [generation]: {
                    min: editingPriceRange.min || '',
                    max: editingPriceRange.max || ''
                }
            }));
        }
        closePriceRangePopup();
    }, [priceRangePopup, editingPriceRange, closePriceRangePopup]);

    const handlePriceRangeChange = useCallback((field, value) => {
        // Only allow numbers
        const numValue = value.replace(/[^0-9]/g, '');
        setEditingPriceRange(prev => ({
            ...prev,
            [field]: numValue
        }));
    }, []);

    // iPhone variant functions
    const getVariantsForGeneration = useCallback((generation) => {
        const variantMap = {
            '17': ['pro_max', 'pro', 'air', 'regular'],  // iPhone 17 variants
            '16': ['pro_max', 'pro', 'plus', 'e', 'regular'],  // iPhone 16 variants
            '15': ['pro_max', 'pro', 'plus', 'regular'],  // iPhone 15 variants
            '14': ['pro_max', 'pro', 'plus', 'regular'],  // iPhone 14 variants
            'older': ['older_model']  // Single variant for all older models
        };
        return variantMap[generation] || [];
    }, []);

    const detectiPhoneVariant = useCallback((title) => {
        if (!title) return null;

        const lowerTitle = title.toLowerCase();

        // Skip obvious non-phone listings (business ads, wholesale, bulk listings)
        if (lowerTitle.includes('business') ||
            lowerTitle.includes('wholesale') ||
            lowerTitle.includes('bulk') ||
            lowerTitle.includes('first business') ||
            lowerTitle.includes('your first business') ||
            lowerTitle.includes('multiple') ||
            lowerTitle.includes('lot of') ||
            lowerTitle.includes('bundle') ||
            lowerTitle.includes('collection') ||
            lowerTitle.includes('various') ||
            lowerTitle.includes('assorted')) {
            // Silently skip business listings
            return null;
        }

        // iPhone 17 variants - require more specific matching
        if (lowerTitle.includes('iphone 17')) {
            // Look for specific patterns that indicate actual phones, not business listings
            if ((lowerTitle.includes('iphone 17 pro max') && !lowerTitle.includes('iphone 17,')) ||
                (lowerTitle.includes('17 pro max') && !lowerTitle.includes('17,'))) {
                return '17_pro_max';
            }
            if ((lowerTitle.includes('iphone 17 pro') && !lowerTitle.includes('iphone 17,')) ||
                (lowerTitle.includes('17 pro') && !lowerTitle.includes('17,'))) {
                return '17_pro';
            }
            if ((lowerTitle.includes('iphone 17 air') && !lowerTitle.includes('iphone 17,')) ||
                (lowerTitle.includes('17 air') && !lowerTitle.includes('17,'))) {
                return '17_air';
            }
            // Regular iPhone 17 (no specific variant mentioned, but clean listing)
            if (!lowerTitle.includes('pro') && !lowerTitle.includes('air') && !lowerTitle.includes('max') &&
                !lowerTitle.includes('iphone 17,') && !lowerTitle.includes('17,')) {
                return '17_regular';
            }
        }

        // iPhone 16 variants - require more specific matching
        if (lowerTitle.includes('iphone 16')) {
            // Skip business/multiple listings that just mention iPhone 16 along with other models
            if (lowerTitle.includes('iphone 16,') || lowerTitle.includes('16,')) {
                return null;
            }

            if ((lowerTitle.includes('iphone 16 pro max') || lowerTitle.includes('16 pro max')) &&
                !lowerTitle.includes('iphone 16,') && !lowerTitle.includes('16,')) {
                return '16_pro_max';
            }
            if ((lowerTitle.includes('iphone 16 pro') || lowerTitle.includes('16 pro')) &&
                !lowerTitle.includes('iphone 16,') && !lowerTitle.includes('16,')) {
                return '16_pro';
            }
            if ((lowerTitle.includes('iphone 16 plus') || lowerTitle.includes('16 plus')) &&
                !lowerTitle.includes('iphone 16,') && !lowerTitle.includes('16,')) {
                return '16_plus';
            }
            if ((lowerTitle.includes('16e') || lowerTitle.includes('16 e')) &&
                !lowerTitle.includes('iphone 16,') && !lowerTitle.includes('16,')) {
                return '16_e';
            }
            // Regular iPhone 16 (no specific variant mentioned, but clean listing)
            if (!lowerTitle.includes('pro') && !lowerTitle.includes('plus') && !lowerTitle.includes('16e') && !lowerTitle.includes('max') &&
                !lowerTitle.includes('iphone 16,') && !lowerTitle.includes('16,')) {
                return '16_regular';
            }
        }

        // iPhone 15 variants - require more specific matching
        if (lowerTitle.includes('iphone 15')) {
            // Skip business/multiple listings
            if (lowerTitle.includes('iphone 15,') || lowerTitle.includes('15,')) {
                return null;
            }

            if ((lowerTitle.includes('iphone 15 pro max') || lowerTitle.includes('15 pro max')) &&
                !lowerTitle.includes('iphone 15,') && !lowerTitle.includes('15,')) {
                return '15_pro_max';
            }
            if ((lowerTitle.includes('iphone 15 pro') || lowerTitle.includes('15 pro')) &&
                !lowerTitle.includes('iphone 15,') && !lowerTitle.includes('15,')) {
                return '15_pro';
            }
            if ((lowerTitle.includes('iphone 15 plus') || lowerTitle.includes('15 plus')) &&
                !lowerTitle.includes('iphone 15,') && !lowerTitle.includes('15,')) {
                return '15_plus';
            }
            // Regular iPhone 15 (no specific variant mentioned, but clean listing)
            if (!lowerTitle.includes('pro') && !lowerTitle.includes('plus') && !lowerTitle.includes('max') &&
                !lowerTitle.includes('iphone 15,') && !lowerTitle.includes('15,')) {
                return '15_regular';
            }
        }

        // iPhone 14 variants - require more specific matching
        if (lowerTitle.includes('iphone 14')) {
            // Skip business/multiple listings
            if (lowerTitle.includes('iphone 14,') || lowerTitle.includes('14,')) {
                return null;
            }

            if ((lowerTitle.includes('iphone 14 pro max') || lowerTitle.includes('14 pro max')) &&
                !lowerTitle.includes('iphone 14,') && !lowerTitle.includes('14,')) {
                return '14_pro_max';
            }
            if ((lowerTitle.includes('iphone 14 pro') || lowerTitle.includes('14 pro')) &&
                !lowerTitle.includes('iphone 14,') && !lowerTitle.includes('14,')) {
                return '14_pro';
            }
            if ((lowerTitle.includes('iphone 14 plus') || lowerTitle.includes('14 plus')) &&
                !lowerTitle.includes('iphone 14,') && !lowerTitle.includes('14,')) {
                return '14_plus';
            }
            // Regular iPhone 14 (no specific variant mentioned, but clean listing)
            if (!lowerTitle.includes('pro') && !lowerTitle.includes('plus') && !lowerTitle.includes('max') &&
                !lowerTitle.includes('iphone 14,') && !lowerTitle.includes('14,')) {
                return '14_regular';
            }
        }

        // iPhone 13 and older - all categorized as "Older Model"
        if (lowerTitle.includes('iphone 13') || lowerTitle.includes('iphone 12') ||
            lowerTitle.includes('iphone 11') || lowerTitle.includes('iphone x') ||
            lowerTitle.includes('iphone 10') || lowerTitle.includes('iphone 8') ||
            lowerTitle.includes('iphone 7') || lowerTitle.includes('iphone 6') ||
            lowerTitle.includes('iphone 5') || lowerTitle.includes('iphone 4')) {
            return 'older_model';
        }

        return null;
    }, []);

    const updateListingsWithVariantData = useCallback((listings) => {
        // Silently process variants without individual logging
        let variantCount = 0;

        const updatedListings = listings.map(listing => {
            const variant = detectiPhoneVariant(listing.title);
            if (variant) {
                variantCount++;
            }
            return {
                ...listing,
                variant: variant || null
            };
        });

        // Variant detection complete (silently processed)
        return updatedListings;
    }, [detectiPhoneVariant]);

    const toggleVariant = useCallback((variant) => {
        setSelectedVariants(prev => {
            let newSelection = prev.includes(variant)
                ? prev.filter(v => v !== variant)
                : [...prev, variant];
            return newSelection;
        });
    }, []);

    const openVariantPopup = useCallback((variant) => {
        const currentRange = variantPriceRanges[variant] || { min: '', max: '' };
        setEditingVariantPriceRange(currentRange);
        setVariantPopup({ show: true, variant });
    }, [variantPriceRanges]);

    const closeVariantPopup = useCallback(() => {
        setVariantPopup({ show: false, variant: '' });
        setEditingVariantPriceRange({ min: '', max: '' });
    }, []);

    const saveVariantPriceRange = useCallback(() => {
        const { variant } = variantPopup;
        if (variant) {
            setVariantPriceRanges(prev => ({
                ...prev,
                [variant]: {
                    min: editingVariantPriceRange.min || '',
                    max: editingVariantPriceRange.max || ''
                }
            }));
        }
        closeVariantPopup();
    }, [variantPopup, editingVariantPriceRange, closeVariantPopup]);

    const handleVariantPriceRangeChange = useCallback((field, value) => {
        const numValue = value.replace(/[^0-9]/g, '');
        setEditingVariantPriceRange(prev => ({
            ...prev,
            [field]: numValue
        }));
    }, []);

    // Function to get unique search cities for filtering
    const getUniqueSearchCities = useCallback(() => {
        const cities = new Set();
        phoneListings.forEach(listing => {
            const city = listing.search_city;
            if (city && city !== 'Unknown') {
                cities.add(city);
            }
        });

        // Debug: Log what cities we found and Phoenix-specific info
        const cityList = Array.from(cities).sort();
        console.log('🏙️ All cities in database:', cityList);

        const phoenixListings = phoneListings.filter(l => l.search_city === 'Phoenix');
        console.log(`🔍 Found ${phoenixListings.length} Phoenix listings:`, phoenixListings.map(l => ({
            title: l.title,
            model: l.model,
            variant: l.variant,
            isIphone: l.title.toLowerCase().includes('iphone')
        })));

        return cityList;
    }, [phoneListings]);

    // Function to get count for each search city
    const getSearchCityCounts = useCallback(() => {
        const counts = { all: phoneListings.length };
        phoneListings.forEach(listing => {
            const city = listing.search_city || 'Unknown';
            counts[city] = (counts[city] || 0) + 1;
        });
        return counts;
    }, [phoneListings]);

    // Function to toggle search city selection
    const toggleSearchCity = useCallback((searchCity) => {
        setSelectedSearchCities(prev => {
            if (searchCity === 'all') {
                return ['all'];
            }
            let newSelection = prev.includes(searchCity)
                ? prev.filter(c => c !== searchCity)
                : [...prev.filter(c => c !== 'all'), searchCity];

            // If no search cities selected, default to 'all'
            if (newSelection.length === 0) {
                return ['all'];
            }
            return newSelection;
        });
    }, []);

    // Function to toggle time range selection
    const toggleTimeRange = useCallback((timeRange) => {
        setSelectedTimeRanges(prev => {
            if (timeRange === 'all') {
                return ['all'];
            }
            let newSelection = prev.includes(timeRange)
                ? prev.filter(t => t !== timeRange)
                : [...prev.filter(t => t !== 'all'), timeRange];

            // If no time ranges selected, default to 'all'
            if (newSelection.length === 0) {
                return ['all'];
            }

            return newSelection;
        });
    }, []);

    // Function to toggle hide/unhide an item
    const toggleHideItem = async (listingId, currentlyHidden) => {
        try {
            const listingRef = firebase.database().ref(`phone_listings/${listingId}`);
            await listingRef.update({ hidden: !currentlyHidden });
            console.log(`✅ ${currentlyHidden ? 'Unhid' : 'Hidden'} item ${listingId}`);
            fetchData(); // Refresh data
        } catch (error) {
            console.error('❌ Error toggling hide status:', error);
        }
    };

    // Function to favorite an item
    const favoriteItem = async (listingId) => {
        try {
            const listingRef = firebase.database().ref(`phone_listings/${listingId}`);
            const snapshot = await listingRef.once('value');
            const currentData = snapshot.val() || {};
            const isCurrentlyFavorited = currentData.favorited || false;

            await listingRef.update({ favorited: !isCurrentlyFavorited });
            console.log(`✅ ${isCurrentlyFavorited ? 'Unfavorited' : 'Favorited'} item ${listingId}`);
            fetchData(); // Refresh data
        } catch (error) {
            console.error('❌ Error favoriting item:', error);
        }
    };

    // Function to delete only currently displayed listings
    const deleteVisibleListings = async () => {
        const currentListings = getFilteredListings();

        if (currentListings.length === 0) {
            console.log('No listings to delete.');
            return;
        }

        // Confirmation dialog
        const isConfirmed = window.confirm(
            `⚠️ Are you sure you want to delete ${currentListings.length} currently displayed listings?\n\n` +
            "This action will delete only the listings that are currently visible based on your filters.\n\n" +
            "This cannot be undone!"
        );

        if (!isConfirmed) return;

        try {
            // Show loading state
            const clearButton = document.getElementById('clear-database-btn');
            if (clearButton) {
                clearButton.disabled = true;
                clearButton.textContent = `🗑️ Deleting 0/${currentListings.length}...`;
            }

            console.log(`🗑️ Deleting ${currentListings.length} visible listings from Firebase...`);

            // Delete items in batches to avoid overwhelming Firebase
            const batchSize = 10;
            let deletedCount = 0;

            for (let i = 0; i < currentListings.length; i += batchSize) {
                const batch = currentListings.slice(i, i + batchSize);

                // Update button progress
                if (clearButton) {
                    clearButton.textContent = `🗑️ Deleting ${deletedCount}/${currentListings.length}...`;
                }

                // Delete this batch
                const deletePromises = batch.map(listing => {
                    const listingRef = firebase.database().ref(`phone_listings/${listing.id}`);
                    return listingRef.remove();
                });

                await Promise.all(deletePromises);
                deletedCount += batch.length;

                // Small delay between batches to prevent overwhelming
                if (i + batchSize < currentListings.length) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }

            console.log(`✅ ${currentListings.length} listings deleted from Firebase`);

            // Reset button
            if (clearButton) {
                clearButton.disabled = false;
                clearButton.textContent = `🗑️ Delete ${filteredListings.length - currentListings.length}`;
            }

            // Show success message
            console.log(`✅ Successfully deleted ${currentListings.length} listings!`);

            // Update local state immediately for smooth UX
            const deletedIds = new Set(currentListings.map(l => l.id));
            setPhoneListings(prev => prev.filter(listing => !deletedIds.has(listing.id)));

        } catch (error) {
            console.error('❌ Error deleting listings:', error);
            console.error('❌ Failed to delete listings. Please try again.');

            // Reset button on error
            const clearButton = document.getElementById('clear-database-btn');
            if (clearButton) {
                clearButton.disabled = false;
                clearButton.textContent = `🗑️ Delete ${filteredListings.length}`;
            }
        }
    };

    // Function to clear all data from database and push to GitHub
    const clearDatabaseAndPushToGitHub = async () => {
        // Confirmation dialog with expanded information
        const isConfirmed = window.confirm(
            "⚠️ Are you sure you want to delete all data from both databases?\n\n" +
            "This action will clear:\n" +
            "• All phone listings from main database\n" +
            "• All processed hashes from CSV monitor\n" +
            "• Reset duplicate detection memory\n\n" +
            "This cannot be undone!"
        );

        if (!isConfirmed) return;

        try {
            // Show loading state
            const clearButton = document.getElementById('clear-database-btn');
            if (clearButton) {
                clearButton.disabled = true;
                clearButton.textContent = '🗑️ Clearing...';
            }

            console.log('🗑️ Clearing all phone listings from Firebase...');

            // Clear all phone listings from Firebase
            const listingsRef = firebase.database().ref('phone_listings');
            await listingsRef.remove();

            console.log('🗑️ Clearing processed hashes from CSV monitor...');

            // Clear all processed hashes from CSV monitor
            const processedHashesRef = firebase.database().ref('processed_hashes');
            await processedHashesRef.remove();

            console.log('✅ All data cleared from Firebase');
            console.log('📤 Pushing changes to GitHub...');

            // Success message logged to console
            console.log('✅ Database cleared successfully!');
            console.log('All phone listings and processed hashes have been deleted from Firebase.');
            console.log('🔗 Firebase Console Links:');
            console.log('• Main Database: https://console.firebase.google.com/project/phone-flipping/database/phone-flipping-default-rtdb/data/~2Fphone_listings');
            console.log('• CSV Monitor: https://console.firebase.google.com/project/phone-flipping/database/phone-flipping-default-rtdb/data/~2Fprocessed_hashes');
            console.log('Note: GitHub integration requires backend setup.');

            // Refresh data
            fetchData();

        } catch (error) {
            console.error('❌ Error clearing database:', error);
            console.error('❌ Failed to clear database. Please try again.');
        } finally {
            // Reset button state
            const clearButton = document.getElementById('clear-database-btn');
            if (clearButton) {
                clearButton.disabled = false;
                clearButton.textContent = '🗑️';
            }
        }
    };

    // Toggle sort order for a column
    const toggleSort = (column) => {
        if (sortBy === column) {
            // If same column, toggle sort order
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            // If different column, set new column with default ascending order
            setSortBy(column);
            setSortOrder('desc'); // Default to descending for most columns
        }
    };

    // Filter and sort listings
    const getFilteredListings = useCallback(() => {
        let filtered = phoneListings;

        // Pre-compute filter flags to use in model filtering
        const generationFilterActive = !selectedGenerations.includes('all');
        const variantFilterActive = selectedVariants.length > 0;

        // Filter by model categories (multiple selection)
        if (!selectedModels.includes('all')) {
            filtered = filtered.filter(listing => {
                const model = (listing.model || 'Unknown').toLowerCase();
                const isIphone = model.includes('iphone');

                // For iPhones, we need to handle generation/variant filtering separately
                // So if iPhone is selected and generation/variant filtering is active, let iPhones through
                if (isIphone && (generationFilterActive || variantFilterActive) && selectedModels.includes('iphone')) {
                    return true; // Let generation/variant filters handle iPhones
                }

                // Check if this listing matches any selected category
                return selectedModels.some(selectedCategory => {
                    if (selectedCategory === 'iphone') {
                        return model.includes('iphone');
                    } else if (selectedCategory === 'ipad') {
                        return model.includes('ipad');
                    } else if (selectedCategory === 'macbook') {
                        return model.includes('macbook') || model.includes('mac book');
                    } else if (selectedCategory === 'android') {
                        return model.includes('samsung') || model.includes('galaxy') || model.includes('pixel') || model.includes('oneplus') || model.includes('lg') || model.includes('sony') || model.includes('motorola') || model.includes('nokia') || model.includes('htc');
                    } else if (selectedCategory === 'android_tablet') {
                        return model.includes('android tablet') || model.includes('galaxy tab') || model.includes('pixel tablet');
                    } else if (selectedCategory === 'other_computers') {
                        return model.includes('laptop') || model.includes('dell') || model.includes('hp') || model.includes('lenovo') || model.includes('asus') || model.includes('acer') || model.includes('microsoft') || model.includes('surface') || model.includes('pc');
                    } else if (selectedCategory === 'other') {
                        return !model.includes('iphone') && !model.includes('ipad') && !model.includes('macbook') &&
                               !model.includes('samsung') && !model.includes('galaxy') && !model.includes('pixel') && !model.includes('oneplus') &&
                               !model.includes('lg') && !model.includes('sony') && !model.includes('motorola') && !model.includes('nokia') && !model.includes('htc') &&
                               !model.includes('android tablet') && !model.includes('galaxy tab') && !model.includes('pixel tablet') &&
                               !model.includes('laptop') && !model.includes('dell') && !model.includes('hp') && !model.includes('lenovo') &&
                               !model.includes('asus') && !model.includes('acer') && !model.includes('microsoft') && !model.includes('surface') && !model.includes('pc');
                    }
                    return false;
                });
            });
        }

        // Combine generation and variant filtering - only applies to iPhones

        if (generationFilterActive || variantFilterActive) {
            // Create detailed debug log
            const debugLog = [];
            debugLog.push('🔍 STARTING IPHONE GENERATION/VARIANT FILTERING');
            debugLog.push(`Selected Generations: ${JSON.stringify(selectedGenerations)}`);
            debugLog.push(`Selected Variants: ${JSON.stringify(selectedVariants)}`);
            debugLog.push(`Starting with ${filtered.length} listings`);
            debugLog.push('─'.repeat(60));

            filtered = filtered.filter((listing, index) => {
                const model = listing.model || '';
                const variant = listing.variant || '';
                const isIphone = model && model.toLowerCase().includes('iphone');
                const title = listing.title || '';

                const logEntry = {
                    index: index + 1,
                    title: title.length > 50 ? title.substring(0, 50) + '...' : title,
                    model,
                    variant,
                    isIphone
                };

                // Non-iPhones pass through all filters
                if (!isIphone) {
                    logEntry.result = '✅ PASSED (not iPhone)';
                    logEntry.passed = true;
                    debugLog.push(logEntry);
                    return true;
                }

                // iPhones must pass BOTH filters (AND logic)
                let passesGenerationFilter = true;
                let passesVariantFilter = true;

                // Check generation filter
                if (generationFilterActive) {
                    passesGenerationFilter = selectedGenerations.some(selectedGeneration => {
                        if (selectedGeneration === 'older') {
                            return !model.includes('17') && !model.includes('16') && !model.includes('15') && !model.includes('14');
                        } else {
                            return model.includes(selectedGeneration);
                        }
                    });
                    logEntry.generationFilter = passesGenerationFilter;
                }

                // Check variant filter (support both old and new variant names during transition)
                if (variantFilterActive) {
                    if (!variant) {
                        passesVariantFilter = false; // If variant filtering active but no variant data, exclude
                        logEntry.variantFilter = 'FAILED (no variant data)';
                    } else {
                        const variantMatches = selectedVariants.some(selectedVariant => {
                            // Handle both old variant names (like "17") and new ones (like "17_regular")
                            const match = variant === selectedVariant ||
                                         (selectedVariant === '17_regular' && variant === '17') ||
                                         (selectedVariant === '16_regular' && variant === '16') ||
                                         (selectedVariant === '15_regular' && variant === '15') ||
                                         (selectedVariant === '14_regular' && variant === '14');
                            return match;
                        });
                        passesVariantFilter = variantMatches;
                        logEntry.variantFilter = variantMatches ? 'PASSED' : 'FAILED';
                    }
                }

                const finalResult = passesGenerationFilter && passesVariantFilter;
                logEntry.result = finalResult ? '✅ PASSED' : '❌ EXCLUDED';
                logEntry.passed = finalResult;

                debugLog.push(logEntry);
                return finalResult;
            });

            debugLog.push('─'.repeat(60));
            debugLog.push(`🎯 FINAL RESULT: ${filtered.length} listings remaining`);

            // Store debug log for display but don't print the massive table
            window.lastFilterDebugLog = debugLog;
        }

        // Filter by search cities (multiple selection)
        if (!selectedSearchCities.includes('all')) {
            filtered = filtered.filter(listing => {
                const searchCity = listing.search_city || 'Unknown';
                return selectedSearchCities.includes(searchCity);
            });
        }

        // Filter by time ranges (multiple selection)
        if (!selectedTimeRanges.includes('all')) {
            filtered = filtered.filter(listing => {
                const foundAt = listing.found_at;
                if (!foundAt) return false;

                const now = new Date();
                const foundTime = new Date(foundAt);
                const hoursDiff = (now - foundTime) / (1000 * 60 * 60);

                return selectedTimeRanges.some(selectedRange => {
                    if (selectedRange === 'just_now') {
                        return hoursDiff <= 1;
                    } else if (selectedRange === '12_hours') {
                        return hoursDiff <= 12;
                    } else if (selectedRange === '24_hours') {
                        return hoursDiff <= 24;
                    } else if (selectedRange === '3_days') {
                        return hoursDiff <= 72;
                    }
                    return false;
                });
            });
        }

        // Filter by price range
        filtered = filtered.filter(listing => {
            const price = listing.price || 0;
            return price >= priceRange.min && price <= priceRange.max;
        });

        // Auto-hide listings that mention "ship to you"
        filtered = filtered.map(listing => {
            const title = (listing.title || '').toLowerCase();
            const location = (listing.location || '').toLowerCase();

            if (title.includes('ship to you') || location.includes('ship to you')) {
                // Auto-hide by setting hidden flag in database if not already hidden
                if (!listing.hidden) {
                    setTimeout(() => hideItem(listing.id), 0);
                }
                return { ...listing, hidden: true };
            }
            return listing;
        });

        // Filter by search term
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filtered = filtered.filter(listing =>
                (listing.title || '').toLowerCase().includes(term) ||
                (listing.model || '').toLowerCase().includes(term) ||
                (listing.location || '').toLowerCase().includes(term)
            );
        }

        // Filter by hidden/favorite status
        if (showFavorites) {
            filtered = filtered.filter(listing => listing.favorited);
        }
        if (!showHidden) {
            filtered = filtered.filter(listing => !listing.hidden);
        }

        // Sort listings
        filtered.sort((a, b) => {
            let aValue = a[sortBy] || '';
            let bValue = b[sortBy] || '';

            if (sortBy === 'price' || sortBy === 'row_number') {
                aValue = parseFloat(aValue) || 0;
                bValue = parseFloat(bValue) || 0;
            } else if (sortBy === 'found_at') {
                aValue = safeParseDate(aValue).getTime();
                bValue = safeParseDate(bValue).getTime();
            } else {
                aValue = aValue.toString().toLowerCase();
                bValue = bValue.toString().toLowerCase();
            }

            if (sortOrder === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });

        return filtered;
    }, [phoneListings, selectedModels, selectedGenerations, selectedVariants, selectedSearchCities, selectedTimeRanges, priceRange, sortBy, sortOrder, searchTerm, showHidden, showFavorites, safeParseDate, getRelativeTime]);

    // Helper function to safely parse date
    const safeParseDate = useCallback((dateString) => {
        if (!dateString) return new Date(0); // Default to epoch if no date

        try {
            const date = new Date(dateString);
            // Check if date is invalid
            if (isNaN(date.getTime())) {
                console.warn(`Invalid date format: ${dateString}`);
                return new Date(0);
            }
            return date;
        } catch (error) {
            console.warn(`Error parsing date: ${dateString}`, error);
            return new Date(0);
        }
    }, []);

    // Helper function to get relative time
    const getRelativeTime = useCallback((dateString) => {
        const date = safeParseDate(dateString);
        if (date.getTime() === 0) {
            return 'No date';
        }

        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMinutes < 1) {
            return 'Just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes}m`;
        } else if (diffHours < 24) {
            return `${diffHours}h`;
        } else {
            return `${diffDays}d`;
        }
    }, [safeParseDate]);

    // Function to remove duplicates and keep oldest entry
    const removeDuplicatesKeepOldest = useCallback((listings) => {
        const linkMap = new Map();

        listings.forEach(listing => {
            const link = listing.link;
            if (!link) return;

            const existingEntry = linkMap.get(link);

            if (!existingEntry) {
                // First time seeing this link, add it
                linkMap.set(link, listing);
            } else {
                // Duplicate found, keep the oldest one
                const existingTime = safeParseDate(existingEntry.detected_at || existingEntry.found_at).getTime();
                const newTime = safeParseDate(listing.detected_at || listing.found_at).getTime();

                // Log for debugging
                if (existingTime === 0 || newTime === 0) {
                    console.log('Date parsing issue:', {
                        link: link.substring(0, 50),
                        existingDate: existingEntry.detected_at || existingEntry.found_at,
                        newDate: listing.detected_at || listing.found_at,
                        existingTime,
                        newTime
                    });
                }

                if (newTime < existingTime) {
                    // New entry is older, replace the existing one
                    console.log(`Replacing duplicate with older entry for link: ${link.substring(0, 50)}...`);
                    linkMap.set(link, listing);
                }
                // If existing entry is older, keep it (do nothing)
            }
        });

        const uniqueListings = Array.from(linkMap.values());
        const duplicateCount = listings.length - uniqueListings.length;

        if (duplicateCount > 0) {
            console.log(`🔄 Removed ${duplicateCount} duplicates, keeping ${uniqueListings.length} unique listings`);
        }

        return uniqueListings;
    }, [safeParseDate]);

    // Fetch data from Firebase
    const fetchData = useCallback(async () => {
        try {
            console.log('🔄 Fetching data from Firebase...');

            // Fetch phone listings
            const listingsRef = firebase.database().ref('phone_listings');
            const listingsSnapshot = await listingsRef.once('value');

            let listings = [];

            if (listingsSnapshot.exists()) {
                const data = listingsSnapshot.val();
                const rawListings = Object.keys(data).map(key => ({
                    id: key,
                    ...data[key]
                }));
                console.log(`✅ Fetched ${rawListings.length} total phone listings`);

                // Remove duplicates, keeping oldest entries
                listings = removeDuplicatesKeepOldest(rawListings);

                // Update listings with variant data
                listings = updateListingsWithVariantData(listings);

                // Update duplicate info
                const duplicateCount = rawListings.length - listings.length;
                setDuplicateInfo({
                    total: rawListings.length,
                    duplicates: duplicateCount,
                    unique: listings.length
                });

                // Batch update existing entries in database with variant data
                const updates = {};
                listings.forEach(listing => {
                    if (listing.variant) {
                        const originalListing = rawListings.find(r => r.id === listing.id);
                        if (!originalListing || !originalListing.variant) {
                            updates[`phone_listings/${listing.id}/variant`] = listing.variant;
                            console.log(`📝 Adding variant ${listing.variant} to: ${listing.title}`);
                        }
                    }
                });

                if (Object.keys(updates).length > 0) {
                    database.ref().update(updates)
                        .then(() => {
                            console.log(`✅ Updated ${Object.keys(updates).length} entries with variant data`);
                        })
                        .catch(error => {
                            console.error('❌ Error updating variant data:', error);
                        });
                } else {
                    console.log(`ℹ️ No new variant data to add`);
                }
            }

            setPhoneListings(listings);
            setLastUpdated(new Date());
            setConnectionStatus('connected');
            setError(null);

            setLoading(false);
        } catch (error) {
            console.error('❌ Error fetching data:', error);
            setError(error.message);
            setConnectionStatus('error');
            setLoading(false);
        }
    }, [removeDuplicatesKeepOldest]);

    // Setup Firebase listener and periodic polling
    useEffect(() => {
        // Initial data fetch
        fetchData();

        // Setup Firebase real-time listeners
        const listingsRef = firebase.database().ref('phone_listings');

        const onListingsChange = (snapshot) => {
            console.log('🔔 Phone listings data changed');
            fetchData();
        };

        // Setup real-time listeners
        listingsRef.on('value', onListingsChange);

        // Cleanup
        return () => {
            listingsRef.off('value', onListingsChange);
        };
    }, [fetchData]);

    const stats = calculateStats();
    const filteredListings = getFilteredListings();
    const uniqueModels = getUniqueModels();
    const modelCounts = getModelCounts();
    const generationCounts = getGenerationCounts();
    const searchCityCounts = getSearchCityCounts();

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <h2>Loading Phone Flipping Dashboard...</h2>
                <p>Connecting to Firebase database...</p>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <h1>📱 Dashboard</h1>
            </header>

            {error && (
                <div className="error-message">
                    <h3>⚠️ Connection Error</h3>
                    <p>{error}</p>
                </div>
            )}

            
            <section className="filters-section">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                    {/* Results count display */}
                    <div style={{
                        fontSize: '0.9rem',
                        color: '#8b949e',
                        fontWeight: '500'
                    }}>
                        Showing {filteredListings.length} results
                    </div>

                    {/* Delete buttons */}
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                            id="clear-database-btn"
                            onClick={deleteVisibleListings}
                            style={{
                                background: 'transparent',
                                color: '#ff4444',
                                border: '2px solid #ff4444',
                                padding: '8px 16px',
                                borderRadius: '6px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                fontSize: '0.9rem'
                            }}
                            onMouseOver={(e) => {
                                e.target.style.background = '#ff4444';
                                e.target.style.color = 'white';
                                e.target.style.transform = 'translateY(-1px)';
                            }}
                            onMouseOut={(e) => {
                                e.target.style.background = 'transparent';
                                e.target.style.color = '#ff4444';
                                e.target.style.transform = 'translateY(0)';
                            }}
                            title="Delete currently visible listings"
                        >
                            🗑️ Delete {filteredListings.length}
                        </button>

                        <button
                            id="clear-all-database-btn"
                            onClick={clearDatabaseAndPushToGitHub}
                            style={{
                                background: 'transparent',
                                color: '#1877f2',
                                border: '2px solid #1877f2',
                                padding: '8px 16px',
                                borderRadius: '6px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                fontSize: '0.9rem'
                            }}
                            onMouseOver={(e) => {
                                e.target.style.background = '#1877f2';
                                e.target.style.color = 'white';
                                e.target.style.transform = 'translateY(-1px)';
                            }}
                            onMouseOut={(e) => {
                                e.target.style.background = 'transparent';
                                e.target.style.color = '#1877f2';
                                e.target.style.transform = 'translateY(0)';
                            }}
                            title="Delete ALL listings from database"
                        >
                            🗑️ Clear All
                        </button>
                    </div>
                </div>

                {/* Device Category Tags */}
                <div className="model-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                    <button
                        className={`model-tag ${selectedModels.includes('all') ? 'active' : ''}`}
                        onClick={() => toggleModel('all')}
                        style={{
                            background: selectedModels.includes('all') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('all') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        All ({modelCounts.all})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('iphone') ? 'active' : ''}`}
                        onClick={() => toggleModel('iphone')}
                        style={{
                            background: selectedModels.includes('iphone') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('iphone') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        iPhone
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('ipad') ? 'active' : ''}`}
                        onClick={() => toggleModel('ipad')}
                        style={{
                            background: selectedModels.includes('ipad') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('ipad') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        iPad
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('macbook') ? 'active' : ''}`}
                        onClick={() => toggleModel('macbook')}
                        style={{
                            background: selectedModels.includes('macbook') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('macbook') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        MacBook
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('android') ? 'active' : ''}`}
                        onClick={() => toggleModel('android')}
                        style={{
                            background: selectedModels.includes('android') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('android') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Android
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('android_tablet') ? 'active' : ''}`}
                        onClick={() => toggleModel('android_tablet')}
                        style={{
                            background: selectedModels.includes('android_tablet') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('android_tablet') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Android Tablets
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('other_computers') ? 'active' : ''}`}
                        onClick={() => toggleModel('other_computers')}
                        style={{
                            background: selectedModels.includes('other_computers') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('other_computers') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Other Computers
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('other') ? 'active' : ''}`}
                        onClick={() => toggleModel('other')}
                        style={{
                            background: selectedModels.includes('other') ? '#1877f2' : '#1c2128',
                            color: selectedModels.includes('other') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Other
                    </button>
                </div>

                {/* iPhone Generation Tags */}
                {selectedModels.some(model => model && model.toLowerCase().includes('iphone')) && (
                    <div className="generation-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                        <button
                            className={`generation-tag ${selectedGenerations.includes('all') ? 'active' : ''}`}
                            onClick={() => toggleGeneration('all')}
                            style={{
                                background: selectedGenerations.includes('all') ? '#1877f2' : '#1c2128',
                                color: selectedGenerations.includes('all') ? 'white' : '#333',
                                border: '2px solid #1877f2',
                                padding: '8px 16px',
                                borderRadius: '20px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease'
                            }}
                        >
                            All iPhones
                        </button>
                        {['17', '16', '15', '14', 'older'].map(gen => (
                            <button
                                key={gen}
                                className={`generation-tag ${selectedGenerations.includes(gen) ? 'active' : ''}`}
                                onClick={() => toggleGeneration(gen)}
                                style={{
                                    background: selectedGenerations.includes(gen) ? '#1877f2' : '#1c2128',
                                    color: selectedGenerations.includes(gen) ? 'white' : '#333',
                                    border: '2px solid #1877f2',
                                    padding: '8px 16px',
                                    borderRadius: '20px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'all 0.3s ease',
                                    position: 'relative',
                                    overflow: 'visible'
                                }}
                            >
                                {gen.charAt(0).toUpperCase() + gen.slice(1)}
                                <span
                                    className="edit-pencil"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        openPriceRangePopup(gen);
                                    }}
                                    title={`Set price range for iPhone ${gen.charAt(0).toUpperCase() + gen.slice(1)}`}
                                >
                                    ✏️
                                </span>
                            </button>
                        ))}
                    </div>
                )}

                {/* iPhone Variant Tags */}
                {selectedModels.some(model => model && model.toLowerCase().includes('iphone')) &&
                 (selectedGenerations.some(gen => gen && gen !== 'all' && ['17', '16', '15', '14', 'older'].includes(gen)) ||
                  selectedGenerations.includes('all')) && (
                    <div className="variant-tags" style={{ marginBottom: '12px' }}>
                        {/* Display each generation's variants on separate lines */}
                        {selectedGenerations.includes('all') || selectedGenerations.some(gen => gen !== 'all' && ['17', '16', '15', '14', 'older'].includes(gen)) ? (
                            ['17', '16', '15', '14', 'older'].filter(gen =>
                                selectedGenerations.includes('all') || selectedGenerations.includes(gen)
                            ).map(gen => {
                                if (gen === 'older') {
                                    return (
                                        <div key={gen} style={{ marginBottom: '12px' }}>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                                <button
                                                    key="older_model"
                                                    className={`variant-tag generation-tag ${selectedVariants.includes('older_model') ? 'active' : ''}`}
                                                    onClick={() => toggleVariant('older_model')}
                                                    style={{
                                                        background: selectedVariants.includes('older_model') ? '#1877f2' : '#1c2128',
                                                        color: selectedVariants.includes('older_model') ? 'white' : '#333',
                                                        border: '2px solid #1877f2',
                                                        padding: '6px 12px',
                                                        borderRadius: '20px',
                                                        fontWeight: '600',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.3s ease',
                                                        position: 'relative',
                                                        overflow: 'visible',
                                                        fontSize: '0.8rem'
                                                    }}
                                                >
                                                    Older Models
                                                    <span
                                                        className="edit-pencil"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            openVariantPopup('older_model');
                                                        }}
                                                        title="Set price range for Older iPhone Models"
                                                    >
                                                        ✏️
                                                    </span>
                                                </button>
                                            </div>
                                        </div>
                                    );
                                }

                                const variants = getVariantsForGeneration(gen);
                                // Reorder variants to put the regular/numeric variant first
                                const reorderedVariants = [
                                    variants.find(v => v === 'regular'),
                                    ...variants.filter(v => v !== 'regular')
                                ].filter(Boolean);

                                return (
                                    <div key={gen} style={{ marginBottom: '12px' }}>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                            {reorderedVariants.map(variant => {
                                                const fullVariantName = `${gen}_${variant}`;
                                                const displayVariant = variant === 'regular' ? gen : variant.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                                                return (
                                                    <button
                                                        key={fullVariantName}
                                                        className={`variant-tag generation-tag ${selectedVariants.includes(fullVariantName) ? 'active' : ''}`}
                                                        onClick={() => toggleVariant(fullVariantName)}
                                                        style={{
                                                            background: selectedVariants.includes(fullVariantName) ? '#1877f2' : '#1c2128',
                                                            color: selectedVariants.includes(fullVariantName) ? 'white' : '#333',
                                                            border: '2px solid #1877f2',
                                                            padding: '6px 12px',
                                                            borderRadius: '20px',
                                                            fontWeight: '600',
                                                            cursor: 'pointer',
                                                            transition: 'all 0.3s ease',
                                                            position: 'relative',
                                                            overflow: 'visible',
                                                            fontSize: '0.8rem'
                                                        }}
                                                    >
                                                        {displayVariant}
                                                        <span
                                                            className="edit-pencil"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                openVariantPopup(fullVariantName);
                                                            }}
                                                            title={`Set price range for iPhone ${gen} ${displayVariant}`}
                                                        >
                                                            ✏️
                                                        </span>
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    </div>
                                );
                            })
                        ) : null}
                    </div>
                )}

                
                {/* Search City Tags */}
                <div className="search-city-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px', marginTop: '12px' }}>
                    <button
                        className={`search-city-tag ${selectedSearchCities.includes('all') ? 'active' : ''}`}
                        onClick={() => toggleSearchCity('all')}
                        style={{
                            background: selectedSearchCities.includes('all') ? '#1877f2' : '#1c2128',
                            color: selectedSearchCities.includes('all') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        All Cities
                    </button>
                    {getUniqueSearchCities().map(searchCity => (
                        <button
                            key={searchCity}
                            className={`search-city-tag ${selectedSearchCities.includes(searchCity) ? 'active' : ''}`}
                            onClick={() => toggleSearchCity(searchCity)}
                            style={{
                                background: selectedSearchCities.includes(searchCity) ? '#1877f2' : '#1c2128',
                                color: selectedSearchCities.includes(searchCity) ? 'white' : '#333',
                                border: '2px solid #1877f2',
                                padding: '8px 16px',
                                borderRadius: '20px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                fontSize: '14px'
                            }}
                        >
                            {searchCity}
                        </button>
                    ))}
                </div>

                {/* Time Range Tags */}
                <div className="time-range-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px', marginTop: '12px' }}>
                    <button
                        className={`time-range-tag ${selectedTimeRanges.includes('all') ? 'active' : ''}`}
                        onClick={() => toggleTimeRange('all')}
                        style={{
                            background: selectedTimeRanges.includes('all') ? '#1877f2' : '#1c2128',
                            color: selectedTimeRanges.includes('all') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        Whenever
                    </button>
                    <button
                        className={`time-range-tag ${selectedTimeRanges.includes('just_now') ? 'active' : ''}`}
                        onClick={() => toggleTimeRange('just_now')}
                        style={{
                            background: selectedTimeRanges.includes('just_now') ? '#1877f2' : '#1c2128',
                            color: selectedTimeRanges.includes('just_now') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        Just Now
                    </button>
                    <button
                        className={`time-range-tag ${selectedTimeRanges.includes('12_hours') ? 'active' : ''}`}
                        onClick={() => toggleTimeRange('12_hours')}
                        style={{
                            background: selectedTimeRanges.includes('12_hours') ? '#1877f2' : '#1c2128',
                            color: selectedTimeRanges.includes('12_hours') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        12 Hours
                    </button>
                    <button
                        className={`time-range-tag ${selectedTimeRanges.includes('24_hours') ? 'active' : ''}`}
                        onClick={() => toggleTimeRange('24_hours')}
                        style={{
                            background: selectedTimeRanges.includes('24_hours') ? '#1877f2' : '#1c2128',
                            color: selectedTimeRanges.includes('24_hours') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        24 Hours
                    </button>
                    <button
                        className={`time-range-tag ${selectedTimeRanges.includes('3_days') ? 'active' : ''}`}
                        onClick={() => toggleTimeRange('3_days')}
                        style={{
                            background: selectedTimeRanges.includes('3_days') ? '#1877f2' : '#1c2128',
                            color: selectedTimeRanges.includes('3_days') ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        3 Days
                    </button>
                </div>

                <div style={{ marginTop: '15px' }}>
                    <input
                        id="search"
                        type="text"
                        placeholder="Search titles, models, locations..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '10px 12px',
                            border: '2px solid #1877f2',
                            borderRadius: '8px',
                            fontSize: '1rem',
                            transition: 'border-color 0.3s ease',
                            background: '#161b22'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#1877f2'}
                        onBlur={(e) => e.target.style.borderColor = '#1877f2'}
                    />
                </div>

                <div className="price-range-filter">
                    <div className="price-inputs" style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
                        <input
                            type="number"
                            placeholder="Min $"
                            value={priceRange.min}
                            onChange={(e) => setPriceRange(prev => ({ ...prev, min: parseInt(e.target.value) || 0 }))}
                            style={{
                                padding: '8px 12px',
                                border: '2px solid #1877f2',
                                borderRadius: '8px',
                                width: '120px',
                                fontSize: '1rem'
                            }}
                        />
                        <span>to</span>
                        <input
                            type="number"
                            placeholder="Max $"
                            value={priceRange.max}
                            onChange={(e) => setPriceRange(prev => ({ ...prev, max: parseInt(e.target.value) || 10000 }))}
                            style={{
                                padding: '8px 12px',
                                border: '2px solid #1877f2',
                                borderRadius: '8px',
                                width: '120px',
                                fontSize: '1rem'
                            }}
                        />
                    </div>
                </div>

                {/* Show Hidden and Show Favorites Toggles */}
                <div style={{ display: 'flex', gap: '10px', marginTop: '15px', marginBottom: '10px' }}>
                    <button
                        onClick={() => setShowHidden(!showHidden)}
                        style={{
                            background: showHidden ? '#1877f2' : '#1c2128',
                            color: showHidden ? 'white' : '#333',
                            border: '2px solid #1877f2',
                            padding: '10px',
                            borderRadius: '50%',
                            width: '40px',
                            height: '40px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '1.2rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                        title={showHidden ? 'Hide hidden items' : 'Show hidden items'}
                    >
                        {showHidden ? '👁️' : '👁️‍🗨️'}
                    </button>
                    <button
                        onClick={() => setShowFavorites(!showFavorites)}
                        style={{
                            background: showFavorites ? '#ffc107' : '#1c2128',
                            color: showFavorites ? '#333' : '#333',
                            border: '2px solid #1877f2',
                            padding: '10px',
                            borderRadius: '50%',
                            width: '40px',
                            height: '40px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '1.2rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                        title={showFavorites ? 'Show all items' : 'Show favorites only'}
                    >
                        ⭐
                    </button>
                </div>

              </section>

            <section className="listings-section">
                {filteredListings.length === 0 ? (
                    <div className="empty-state">
                        <h3>No phone listings found</h3>
                        <p>Run the CSV monitor to start detecting Facebook Marketplace listings</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="listings-table">
                            <thead>
                                <tr>
                                                                        <th
                                        style={{ cursor: 'default', minWidth: '120px', textAlign: 'center', padding: '10px 8px' }}
                                    >
                                        Variant
                                    </th>
                                    <th
                                        onClick={() => toggleSort('title')}
                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                        title="Click to sort by title"
                                    >
                                        Title
                                        {sortBy === 'title' && (
                                            <span style={{ marginLeft: '5px', fontSize: '0.8rem' }}>
                                                {sortOrder === 'asc' ? '↑' : '↓'}
                                            </span>
                                        )}
                                    </th>
                                    <th
                                        onClick={() => toggleSort('price')}
                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                        title="Click to sort by price"
                                    >
                                        Price
                                        {sortBy === 'price' && (
                                            <span style={{ marginLeft: '5px', fontSize: '0.8rem' }}>
                                                {sortOrder === 'asc' ? '↑' : '↓'}
                                            </span>
                                        )}
                                    </th>
                                    <th
                                        onClick={() => toggleSort('location')}
                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                        title="Click to sort by location"
                                    >
                                        Location
                                        {sortBy === 'location' && (
                                            <span style={{ marginLeft: '5px', fontSize: '0.8rem' }}>
                                                {sortOrder === 'asc' ? '↑' : '↓'}
                                            </span>
                                        )}
                                    </th>
                                    <th
                                        onClick={() => toggleSort('found_at')}
                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                        title="Click to sort by found time"
                                    >
                                        Found
                                        {sortBy === 'found_at' && (
                                            <span style={{ marginLeft: '5px', fontSize: '0.8rem' }}>
                                                {sortOrder === 'asc' ? '↑' : '↓'}
                                            </span>
                                        )}
                                    </th>
                                    <th style={{ cursor: 'default' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredListings.map(listing => (
                                    <tr
                                        key={listing.id}
                                        onTouchStart={(e) => handleTouchStart(e, listing.id)}
                                        onTouchMove={handleTouchMove}
                                        onTouchEnd={handleTouchEnd}
                                        onMouseDown={(e) => handleMouseDown(e, listing.id)}
                                        style={{ cursor: 'grab' }}
                                    >
                                                                                <td className="variant-cell" style={{ width: '120px', maxWidth: '120px' }}>
                                            <div style={{
                                                color: listing.variant ? '#1877f2' : '#999',
                                                fontSize: '0.75rem',
                                                fontWeight: listing.variant ? '600' : '400',
                                                lineHeight: '1.3',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap',
                                                backgroundColor: listing.variant ? '#e3f2fd' : 'transparent',
                                                padding: '2px 6px',
                                                borderRadius: '4px',
                                                textAlign: 'center'
                                            }}>
                                                {listing.variant ?
                                                    listing.variant === 'older_model' ? 'Older Model' :
                                                    listing.variant.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) :
                                                    'None'
                                                }
                                            </div>
                                        </td>
                                        <td className="title-cell" style={{ width: '160px', maxWidth: '160px' }}>
                                            {listing.link ? (
                                                <a
                                                    href={listing.link}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="title-link"
                                                    style={{
                                                        color: '#1877f2',
                                                        textDecoration: 'none',
                                                        cursor: 'pointer',
                                                        display: 'block',
                                                        whiteSpace: 'pre-wrap',
                                                        wordBreak: 'break-word',
                                                        WebkitBoxOrient: 'vertical',
                                                        WebkitLineClamp: 'unset',
                                                        overflow: 'visible',
                                                        lineHeight: '1.4',
                                                        fontSize: '0.85rem'
                                                    }}
                                                    onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                                                    onMouseOut={(e) => e.target.style.textDecoration = 'none'}
                                                >
                                                    {truncateText(listing.title)}
                                                </a>
                                            ) : (
                                                <div className="title-text" style={{
                                                    whiteSpace: 'pre-wrap',
                                                    wordBreak: 'break-word',
                                                    WebkitBoxOrient: 'vertical',
                                                    WebkitLineClamp: 'unset',
                                                    overflow: 'visible',
                                                    lineHeight: '1.4',
                                                    fontSize: '0.85rem'
                                                }}>
                                                    {truncateText(listing.title)}
                                                </div>
                                            )}
                                        </td>
                                        <td className="price-cell">
                                            <span className="price-value">${listing.price}</span>
                                        </td>
                                        <td className="location-cell">
                                            {listing.location}
                                        </td>
                                                                                <td className="detected-cell">
                                            {getRelativeTime(listing.found_at)}
                                        </td>
                                        <td className="actions-cell" style={{ textAlign: 'center', minWidth: '100px' }}>
                                            <button
                                                onClick={() => favoriteItem(listing.id)}
                                                style={{
                                                    background: listing.favorited ? '#ffc107' : '#1c2128',
                                                    color: listing.favorited ? '#333' : '#666',
                                                    border: '1px solid #1877f2',
                                                    borderRadius: '4px',
                                                    padding: '4px 8px',
                                                    marginRight: '5px',
                                                    cursor: 'pointer',
                                                    fontSize: '1rem',
                                                    transition: 'all 0.2s ease'
                                                }}
                                                title={listing.favorited ? 'Remove from favorites' : 'Add to favorites'}
                                            >
                                                {listing.favorited ? '⭐' : '☆'}
                                            </button>
                                            <button
                                                onClick={() => toggleHideItem(listing.id, listing.hidden)}
                                                style={{
                                                    background: listing.hidden ? '#1877f2' : '#1c2128',
                                                    color: listing.hidden ? 'white' : '#666',
                                                    border: '1px solid #1877f2',
                                                    borderRadius: '4px',
                                                    padding: '4px 8px',
                                                    marginLeft: '5px',
                                                    cursor: 'pointer',
                                                    fontSize: '1rem',
                                                    transition: 'all 0.2s ease'
                                                }}
                                                title={listing.hidden ? 'Unhide this listing' : 'Hide this listing'}
                                            >
                                                {showHidden ? (listing.hidden ? '👁️' : '👁️‍🗨️') : '👁️‍🗨️'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            {/* Price Range Popup Overlay */}
            {priceRangePopup.show && (
                <div className={`price-range-overlay ${priceRangePopup.show ? 'active' : ''}`} onClick={closePriceRangePopup}>
                    <div className="price-range-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="price-range-header">
                            <div>
                                <h2 className="price-range-title">
                                    Set Price Range
                                </h2>
                                <p className="price-range-subtitle">
                                    iPhone {priceRangePopup.generation.charAt(0).toUpperCase() + priceRangePopup.generation.slice(1)}
                                </p>
                            </div>
                            <button className="close-button" onClick={closePriceRangePopup}>
                                ×
                            </button>
                        </div>

                        <div className="price-range-form">
                            <div className="form-group">
                                <label>Price Range ($)</label>
                                <div className="price-inputs">
                                    <div className="price-input">
                                        <label htmlFor="min-price">Minimum</label>
                                        <input
                                            id="min-price"
                                            type="text"
                                            placeholder="Min price"
                                            value={editingPriceRange.min}
                                            onChange={(e) => handlePriceRangeChange('min', e.target.value)}
                                        />
                                    </div>
                                    <div className="price-input">
                                        <label htmlFor="max-price">Maximum</label>
                                        <input
                                            id="max-price"
                                            type="text"
                                            placeholder="Max price"
                                            value={editingPriceRange.max}
                                            onChange={(e) => handlePriceRangeChange('max', e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="form-actions">
                                <button className="btn-cancel" onClick={closePriceRangePopup}>
                                    Cancel
                                </button>
                                <button className="btn-save" onClick={savePriceRange}>
                                    Save Price Range
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Variant Price Range Popup Overlay */}
            {variantPopup.show && (
                <div className={`price-range-overlay ${variantPopup.show ? 'active' : ''}`} onClick={closeVariantPopup}>
                    <div className="price-range-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="price-range-header">
                            <div>
                                <h2 className="price-range-title">
                                    Set Price Range
                                </h2>
                                <p className="price-range-subtitle">
                                    {variantPopup.variant.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </p>
                            </div>
                            <button className="close-button" onClick={closeVariantPopup}>
                                ×
                            </button>
                        </div>

                        <div className="price-range-form">
                            <div className="form-group">
                                <label>Price Range ($)</label>
                                <div className="price-inputs">
                                    <div className="price-input">
                                        <label htmlFor="variant-min-price">Minimum</label>
                                        <input
                                            id="variant-min-price"
                                            type="text"
                                            placeholder="Min price"
                                            value={editingVariantPriceRange.min}
                                            onChange={(e) => handleVariantPriceRangeChange('min', e.target.value)}
                                        />
                                    </div>
                                    <div className="price-input">
                                        <label htmlFor="variant-max-price">Maximum</label>
                                        <input
                                            id="variant-max-price"
                                            type="text"
                                            placeholder="Max price"
                                            value={editingVariantPriceRange.max}
                                            onChange={(e) => handleVariantPriceRangeChange('max', e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="form-actions">
                                <button className="btn-cancel" onClick={closeVariantPopup}>
                                    Cancel
                                </button>
                                <button className="btn-save" onClick={saveVariantPriceRange}>
                                    Save Price Range
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Dashboard />);