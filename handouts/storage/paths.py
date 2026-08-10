"""Filesystem paths and cross-cutting constants for the storage package.

The lowest layer of the package: no imports from any sibling module, so every
other module can depend on it without risk of an import cycle. Holds the on-disk
locations (DB file, upload/map folders) and the small shared enums/keys that
more than one domain module refers to (view types, the settings keys for POP and
the map, the POP TTL).
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.json')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
# The interactive map's background image lives in its own folder, kept apart
# from the handout library so a large campaign map never mixes in with the
# handouts and can be managed (and cleared) independently.
MAP_DIR = os.path.join(BASE_DIR, 'static', 'maps')

# Extension whitelist (images + PDF). Kept lowercase, no leading dot.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

# Map backgrounds are images only -- no PDF (the map viewer draws an <img>).
MAP_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# How a handout's files are presented to players. This is a handout-level
# property (distinct from each file's `reader`, which is image/pdf).
VIEW_TYPES = ('carousel', 'book')
DEFAULT_VIEW_TYPE = 'carousel'

# Key under `settings` holding the current POP broadcast (see pop_state).
POP_KEY = 'pop'

# Top-level DB key holding the interactive map's shared state (see
# get_map_state / update_map_state). Kept at the root, alongside `handouts`
# and `folders`, because the map is table-wide state rather than a per-handout
# or display setting.
#
# MAP_KEY is the LEGACY single-map key: databases written before multi-map
# support stored one map object here. It is read once by the migration in
# db._normalize (which converts it into maps[0]) and then removed, so nothing
# else should reference it. MAPS_KEY is the current home: a LIST of map
# objects, each with an id, a name, and the same state fields the single map
# used to carry.
MAP_KEY = 'map_state'
MAPS_KEY = 'maps'

# Cap on a map's display name so it stays a label, not prose. The name is shown
# in the master's map list and the player's map chooser.
MAP_NAME_MAX = 80

# How long a POP stays live, in seconds.
#
# A POP is a moment at the table ("look at this, now"), not a piece of state.
# Without an expiry the stored pointer stays true forever, so every player who
# joined, reloaded or woke their phone hours later got the modal again -- the
# handout is still popped, as far as the DB is concerned. Two minutes is long
# enough to cover a latecomer or a phone that was asleep during the reveal, and
# short enough that the POP is over before the scene is.
POP_TTL_SECONDS = 120
