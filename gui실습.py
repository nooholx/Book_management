import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("stackEx.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QWidget, form_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)
        self.btn_login.clicked.connect(self.btn_loginFunction)
        self.btn_join.clicked.connect(self.btn_joinFunction)
        self.btn_cancel.clicked.connect(self.btn_cancelFunction)

    def btn_loginFunction(self):
        print("btn_2 Clicked")

    def btn_joinFunction(self):
        self.stackedWidget.setCurrentIndex(1)

    def btn_cancelFunction(self):
        self.stackedWidget.setCurrentIndex(0)


    # btn_1이 눌리면 작동할 함수
    def button1Function(self, event):
        print("btn_1 Clicked")
        id = self.let_id.text()
        pw = self.let_pw.text()
        print(id,pw)
        reply = QMessageBox.question(self, 'Message', '가입하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            print(id, pw)
        else:
            event.ignore()

    # btn_2가 눌리면 작동할 함수
    def button2Function(self):
        print("btn_2 Clicked")
        self.let_id.setText("")
        self.let_pw.setText("")
        self.let_name.setText("")

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()