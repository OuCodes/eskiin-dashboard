# Reports Storage

This directory stores uploaded reports for easy access in the dashboard.

## Directory Structure

```
reports/
├── kandy/          # Kandy agency creative reports
├── internal/       # Internal top performer reports  
└── ad-sets/        # Ad set testing reports
```

## Naming Convention

Reports are automatically named when uploaded:
- `{type}-{YYYY-MM-DD}.md` (e.g., `kandy-2025-12-08.md`)
- Or use custom names when uploading

## How It Works

1. Upload a report in the dashboard
2. It's automatically saved to the appropriate folder
3. Available in the dropdown for future viewing
4. Committed to GitHub for persistence
