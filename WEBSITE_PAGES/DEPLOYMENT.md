# Website Pages Deployment

## Pages Created

Two new pages have been added to the Django application:

1. **Privacy Policy** - `/privacy-policy/`
2. **Support** - `/support/`

## Files Created/Modified

### New Templates
- `templates/privacy-policy.html` - Privacy policy page with comprehensive privacy information
- `templates/support.html` - Support page with FAQ and contact information

### Modified Files
- `myproject/views.py` - Added `privacy_policy()` and `support()` view functions
- `myproject/urls.py` - Added URL routes for both pages
- `templates/base.html` - Added footer links to Privacy Policy and Support pages

## Deployment

The pages will be automatically deployed when you push to the `main` branch via GitHub Actions.

The deployment workflow (`.github/workflows/deploy.yml`) will:
1. Build a Docker image
2. Push to AWS ECR
3. Deploy to AWS App Runner service `thespacedata-service`

## URLs

After deployment, the pages will be available at:

- **Privacy Policy**: `https://<your-app-runner-url>/privacy-policy/`
- **Support**: `https://<your-app-runner-url>/support/`

To get your App Runner service URL, run:
```bash
aws apprunner list-services --region us-east-1 --query "ServiceSummaryList[?ServiceName=='thespacedata-service'].ServiceUrl" --output text
```

Or check the AWS Console:
1. Go to AWS App Runner console
2. Find the service named `thespacedata-service`
3. Copy the Service URL

## Testing Locally

Before deploying, you can test locally:

```bash
cd /Users/rasmusmencke/Projects/thespacedata/myproject
python manage.py runserver
```

Then visit:
- http://localhost:8000/privacy-policy/
- http://localhost:8000/support/

## Next Steps

1. **Commit and push** the changes to trigger deployment:
   ```bash
   git add .
   git commit -m "Add privacy policy and support pages"
   git push origin main
   ```

2. **Wait for deployment** - GitHub Actions will automatically deploy (usually takes 5-10 minutes)

3. **Get the URLs** - Once deployed, get the App Runner service URL and append the paths:
   - `https://<service-url>/privacy-policy/`
   - `https://<service-url>/support/`

## Footer Links

Both pages are now linked in the site footer, so they're accessible from any page on the site.
