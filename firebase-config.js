// Firebase Configuration for Phone Flipping Dashboard
const firebaseConfig = {
    apiKey: "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    authDomain: "phone-flipping.firebaseapp.com",
    databaseURL: "https://phone-flipping-default-rtdb.firebaseio.com",
    projectId: "phone-flipping",
    storageBucket: "phone-flipping.firebasestorage.app",
    messagingSenderId: "523828027077",
    appId: "1:523828027077:web:048a5003d81e6f3982daac"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Get a reference to the database service
const database = firebase.database();

// Test database connection
console.log('🔧 Firebase initialized with database URL:', firebaseConfig.databaseURL);
console.log('🔧 Testing database connection...');

// Test basic connection
database.ref('.info/connected').once('value').then((snapshot) => {
    const connected = snapshot.val();
    console.log('🔌 Firebase connection test:', connected ? 'Connected' : 'Disconnected');
}).catch((error) => {
    console.error('❌ Firebase connection test failed:', error);
});