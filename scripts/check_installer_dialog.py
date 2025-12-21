import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PyQt5.QtWidgets import QApplication
from installer import BloretInstaller

app = QApplication.instance() or QApplication([])
inst = BloretInstaller()
# don't show main window
inst.show_downloading_dialog()
inst.show_downloading_dialog()
from PyQt5.QtWidgets import QApplication
QApplication.processEvents()

# Find dialogs titled '正在下载'
dialogs = [w for w in QApplication.topLevelWidgets() if getattr(w, 'windowTitle', None) and callable(w.windowTitle) and w.windowTitle() == '正在下载']
print('找到正在下载对话框数量:', len(dialogs))
for d in dialogs:
    print('对话框对象:', d, 'visible:', d.isVisible(), 'size:', d.size())

# Also print installer.downloading_dialog
print('inst.downloading_dialog:', inst.downloading_dialog)

print('检查完成')
