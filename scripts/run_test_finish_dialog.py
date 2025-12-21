import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_download_progress import test_finish_dialog_buttons

print('Running test_finish_dialog_buttons...')
try:
    test_finish_dialog_buttons()
    print('PASS')
except AssertionError as e:
    print('FAIL:', e)
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
