# 📊 How to View Admin Data & Data Persistence Guide

## 🎯 Quick Summary

✅ **Data saves automatically** when you:
- Generate a Valentine's link
- Upload a photo

✅ **Data persists** even when:
- You close the tab
- You close the browser
- You close the computer

✅ **View your data** in admin dashboard

---

## 🔍 How to View Admin Data

### Step 1: Open Admin Dashboard
- Open `admin.html` in your browser
- URL: `admin.html` or `http://localhost/admin.html`

### Step 2: Enter Password
- Password: `valentine2026`
- Click OK

### Step 3: View Your Data

You'll see:

**📊 Statistics at Top:**
```
Total Users: X
With Photos: X
Last 24 Hours: X
```

**📋 Table Below:**
```
#  | From      | To        | Date & Time          | Photo
1  | Alice     | Bob       | 2/8/2026, 3:45 PM    | Yes
2  | Charlie   | Diana     | 2/7/2026, 2:30 PM    | No
```

---

## 💾 How Data is Saved

### Where Data is Stored:
**Browser's localStorage** (on your device)

### When Data Saves:

**1. When you create a link:**
```
Enter "From" name → Enter "To" name → Click "Generate Link"
                           ↓
              Data saved automatically
```

**2. When you upload a photo:**
```
Click "Add Photos" → Select Photo → Crop → Click "Use This Photo"
                                      ↓
                        Data saved automatically
                        (photo status updated to "Yes")
```

### Data Saved Includes:
```javascript
{
  from: "Your Name",
  to: "Their Name",
  timestamp: "2/8/2026, 3:45 PM",
  photo: "Yes" or "No"
}
```

---

## ✅ Data Persistence - How It Works

### Scenario 1: Close Tab
```
Generate Link → Close Tab → Close Browser
     ↓
  Data saved in localStorage
     ↓
  Reopen browser & admin.html
     ↓
  Data still there! ✓
```

### Scenario 2: Computer Restart
```
Generate Link → Restart Computer
     ↓
  Data saved in localStorage
     ↓
  Open browser & admin.html
     ↓
  Data still there! ✓
```

### Scenario 3: Download & Restore
```
Export Data (admin.html) → Backup JSON file
     ↓
  Transfer to another computer
     ↓
  Open admin.html → Click "Import Data" → Select JSON
     ↓
  Data restored! ✓
```

---

## 🔧 Access Admin Data - Easy Steps

### Quick Access:
1. **Open:** `admin.html`
2. **Password:** `valentine2026`
3. **View:** All user registrations

### What You See:
- Total number of users
- Number of photos uploaded
- Recent users (last 24 hours)
- Complete user table

---

## 📱 Verify Data is Saving

### Test 1: Check After Generating Link
1. Enter names and generate link
2. Open `admin.html` (password: valentine2026)
3. Check that your entry appears in table ✓

### Test 2: Check After Uploading Photo
1. Click "Add Photos" and upload
2. Open `admin.html` (password: valentine2026)
3. Check that "Photo" column shows "Yes" ✓

### Test 3: Close & Reopen
1. Generate a link
2. **Close the entire browser**
3. **Reopen browser**
4. Go to `admin.html` (password: valentine2026)
5. Data still there! ✓

### Test 4: Export to Verify
1. Go to `admin.html`
2. Click "Export Data"
3. File downloads as JSON
4. Open the JSON file in text editor
5. See all your data saved! ✓

---

## 💡 Pro Tips

### Backup Your Data
**Every week:**
1. Open admin.html
2. Click "Export Data"
3. Save the JSON file somewhere safe
4. You now have a backup!

### Restore Data
**When you need to:**
1. Open admin.html
2. Click "Import Data"
3. Select your backup JSON file
4. Data is restored!

### On GitHub Pages
**Data persists locally:**
- Each browser keeps own copy
- Use Export/Import to share data
- Perfect for tracking registrations

---

## ❓ FAQ

### Q: Where is my data stored?
**A:** In your browser's localStorage. Not uploaded anywhere!

### Q: Will data disappear if I clear cache?
**A:** Yes. That's why we Export backups.

### Q: Can I see data on another device?
**A:** Export here, Import there. Simple!

### Q: Is data secure?
**A:** Yes! It's stored locally on your device.

### Q: What if I forget password?
**A:** Edit admin.html and change `valentine2026` to your new password.

### Q: How much data can I store?
**A:** Depends on browser, usually 5-10MB.

### Q: Does data need internet?
**A:** No! Everything works offline.

---

## 📋 Admin Features

### View Data
✓ See all registrations
✓ See photo upload status
✓ See registration dates

### Export Data
✓ Download as JSON file
✓ Perfect for backup
✓ Share between devices

### Import Data
✓ Upload previous backup
✓ Restore data anytime
✓ Merge with existing data

### Clear Data
✓ Delete all data
✓ Password protected
✓ Careful! Can't undo

### Refresh Data
✓ Reload latest data
✓ See new registrations
✓ Update statistics

---

## 🎯 Data Flow Diagram

```
User Creates Link
       ↓
Data Generated
       ↓
Saved to localStorage
       ↓
User Uploads Photo
       ↓
Data Updated (photo: "Yes")
       ↓
Saved to localStorage
       ↓
Admin Opens Dashboard
       ↓
Displays all data from localStorage
       ↓
Admin Exports → JSON backup file
       ↓
Admin can Import backup anytime
```

---

## ✨ Your Data is Always Safe

### Automatic Saving ✓
- No manual save needed
- Happens instantly
- Works offline

### Persistent Storage ✓
- Survives browser restart
- Survives computer restart
- Survives app updates

### Backup Capability ✓
- Export anytime
- Import anytime
- Keep multiple backups

### Privacy First ✓
- Data stays local
- Not uploaded anywhere
- You have full control

---

## 🚀 Next Steps

1. **Test the crop tool:** Upload a photo and crop it
2. **Generate a link:** Enter names and create link
3. **Check admin:** Open admin.html, password: valentine2026
4. **See your data:** View the table with your registration
5. **Export backup:** Click "Export Data" to backup
6. **Close browser:** Restart and verify data persists

---

## 📞 Remember

- **Crop Tool:** Just click and drag to select area
- **Admin Access:** password = valentine2026
- **Data Saves:** Automatically when you create/upload
- **Data Persists:** Even after closing everything
- **Export:** Use to backup your data
- **Import:** Use to restore from backup

---

**Your data is safe, secure, and always saved!** 💾✓

