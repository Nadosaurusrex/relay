# Relay Landing Page

Production-ready landing page for Relay, the accountability infrastructure for AI agents.

## Features

- ⚡ **Vite + React + TypeScript** - Fast, modern stack
- 🎨 **Tailwind CSS v4** - Utility-first styling with custom theme
- 🎭 **Terminal Aesthetic** - Monospace fonts, code-inspired design
- 🎬 **Smooth Animations** - Scroll-triggered reveals and micro-interactions
- 📱 **Fully Responsive** - Mobile-first design
- ♿ **Accessible** - WCAG AA compliant
- 🚀 **Performance Optimized** - Fast loading, GPU-accelerated animations

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd lib/relay-landing
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view it in the browser.

### Build

```bash
npm run build
```

Output will be in the `dist/` directory, ready to be served by the FastAPI backend.

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
cp .env.example .env.local
```

Variables:
- `VITE_SHEETS_URL` - Google Apps Script Web App URL for waitlist
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_ENVIRONMENT` - Environment (development/production)

## Project Structure

```
src/
├── components/           # React components
│   ├── ui/              # Base UI components (Button, Card, Input)
│   ├── AnimatedBackground.tsx
│   ├── Hero.tsx
│   ├── ProblemViz.tsx
│   ├── SolutionCards.tsx
│   ├── HowItWorks.tsx
│   ├── Waitlist.tsx
│   └── Footer.tsx
├── lib/
│   └── utils.ts         # Utility functions
├── App.tsx              # Main app component
├── main.tsx             # Entry point
└── index.css            # Global styles + Tailwind
```

## Design System

### Colors

- **Background**: Deep charcoal with subtle blue tint
- **Primary**: Electric blue (#4E9FF5)
- **Accent**: Purple (#B857FF)
- **Success**: Green (for approvals)
- **Error**: Red (for denials)

### Typography

- **Headings**: JetBrains Mono (bold, monospace)
- **Body**: Space Mono (monospace for technical aesthetic)
- **Code**: JetBrains Mono

### Animations

All animations respect `prefers-reduced-motion` for accessibility.

## Google Sheets Integration

The waitlist form submits to Google Sheets via Google Apps Script Web App.

### Setup Instructions

1. Create a new Google Sheet with two tabs:
   - `Waitlist`: Columns: Email, Timestamp, UTM Source, UTM Medium, UTM Campaign
   - `Analytics`: Columns: Event Type, Timestamp, Page, Metadata

2. Create a Google Apps Script (Extensions → Apps Script):

```javascript
function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet();
  const data = JSON.parse(e.postData.contents);

  if (data.type === 'waitlist') {
    sheet.getSheetByName('Waitlist').appendRow([
      data.email,
      new Date(),
      data.utm_source || '',
      data.utm_medium || '',
      data.utm_campaign || ''
    ]);
  } else if (data.type === 'analytics') {
    sheet.getSheetByName('Analytics').appendRow([
      data.event_type,
      new Date(),
      data.page || '',
      JSON.stringify(data.metadata || {})
    ]);
  }

  return ContentService.createTextOutput(JSON.stringify({success: true}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

3. Deploy as Web App:
   - Click "Deploy" → "New deployment"
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Copy the Web App URL

4. Add to `.env.local`:
```
VITE_SHEETS_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
```

## Integration with Backend

The built frontend is served by the FastAPI backend:

1. Build the frontend:
```bash
npm run build
```

2. Copy `dist/` contents to `gateway/static/`:
```bash
cp -r dist/* ../../gateway/static/
```

3. The FastAPI backend will serve the landing page at `/` and API at `/api/v1/*`.

See the main project README for deployment instructions.

## License

Same as parent project.
