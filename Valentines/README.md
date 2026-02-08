# 💕 Valentine's Day Memory Gallery

A beautiful, interactive Valentine's Day website with photo gallery and romantic proposal features. Perfect for creating digital memories and special moments together!

## 🌟 Features

- **Main Index Page**: All features on one page
- **Link Generator**: Create personalized Valentine's links with names and Instagram
- **Exact Live Preview**: See the complete teddy bear proposal interface
- **Teddy Bear Proposal**: Cute teddy bear "Yes/No" interactive proposal
- **Kissing Animation**: Two teddy bears kiss when "Yes" is clicked
- **Creator Credit**: Display your name and Instagram handle
- **Photo Gallery**: Upload and display photos directly on main page
- **✨ NEW - Photo Crop Tool**: Crop, zoom, rotate, and position photos before uploading
  - Multiple aspect ratio presets (1:1, 4:3, 16:9, 9:16)
  - Zoom and rotation controls
  - Real-time preview
  - Position adjustments
- **Professional Poster Creation**: Transform photos into elegant Valentine's posters
- **Name Integration**: Posters show "Name1 ❤️ Name2" format
- **Dual Action Buttons**: Copy and Live Preview options
- **Animated Design**: Floating hearts, bubbles, and smooth animations
- **Mobile-First Design**: Fully optimized for all mobile devices and screen sizes
- **Touch-Friendly**: Perfect for smartphones and tablets
- **GitHub Ready**: Optimized for hosting on GitHub Pages
- **✨ NEW - Data Persistence**: User registration and photo uploads tracked via localStorage
- **✨ NEW - Admin Dashboard**: View all user registrations and photo uploads
- **✨ NEW - Data Import/Export**: Backup and restore user data

## 📊 Admin Dashboard Features

- **View User Statistics**: Total users, users with photos, users in last 24 hours
- **User Registration Table**: See all registrations with dates and photo status
- **Import Data**: Upload previously exported JSON files to restore data
- **Export Data**: Download all user data as JSON for backup
- **Clear Data**: Remove all data (password protected)
- **Password Protected**: Access code required: `valentine2026`

## 📸 Photo Crop Tool

The new crop tool allows users to customize their photos before uploading:

1. Click "Add Photos" button
2. Select one or more photos
3. Use the crop interface to:
   - Choose aspect ratio (Square, 4:3, 16:9, 9:16)
   - Zoom in/out
   - Rotate the image
   - Adjust X and Y position
4. Click "Use This Photo" to add to gallery
5. Click "Create Poster" to generate the Valentine's poster

## 💾 Data Storage & GitHub Pages

### How Data is Stored
- **Local Storage**: User data is stored in browser's localStorage
- **Persistent**: Data persists for each browser and device
- **On GitHub Pages**: Data remains on the device that created it

### Important Notes
- Each browser/device maintains its own data copy
- Clearing browser cache will remove stored data
- Use **Export Data** to backup your data
- Use **Import Data** to restore from backup

### Multi-Device Data Sync (Optional)
To sync data across devices and GitHub deployments:
1. Set up a Firebase Realtime Database (free)
2. Get your Firebase config from Firebase Console
3. Update the firebaseConfig in `index.html`:
   ```javascript
   const firebaseConfig = {
       apiKey: "YOUR_API_KEY",
       authDomain: "YOUR_PROJECT.firebaseapp.com",
       databaseURL: "https://YOUR_PROJECT-default-rtdb.firebaseio.com/",
       projectId: "YOUR_PROJECT_ID",
       storageBucket: "YOUR_PROJECT.appspot.com",
       messagingSenderId: "YOUR_SENDER_ID",
       appId: "YOUR_APP_ID"
   };
   ```
4. Data will automatically sync across all devices

## 🚀 Quick Start

### Hosting on GitHub Pages

