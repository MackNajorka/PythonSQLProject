#   Reduce amount of processing time to check out tool to less 2 minutes  --- Ronell #Done by Mack except for standing check
#   #missing good standing check. If employee inventory > 3 hide button to check out.
#
#   Provide each employee with periodic statement of their inventory and actions --- Ronell #Randel DONE
#
#   Reduce amount of processing time of employee termination to less 2 minutes
#   HOW TO DO:user needs to be indexed to have fast processing time
#   #tool by tool decrement empInventory by 1 and then and increment warehouseInventory by 1 --- Jacob
#
#   Automated notification system upon equipment arrival/check-in --- Jacob #Done by Mack
#
#   Less than 30 seconds to locate employee to whom the returned equipment belongs 
#   HOW TO DO:#Index date to improve searching time in combination with toolID to see who has checked out X tool. --- Randel
#   #Can try import random and use rand to assign tools random ID as they are withdrawn. 
#
#   Staff has ability to obtain and create immediate access to records and reports ---Randel DONE
#
#   System will validate that employee has proper skill classification for check out ---Brittany ---Done by Mack
#
#   Classify employees based on good or bad standing according to equipment count --- Brittany DONE by Randel and Mack
#   HOW TO DO:# Count statement in SQL to check how many tools an employee has.
#   #Count of tools > 3 tools = bad standing     
# 
#   LOGIN PAGE --- Mack DONE
#   Working GUI + Functions --- Mack DONE


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
    selectedtoolID = None
    
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
                query = """ CREATE TABLE reports(
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
            #@note 
                #Check if still in stock
                #check if already withdrawn
                #check if toolID exists. Currently can withdraw anything.
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


    def dbWareHouseAvailableTools(self, empID):
        if self.connection is None or not self.connection.is_connected():
            return
        records = None
        try:
            cursor = self.connection.cursor(dictionary = True)
            query = """ SELECT
                            w.toolID, w.toolName 
                        FROM
                            WareHouseInventory w
                        LEFT JOIN
                            employee e
                        ON
                            e.skillID = w.skillID OR w.skillID = 'All'
                        WHERE 
                            w.inStock > 0 AND e.empID = %s;"""
            
            cursor.execute(query, (empID,))
            records = cursor.fetchall()
            cursor.close()         
              
        except Error as e:
            print("Error while dbWareHouseAvailableTools", e)
        return records

    def dbWareHouseCheckedOutTools(self, empID, skipempty=True):
        if self.connection is None or not self.connection.is_connected():
            return
        records = None
        try:
            cursor = self.connection.cursor(dictionary = True)
            query = """ SELECT 
                            toolID, reportType, COUNT(reportID) AS reportCount
                        FROM 
                            reports 
                        WHERE 
                            empID = %s 
                        GROUP BY 
                            toolID, reportType
                        ORDER BY 
                            toolID, reportType;"""
            
            cursor.execute(query, (empID,))
            records = cursor.fetchall()
            cursor.close()         
            
            tools={}
            for record in records:
                if record['toolID'] not in tools:
                    tools[record['toolID']] = 0
                if record['reportType'] == 'withdraw':
                    tools[record['toolID']] += record['reportCount']
                else:
                    tools[record['toolID']] -= record['reportCount']
            records = []
            if tools != None:
                for key, value in tools.items():
                    if int (value) > 0 or not skipempty:
                        records.append({
                            'toolID': key,
                            'count': value, 
                        })
            
        except Error as e:
            print("Error while dbWareHouseCheckedOutTools", e)
        return records
    
    def dbWareHouseInventoryReturn(self, empID, toolID):
        if self.connection is None or not self.connection.is_connected():
            return
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
            
    def dbDeleteEmployee(self, empFirstName): 
        try:  
            if self.connection is None or not self.connection.is_connected():
                return None
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM employee WHERE empfirstname = %s"
            cursor.execute(query, (empFirstName, ))
            records = cursor.fetchall()
            self.connection.commit()
            cursor.close()
            print(records)
    
            cursor = self.connection.cursor(dictionary=True)
            query = "DELETE FROM employee WHERE empFirstName = %s"
            cursor.execute(query, (empFirstName, ))
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Error while deleting employee", e)
    
    def dbReportGenerateToExcelFile(self): #Randels function revised
        if self.connection is None or not self.connection.is_connected():
            return
        try:
            reportsQuery ="""  SELECT 
                                    * 
                                FROM 
                                    reports 
                                WHERE 
                                    reportTime 
                                BETWEEN 
                                    curdate() 
                                AND 
                                    DATE_ADD(curdate(), INTERVAL 1 DAY)
                         ;"""
                                    
            # Read data from SQL with pandas dataframe and export to csv file for report table
            df = pd.read_sql_query(reportsQuery,self.connection)
            df.to_csv(f"Inventory_report{datetime.datetime.now().strftime('%b-%d-%Y')}.csv", index=False)

            employeeQuery = """ SELECT 
                                    * 
                                FROM 
                                    employee 
                                WHERE 
                                    numTools >= 3
                            ;"""
            #Read data from SQL with pandas dataframe and export to csv file for report table
            df = pd.read_sql_query(employeeQuery,self.connection)
            df.to_csv(f"reports/Employee_Bad_Standing_report{datetime.datetime.now().strftime('%b-%d-%Y')}.csv", index=False)

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
        self.groupBoxEmpProfile.hide()
        self.withdrawButton.hide()
        self.returnButton.hide()
        self.listWidgetAvailableTools.clicked.connect(self.on_click_selectAvailableTool)
        self.listWidgetCheckedOut.clicked.connect(self.on_click_selectCheckedOutTool)
        
        
    @pyqtSlot()
    def on_click_allEmployees(self):
        self.searchResultsList.clear()
        emps = self.dbEmployeeAll()
        if emps is not None:
            for emp in emps:
                self.searchResultsList.addItem("{} {} {}".format(emp['empID'], emp['empFirstName'], emp['empLastName']))
                notification.notify(title="Employee Tool Status", 
                                message=f"Employee " + emp ['empFirstName'] + " " + emp ['empLastName']
                                + " has " + str(emp['numTools']) + " tools in inventory.", timeout=15)
        else:
            print(f'No users found...')
            
    def on_click_terminate(self):
        empFirstName = self.searchBox.text()
        self.dbDeleteEmployee(empFirstName)
        print("Employee Terminated")

    def on_click_reports(self):
        self.dbReportGenerateToExcelFile()
        
    def on_click_withdraw(self):
        toolID = self.selectedtoolID
        if self.selectedtoolID == None:
            print(f"No user selected to withdraw tool {toolID}")
            return
        print(f"Withdrawing tool {toolID}")
        self.dbWareHouseInventoryWithdraw(self.selectedUserId, toolID)
        self.profileRefresh()

    def on_click_return(self):
        toolID = self.selectedtoolID
        if self.selectedtoolID == None:
            print(f"No user selected to return tool {toolID}")
            return
        print(f"Returning tool {toolID}")
        self.dbWareHouseInventoryReturn(self.selectedUserId, toolID)
        self.profileRefresh()
        tools = self.dbWareHouseCheckedOutTools(self.selectedUserId, skipempty= False)
        for tool in tools:
            if tool['toolID'] == toolID:
                if int(tool['count']) == 0:
                    self.selectedtoolID = None
                    self.returnButton.hide()
                break
        
    # Search Emp Button Callback
    def on_click_search(self):
        self.searchResultsList.clear()
        empFirstName = self.searchBox.text()
        print(f'Searching for users {empFirstName}')
        emps = self.dbEmployeeSearch(empFirstName)
        if emps is not None:
            for emp in emps:
                self.searchResultsList.addItem("{} {} {}".format(emp['empID'], emp['empFirstName'], emp['empLastName']))
        else:
            print(f'User {empFirstName} not found')

    # Search List Selected User Callback
    def on_click_searchResult(self):
        emp = self.searchResultsList.currentItem()
        empString = emp.text()
        print(f'Selected users {empString}')
        self.groupBoxEmpProfile.show()
        empID, empFName, empLName = empString.split()
        self.selectedUserId = empID
        self.groupBoxEmpProfile.setTitle(f'Profile {empFName} {empLName}')
        self.profileRefresh()
                
    def on_click_selectAvailableTool(self):
        tool = self.listWidgetAvailableTools.currentItem()
        toolString = tool.text()
        print(f'Selected tool to check out {toolString}')
        self.selectedtoolID = toolString[:2]
        self.withdrawButton.show()
        self.returnButton.hide()

        
    def on_click_selectCheckedOutTool(self):
        tool = self.listWidgetCheckedOut.currentItem()
        toolString = tool.text()
        print(f'Selected tool to check in {toolString}')
        self.selectedtoolID = toolString[:2]
        self.returnButton.show()
        self.withdrawButton.hide()
        

    def on_click_install(self):
        print('Installing {} Database'.format(self.host))
        self.dbInstall()
    
    def on_click_logout(self):
        self.dbClose(self.connection)
        self.connection = None
        
    def profileRefresh(self):
        tools = self.dbWareHouseAvailableTools(self.selectedUserId)    
        self.listWidgetAvailableTools.clear()
        if tools is not None:
            for tool in tools:
                self.listWidgetAvailableTools.addItem("{} {}".format(tool['toolID'], tool['toolName']))
        tools = self.dbWareHouseCheckedOutTools(self.selectedUserId)        
        self.listWidgetCheckedOut.clear()
        if tools is not None:
            for tool in tools:
                self.listWidgetCheckedOut.addItem("{} count {}".format(tool['toolID'], tool['count']))
