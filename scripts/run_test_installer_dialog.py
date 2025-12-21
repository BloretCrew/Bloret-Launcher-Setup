import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_download_progress import test_installer_single_dialog

print('Running test_installer_single_dialog...')
try:
    test_installer_single_dialog()
    print('PASS')
except AssertionError as e:
    print('FAIL:', e)
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
