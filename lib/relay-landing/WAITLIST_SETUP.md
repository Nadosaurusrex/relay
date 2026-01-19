# Google Sheets Waitlist Setup Guide

This guide will help you set up the Google Sheets integration for your Relay landing page waitlist.

## Step 1: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Relay Waitlist" (or any name you prefer)
4. In row 1, add these column headers:
   - A1: `Timestamp`
   - B1: `Email`
   - C1: `Company`
   - D1: `Framework`
   - E1: `Use Case`
   - F1: `UTM Source`
   - G1: `UTM Medium`
   - H1: `UTM Campaign`

## Step 2: Add Apps Script

1. In your Google Sheet, click **Extensions** > **Apps Script**
2. Delete any existing code in the editor
3. Copy the entire contents of `google-apps-script.js` and paste it
4. Click the **Save** icon (💾) or press `Ctrl+S` / `Cmd+S`
5. Name your project (e.g., "Relay Waitlist API")

## Step 3: Deploy as Web App

1. In the Apps Script editor, click **Deploy** > **New deployment**
2. Click the gear icon (⚙️) next to "Select type"
3. Select **Web app**
4. Configure the deployment:
   - **Description**: "Relay Waitlist v1" (or any description)
   - **Execute as**: **Me** (your@email.com)
   - **Who has access**: **Anyone**
5. Click **Deploy**
6. You may need to authorize the script:
   - Click **Authorize access**
   - Choose your Google account
   - Click **Advanced** > **Go to [Project Name] (unsafe)**
   - Click **Allow**
7. Copy the **Web app URL** (it will look like: `https://script.google.com/macros/s/AKfycby.../exec`)

## Step 4: Configure Environment Variables

1. In your project, create or edit `.env.local`:
   ```bash
   VITE_SHEETS_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
   ```
2. Replace `YOUR_SCRIPT_ID` with the URL you copied in Step 3

## Step 5: Test the Integration

### Local Testing

1. Start your dev server:
   ```bash
   npm run dev
   ```
2. Navigate to the waitlist section
3. Fill out the form with test data
4. Submit the form
5. Check your Google Sheet - you should see a new row with your test data

### Testing POST Requests (Optional)

You can test the endpoint directly using curl:

```bash
curl -X POST "YOUR_WEB_APP_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "waitlist",
    "email": "test@example.com",
    "company_name": "Test Company",
    "framework": "langchain",
    "use_case": "infrastructure",
    "utm_source": "twitter",
    "utm_medium": "social",
    "utm_campaign": "launch",
    "timestamp": "2026-01-19T12:00:00Z"
  }'
```

## Optional: Enable Email Notifications

If you want to receive an email every time someone joins the waitlist:

1. In `google-apps-script.js`, replace `doPost` function name with `doPostWithNotification`
2. Update line 115 with your email:
   ```javascript
   const notificationEmail = 'your-email@example.com'; // Change this!
   ```
3. Save and redeploy (Deploy > Manage deployments > Edit > Version: New version > Deploy)

## Troubleshooting

### "Script function not found: doPost"
- Make sure you saved the script before deploying
- Redeploy the web app

### "Authorization required"
- Go back to step 3.6 and complete the authorization process
- Make sure you selected "Execute as: Me" in deployment settings

### Form submits but no data appears in sheet
- Check the Apps Script logs: In Apps Script editor, click **Executions** (⏱️ icon on left sidebar)
- Verify the Web App URL in your `.env.local` file is correct
- Make sure you're using the `/exec` URL, not the `/dev` URL

### CORS errors in browser console
- This is expected! The script uses `mode: 'no-cors'` in the fetch request
- Data is still being sent correctly even with CORS errors
- Check your Google Sheet to verify data is arriving

## Data Structure

Each row in your sheet will contain:

| Timestamp | Email | Company | Framework | Use Case | UTM Source | UTM Medium | UTM Campaign |
|-----------|-------|---------|-----------|----------|------------|------------|--------------|
| 2026-01-19T10:30:00.000Z | user@company.com | Acme Corp | langchain | infrastructure | twitter | social | launch |

## Security Considerations

- The script runs as **you**, so it has access to your Google account
- Anyone can POST data to the endpoint, so consider adding rate limiting if needed
- The script validates email format and checks for duplicates (if using notification version)
- No sensitive data should be collected in this form

## Production Deployment

When deploying to production (Netlify/Vercel):

1. Add the environment variable to your hosting platform:
   - **Netlify**: Site settings > Environment variables
   - **Vercel**: Project settings > Environment Variables
   - **AWS Amplify**: App settings > Environment variables

2. Set the variable:
   ```
   VITE_SHEETS_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
   ```

3. Redeploy your site

## Monitoring & Analytics

To track waitlist performance:

1. Open your Google Sheet
2. Click **Extensions** > **Google Sheets** > **Create a pivot table**
3. Suggested views:
   - Signups by date (Timestamp)
   - Signups by framework (Framework)
   - Signups by use case (Use Case)
   - Signups by UTM source (UTM Source)

## Alternative: Export Data

To export your waitlist data:

1. Open your Google Sheet
2. Click **File** > **Download** > **Comma-separated values (.csv)**
3. Import into your CRM or email service provider

---

**Need Help?**
- Check the Apps Script execution logs for errors
- Verify your `.env.local` file is in the project root
- Ensure the Google Sheet is in your Google Drive
- Test the endpoint with curl before testing through the website
