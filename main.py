import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QStackedWidget
from PyQt5.uic import loadUi
from PyQt5.uic.uiparser import WidgetStack
from dashboard import dashboardApp

class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.loginbutton.clicked.connect(self.loginfunction)
        #this line will give the ***** you normally see on passwords.
        self.password.setEchoMode(QtWidgets.QLineEdit.Password) 
        self.createaccbutton.clicked.connect(self.gotocreate)
    
    def loginfunction(self):
        username=self.username.text()
        password=self.password.text()
        print("Successfully logged in with username: ", username, "and password:", password)
        dash = dashboardApp()
        widget.addWidget(dash)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def gotocreate(self):
        createacc=CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex()+1)
     
class CreateAcc(QDialog):
    def __init__(self):
        super(CreateAcc, self).__init__()
        loadUi("createacc.ui", self)
        self.signupbutton.clicked.connect(self.createaccfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password) 
        login=Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def createaccfunction(self):
        username = self.username.text
        if self.password.text()==self.confirmpass.text():
            password=self.password.text()
            print("Successfully created account with username: ", username, "and password: ", password)
            login=Login()
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex()+1)
    
            
app=QApplication(sys.argv)
mainwindow=Login()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(480)
widget.setFixedHeight(620)
widget.show()
app.exec_()