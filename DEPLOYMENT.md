# Deployment checklist

- [ ] Create private Backblaze B2 bucket
- [ ] Create restricted B2 application key
- [ ] Put B2 credentials only in Render environment variables
- [ ] Create Render PostgreSQL
- [ ] Push repository to GitHub
- [ ] Configure Render build command: `pip install -r requirements.txt`
- [ ] Configure Render start command: `./scripts/start.sh`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set a strong admin password
- [ ] Deploy
- [ ] Verify `/health`
- [ ] Verify admin login
- [ ] Upload an image
- [ ] Confirm the object exists in the private B2 bucket
- [ ] Confirm the portfolio can display the image
- [ ] Confirm the signed URL expires
- [ ] Delete the image and confirm it is removed from B2
