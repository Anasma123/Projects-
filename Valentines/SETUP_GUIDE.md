# 🚀 Quick Setup & Usage Guide

## What's New?

### 1️⃣ Photo Crop Tool
Users can now crop, zoom, rotate, and adjust photos before uploading them to the gallery.

### 2️⃣ Data Tracking & Admin Dashboard
All user registrations and photo uploads are now tracked. View statistics in the admin dashboard.

---

## 📸 How to Use Photo Crop Tool

**For End Users:**

1. Click the **"Add Photos"** button in the gallery section
2. Select one or multiple photos from your device
3. **Crop Tool Modal** appears with controls:
   - **Aspect Ratio Buttons**: Choose from 1:1, 4:3, 16:9, or 9:16
   - **Zoom Slider**: Adjust zoom from 50% to 200%
   - **Rotate Slider**: Rotate image from 0° to 360°
   - **X & Y Sliders**: Move the image position
4. Preview updates in real-time as you adjust
5. Click **"Use This Photo"** to add it to the gallery
6. Click **"Create Poster"** to generate Valentine's poster
7. Click **"Cancel"** to discard and try another photo

**Tips:**
- Square (1:1) is great for profile photos
- 16:9 is best for landscape photos
- Use zoom to frame faces nicely
- Use position sliders to center your subject

---

## 👨‍💼 Admin Dashboard Usage

**Access Admin Dashboard:**

1. Open `admin.html` in your browser
2. Enter admin password: `valentine2026`
3. Click "OK"

**What You Can See:**

- **Total Users**: Number of people who generated links
- **Users with Photos**: How many uploaded photos
- **Last 24 Hours**: Recent activity count
- **User Table**: All registrations with dates and photo status

**Admin Functions:**

| Function | Purpose |
|----------|---------|
| **Refresh Data** | Reload user data from storage |
| **Import Data** | Upload previously exported JSON file |
| **Export Data** | Download all user data as JSON backup |
| **Clear All Data** | Delete all stored data (password protected) |

---

## 💾 Backing Up Your Data

### Export Data (Create Backup)

1. Go to `admin.html`
2. Enter password: `valentine2026`
3. Click **"Export Data"**
4. File `valentines-data-YYYY-MM-DD.json` downloads to your computer

### Import Data (Restore Backup)

1. Go to `admin.html`
2. Enter password: `valentine2026`
3. Click **"Import Data"**
4. Select your previously exported JSON file
5. Click "Open"
6. Data is merged and restored

**Example Backup Filename:**
```
valentines-data-2026-02-08.json
```

---

## 🔒 Security Notes

**Default Admin Password:** `valentine2026`

**To Change Password:**

1. Open `admin.html` in a text editor
2. Find this line (around line 237):
   ```javascript
   if (password !== 'valentine2026') {
   ```
3. Replace `'valentine2026'` with your new password
4. Save the file

**Example:**
```javascript
if (password !== 'MySecurePassword123') {
```

---

## 📊 Data Structure

When you export data, you get a JSON file like this:

```json
[
  {
    "from": "Alice",
    "to": "Bob",
    "timestamp": "2/8/2026, 3:45 PM",
    "photo": "Yes"
  },
  {
    "from": "Charlie",
    "to": "Diana",
    "timestamp": "2/7/2026, 2:30 PM",
    "photo": "No"
  }
]
```

Each entry shows:
- **from**: Person who created the link
- **to**: Person receiving the Valentine's
- **timestamp**: When the link was created
- **photo**: Whether they uploaded a photo

---

## 🐛 Troubleshooting

### Photo Won't Upload After Cropping

- Make sure the image is in a supported format (JPG, PNG, GIF, etc.)
- Check that your browser allows file uploads
- Try a different photo
- Clear browser cache and try again

### Can't Access Admin Dashboard

- Make sure you're using the correct password
- Check if cookies/localStorage are enabled
- Try opening in incognito/private mode
- Make sure admin.html is in the same folder

### Data Not Showing in Admin

- Click "Refresh Data" button
- Make sure photos have been uploaded from the main page
- Check that localStorage is enabled in your browser
- Try exporting/importing to reset data

### Admin Password Not Working

- Password is case-sensitive
- Make sure caps lock is off
- Correct password: `valentine2026`
- If you changed it, use your new password

---

## 📱 Mobile Usage

**On Mobile Phones:**

✅ Crop tool works great on touchscreen
✅ All sliders are touch-responsive
✅ Admin dashboard is mobile-friendly
✅ Export/Import works on mobile

**Tips for Mobile:**
- Use landscape mode for better cropping experience
- Give yourself space around the device
- Take your time with slider adjustments
- Screenshots can be directly cropped

---

## 🌐 GitHub Pages Deployment

1. Upload all files to GitHub repository
2. Enable GitHub Pages in settings
3. Site goes live at: `https://yourusername.github.io/repo-name`
4. Data is stored locally on each device
5. Use Export/Import to transfer data between devices

---

## 🔄 Workflow Example

**As a User:**

1. Go to main page (`index.html`)
2. Enter my name and crush's name
3. Click "Generate Link"
4. Copy the link and send it
5. Click "Add Photos"
6. Select a cute photo
7. Use crop tool to frame it nicely
8. Click "Create Poster"
9. Download poster

**As an Admin:**

1. Go to admin page (`admin.html`)
2. Enter password
3. See how many people participated
4. Export data as backup
5. Monitor new registrations

---

## 💡 Pro Tips

### For Best Crop Results:

- **Profile Photos**: Use 1:1 (square) aspect ratio
- **Group Photos**: Use 16:9 (wide) aspect ratio
- **Full Body**: Use 4:3 aspect ratio
- **Portraits**: Use 9:16 (tall) aspect ratio

### For Data Management:

- Export data weekly as backup
- Save backups with dates (backup-Feb-08-2026.json)
- Import backups before deploying to new server
- Keep multiple backups in case of issues

### For Best Experience:

- Use modern browsers (Chrome, Firefox, Safari, Edge)
- Enable JavaScript
- Allow file uploads in browser settings
- Use Wi-Fi for faster uploads

---

## 📞 Support

If you need help:

1. Check the main `README.md` for feature overview
2. Check `CHANGES.md` for technical details
3. Review this document for common issues
4. Check browser console for error messages (F12)
5. Try clearing cache and refreshing page

---

## 🎉 You're All Set!

Your Valentine's website now has:
- ✅ Professional photo cropping tool
- ✅ Automatic data tracking
- ✅ Admin dashboard
- ✅ Data backup/restore
- ✅ GitHub Pages ready
- ✅ Mobile friendly

**Happy Valentine's! 💕**

