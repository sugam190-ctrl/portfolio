# Portfolio — FastAPI + Private Backblaze B2

A server-rendered personal portfolio built with FastAPI, SQLAlchemy, Alembic and Jinja2.

## Production architecture

- **Application:** Render Web Service
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Image storage:** Private Backblaze B2
- **Image delivery:** temporary S3-compatible signed URLs
- **Migrations:** Alembic
- **Secrets:** Render environment variables

Images are not stored on the Render filesystem in production.

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure the database and, if testing B2 locally, the B2 credentials.

Run migrations:

```bash
alembic upgrade head
```

Start the application:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Backblaze B2

Create a **private** B2 bucket and a dedicated application key.

Required environment variables:

```env
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=
B2_ENDPOINT=
B2_REGION=
B2_SIGNED_URL_EXPIRES=3600
```

Never commit `.env` or real B2 credentials.

The browser receives only temporary signed URLs. B2 credentials remain server-side.

## Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
./scripts/start.sh
```

Add the production environment variables in Render. Do not put secrets in GitHub.

## Database

Production schema is managed by Alembic:

```bash
alembic upgrade head
```

The application does not call `Base.metadata.create_all()` at startup.

## Security notes

- Use a strong random `SECRET_KEY`.
- Do not use default admin credentials.
- Keep the B2 bucket private.
- Keep B2 application keys server-side.
- Limit image upload size.
- Validate image content, not just filename extensions.
- Use HTTPS in production.
