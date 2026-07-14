"""One-off setup: fetch the self-hosted vendor libraries the app needs.

Currently this downloads StPageFlip (page-flip 2.0.7, MIT licence), the
library that powers the realistic page-curl in the Book viewer. Run this once
after cloning; the file lands in static/vendor/ and is then served locally, so
the app keeps working offline.

    python fetch_vendor.py

Safe to re-run: it overwrites the existing copy.
"""

import io
import os
import sys
import tarfile
import urllib.request

VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'static', 'vendor')

# npm tarball for page-flip; we only extract the browser bundle from it.
PAGEFLIP_VERSION = '2.0.7'
PAGEFLIP_TARBALL = (
    f'https://registry.npmjs.org/page-flip/-/page-flip-{PAGEFLIP_VERSION}.tgz')
PAGEFLIP_MEMBER = 'package/dist/js/page-flip.browser.js'
PAGEFLIP_OUT = os.path.join(VENDOR_DIR, 'page-flip.browser.js')


def fetch_pageflip():
    os.makedirs(VENDOR_DIR, exist_ok=True)
    print(f'Downloading page-flip {PAGEFLIP_VERSION}...')
    with urllib.request.urlopen(PAGEFLIP_TARBALL) as resp:
        data = resp.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        member = tar.extractfile(PAGEFLIP_MEMBER)
        if member is None:
            print(f'ERROR: {PAGEFLIP_MEMBER} not found in tarball',
                  file=sys.stderr)
            sys.exit(1)
        with open(PAGEFLIP_OUT, 'wb') as out:
            out.write(member.read())
    print(f'Wrote {PAGEFLIP_OUT}')


if __name__ == '__main__':
    fetch_pageflip()
    print('Done. Vendor libraries are in static/vendor/.')
