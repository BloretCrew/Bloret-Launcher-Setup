import sys, os
# Ensure project root in path to import test helper
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PyQt5.QtWidgets import QApplication
from test_download_progress import DownloadDialogTester

app = QApplication.instance() or QApplication([])
t = DownloadDialogTester()
# do not show main tester window (to avoid a blocking UI in CI)
# t.show()

# call twice
t.show_downloading_dialog()
t.show_downloading_dialog()

from PyQt5.QtWidgets import QApplication
QApplication.processEvents()

dialogs = [w for w in QApplication.topLevelWidgets() if getattr(w, 'windowTitle', None) and callable(w.windowTitle) and w.windowTitle() == '正在下载']
print('找到正在下载对话框数量:', len(dialogs))
for d in dialogs:
    print('对话框对象:', d, 'size:', d.size())

# check progress bar
if hasattr(t, 'download_progress_bar'):
    pb = t.download_progress_bar
    print('progress objectName:', getattr(pb, 'objectName', lambda: '')())
    try:
        print('progress min height:', pb.minimumHeight())
        print('progress value:', pb.value())
    except Exception as e:
        print('读取进度属性失败', e)

# clean up
for d in dialogs:
    d.hide()

print('检查完成')
