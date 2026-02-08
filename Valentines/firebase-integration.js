// Firebase Integration for Valentine's Website
// Add this code to your index.html file

// 1. FIRST: Add Firebase SDKs to your HTML <head> section
/*
<script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-database-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-storage-compat.js"></script>
*/

// 2. SECOND: Add your Firebase configuration (get this from Firebase Console)
const firebaseConfig = {
  // REPLACE THESE VALUES WITH YOUR ACTUAL FIREBASE CONFIG
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  databaseURL: "https://YOUR_PROJECT-default-rtdb.firebaseio.com/",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// 3. THIRD: Initialize Firebase (add this after the config)
let database;
let firebaseInitialized = false;

function initializeFirebase() {
    if (firebaseConfig.apiKey && firebaseConfig.apiKey !== "YOUR_API_KEY_HERE") {
        try {
            firebase.initializeApp(firebaseConfig);
            database = firebase.database();
            firebaseInitialized = true;
            console.log("Firebase initialized successfully");
            return true;
        } catch (error) {
            console.error("Firebase initialization error:", error);
            firebaseInitialized = false;
            return false;
        }
    }
    firebaseInitialized = false;
    return false;
}

// 4. FOURTH: Function to store user data in Firebase
function storeUserInFirebase(fromName, toName, hasPhoto = false) {
    if (!firebaseInitialized || !database) {
        console.log("Firebase not initialized - storing in localStorage instead");
        storeUserInLocalStorage(fromName, toName, hasPhoto);
        return;
    }
    
    // Get user's IP address (optional - for tracking)
    fetch('https://api.ipify.org?format=json')
        .then(response => response.json())
        .then(data => {
            const userData = {
                from: fromName,
                to: toName,
                timestamp: new Date().toLocaleString(),
                photo: hasPhoto ? 'Yes' : 'No',
                ip: data.ip,
                userAgent: navigator.userAgent
            };
            
            // Generate unique key and store data
            const newKey = database.ref().child('valentineUsers').push().key;
            database.ref('valentineUsers/' + newKey).set(userData)
                .then(() => {
                    console.log("User data stored in Firebase successfully");
                    // Also store in localStorage as backup
                    storeUserInLocalStorage(fromName, toName, hasPhoto);
                })
                .catch((error) => {
                    console.error("Error storing data in Firebase:", error);
                    storeUserInLocalStorage(fromName, toName, hasPhoto);
                });
        })
        .catch(error => {
            console.error("Error getting IP address:", error);
            const userData = {
                from: fromName,
                to: toName,
                timestamp: new Date().toLocaleString(),
                photo: hasPhoto ? 'Yes' : 'No',
                ip: 'Unknown',
                userAgent: navigator.userAgent
            };
            
            const newKey = database.ref().child('valentineUsers').push().key;
            database.ref('valentineUsers/' + newKey).set(userData);
        });
}

// 5. FIFTH: Function to retrieve data from Firebase
function getUserDataFromFirebase(callback) {
    if (!firebaseInitialized || !database) {
        console.log("Firebase not initialized - retrieving from localStorage");
        const data = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
        callback(data);
        return;
    }
    
    database.ref('valentineUsers').on('value', (snapshot) => {
        const firebaseData = snapshot.val();
        const dataArray = [];
        
        if (firebaseData) {
            Object.values(firebaseData).forEach(user => {
                dataArray.push(user);
            });
        }
        
        callback(dataArray);
    });
}

// 6. SIXTH: Fallback localStorage function (for when Firebase isn't configured)
function storeUserInLocalStorage(fromName, toName, hasPhoto = false) {
    const userData = {
        from: fromName,
        to: toName,
        timestamp: new Date().toLocaleString(),
        photo: hasPhoto ? 'Yes' : 'No'
    };
    
    let allUsers = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
    allUsers.push(userData);
    localStorage.setItem('valentineUsers', JSON.stringify(allUsers));
    console.log("User data stored in localStorage");
}

// 7. SEVENTH: Get all user data (works with both Firebase and localStorage)
function getAllUserData(callback) {
    if (firebaseInitialized && database) {
        getUserDataFromFirebase(callback);
    } else {
        const data = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
        callback(data);
    }
}

// Call initializeFirebase() on page load to set up Firebase
// This will automatically fall back to localStorage if Firebase isn't configured

// 6. SIXTH: Modified functions to use Firebase storage

// Modified generateLink function
function generateLinkWithFirebase() {
    const fromName = document.getElementById('fromName').value.trim();
    const toName = document.getElementById('toName').value.trim();
    
    if (!fromName || !toName) {
        alert('Please enter both names!');
        return;
    }
    
    // Store in Firebase (or localStorage as fallback)
    storeUserInFirebase(fromName, toName, false);
    
    // Generate the link normally
    const baseUrl = window.location.origin + window.location.pathname;
    const link = `${baseUrl}?from=${encodeURIComponent(fromName)}&to=${encodeURIComponent(toName)}`;
    
    document.getElementById('generatedLinkText').textContent = link;
    document.getElementById('generatedLink').style.display = 'block';
}

// Modified photo upload function
function handlePhotoUploadWithFirebase() {
    const fileInput = document.getElementById('photoUpload');
    const galleryGrid = document.getElementById('galleryGrid');
    
    // Remove empty state
    const emptyState = galleryGrid.querySelector('div[style*="grid-column"]');
    if (emptyState) {
        emptyState.remove();
    }
    
    for (let i = 0; i < fileInput.files.length; i++) {
        const file = fileInput.files[i];
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Store user data with photo in Firebase
                const fromName = document.getElementById('fromName').value.trim() || 'Anonymous';
                const toName = document.getElementById('toName').value.trim() || 'Special';
                storeUserInFirebase(fromName, toName, true);
                
                // Create photo card normally
                const card = document.createElement('div');
                card.className = 'photo-card';
                card.innerHTML = `
                    <img src="${e.target.result}" alt="Photo" class="photo-img">
                    <div style="position: absolute; bottom: 10px; left: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 8px; border-radius: 10px; text-align: center; font-size: 0.8rem; cursor: pointer;" onclick="createValentinePoster('${e.target.result}')">
                        <i class="fas fa-heart"></i> Create Poster
                    </div>
                `;
                galleryGrid.appendChild(card);
            };
            reader.readAsDataURL(file);
        }
    }
}

// 7. SEVENTH: Initialize Firebase when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Try to initialize Firebase
    initializeFirebase();
    
    // You can also add buttons or functions to test the connection
    window.testFirebaseConnection = function() {
        if (initializeFirebase()) {
            alert('✅ Firebase connected successfully!');
        } else {
            alert('❌ Firebase not configured. Please add your configuration.');
        }
    };
});

// USAGE INSTRUCTIONS:
// 1. Add the Firebase SDK script tags to your HTML <head>
// 2. Replace the firebaseConfig values with your actual Firebase project config
// 3. Replace your existing generateLink() calls with generateLinkWithFirebase()
// 4. Replace your existing handlePhotoUpload() calls with handlePhotoUploadWithFirebase()
// 5. Open firebase-dashboard.html to view all collected data