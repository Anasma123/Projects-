// PDF Generator for Exam Timetable with Beautiful Design
class TimetablePDFGenerator {
    constructor() {
        this.logoBase64 = 'images/logo.jpg';
    }

    generatePDF(examData) {
        const { year, classId, term, timetable, classNames, terms } = examData;
        
        const filename = `Exam_Timetable_${classNames[classId]}_${terms[term]}_${year}.pdf`;
        
        // Create HTML content for PDF
        const htmlContent = this.generateHTMLContent(examData);
        
        // Create a new window for printing
        const printWindow = window.open('', '_blank');
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        printWindow.focus();
        
        // Wait for content to load, then trigger print
        setTimeout(() => {
            printWindow.print();
            // Close window after print dialog is shown
            setTimeout(() => {
                printWindow.close();
            }, 1000);
        }, 1500);
    }

    generateHTMLContent(examData) {
        const { year, classId, term, timetable, classNames, terms } = examData;
        
        const classNameFull = classNames[classId];
        const termName = terms[term];
        
        // Generate table rows
        const tableRows = timetable.map((entry, index) => `
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 14px 16px; text-align: center; background-color: ${index % 2 === 0 ? '#ffffff' : '#f8fafc'};">${entry.date}</td>
                <td style="padding: 14px 16px; text-align: center; background-color: ${index % 2 === 0 ? '#ffffff' : '#f8fafc'};">${entry.day}</td>
                <td style="padding: 14px 16px; text-align: left; font-weight: 600; background-color: ${index % 2 === 0 ? '#ffffff' : '#f8fafc'};">${entry.subject}</td>
                <td style="padding: 14px 16px; text-align: center; background-color: ${index % 2 === 0 ? '#ffffff' : '#f8fafc'};">${entry.time}</td>
            </tr>
        `).join('');

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Exam Timetable - ${classNameFull} ${termName}</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                        padding: 20px;
                    }
                    
                    .container {
                        max-width: 900px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 15px;
                        overflow: hidden;
                        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
                    }
                    
                    .header {
                        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 50%, #0c4a6e 100%);
                        color: white;
                        padding: 50px 30px;
                        text-align: center;
                        position: relative;
                        overflow: hidden;
                    }
                    
                    .header::before {
                        content: "";
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
                                    radial-gradient(circle at 80% 80%, rgba(255,255,255,0.05) 0%, transparent 50%);
                        pointer-events: none;
                    }
                    
                    .header-content {
                        position: relative;
                        z-index: 1;
                    }
                    
                    .logo-section {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 20px;
                    }
                    
                    .logo {
                        width: 100px;
                        height: 100px;
                        background: white;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 20px;
                        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
                        overflow: hidden;
                    }
                    
                    .logo img {
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                    }
                    
                    .academy-info h1 {
                        font-size: 32px;
                        font-weight: 700;
                        margin-bottom: 5px;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    
                    .academy-info p {
                        font-size: 14px;
                        opacity: 0.9;
                        letter-spacing: 1px;
                    }
                    
                    .exam-title {
                        margin-top: 30px;
                        padding-top: 30px;
                        border-top: 2px solid rgba(255, 255, 255, 0.2);
                    }
                    
                    .exam-title h2 {
                        font-size: 28px;
                        margin-bottom: 10px;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    }
                    
                    .exam-title p {
                        font-size: 16px;
                        opacity: 0.85;
                    }
                    
                    .content {
                        padding: 40px;
                    }
                    
                    .exam-details {
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
                        gap: 20px;
                        margin-bottom: 40px;
                    }
                    
                    .detail-card {
                        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                        border-left: 5px solid #1e40af;
                        padding: 20px;
                        border-radius: 8px;
                    }
                    
                    .detail-card label {
                        display: block;
                        font-size: 12px;
                        font-weight: 600;
                        color: #1e3a8a;
                        text-transform: uppercase;
                        margin-bottom: 8px;
                        letter-spacing: 1px;
                    }
                    
                    .detail-card .value {
                        font-size: 20px;
                        font-weight: 700;
                        color: #0c4a6e;
                    }
                    
                    .timetable-section h3 {
                        font-size: 22px;
                        color: #1e40af;
                        margin-bottom: 20px;
                        padding-bottom: 10px;
                        border-bottom: 3px solid #1e40af;
                    }
                    
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 30px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                    }
                    
