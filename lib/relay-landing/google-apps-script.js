/**
 * Relay Landing Page - Waitlist Google Apps Script
 *
 * Setup Instructions:
 * 1. Open Google Sheets and create a new spreadsheet named "Relay Waitlist"
 * 2. Create headers in row 1: Timestamp | Email | Company | Framework | Use Case | UTM Source | UTM Medium | UTM Campaign
 * 3. Go to Extensions > Apps Script
 * 4. Delete any existing code and paste this script
 * 5. Click Deploy > New deployment
 * 6. Select type: Web app
 * 7. Execute as: Me
 * 8. Who has access: Anyone
 * 9. Click Deploy and copy the Web app URL
 * 10. Add the URL to your .env file as VITE_SHEETS_URL
 */

function doPost(e) {
  try {
    // Check if postData exists
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'No data received'
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Parse the JSON payload
    const data = JSON.parse(e.postData.contents);

    // Get the active spreadsheet
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Ensure headers exist (run once or check if first row is empty)
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Timestamp',
        'Email',
        'Company',
        'Framework',
        'Use Case',
        'UTM Source',
        'UTM Medium',
        'UTM Campaign'
      ]);
    }

    // Append the new row
    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.email || '',
      data.company_name || '',
      data.framework || '',
      data.use_case || '',
      data.utm_source || '',
      data.utm_medium || '',
      data.utm_campaign || ''
    ]);

    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    // Log error and return error response
    Logger.log('Error: ' + error.toString());
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  // Handle GET requests (for testing and health checks)
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'ok',
      message: 'Relay Waitlist API is running',
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Test function - run this from the Apps Script editor to test
 */
function testDoPost() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        type: 'waitlist',
        email: 'test@example.com',
        company_name: 'Test Company',
        framework: 'langchain',
        use_case: 'infrastructure',
        utm_source: 'test',
        utm_medium: 'test',
        utm_campaign: 'test',
        timestamp: new Date().toISOString()
      })
    }
  };

  const result = doPost(testData);
  Logger.log('Test result: ' + result.getContent());
}

/**
 * Optional: Add data validation and email notifications
 * To use this version, replace the doPost function with this one
 */
function doPostWithNotification(e) {
  try {
    // Check if postData exists
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService
        .createTextOutput(JSON.stringify({
          success: false,
          error: 'No data received'
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!data.email || !emailRegex.test(data.email)) {
      throw new Error('Invalid email address');
    }

    // Check for duplicates
    const emails = sheet.getRange('B:B').getValues().flat();
    if (emails.includes(data.email)) {
      return ContentService
        .createTextOutput(JSON.stringify({
          success: true,
          message: 'Already subscribed'
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Append row
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Timestamp',
        'Email',
        'Company',
        'Framework',
        'Use Case',
        'UTM Source',
        'UTM Medium',
        'UTM Campaign'
      ]);
    }

    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.email || '',
      data.company_name || '',
      data.framework || '',
      data.use_case || '',
      data.utm_source || '',
      data.utm_medium || '',
      data.utm_campaign || ''
    ]);

    // Optional: Send notification email to yourself
    const notificationEmail = 'your-email@example.com'; // Change this!
    MailApp.sendEmail({
      to: notificationEmail,
      subject: '🎉 New Relay Waitlist Signup',
      body: `
New signup details:
- Email: ${data.email}
- Company: ${data.company_name}
- Framework: ${data.framework}
- Use Case: ${data.use_case}
- UTM Source: ${data.utm_source}

View all signups: ${SpreadsheetApp.getActiveSpreadsheet().getUrl()}
      `
    });

    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    Logger.log('Error: ' + error.toString());
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
