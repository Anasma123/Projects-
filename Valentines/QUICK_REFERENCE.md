# 🚀 Quick Reference Card

## 📸 Photo Crop Tool

**How to Use:**
1. Click "Add Photos"
2. Select image
3. Adjust using controls
4. Click "Use This Photo"

**Controls:**
| Control | Range | Default |
|---------|-------|---------|
| Aspect Ratio | 1:1, 4:3, 16:9, 9:16 | 1:1 (Square) |
| Zoom | 50% - 200% | 100% |
| Rotate | 0° - 360° | 0° |
| X Position | -200 to 200 | 0 |
| Y Position | -200 to 200 | 0 |

---

## 👨‍💼 Admin Dashboard

**Access:**
- URL: `admin.html`
- Password: `valentine2026`

**Features:**
- View total users
- View users with photos
- View recent users (24h)
- User registration table
- Export data as JSON
- Import data from JSON
- Clear all data

**Data Stored:**
```
from, to, timestamp, photo status
```

---

## 💾 Backup & Restore

**Export (Backup):**
1. Open admin.html
2. Enter password
3. Click "Export Data"
4. File downloads as JSON

**Import (Restore):**
1. Open admin.html
2. Enter password
3. Click "Import Data"
4. Select JSON file
5. Data is merged

---

## 🔒 Security

**Default Password:** `valentine2026`

**Change Password:**
1. Edit admin.html
2. Find: `'valentine2026'`
3. Replace with new password
4. Save file

---

## 🌐 Deployment

**GitHub Pages:**
1. Create GitHub repo
2. Upload files
3. Enable Pages in settings
4. Deploy to: `yourusername.github.io/repo-name`

**Local:**
- Just open `index.html`
- Everything works offline

---

## 📊 Data Storage

**Where Data is Stored:**
- Primary: Browser localStorage
- Backup: JSON export files
- Optional: Firebase cloud

**Per Device:**
- Each browser keeps own copy
- Use export/import to share

---

## 🎯 Workflow

**User Workflow:**
```
Enter Names → Generate Link → Add Photos 
→ Crop Photo → Create Poster → Download
```

**Admin Workflow:**
```
Access Dashboard → View Stats → Export Data 
→ Backup → Import Later → Restore
```

---

## 🔧 File Structure

```
/
├── index.html          Main website
├── admin.html          Admin dashboard
├── README.md           Main guide
├── SETUP_GUIDE.md      Instructions
├── CHANGES.md          Technical details
├── admin-functions.js  Helper functions
└── firebase-integration.js  Firebase setup
```

---

## 📱 Compatibility

✅ Desktop (Windows, Mac, Linux)
✅ Mobile (iOS, Android)
✅ Tablet
✅ All modern browsers
✅ Offline capability

---

## 💡 Pro Tips

**Best Crop Ratios:**
- Profile: 1:1 (Square)
- Group: 16:9 (Wide)
- Full Body: 4:3
- Portrait: 9:16 (Tall)

**Data Management:**
- Export weekly
- Keep backups
- Import to new device
- Never delete export files

---

## 🆘 Troubleshooting

**Crop tool not working:**
- Refresh page
- Try different image
- Check browser supports Canvas
- Clear cache

**Admin not loading:**
- Check password (case-sensitive)
- Make sure JavaScript enabled
- Try incognito mode
- Clear cookies

**Data not showing:**
- Click Refresh Data
- Make sure localStorage enabled
- Try uploading new photo
- Export existing data

---

## 📞 Commands

**View Data (Console):**
```javascript
JSON.parse(localStorage.getItem('valentineUsers'))
```

**Clear Data (Console):**
```javascript
localStorage.removeItem('valentineUsers')
```

**Export Data (Admin UI):**
Click "Export Data" button

**Import Data (Admin UI):**
Click "Import Data" button

---

## 🎁 Features

✨ Photo cropping with zoom/rotate
📊 User statistics dashboard
💾 Data export/import
🔐 Password protection
📱 Mobile responsive
🌐 GitHub Pages ready
⚡ No server needed
🔒 Privacy-first

---

## ✅ Checklist

- [ ] Upload to GitHub
- [ ] Enable GitHub Pages
- [ ] Test on mobile
- [ ] Export first backup
- [ ] Share link with friends
- [ ] Monitor registrations
- [ ] Export data weekly
- [ ] Update photos

---

**Made with ❤️ for Valentine's Day**

