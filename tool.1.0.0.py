import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import threading
import PyQt5
from socket import *


class MyWindow(QtGui.QDialog):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.ui = Ui_MyWindow()
        self.ui.setupUi(self)

        # go on setting up your handlers like:
        # self.ui.okButton.clicked.connect(function_name)
        # etc...

def main():
    app = QtGui.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
