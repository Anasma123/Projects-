// Valentine's Admin Functions - Add to index.html

// Store user data when they generate links
function storeUserRegistration(fromName, toName) {
    const userData = {
        from: fromName,
        to: toName,
        timestamp: new Date().toLocaleString(),
        photo: 'No'
    };
    
    let allUsers = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
    allUsers.push(userData);
    localStorage.setItem('valentineUsers', JSON.stringify(allUsers));
}

// Store user data when they upload photos
function storeUserPhoto(fromName, toName) {
    const userData = {
        from: fromName || 'Anonymous',
        to: toName || 'Special',
        timestamp: new Date().toLocaleString(),
        photo: 'Yes'
    };
    
    let allUsers = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
    
    // Check if this user already exists
    const existingIndex = allUsers.findIndex(u => u.from === userData.from && u.to === userData.to);
    if (existingIndex !== -1) {
        // Update photo status for existing user
        allUsers[existingIndex].photo = 'Yes';
    } else {
        // Add new user entry
        allUsers.push(userData);
    }
    
    localStorage.setItem('valentineUsers', JSON.stringify(allUsers));
}

// Show admin dashboard (call this function when needed)
function showAdminDashboard() {
    const password = prompt('Enter admin password:');
    if (password === 'valentine2026') { // Default password - change if needed
        const allUsers = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
        
        if (allUsers.length === 0) {
            alert('No user data found yet.');
            return;
        }
        
        let dashboardContent = '📊 VALENTINE\'S USER DASHBOARD 📊\n\n';
        dashboardContent += `Total Users: ${allUsers.length}\n`;
        dashboardContent += `Users with Photos: ${allUsers.filter(u => u.photo === 'Yes').length}\n\n`;
        dashboardContent += '='.repeat(50) + '\n\n';
        
        allUsers.forEach((user, index) => {
            dashboardContent += `User #${index + 1}:\n`;
            dashboardContent += `  From: ${user.from}\n`;
            dashboardContent += `  To: ${user.to}\n`;
            dashboardContent += `  Date: ${user.timestamp}\n`;
            dashboardContent += `  Photo: ${user.photo}\n`;
            dashboardContent += '-'.repeat(30) + '\n';
        });
        
        alert(dashboardContent);
        
        // Also log to console for easier viewing
        console.log('=== Valentine\'s User Data ===');
        console.table(allUsers);
    } else if (password !== null) {
        alert('Incorrect password!');
    }
}

// Export data to JSON file
function exportUserDataToJSON() {
    const password = prompt('Enter admin password:');
    if (password !== 'valentine2026') {
        alert('Incorrect password!');
        return;
    }
    
    const allUsers = JSON.parse(localStorage.getItem('valentineUsers') || '[]');
    
    if (allUsers.length === 0) {
        alert('No data to export.');
        return;
    }
    
    const dataStr = JSON.stringify(allUsers, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `valentines-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// To use this:
// 1. Add this code to your index.html file
// 2. Call storeUserRegistration() when users generate links
// 3. Call storeUserPhoto() when users upload photos
// 4. Call showAdminDashboard() to view the data (password: valentine2026)
// 5. Call exportUserDataToJSON() to download all data as JSON