"""One-off setup: fetch the self-hosted vendor libraries the app needs.

Run this once after cloning; the files land in static/vendor/ and are then
served locally, so the app keeps working offline (no CDN at the table).

    python fetch_vendor.py

It downloads:

  * StPageFlip (page-flip 2.0.7, MIT) -> the realistic page-curl used by the
    Book viewer. Lands as static/vendor/page-flip.browser.js.

  * Three.js (r160, MIT) -> the WebGL engine, GLTF model loader and
    OrbitControls used by the 3D "object inspection" viewer (object3d). The
    build and its addons are laid out under static/vendor/three/ so an import
    map in the reader can resolve bare 'three' / 'three/addons/...' specifiers:

        static/vendor/three/three.module.min.js
        static/vendor/three/addons/loaders/GLTFLoader.js
        static/vendor/three/addons/controls/OrbitControls.js
        static/vendor/three/addons/utils/BufferGeometryUtils.js

    The addon folder layout mirrors three's own examples/jsm/ tree, because
    GLTFLoader.js imports '../utils/BufferGeometryUtils.js' by relative path.

Safe to re-run: it overwrites the existing copies.
"""

import io
import os
import sys
import tarfile
import urllib.request

VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'static', 'vendor')
THREE_DIR = os.path.join(VENDOR_DIR, 'three')

# --------------------------------------------------------------------------
# StPageFlip (Book viewer)
# --------------------------------------------------------------------------

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


# --------------------------------------------------------------------------
# Three.js (object3d viewer)
# --------------------------------------------------------------------------

THREE_VERSION = '0.160.1'
THREE_TARBALL = (
    f'https://registry.npmjs.org/three/-/three-{THREE_VERSION}.tgz')

# tarball member -> destination path under static/vendor/three/. The addon
# destinations keep three's examples/jsm/ sub-tree (loaders/, controls/,
# utils/) because GLTFLoader imports BufferGeometryUtils by relative path.
THREE_MEMBERS = {
    'package/build/three.module.min.js':
        os.path.join(THREE_DIR, 'three.module.min.js'),
    'package/examples/jsm/loaders/GLTFLoader.js':
        os.path.join(THREE_DIR, 'addons', 'loaders', 'GLTFLoader.js'),
    'package/examples/jsm/controls/OrbitControls.js':
        os.path.join(THREE_DIR, 'addons', 'controls', 'OrbitControls.js'),
    'package/examples/jsm/utils/BufferGeometryUtils.js':
        os.path.join(THREE_DIR, 'addons', 'utils', 'BufferGeometryUtils.js'),
}


def fetch_three():
    print(f'Downloading three {THREE_VERSION}...')
    with urllib.request.urlopen(THREE_TARBALL) as resp:
        data = resp.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        for member_name, dest in THREE_MEMBERS.items():
            member = tar.extractfile(member_name)
            if member is None:
                print(f'ERROR: {member_name} not found in tarball',
                      file=sys.stderr)
                sys.exit(1)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as out:
                out.write(member.read())
            print(f'Wrote {dest}')


if __name__ == '__main__':
    fetch_pageflip()
    fetch_three()
    print('Done. Vendor libraries are in static/vendor/.')
