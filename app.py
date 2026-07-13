import json
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.json')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')

# Extension whitelist (images + PDF). Kept lowercase, no leading dot.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
ALLOWED_READERS = {'image', 'pdf'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Normalize legacy single-file records into the files: [...] shape
    # so templates and routes can rely on one consistent structure.
    for h in data.get('handouts', []):
        if 'files' not in h:
            h['files'] = [{
                'filename': h.get('filename', ''),
                'reader': h.get('reader', 'image'),
            }]
    return data


def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def group_by_session(handouts):
    """Group handouts by session number for the player view.

    Returns a list of dicts ordered by session number (unsorted last), each:
      {'number': int|None, 'title': str, 'handouts': [handout, ...]}
    Items within a session are ordered chronologically. The session title is
    taken from the earliest handout in that session that defines one.
    """
    buckets = {}
    for h in handouts:
        num = h.get('session_number')
        buckets.setdefault(num, []).append(h)

    groups = []
    for num, items in buckets.items():
        items.sort(key=lambda h: h.get('created_at', ''))
        title = next((h.get('session_title', '').strip()
                      for h in items if h.get('session_title', '').strip()), '')
        groups.append({'number': num, 'title': title, 'handouts': items})

    # Numbered sessions ascending; unsorted (None) goes last.
    groups.sort(key=lambda g: (g['number'] is None, g['number'] or 0))
    return groups


# Players
@app.route('/')
def home():
    db = load_db()
    visible = [h for h in db['handouts'] if h.get('visible')]
    sessions = group_by_session(visible)
    return render_template('player_hub.html', sessions=sessions)


# Master
@app.route('/dm-panel')
def dm_panel():
    db = load_db()
    categories = sorted({h.get('category', '').strip()
                         for h in db['handouts'] if h.get('category', '').strip()})
    return render_template('master_dashboard.html',
                           handouts=db['handouts'],
                           categories=categories)


@app.route('/upload', methods=['POST'])
def upload_handout():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    alt_text = request.form.get('alt_text', '').strip()
    category = request.form.get('category', '').strip()
    session_title = request.form.get('session_title', '').strip()
    files = request.files.getlist('files')

    # Session number is optional; blank or invalid -> None (Unsorted).
    session_raw = request.form.get('session_number', '').strip()
    try:
        session_number = int(session_raw) if session_raw else None
    except ValueError:
        session_number = None

    # Basic validation
    if not title:
        abort(400, 'A title is required.')
    files = [f for f in files if f and f.filename]
    if not files:
        abort(400, 'No file selected.')
    for f in files:
        if not allowed_file(f.filename):
            abort(400, f'File type not allowed: {f.filename}')

    handout_id = uuid.uuid4().hex
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save every file with a unique name; derive its reader from the extension.
    stored_files = []
    for idx, f in enumerate(files):
        safe_name = secure_filename(f.filename)
        ext = safe_name.rsplit('.', 1)[1].lower()
        stored_filename = f'{handout_id}_{idx}.{ext}'
        f.save(os.path.join(UPLOAD_DIR, stored_filename))
        reader = 'pdf' if ext == 'pdf' else 'image'
        stored_files.append({'filename': stored_filename, 'reader': reader})

    db = load_db()
    db['handouts'].append({
        'id': handout_id,
        'title': title,
        'description': description,
        'alt_text': alt_text,
        'files': stored_files,
        'visible': False,
        'category': category,
        'session_number': session_number,
        'session_title': session_title,
        'created_at': datetime.now(timezone.utc).isoformat(),
    })
    save_db(db)

    return redirect(url_for('dm_panel'))


@app.route('/toggle/<handout_id>', methods=['POST'])
def toggle_visibility(handout_id):
    db = load_db()
    for handout in db['handouts']:
        if handout['id'] == handout_id:
            handout['visible'] = not handout.get('visible', False)
            save_db(db)
            return redirect(url_for('dm_panel'))
    abort(404, 'Handout not found.')


@app.route('/delete/<handout_id>', methods=['POST'])
def delete_handout(handout_id):
    db = load_db()
    for i, handout in enumerate(db['handouts']):
        if handout['id'] == handout_id:
            # Remove every stored file for this handout, best-effort.
            for entry in handout.get('files', []):
                try:
                    os.remove(os.path.join(UPLOAD_DIR, entry['filename']))
                except OSError:
                    pass
            db['handouts'].pop(i)
            save_db(db)
            return redirect(url_for('dm_panel'))
    abort(404, 'Handout not found.')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)