1. **Create a GitHub Repository**
   - Go to [GitHub](https://github.com) and create a new repository
   - Name it something like `valentines-memory-gallery`

2. **Upload Files**
   - Upload all files to the repository
   - Make sure `index.html` is at the root level

3. **Enable GitHub Pages**
   - Go to your repository settings
   - Scroll down to "Pages" section
   - Select "Deploy from a branch"
   - Choose your main branch
   - Click "Save"

4. **Access Your Site**
   - Your site will be available at: `https://yourusername.github.io/valentines-memory-gallery`
   - It may take a few minutes to deploy

### Local Development

1. Clone or download this repository
2. Open `index.html` in your web browser
3. Start uploading photos!

## 🎨 Customization

You can easily customize the colors and styling:

### Color Scheme
Edit the CSS variables in the `:root` section:
```css
:root {
    --primary-pink: #ff6b9d;    /* Main accent color */
    --light-pink: #ffafcc;      /* Light accent */
    --deep-pink: #d74177;       /* Dark accent */
    --rose-gold: #f8a5c2;       /* Secondary accent */
}
```

### Background Gradient
Modify the background gradient:
```css
background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
```

## 📱 Features Breakdown

### Link Generation
- **Three Input Fields**: Your name, Valentine's name, and Instagram handle
- **Single Link Created**: One unified link containing all information
- **Exact Live Preview**: Shows complete teddy bear proposal interface
- **Dual Options**: Copy button and Live Preview button
- **Personalized URLs**: Names and Instagram encoded in link parameters
- **Creator Credit**: Instagram handle displayed in shared links
- **Teddy Bear Experience**: Link opens interactive proposal with teddy bears

### Content Personalization
- **Dynamic Text**: Proposal messages update with entered names
- **Automatic Greeting**: "ToName, will you be FromName's Valentine?"
- **Success Messages**: Personalized celebration text

### Photo Gallery & Posters
- **Direct Upload**: Add photos on the main index page
- **Professional Poster Creation**: Elegant, high-quality Valentine's posters
- **Name Display**: Posters show "Name1 ❤️ Name2" format
- **Creator Credit**: Your name and Instagram handle on posters
- **Download Option**: Save beautiful Valentine's posters
- **Mobile Grid**: Responsive photo display
- **Working Upload**: Fully functional photo handling
- **Hover Effects**: Interactive photo cards

### Romantic Proposal
- **Interactive Buttons**: "Yes" button stays, "No" button moves away playfully
- **Teddy Bear Design**: Cute teddy bear character with animated heart
- **Kissing Animation**: Two teddy bears kiss when "Yes" is selected
- **Romantic Quotes**: Inspirational love quotes on success
- **Celebration Effects**: Confetti and animations on acceptance

### Mobile Optimization
- **Touch Controls**: All buttons optimized for finger tapping
- **Responsive Layout**: Adapts perfectly to any screen size
- **Prevent Zoom**: Double-tap zoom disabled for better experience
- **Fast Loading**: Optimized for mobile network speeds

### Animations
- Floating hearts in the background
- Bouncing upload icon
- Smooth hover effects on photo cards
- Glowing text animations
- Fade-in transitions

### Responsive Design
- Mobile-first approach
- Grid layout adapts to screen size
- Touch-friendly buttons
- Optimized for all devices

## 🔧 Technical Details

- **Pure HTML/CSS/JavaScript**: No external dependencies except Font Awesome icons
- **Modern CSS**: Uses CSS variables, flexbox, grid, and advanced animations
- **File API**: Uses modern browser File API for image handling
- **Progressive Enhancement**: Works even with JavaScript disabled (basic functionality)

## 🎁 Perfect For

- Valentine's Day gifts
- Anniversary celebrations
- Couple photo sharing
- Digital memory books
- Wedding preludes
- Romantic surprises
- Personalized couple gifts
- Professional poster creation
- Direct photo sharing
- Love note creation
- Live preview experiences
- Teddy bear themed proposals

## 📝 License

This project is open source and available under the MIT License.

## 💖 Made With Love

Created for Valentine's Day to help couples share beautiful memories together!

---

*Happy Valentine's Day! May your love story be as beautiful as this gallery!*