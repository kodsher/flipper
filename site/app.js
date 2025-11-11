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
    const [priceRange, setPriceRange] = useState({ min: 0, max: 10000 });
    const [sortBy, setSortBy] = useState('price');
    const [sortOrder, setSortOrder] = useState('asc');
    const [searchTerm, setSearchTerm] = useState('');
    const [showHidden, setShowHidden] = useState(false);
    const [showFavorites, setShowFavorites] = useState(false);

    // Dark mode state - enabled by default
    const [darkMode, setDarkMode] = useState(() => {
        // Check for saved preference or default to true (dark mode)
        const savedTheme = localStorage.getItem('theme');
        return savedTheme !== null ? savedTheme === 'dark' : true;
    });

    // Toggle theme function
    const toggleTheme = () => {
        const newDarkMode = !darkMode;
        setDarkMode(newDarkMode);
        localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');

        // Apply theme to body
        if (newDarkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    };

    // Apply theme on mount
    useEffect(() => {
        if (darkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }, [darkMode]);

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
                return ['all'];
            }
            let newSelection = prev.includes(model)
                ? prev.filter(m => m !== model)
                : [...prev.filter(m => m !== 'all'), model];

            // If no models selected, default to 'all'
            if (newSelection.length === 0) {
                return ['all'];
            }
            return newSelection;
        });
    }, []);

    // Function to toggle generation selection
    const toggleGeneration = useCallback((generation) => {
        setSelectedGenerations(prev => {
            if (generation === 'all') {
                return ['all'];
            }
            let newSelection = prev.includes(generation)
                ? prev.filter(g => g !== generation)
                : [...prev.filter(g => g !== 'all'), generation];

            // If no generations selected, default to 'all'
            if (newSelection.length === 0) {
                return ['all'];
            }
            return newSelection;
        });
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
        return Array.from(cities).sort();
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

            // Show success message with Firebase console links
            alert(
                '✅ Database cleared successfully!\n\n' +
                'All phone listings and processed hashes have been deleted from Firebase.\n\n' +
                '🔗 Firebase Console Links:\n' +
                '• Main Database: https://console.firebase.google.com/project/phone-flipping/database/phone-flipping-default-rtdb/data/~2Fphone_listings\n' +
                '• CSV Monitor: https://console.firebase.google.com/project/phone-flipping/database/phone-flipping-default-rtdb/data/~2Fprocessed_hashes\n\n' +
                'Note: GitHub integration requires backend setup.'
            );

            // Refresh data
            fetchData();

        } catch (error) {
            console.error('❌ Error clearing database:', error);
            alert('❌ Failed to clear database. Please try again.');
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

        // Filter by model categories (multiple selection)
        if (!selectedModels.includes('all')) {
            filtered = filtered.filter(listing => {
                const model = (listing.model || 'Unknown').toLowerCase();

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

        // Filter by generations (multiple selection) - only applies to iPhones
        if (!selectedGenerations.includes('all')) {
            filtered = filtered.filter(listing => {
                const model = listing.model || '';

                // Only filter by generation if it's an iPhone
                if (!model.toLowerCase().includes('iphone')) {
                    return true; // Non-iPhones pass through generation filter
                }

                // Check if this iPhone matches any selected generation
                return selectedGenerations.some(selectedGeneration => {
                    if (selectedGeneration === 'older') {
                        return !model.includes('17') && !model.includes('16') && !model.includes('15') && !model.includes('14');
                    } else {
                        return model.includes(selectedGeneration);
                    }
                });
            });
        }

        // Filter by search cities (multiple selection)
        if (!selectedSearchCities.includes('all')) {
            filtered = filtered.filter(listing => {
                const searchCity = listing.search_city || 'Unknown';
                return selectedSearchCities.includes(searchCity);
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
    }, [phoneListings, selectedModels, selectedGenerations, selectedSearchCities, priceRange, sortBy, sortOrder, searchTerm, showHidden, showFavorites, safeParseDate, getRelativeTime]);

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

                // Update duplicate info
                const duplicateCount = rawListings.length - listings.length;
                setDuplicateInfo({
                    total: rawListings.length,
                    duplicates: duplicateCount,
                    unique: listings.length
                });
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
                <button
                    className="theme-toggle"
                    onClick={toggleTheme}
                    title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                >
                    <span className="icon">{darkMode ? '☀️' : '🌙'}</span>
                    <span>{darkMode ? 'Light' : 'Dark'}</span>
                </button>
            </header>

            {error && (
                <div className="error-message">
                    <h3>⚠️ Connection Error</h3>
                    <p>{error}</p>
                </div>
            )}

            
            <section className="filters-section">
                <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginBottom: '15px' }}>
                    <button
                        id="clear-database-btn"
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
                    >
                        🗑️
                    </button>
                </div>

                {/* Device Category Tags */}
                <div className="model-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                    <button
                        className={`model-tag ${selectedModels.includes('all') ? 'active' : ''}`}
                        onClick={() => toggleModel('all')}
                        style={{
                            background: selectedModels.includes('all') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('all') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
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
                            background: selectedModels.includes('iphone') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('iphone') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        iPhone ({modelCounts.iphone})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('ipad') ? 'active' : ''}`}
                        onClick={() => toggleModel('ipad')}
                        style={{
                            background: selectedModels.includes('ipad') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('ipad') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        iPad ({modelCounts.ipad})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('macbook') ? 'active' : ''}`}
                        onClick={() => toggleModel('macbook')}
                        style={{
                            background: selectedModels.includes('macbook') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('macbook') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        MacBook ({modelCounts.macbook})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('android') ? 'active' : ''}`}
                        onClick={() => toggleModel('android')}
                        style={{
                            background: selectedModels.includes('android') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('android') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Android ({modelCounts.android})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('android_tablet') ? 'active' : ''}`}
                        onClick={() => toggleModel('android_tablet')}
                        style={{
                            background: selectedModels.includes('android_tablet') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('android_tablet') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Android Tablets ({modelCounts.android_tablet})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('other_computers') ? 'active' : ''}`}
                        onClick={() => toggleModel('other_computers')}
                        style={{
                            background: selectedModels.includes('other_computers') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('other_computers') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Other Computers ({modelCounts.other_computers})
                    </button>
                    <button
                        className={`model-tag ${selectedModels.includes('other') ? 'active' : ''}`}
                        onClick={() => toggleModel('other')}
                        style={{
                            background: selectedModels.includes('other') ? '#1877f2' : '#f8f9fa',
                            color: selectedModels.includes('other') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        Other ({modelCounts.other})
                    </button>
                </div>

                {/* iPhone Generation Tags */}
                {selectedModels.some(model => model && model.toLowerCase().includes('iphone')) && (
                    <div className="generation-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                        <button
                            className={`generation-tag ${selectedGenerations.includes('all') ? 'active' : ''}`}
                            onClick={() => toggleGeneration('all')}
                            style={{
                                background: selectedGenerations.includes('all') ? '#1877f2' : '#f8f9fa',
                                color: selectedGenerations.includes('all') ? 'white' : '#333',
                                border: '2px solid #e1e1e1',
                                padding: '8px 16px',
                                borderRadius: '20px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease'
                            }}
                        >
                            All iPhones ({generationCounts.all})
                        </button>
                        {['17', '16', '15', '14', 'older'].map(gen => (
                            <button
                                key={gen}
                                className={`generation-tag ${selectedGenerations.includes(gen) ? 'active' : ''}`}
                                onClick={() => toggleGeneration(gen)}
                                style={{
                                    background: selectedGenerations.includes(gen) ? '#1877f2' : '#f8f9fa',
                                    color: selectedGenerations.includes(gen) ? 'white' : '#333',
                                    border: '2px solid #e1e1e1',
                                    padding: '8px 16px',
                                    borderRadius: '20px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    transition: 'all 0.3s ease'
                                }}
                            >
                                {gen.charAt(0).toUpperCase() + gen.slice(1)} ({generationCounts[gen]})
                            </button>
                        ))}
                    </div>
                )}

                {/* Search City Tags */}
                <div className="search-city-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px', marginTop: '12px' }}>
                    <button
                        className={`search-city-tag ${selectedSearchCities.includes('all') ? 'active' : ''}`}
                        onClick={() => toggleSearchCity('all')}
                        style={{
                            background: selectedSearchCities.includes('all') ? '#1877f2' : '#f8f9fa',
                            color: selectedSearchCities.includes('all') ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
                            padding: '8px 16px',
                            borderRadius: '20px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            fontSize: '14px'
                        }}
                    >
                        All Cities ({searchCityCounts.all})
                    </button>
                    {getUniqueSearchCities().map(searchCity => (
                        <button
                            key={searchCity}
                            className={`search-city-tag ${selectedSearchCities.includes(searchCity) ? 'active' : ''}`}
                            onClick={() => toggleSearchCity(searchCity)}
                            style={{
                                background: selectedSearchCities.includes(searchCity) ? '#1877f2' : '#f8f9fa',
                                color: selectedSearchCities.includes(searchCity) ? 'white' : '#333',
                                border: '2px solid #e1e1e1',
                                padding: '8px 16px',
                                borderRadius: '20px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                fontSize: '14px'
                            }}
                        >
                            {searchCity} ({searchCityCounts[searchCity] || 0})
                        </button>
                    ))}
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
                            border: '2px solid #e1e1e1',
                            borderRadius: '8px',
                            fontSize: '1rem',
                            transition: 'border-color 0.3s ease',
                            background: 'white'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#1877f2'}
                        onBlur={(e) => e.target.style.borderColor = '#e1e1e1'}
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
                                border: '2px solid #e1e1e1',
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
                                border: '2px solid #e1e1e1',
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
                            background: showHidden ? '#1877f2' : '#f8f9fa',
                            color: showHidden ? 'white' : '#333',
                            border: '2px solid #e1e1e1',
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
                            background: showFavorites ? '#ffc107' : '#f8f9fa',
                            color: showFavorites ? '#333' : '#333',
                            border: '2px solid #e1e1e1',
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
                                        onClick={() => toggleSort('model')}
                                        style={{ cursor: 'pointer', userSelect: 'none', display: 'none' }}
                                        title="Click to sort by model"
                                    >
                                        Model
                                        {sortBy === 'model' && (
                                            <span style={{ marginLeft: '5px', fontSize: '0.8rem' }}>
                                                {sortOrder === 'asc' ? '↑' : '↓'}
                                            </span>
                                        )}
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
                                        <td className="model-cell" style={{ width: '180px', maxWidth: '180px', display: 'none' }}>
                                            <div style={{
                                                color: '#333',
                                                fontSize: '0.85rem',
                                                lineHeight: '1.3',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap'
                                            }}>
                                                {listing.model || 'Unknown'}
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
                                                    background: listing.favorited ? '#ffc107' : '#f8f9fa',
                                                    color: listing.favorited ? '#333' : '#666',
                                                    border: '1px solid #e1e1e1',
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
                                                    background: listing.hidden ? '#1877f2' : '#f8f9fa',
                                                    color: listing.hidden ? 'white' : '#666',
                                                    border: '1px solid #e1e1e1',
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
        </div>
    );
};

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Dashboard />);