"""Folders: master-defined {id, name} groups with multi-membership on handouts.
"""

import uuid


def all_folders(db):
    """Folders sorted by name (case-insensitive). Each is {id, name}."""
    return sorted(db.get('folders', []),
                  key=lambda fo: fo.get('name', '').lower())


def find_folder(db, folder_id):
    return next((fo for fo in db.get('folders', [])
                 if fo['id'] == folder_id), None)


def create_folder(db, name):
    """Create a folder if the name is non-empty and not a duplicate.

    Returns the folder dict (existing or new); returns None for empty names.
    Name matching is case-insensitive to avoid near-duplicate folders.
    """
    name = (name or '').strip()
    if not name:
        return None
    existing = next((fo for fo in db.get('folders', [])
                     if fo.get('name', '').lower() == name.lower()), None)
    if existing:
        return existing
    folder = {'id': uuid.uuid4().hex, 'name': name}
    db.setdefault('folders', []).append(folder)
    return folder


def rename_folder(db, folder_id, name):
    """Rename a folder in place. No-op if the folder is gone or name empty."""
    name = (name or '').strip()
    folder = find_folder(db, folder_id)
    if folder and name:
        folder['name'] = name
    return folder


def delete_folder(db, folder_id):
    """Remove a folder and detach it from every handout (handouts are kept)."""
    db['folders'] = [fo for fo in db.get('folders', [])
                     if fo['id'] != folder_id]
    for h in db['handouts']:
        if folder_id in h.get('folders', []):
            h['folders'] = [fid for fid in h['folders'] if fid != folder_id]


def valid_folder_ids(db, folder_ids):
    """Keep only ids that correspond to folders that actually exist."""
    known = {fo['id'] for fo in db.get('folders', [])}
    return [fid for fid in folder_ids if fid in known]
