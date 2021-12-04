#  Reduce amount of processing time to check out tool to less 2 minutes  --- Ronell
#       user needs to be indexed to have fast processing time, toolID is also going to be indexed.
#  HOW TO DO:search for user they show up in list, query the database to see if item is in stock, \
#       #if in stock AND user is in good standing, allow them to check out the tool then increment empInventory by 1 decrement WareHouseInventory by 1
#
# 	Provide each employee with periodic statement of their inventory and actions  
#       HOW TO DO:#### INSTALL WIN10TOAST FOR PERIOD MESSAGES --- Ronell
#
#  Reduce amount of processing time of employee termination to less 2 minutes
#  HOW TO DO:user needs to be indexed to have fast processing time
#  #tool by tool decrement empInventory by 1 and then and increment warehouseInventory by 1 --- Jacob
#
#  Automated notification system upon equipment arrival/check-in
#       HOW TO DO:#HOW TO DO:On click function for return/withdraw a list box will display empInventory clicking an item in the list will return that item to WareHouseINventory
#       #This click could also be something like --> takes you to tool page, displays information(checkout date/time) and offers you the option to return it. --- Jacob
#
#  Less than 30 seconds to locate employee to whom the returned equipment belongs 
#       HOW TO DO:#Index date to improve searching time in combination with toolID to see who has checked out X tool. --- Randel
#       #Can try import random and use rand to assign tools random ID as they are withdrawn. 
#
#  Staff has ability to obtain and create immediate access to records and reports ---Randel
#      HOW TO DO:#Staff can query server for empInventory
#      #Can search by reportID or by name
#
#  System will validate that employee has proper skill classification for check out 
#      HOW TO DO:#when checking out tool look up wareHouseInventory and Compare SkillID with ToolID for proper check --- Brittany
#
# 	Classify employees based on good or bad standing according to equipment losses --- Brittany
#      HOW TO DO:# Sum statement in SQL to check how many tools and employee has.
#      #Sum of tools > 5 tools = bad standing     
#   
#   LOGIN PAGE --- Mack
#       HOW TO DO: Reference youtube videos https://www.youtube.com/watch?v=RHu3mQodroM for example.
#       #This will need to authenticate users and establish if they are admins or not as admin page will have access to additional tools employees do not have.
#   Working GUI + Functions --- Mack
#   #@note check terminate code.

import mysql.connector
from mysql.connector import Error

import sys
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QListWidget, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi


# imports for report generation --- Randel
import pandas as pd
import datetime
from plyer import notification

