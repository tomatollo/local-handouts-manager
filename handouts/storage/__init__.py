"""Data + file storage for handouts.

Everything that touches the JSON database or the uploads folder lives here, so
the route modules stay thin and free of persistence details. This package
replaces the former single storage.py; its public surface is UNCHANGED, so the
rest of the app keeps calling `storage.load_db()`, `storage.save_db(...)`,
`storage.get_map_state(...)`, etc. exactly as before -- only the internals are
split by responsibility:

    paths.py       on-disk paths + shared constants (view types, POP/map keys)
    util.py        small pure helpers (view-type, allowed_file, ids, timestamps)
    formats.py     source-format labelling for the "Group by Format" view
    materials.py   object3d sheet material presets (roughness/metalness/depth)
    records.py     handout lookup, player_payload, secret reveal, tag/category
                   /password/session parsing
    folders.py     master-defined folders (id + name, multi-membership)
    settings.py    global theme get/set
    welcome.py     player-hub welcome header (titles/subtitles/random)
    pop.py         POP broadcasts (fire, clear, liveness/TTL)
    map_state.py   interactive maps: a list of maps, each with confirmed +
                   pending (draft) state, POIs, focus broadcasts; plus the
                   map collection CRUD and the legacy single-map migration
    files.py       upload/file operations (save/remove handout + map files)
    db.py          load/save/normalize, the write lock, and the opt-in
                   per-request cache

The DB layer stays free of any Flask import: the per-request cache is injected
by the web layer through set_request_cache_hooks (wired to flask.g in app.py),
so storage keeps working unchanged from the CLI, where the hooks are never set.

The public API below is re-exported flat so `from handouts import storage` and
every `storage.xxx()` call keeps working without touching a single consumer
(app.py, routes_master, routes_player, transfer, pdfs, organize, mapmask, auth,
security). `_normalize` is re-exported too: transfer.py calls it on an imported
DB before saving, so it is part of the surface despite the leading underscore.

See docs/STORAGE.md for the module map and the map staging model.
"""

# Paths + shared constants
from .paths import (
    BASE_DIR,
    DB_PATH,
    UPLOAD_DIR,
    MAP_DIR,
    ALLOWED_EXTENSIONS,
    MAP_EXTENSIONS,
    VIEW_TYPES,
    DEFAULT_VIEW_TYPE,
    POP_KEY,
    MAP_KEY,
    MAPS_KEY,
    MAP_NAME_MAX,
    POP_TTL_SECONDS,
)

# Small pure helpers
from .util import (
    clean_view_type,
    allowed_file,
    reader_for,
    new_handout_id,
    now_iso,
    now_stamp,
)

# Source-format labelling
from .formats import (
    FORMAT_UNKNOWN,
    _PDF_PAGE_MARKER,
    ext_of,
    normalize_format,
    format_of_handout,
    source_format_from_uploads,
    all_formats,
)

# Record helpers + parsing/aggregation over the handout list
from .records import (
    find,
    player_payload,
    reveal_secret,
    all_categories,
    all_tags,
    parse_tags,
    parse_passwords,
    parse_session_number,
)

# Folders
from .folders import (
    all_folders,
    non_empty_folders,
    find_folder,
    create_folder,
    rename_folder,
    delete_folder,
    valid_folder_ids,
)

# Global settings (theme)
from .settings import (
    get_theme,
    set_theme,
)

# Object3d sheet material presets
from .materials import (
    SHEET_MATERIAL_PRESETS,
    DEFAULT_SHEET_MATERIAL_PRESET,
    default_sheet_material,
    clean_sheet_material,
    sheet_material_from_form,
)

# Welcome header
from .welcome import (
    WELCOME_TITLE_MAX,
    WELCOME_SUBTITLE_MAX,
    WELCOME_MAX_LINES,
    get_welcome_config,
    set_welcome,
    pick_welcome,
)

# POP broadcasts
from .pop import (
    pop_state,
    pop_age_seconds,
    pop_is_live,
    set_pop,
    clear_pop,
)

# Interactive maps
from .map_state import (
    GRID_MIN,
    GRID_MAX,
    POI_MAX,
    POI_LABEL_MAX,
    POI_ICON_MAX,
    SCALE_MIN,
    SCALE_MAX,
    POI_DEFAULT_COLOR,
    clean_map_name,
    all_maps,
    find_map,
    get_map,
    create_map,
    rename_map,
    delete_map,
    update_map_state,
    set_map_image,
    confirm_map_state,
    discard_map_state,
    set_map_focus,
)

# Upload/file operations
from .files import (
    save_files,
    remove_files,
    save_back_cover,
    save_back_texture,
    allowed_map_file,
    save_map_image,
    remove_map_image,
)

# Database load / save / normalize + request cache
from .db import (
    set_request_cache_hooks,
    load_db,
    save_db,
    is_current_schema,
    _normalize,
)

__all__ = [
    # paths
    'BASE_DIR', 'DB_PATH', 'UPLOAD_DIR', 'MAP_DIR', 'ALLOWED_EXTENSIONS',
    'MAP_EXTENSIONS', 'VIEW_TYPES', 'DEFAULT_VIEW_TYPE', 'POP_KEY', 'MAP_KEY',
    'MAPS_KEY', 'MAP_NAME_MAX', 'POP_TTL_SECONDS',
    # util
    'clean_view_type', 'allowed_file', 'reader_for', 'new_handout_id',
    'now_iso', 'now_stamp',
    # formats
    'FORMAT_UNKNOWN', '_PDF_PAGE_MARKER', 'ext_of', 'normalize_format',
    'format_of_handout', 'source_format_from_uploads', 'all_formats',
    # records
    'find', 'player_payload', 'reveal_secret', 'all_categories', 'all_tags',
    'parse_tags', 'parse_passwords', 'parse_session_number',
    # folders
    'all_folders', 'non_empty_folders', 'find_folder', 'create_folder',
    'rename_folder', 'delete_folder', 'valid_folder_ids',
    # settings
    'get_theme', 'set_theme',
    # materials
    'SHEET_MATERIAL_PRESETS', 'DEFAULT_SHEET_MATERIAL_PRESET',
    'default_sheet_material', 'clean_sheet_material', 'sheet_material_from_form',
    # welcome
    'WELCOME_TITLE_MAX', 'WELCOME_SUBTITLE_MAX', 'WELCOME_MAX_LINES',
    'get_welcome_config', 'set_welcome', 'pick_welcome',
    # pop
    'pop_state', 'pop_age_seconds', 'pop_is_live', 'set_pop', 'clear_pop',
    # map
    'GRID_MIN', 'GRID_MAX', 'POI_MAX', 'POI_LABEL_MAX', 'POI_ICON_MAX',
    'SCALE_MIN', 'SCALE_MAX', 'POI_DEFAULT_COLOR', 'clean_map_name',
    'all_maps', 'find_map', 'get_map', 'create_map', 'rename_map',
    'delete_map', 'update_map_state', 'set_map_image', 'confirm_map_state',
    'discard_map_state', 'set_map_focus',
    # files
    'save_files', 'remove_files', 'save_back_cover', 'save_back_texture',
    'allowed_map_file', 'save_map_image', 'remove_map_image',
    # db
    'set_request_cache_hooks', 'load_db', 'save_db', 'is_current_schema',
    '_normalize',
]
