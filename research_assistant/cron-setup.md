# Weekly Competitor Intelligence - Cron Setup

## Option 1: Cron Job (Linux/macOS)

Add to your crontab (`crontab -e`):

```bash
# Run every Monday at 9:00 AM
0 9 * * 1 cd /path/to/research_assistant && /path/to/venv/bin/research-assistant weekly-report -d /path/to/reports

# Run every Monday at 9:00 AM with email notification
0 9 * * 1 cd /path/to/research_assistant && /path/to/venv/bin/research-assistant weekly-report -d /path/to/reports 2>&1 | mail -s "Weekly Competitor Report" ceo@webnode.com
```

## Option 2: GitHub Actions (Scheduled)

Create `.github/workflows/competitor-report.yml`:

```yaml
name: Weekly Competitor Intelligence

on:
  schedule:
    # Every Monday at 9:00 AM UTC
    - cron: '0 9 * * 1'
  workflow_dispatch:  # Allow manual trigger

jobs:
  generate-report:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd research_assistant
          pip install -e .

      - name: Generate report
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SEARCH_API_KEY: ${{ secrets.SEARCH_API_KEY }}
        run: |
          cd research_assistant
          research-assistant weekly-report -d ./reports

      - name: Upload report artifact
        uses: actions/upload-artifact@v4
        with:
          name: competitor-report-${{ github.run_id }}
          path: research_assistant/reports/*.md

      - name: Send to Slack (optional)
        if: success()
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        run: |
          REPORT=$(cat research_assistant/reports/*.md | head -100)
          curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\": \"Weekly Competitor Report Generated\n\n\`\`\`${REPORT}\`\`\`\"}" \
            $SLACK_WEBHOOK
```

## Option 3: AWS Lambda + EventBridge

For serverless execution, you can deploy as a Lambda function triggered by EventBridge:

```python
# lambda_handler.py
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key'  # Use Secrets Manager in production

from research_assistant.graph.competitor_workflow import run_competitor_report

def handler(event, context):
    result = run_competitor_report()
    report = result.get('report', 'No report')

    # Send via SNS, SES, or store in S3
    # ...

    return {'statusCode': 200, 'body': report}
```

## Required Environment Variables

Make sure these are available in your cron/scheduled environment:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export SEARCH_API_KEY=...  # Optional but recommended for better results (Tavily)
```

## Email Integration (Optional)

To email reports automatically, add to `cli.py` or create a wrapper script:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_report_email(report: str, recipient: str = "ceo@webnode.com"):
    msg = MIMEMultipart()
    msg['Subject'] = f'Weekly Competitor Intelligence - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = 'reports@webnode.com'
    msg['To'] = recipient

    msg.attach(MIMEText(report, 'plain'))

    with smtplib.SMTP('smtp.webnode.com', 587) as server:
        server.starttls()
        server.login('reports@webnode.com', 'password')
        server.send_message(msg)
```

## Quick Test

Run manually to verify everything works:

```bash
# Single competitor
research-assistant competitors Wix

# Full weekly report
research-assistant weekly-report -d ./reports
```