                    thead {
                        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
                        color: white;
                    }
                    
                    th {
                        padding: 16px;
                        text-align: left;
                        font-weight: 600;
                        text-transform: uppercase;
                        font-size: 12px;
                        letter-spacing: 1px;
                    }
                    
                    td {
                        padding: 14px 16px;
                        text-align: left;
                    }
                    
                    .footer {
                        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                        padding: 30px;
                        text-align: center;
                        border-top: 2px solid #d1d5db;
                    }
                    
                    .footer p {
                        color: #6b7280;
                        font-size: 12px;
                        margin-bottom: 10px;
                    }
                    
                    .footer .website {
                        color: #1e40af;
                        font-weight: 600;
                    }
                    
                    .watermark {
                        position: fixed;
                        bottom: 30px;
                        right: 30px;
                        opacity: 0.05;
                        font-size: 100px;
                        font-weight: bold;
                        color: #1e40af;
                        transform: rotate(-30deg);
                        pointer-events: none;
                        z-index: -1;
                    }
                    
                    .note {
                        background: linear-gradient(135deg, #fef08a 0%, #fde047 100%);
                        border-left: 5px solid #ca8a04;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 30px;
                    }
                    
                    .note p {
                        color: #854d0e;
                        font-size: 13px;
                        line-height: 1.6;
                    }
                    
                    @media print {
                        body {
                            background: white;
                            padding: 0;
                        }
                        
                        .container {
                            box-shadow: none;
                            border-radius: 0;
                        }
                        
                        .header {
                            print-color-adjust: exact;
                            -webkit-print-color-adjust: exact;
                        }
                        
                        table {
                            page-break-inside: avoid;
                        }
                        
                        .watermark {
                            opacity: 0.05;
                        }
                    }
                    
                    @page {
                        margin: 0.5in;
                    }
                </style>
            </head>
            <body>
                <div class="watermark">CH ACADEMY</div>
                
                <div class="container">
                    <!-- Header -->
                    <div class="header">
                        <div class="header-content">
                            <div class="logo-section">
                                <div class="logo">
                                    <img src="images/logo.jpg" alt="CH Academy Logo">
                                </div>
                                <div class="academy-info">
                                    <h1>CH ACADEMY</h1>
                                    <p>FOR EDUCATION</p>
                                </div>
                            </div>
                            
                            <div class="exam-title">
                                <h2>EXAMINATION TIMETABLE</h2>
                                <p>${classNameFull} | ${termName} | Academic Year ${year}</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Content -->
                    <div class="content">
                        <!-- Exam Details Cards -->
                        <div class="exam-details">
                            <div class="detail-card">
                                <label>Class</label>
                                <div class="value">${classNameFull}</div>
                            </div>
                            <div class="detail-card">
                                <label>Term</label>
                                <div class="value">${termName}</div>
                            </div>
                            <div class="detail-card">
                                <label>Year</label>
                                <div class="value">${year}</div>
                            </div>
                        </div>
                        
                        <!-- Timetable Section -->
                        <div class="timetable-section">
                            <h3>📅 Examination Schedule</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Day</th>
                                        <th>Subject</th>
                                        <th>Time</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tableRows}
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Note -->
                        <div class="note">
                            <p><strong>Note:</strong> Please arrive 15 minutes before the scheduled time.</p>
                            <p>Ensure to bring all necessary materials and identification.</p>
                            <p>Follow all exam guidelines as provided by the academy.</p>
                            <p>any malpractice will lead to disqualification.</p>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="footer">
                        <p><strong>CH Academy For Education</strong></p>
                        <p>📍 Kerala, India | 📞 +91 9656934482 | 📧 chacademyinfo@gmail.com</p>
                        <p class="website">https://anasma123.github.io/Projects-/ch%20acadey/</p>
                        <p style="margin-top: 15px; border-top: 1px solid #d1d5db; padding-top: 15px;">
                            Generated on ${new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })} | 
                            Exam Portal 2025
                        </p>
                    </div>
                </div>
            </body>
            </html>
        `;
    }
}

// Export for use in HTML
window.TimetablePDFGenerator = TimetablePDFGenerator;
