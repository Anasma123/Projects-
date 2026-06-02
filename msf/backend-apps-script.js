// Google Apps Script Backend for Urava 2026 Event Registration Portal
// Saves registration data to Google Sheet and uploads certificates to Google Drive

const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'; // Replace with your actual Google Sheet ID
const SHEET_NAME = 'Sheet1';                       // Replace with your actual Sheet tab name (e.g. Sheet1)
const DRIVE_FOLDER_ID = 'YOUR_FOLDER_ID_HERE';     // Replace with your actual Google Drive Folder ID

function doGet(e) {
  return ContentService.createTextOutput("Urava 2026 Registration API is running successfully. Send a POST request to register.")
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  try {
    const p = e.parameter;
    
    // Extract registration data from POST request parameters
    const fullName = String(p.fullName || '').trim();
    const fatherName = String(p.fatherName || '').trim();
    const phone = String(p.phone || '').trim();
    const place = String(p.place || '').trim();
    const dob = String(p.dob || '').trim();
    const gender = String(p.gender || '').trim();
    const academicCategory = String(p.academicCategory || '').trim();
    
    // Validation: check for required fields
    if (!fullName || !fatherName || !phone || !place || !dob || !gender || !academicCategory) {
      return jsonResponse_({
        success: false,
        message: 'Registration failed: Missing required fields.'
      });
    }
    
    let fileUrl = '';
    let storedFileName = '';
    
    // Process and save certificate file to Google Drive if applicable
    if (academicCategory !== 'None of the Above' && p.certificateBase64) {
      const base64Data = p.certificateBase64;
      const originalFileName = String(p.certificateName || 'certificate.pdf').trim();
      const mimeType = String(p.certificateMime || 'application/pdf').trim();
      
      // Dynamic clean file renaming: [Full Name] - [Academic Excellence Category] - [Original Filename]
      const fileExtension = originalFileName.includes('.') 
        ? originalFileName.substring(originalFileName.lastIndexOf('.')) 
        : '';
      const sanitizedFullName = fullName.replace(/[^a-zA-Z0-9\s]/g, '');
      const sanitizedCategory = academicCategory.replace(/[^a-zA-Z0-9\s\+]/g, '');
      
      storedFileName = `${sanitizedFullName} - ${sanitizedCategory}${fileExtension}`;
      
      // Decode Base64 and write file to Drive folder
      const bytes = Utilities.base64Decode(base64Data);
      const blob = Utilities.newBlob(bytes, mimeType, storedFileName);
      
      const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
      const file = folder.createFile(blob);
      
      // Set sharing settings so organizers can view/download from URL
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      
      fileUrl = file.getUrl();
    } else {
      // Set default values if Academic Category is "None of the Above"
      storedFileName = 'N/A';
      fileUrl = 'N/A';
    }
    
    // Open Google Sheet and save registration row
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
    if (!sheet) {
      return jsonResponse_({
        success: false,
        message: `Spreadsheet tab "${SHEET_NAME}" not found.`
      });
    }
    
    // Append row matching the required column structure
    sheet.appendRow([
      new Date(),       // Column A: Timestamp
      fullName,         // Column B: Full Name
      fatherName,       // Column C: Father Name
      phone,            // Column D: Phone Number
      place,            // Column E: Place
      dob,              // Column F: Date of Birth
      gender,           // Column G: Gender
      academicCategory, // Column H: Academic Category
      storedFileName,   // Column I: Certificate File Name
      fileUrl           // Column J: Certificate Drive URL
    ]);
    
    return jsonResponse_({
      success: true,
      message: 'Registration completed successfully.',
      fileName: storedFileName,
      fileUrl: fileUrl
    });
    
  } catch (error) {
    return jsonResponse_({
      success: false,
      message: 'Server error: ' + error.toString()
    });
  }
}

// Utility function to respond with standard JSON format
function jsonResponse_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
