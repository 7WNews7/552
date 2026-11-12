"""Importing this package registers every emoji module in this folder.

A module that fails to import is reported and skipped, so one broken file does not
block building the others."""
import importlib
import pkgutil
import sys
import traceback

FAILED = {}

for _m in sorted(m.name for m in pkgutil.iter_modules(__path__)):
    if _m.startswith('_'):
        continue
    try:
        importlib.import_module(__name__ + '.' + _m)
    except Exception:  # noqa: BLE001
        FAILED[_m] = traceback.format_exc()
        print('WARNING: emojis/%s.py failed to import and was skipped:\n%s' % (_m, FAILED[_m]), file=sys.stderr)
