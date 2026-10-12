# Old Millstone Forge

Flask rebuild of https://oldmillstoneforge.org (same pages and content).

## Run
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    flask --app app run --debug        # http://127.0.0.1:5000

## Production
    gunicorn app:app

## Editing content
Hours, events, gallery photos and newsletters live at the top of `app.py`.
- **Events/hours:** edit `HOURS` and `EVENTS` (the "Journey Through the Past - October 7th and 8th" entry was copied as-is from the old site and may be out of date).
- **Newsletters:** put PDFs in `static/chronicles/` (used automatically); otherwise links fall back to the old site.
- **Images:** by default they load from oldmillstoneforge.org. To self-host, copy the old site's `images/` folder into `static/images/` and run with `LOCAL_IMAGES=1`.
- Old URLs such as `/aboutus.html` redirect to the new routes.