class dashboardApp(QDialog):

    # DB settings note: move to config file
    host='localhost'
    database='gb_manufacturing2'
    user='root'
    password ='password'

    # DB vars
    connection = None
    selectedUserId = None
    
    #
    # db functions

    def dbConnect(self, host=host, database=database, user=user, password=password):
        connection = None
        try:
            connection = mysql.connector.connect(host=host,
                                    database=database,
                                    user=user,
                                    password =password)
        except Error as e:
            print("Error while connecting to MySQL", e)

        return connection

    def dbClose(self, connection):
        try:
            if connection != None and connection.is_connected():
                connection.close()
        except Error as e:
            print("Error while closing MySQL connection", e)

    #
    # db data functions

    def dbInstall(self):
        # Connect and create db
        try:
            self.connection = self.dbConnect(database=None)

            if self.connection is None:
                print("Failed to connect to db")
                return

            if self.connection.is_connected():
                cursor = self.connection.cursor()
                query = """DROP DATABASE IF EXISTS gb_manufacturing2;"""
                cursor.execute(query)
                query = """CREATE DATABASE gb_manufacturing2;""" 
                cursor.execute(query)
                
        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.commit()
                cursor.close()
                self.dbClose(self.connection)
                self.connection = None

        # Connect again but to the new db
        try:
            self.connection = self.dbConnect()

            if self.connection is None:
                print("Failed to connect to db")
                return

            if self.connection.is_connected():
                cursor = self.connection.cursor()

                # Employee Table
                query = """ CREATE TABLE employee(
                                empID           VARCHAR(3),
                                empLastName     VARCHAR(15) NOT NULL,
                                empFirstName    VARCHAR(15) NOT NULL,
                                SkillID         VARCHAR(15) DEFAULT '',
                                numTools        INT NOT NULL DEFAULT 0,
                                isStaff         INT NOT NULL DEFAULT 0,
                                PRIMARY KEY (empID)
                            );
                        """
                cursor.execute(query)

                # Employee Data
                query = """ INSERT INTO 
                                employee (empID, empLastName, empFirstName, SkillID, numTools, isStaff) 
                            VALUES
                                ('E1', 'Najorka', 'Mack', 'M1', 0, 1),
                                ('E2', 'Cousar', 'Ronell', 'C1', 0, 1),
                                ('E3', 'Rundio', 'Jacob', 'M1', 0, 0),
                                ('E4', 'Hall', 'Randel', 'C1', 0, 1),
                                ('E5', 'Baity', 'Brittany', 'C1', 0, 0);
                        """
                cursor.execute(query)

                # WareHouseInventory Table
                query = """ CREATE TABLE WareHouseInventory(
                                SkillID     VARCHAR (15),
                                toolID      VARCHAR (4),
                                toolName    VARCHAR (20),
                                inStock     INT NOT NULL,
                                primary key (toolID)
                            );
                        """
                cursor.execute(query)

                # WareHouseInventory Data
                query = """ INSERT INTO 
                                WareHouseInventory (SkillID, toolID, toolName, inStock)
                            VALUES
                                ("M1", "T1", "Impact Wrech", 100),
                                ("All", "T2", "Skrewdriver", 100),
                                ("All", "T3", "Shakeweight", 10),
                                ("C1", "T4", "Table Saw", 50);
                        """
                cursor.execute(query)

                #When generating reports there needs to be createReport() function. This will display the reportID, EmpID, toolID, reportType type, time
                query = """ create table reports(
                            reportID INT NOT NULL AUTO_INCREMENT,
                            empID varchar(3),
                            reportType varchar(10),
                            toolID varchar(4),
                            reportTime datetime DEFAULT CURRENT_TIMESTAMP,
                            primary key (reportID)
                            );"""
                cursor.execute(query)

        except Error as e:
            print("Error while on_click_install", e)
        finally:
            if  self.connection and self.connection.is_connected():
                self.connection.commit()
                cursor.close()

    def dbEmployeeSearch(self, empFirstName):
        records = None

        if self.connection is None or not self.connection.is_connected():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """ SELECT 
                            * 
                        FROM 
                            employee 
                        WHERE 
                            empFirstName = %s
                    """
            cursor.execute(query, (empFirstName, ))
            records = cursor.fetchall()
            cursor.close()
        except Error as e:
            print("Error while on_click_search", e)


        return records

    def dbEmployeeAll(self):
        records = None

        if self.connection is None or not self.connection.is_connected():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """ SELECT 
                            * 
                        FROM 
                            employee;
                    """
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
        except Error as e:
            print("Error while on_click_search", e)
       
            

        return records

    def dbWareHouseInventoryWithdraw(self, empID, toolID):
        if self.connection is None or not self.connection.is_connected():
            return

        try:
           # Check if still in stock
           # check if already withdrawn
            cursor = self.connection.cursor()
            query = """ UPDATE
                            employee
                        SET
                            numTools = numTools + 1
                        WHERE
                            empID = %s;
                    """
            cursor.execute(query, (empID,))

            query = """ UPDATE
                            WareHouseInventory
                        SET
                            inStock = inStock - 1
                        WHERE
                            toolID = %s;
                    """
            cursor.execute(query, (toolID,))
            self.connection.commit()
            cursor.close()
            self.dbReportCreate(empID, toolID, "withdraw")

        except Error as e:
            print("Error while dbWareHouseInventoryWithdraw", e)
         

    def dbWareHouseInventoryReturn(self, empID, toolID):
        if self.connection is None or not self.connection.is_connected():
            return
        self.dbReportCreate(empID, toolID, "return")
        try:
            # Check if still checked out
            cursor = self.connection.cursor()
            query = """ UPDATE
                            employee
                        SET
                            numTools = numTools - 1
                        WHERE
                            empID = %s;
                    """
            cursor.execute(query, (empID,))

            query = """ UPDATE
                            WareHouseInventory
                        SET
                            inStock = inStock + 1
                        WHERE
                            toolID = %s;
                    """
            cursor.execute(query, (toolID,))

            self.dbReportCreate(empID, toolID, "return")

        except Error as e:
            print("Error while dbWareHouseInventoryReturn", e)
        finally:
            self.connection.commit()
            cursor.close()

    def dbReportCreate(self, empID, toolID, reportType):
        if self.connection is None or not self.connection.is_connected():
            return

        try:
            cursor = self.connection.cursor()
            
            query = """ INSERT INTO 
                            reports (empID, toolID, reportType) 
                        VALUES
                            (%s, %s, %s);
                    """
            cursor.execute(query, (empID, toolID, reportType,))

        except Error as e:
            print("Error while dbReportCreate", e)
        finally:
            self.connection.commit()
            cursor.close()
    
    def dbReportGenerateToExcelFile(self): #Randels function revised
        if self.connection is None or not self.connection.is_connected():
            return
        try:
            reportsQuery = """  SELECT 
                                    * 
                                FROM 
                                    reports 
                                WHERE 
                                    reportTime 
                                BETWEEN 
                                    curdate() 
                                AND 
                                    DATE_ADD(curdate(), INTERVAL 1 DAY);"""
            
            employeeQuery = """ SELECT 
                                    * 
                                FROM 
                                    employee 
                                WHERE 
                                    numTools >= 3"""

            # Read data from SQL with pandas dataframe and export to csv file for report table
            df = pd.read_sql_query(reportsQuery,self.connection)
            df.to_csv("reports/Inventory_report"+datetime.datetime.now().strftime('%b-%d-%Y')+".csv", index=False)

            #Read data from SQL with pandas dataframe and export to csv file for report table
            df = pd.read_sql_query(employeeQuery,self.connection)
            df.to_csv("reports/Employee_Tool_report"+datetime.datetime.now().strftime('%b-%d-%Y')+".csv", index=False)

            #notify user of successful export
            notification.notify(title="Export Status", 
                                message=f"Data has been successfully exported to Excel.", timeout=10)

        except Error as e:
            print("Error generating report", e)

    def __init__(self):
        super().__init__()
        self.initUI()

        self.connection = self.dbConnect()
        if self.connection == None:
            print('Failed to connect to {} Database, try installing the db or check mysql settings'.format(self.host))
            # Enable Install button
    #@note: Need to add exit button to app.


    def initUI(self):
        loadUi("dashboard.ui", self)      

        self.installButton.clicked.connect(self.on_click_install)
        self.employeeNamesButton.clicked.connect(self.on_click_allEmployees)
        self.withdrawButton.clicked.connect(self.on_click_withdraw)
        self.returnButton.clicked.connect(self.on_click_return)
        self.reportsButton.clicked.connect(self.on_click_reports)
        self.searchButton.clicked.connect(self.on_click_search)
        self.terminateButton.clicked.connect(self.on_click_terminate)
        self.searchResultsList.clicked.connect(self.on_click_searchResult)
        self.logoutButton.clicked.connect(self.on_click_logout)
    
        
    @pyqtSlot()
    def on_click_allEmployees(self):
        emps = self.dbEmployeeAll()
        if emps is not None:
            for emp in emps:
                print(emp["empFirstName"], emp["empLastName"])
        else:
            print(f'No users found...')
            
    def on_click_terminate(self):
        print("Terminate Stub")

    def on_click_reports(self):
        self.dbReportGenerateToExcelFile()
        
    # @note: move to list vs a button
    def on_click_withdraw(self):
        toolID = self.searchBox.text()
        if self.selectedUserId == None:
            print(f"No user selected to withdraw tool {toolID}")
            return
        print(f"Withdrawing tool {toolID}")
        self.dbWareHouseInventoryWithdraw(self.selectedUserId, toolID)

    # @note: move to list vs a button
    def on_click_return(self):
        toolID = self.searchBox.text()
        if self.selectedUserId == None:
            print(f"No user selected to return tool {toolID}")
            return
        print(f"Returning tool {toolID}")
        self.dbWareHouseInventoryReturn(self.selectedUserId, toolID)

    # Search Emp Button Callback
    def on_click_search(self):
        empFirstName = self.searchBox.text()
        print(f'Searching for users {empFirstName}')
        emps = self.dbEmployeeSearch(empFirstName)
        if emps is not None:
            for emp in emps:
                self.searchResultsList.addItem("{} {}".format(emp['empFirstName'], emp['empLastName']))
        else:
            print(f'User {empFirstName} not found')

    # Search List Selected User Callback
    def on_click_searchResult(self, item):
        emp = self.searchResultsList.currentItem()
        print(f'Selected users {emp}')
        # @note convert to emp ID
        self.selectedUserId = "E1"
        #self.selectedUserId = emp

    def on_click_install(self):
        print('Installing {} Database'.format(self.host))
        self.dbInstall()
    
    def on_click_logout(self):
        self.dbClose(self.connection)
        self.connection = None
#if __name__ == '__main__':
#    app = QApplication(sys.argv)
#    ex = App()
#    sys.exit(app.exec_())

