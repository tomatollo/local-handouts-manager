"""Command-line export / import, as an alternative to the Master UI.

Usage:
    python transfer_cli.py export [OUTPUT.zip]
    python transfer_cli.py import BUNDLE.zip [--replace-conflicts]

export  writes the whole library (database + uploads) to a .zip
        (default: handouts-export.zip).

import  merges a bundle into the current library. New handouts are added.
        Conflicts (same id, different content) are kept LOCAL by default;
        pass --replace-conflicts to take the imported version for all of them.
        For per-handout choices, use the Master UI instead.
"""

import sys

from handouts import transfer


def do_export(args):
    out = args[0] if args else 'handouts-export.zip'
    data = transfer.export_bytes()
    with open(out, 'wb') as f:
        f.write(data)
    print(f'Exported library to {out} ({len(data)} bytes).')


def do_import(args):
    if not args:
        print('Usage: python transfer_cli.py import BUNDLE.zip '
              '[--replace-conflicts]', file=sys.stderr)
        sys.exit(2)
    path = args[0]
    replace = '--replace-conflicts' in args[1:]

    with open(path, 'rb') as f:
        zip_bytes = f.read()

    report = transfer.analyze(zip_bytes)
    print(f'{len(report["new"])} new, {len(report["identical"])} identical, '
          f'{len(report["conflicts"])} conflict(s).')

    resolutions = {}
    if report['conflicts']:
        choice = 'imported' if replace else 'local'
        for cf in report['conflicts']:
            resolutions[cf['id']] = choice
        print(f'Resolving all conflicts as: '
              f'{"imported" if replace else "local"}.')

    summary = transfer.apply_import(zip_bytes, resolutions)
    print(f'Done. Added {summary["added"]}, replaced {summary["replaced"]}, '
          f'kept {summary["kept_local"]} local.')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('export', 'import'):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == 'export':
        do_export(sys.argv[2:])
    else:
        do_import(sys.argv[2:])


if __name__ == '__main__':
    main()
