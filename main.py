#!/usr/bin/python
# Author: Johnny Xu
# Email: xu.johnny92@gmail.com

import dicom, sys, os, wx
import MySQLdb as mdb

class Main(wx.Frame):
    
    # Variables
    dbHostname  = ""
    dbUsername  = ""
    dbPassword  = ""
    dbSafePass  = ""
    dbDatabase  = ""
    dbTable     = ""
    sPath       = ""
    commitMode  = "QUICK"
    
    def __init__(self):
        wx.Frame.__init__(self, None, title="pydtk - MySQL Tool", size=(600,228))
        
        # Panels
        self.panel      = wx.Panel(self)
        
        # Sizers
        self.container  = wx.BoxSizer(wx.VERTICAL)
        self.vboxA      = wx.BoxSizer(wx.VERTICAL)
        self.hboxA1     = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxA2     = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxA3     = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxB      = wx.BoxSizer(wx.VERTICAL)
        self.hboxB1     = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxC      = wx.BoxSizer(wx.VERTICAL)
        self.hboxC1     = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxD      = wx.BoxSizer(wx.HORIZONTAL)
        
        # Line
        self.line1      = wx.StaticLine(self.panel, 0, size=(600,1))
        self.line2      = wx.StaticLine(self.panel, 0, size=(600,1))
        
        # Button
        self.sourceBtn  = wx.Button(self.panel, 0, "Select Source", size=(150,25))
        self.commitBtn  = wx.Button(self.panel, 0, "Commit", size=(150,25))
        
        # Radio
        self.depthRB    = wx.RadioButton(self.panel, 0, "Depth Mode", (10, 10), style=wx.RB_GROUP)
        self.quickRB    = wx.RadioButton(self.panel, 0, "Quick Mode", (10, 20))
        self.columnRB   = wx.RadioButton(self.panel, 0, "Generate Columns", (10, 30))
        
        # Static Text
        self.hostTxt    = wx.StaticText(self.panel, 0, "Hostname :")
        self.userTxt    = wx.StaticText(self.panel, 0, "Username :")
        self.passTxt    = wx.StaticText(self.panel, 0, "Password :")
        self.dbTxt      = wx.StaticText(self.panel, 0, "Database :")
        self.tblTxt     = wx.StaticText(self.panel, 0, "Tablename :")
        self.sourceTxt  = wx.StaticText(self.panel, 0, "Source Directory :")
        
        # Text Control
        self.hostTC     = wx.TextCtrl(self.panel, 0, Main.dbHostname, size=(500,22))
        self.userTC     = wx.TextCtrl(self.panel, 0, Main.dbUsername, size=(204,22))
        self.passTC     = wx.TextCtrl(self.panel, 0, Main.dbSafePass, size=(204,22))
        self.dataTC     = wx.TextCtrl(self.panel, 0, Main.dbDatabase, size=(204,22))
        self.tableTC    = wx.TextCtrl(self.panel, 0, Main.dbTable, size=(204,22))
        self.sourceTC   = wx.TextCtrl(self.panel, 0, Main.sPath, size=(460,22))
        
        # Layout
        self.container.Add(self.vboxA, 0, wx.ALL, 10)
        self.container.Add(self.line1)
        self.container.Add(self.vboxB, 0, wx.ALL, 10)
        self.container.Add(self.line2)
        self.container.Add(self.vboxC, 0, wx.ALL, 10)
        self.container.Add(self.hboxD)
        
            #A - Database Input
        self.vboxA.Add(self.hboxA1)
        self.hboxA1.Add(self.hostTxt)
        self.hboxA1.Add(self.hostTC, 0, wx.LEFT, 10)
        self.vboxA.Add(self.hboxA2, 0, wx.TOP, 5)
        self.hboxA2.Add(self.userTxt)
        self.hboxA2.Add(self.userTC, 0, wx.LEFT, 10)
        self.hboxA2.Add(self.passTxt, 0, wx.LEFT, 5)
        self.hboxA2.Add(self.passTC, 0, wx.LEFT, 19)
        self.vboxA.Add(self.hboxA3, 0, wx.TOP, 5)
        self.hboxA3.Add(self.dbTxt)
        self.hboxA3.Add(self.dataTC, 0, wx.LEFT, 15)
        self.hboxA3.Add(self.tblTxt, 0, wx.LEFT, 5)
        self.hboxA3.Add(self.tableTC, 0, wx.LEFT, 9)
            #B - Mode Selection
        self.vboxB.Add(self.hboxB1)
        self.hboxB1.Add(self.quickRB)
        self.hboxB1.Add(self.depthRB, 0, wx.LEFT, 15)
        self.hboxB1.Add(self.columnRB, 0, wx.LEFT, 15)
            # C - Source Selection
        self.vboxC.Add(self.hboxC1)
        self.hboxC1.Add(self.sourceTxt)
        self.hboxC1.Add(self.sourceTC, 0, wx.LEFT, 10)
            # D - Buttons
        self.hboxD.Add(self.sourceBtn, 0, wx.LEFT, 283)
        self.hboxD.Add(self.commitBtn, 0, wx.LEFT, 10)

        # Bindings
        self.sourceBtn.Bind(wx.EVT_BUTTON, self.setSource)
        self.commitBtn.Bind(wx.EVT_BUTTON, self.commit)
        self.hostTC.Bind(wx.EVT_TEXT, self.updateText)
        self.userTC.Bind(wx.EVT_TEXT, self.updateText)
        self.passTC.Bind(wx.EVT_KEY_UP, self.hidePassword)
        self.dataTC.Bind(wx.EVT_TEXT, self.updateText)
        self.tableTC.Bind(wx.EVT_TEXT, self.updateText)
        self.sourceTC.Bind(wx.EVT_TEXT, self.updateText)
        self.depthRB.Bind(wx.EVT_RADIOBUTTON, self.setMode)
        self.quickRB.Bind(wx.EVT_RADIOBUTTON, self.setMode)
        self.columnRB.Bind(wx.EVT_RADIOBUTTON, self.setMode)

        # Init Settings
        self.quickRB.SetValue(1)
        
        self.panel.SetSizer(self.container)
        self.Centre()
        
    # Handlers
    def setSource(self, event):
        self.filePrompt = wx.DirDialog(self, "Choose the Source Directory:", style=wx.DD_DEFAULT_STYLE)
        
        if self.filePrompt.ShowModal() == wx.ID_OK:
            Main.sPath = self.filePrompt.GetPath() + '/'
            self.sourceTC.SetValue(Main.sPath)
            
        self.filePrompt.Destroy()
        
    def updateText(self, event):
        Main.dbHostname  = self.hostTC.GetValue()
        Main.dbUsername  = self.userTC.GetValue()
        Main.dbDatabase  = self.dataTC.GetValue()
        Main.dbTable     = self.tableTC.GetValue()
        Main.sPath       = self.sourceTC.GetValue()
        
    def hidePassword(self, event):
        newPass = self.passTC.GetValue()
        
        if len(Main.dbPassword) == 0:
            Main.dbPassword = newPass
            Main.dbSafePass = newPass
        else:
            Main.dbPassword = Main.dbPassword + newPass[-1]
            Main.dbSafePass = "*" * len(Main.dbPassword)
            
        self.passTC.SetValue(Main.dbSafePass)
        self.passTC.SetInsertionPointEnd()
    
    def setMode(self, event):
        if self.depthRB.GetValue():
            Main.commitMode = "DEPTH"
        elif self.quickRB.GetValue():
            Main.commitMode = "QUICK"
        elif self.columnRB.GetValue():
            Main.commitMode = "COLUMN"
            
    def updateValues(self):
        self.hostTC.SetValue(Main.dbHostname)
        self.userTC.SetValue(Main.dbUsername)
        self.dataTC.SetValue(Main.dbDatabase)
        self.tableTC.SetValue(Main.dbTable)
        self.sourceTC.SetValue(Main.sPath)
    
    def commit(self, event):
        saveSession()

        if Main.commitMode == "DEPTH":
            self.commitDepth()
        elif Main.commitMode == "QUICK":
            self.commitQuick()
        elif Main.commitMode == "COLUMN":
            self.generateColumns()
        
    def commitQuick(self):
        conn    = mdb.connect(host=Main.dbHostname, user=Main.dbUsername, passwd=Main.dbPassword, db=Main.dbDatabase);
        curs    = conn.cursor()
        
        for dirname in os.walk(Main.sPath):
            filename    = "MR0001.DCM"
            fPath       = dirname[0] + "/" + filename
            try:
                if isDicom(fPath):
                    dataset = dicom.read_file(fPath)
                    timePoint = convertTimePoint(str(dataset.ClinicalTrialTimePointDescription))
                    patientKey = str(dataset.PatientsName) +"_"+ timePoint
                    insQry  = "INSERT INTO %s (Patients_Name) VALUES ('%s')" % (Main.dbTable, patientKey) 
                    try:
                        curs.execute(insQry)
                        conn.commit()
                
                        for data_element in dataset:
                            tagName = str(data_element.name).replace(" ","_")
                            tagName = tagName.replace("'", "")
                            value   = str(data_element.value)[:60]
                            updQry  = "UPDATE %s SET %s='%s' WHERE Patients_Name='%s';" %(Main.dbTable ,tagName, value, patientKey)
                            if tagName != "Patients_Name":
                                try:
                                    curs.execute(updQry)
                                    conn.commit()
                                except:
                                    conn.rollback()
                            else:
                                pass
                    except:
                        conn.rollback()  
            except:
                pass
        
        popupWindow("Quick Commit Completed.")
        conn.close()

    def commitDepth(self):
        conn    = mdb.connect(host=Main.dbHostname, user=Main.dbUsername, passwd=Main.dbPassword, db=Main.dbDatabase);
        curs    = conn.cursor()
    
        for dirname, dirs, files, in os.walk(Main.sPath):
            for filename in files:
                fPath = dirname + '/' + filename
                try:
                    if isDicom(fPath):
                        dataset     = dicom.read_file(fPath)
                        timePoint   = convertTimePoint(str(dataset.ClinicalTrialTimePointDescription))
                        fName       = filename[:-4]
                        patientKey  = str(dataset.PatientsName) + "_" + timePoint + "_" + fName
                        insertQry   = "INSERT INTO %s (Patients_Name) VALUES ('%s')" % (Main.dbTable, patientKey) 
            
                        try:
                            curs.execute(insertQry)
                            conn.commit()
                
                            for data_element in dataset:
                                tagName     = str(data_element.name).replace(" ","_")
                                tagName     = tagName.replace("'", "")
                                value       = str(data_element.value)[:60]
                                updateQry   = "UPDATE %s SET %s='%s' WHERE Patients_Name='%s';" %(Main.dbTable ,tagName, value, patientKey)
                                
                                if tagName != "Patients_Name":
                                    try:
                                        curs.execute(updateQry)
                                        conn.commit()
                                    except:
                                        conn.rollback()
                                else:
                                    pass
                        except:
                            conn.rollback()
                except:
                    pass
        
        popupWindow("Depth Commit Completed")
        conn.close()
        
    def generateColumns(self):
        conn    = mdb.connect(host=Main.dbHostname, user=Main.dbUsername, passwd=Main.dbPassword, db=Main.dbDatabase);
        curs    = conn.cursor()
        
        for dirname in os.walk(Main.sPath):
            fPath       = dirname[0] + "/" + "MR0001.DCM"
            try:
                if isDicom(fPath):
                    dataset = dicom.read_file(fPath)
                    for data_element in dataset:
                        tagName = data_element.name.replace(" ", "_")
                        tagName = tagName.replace("'", "")
                        try:
                            alterQry = "ALTER TABLE %s ADD COLUMN %s VARCHAR(60)" %(Main.dbTable, tagName)
                            curs.execute(alterQry)
                            conn.commit()
                        except:
                            conn.rollback()
            except:
                pass
     
        popupWindow("Generating Columns Completed.")
        conn.close()
    
        
def convertTimePoint(timepoint):
    if timepoint == "BASELINE":
        return "00"
    elif timepoint == "Month 12":
        return "12"
    elif timepoint == "Month 24":
        return "24"
        
def saveSession():
    session = open("session.txt", "wb")
    
    session.write("dbHostname = %s\n" %(Main.dbHostname))
    session.write("dbUsername = %s\n" %(Main.dbUsername))
    session.write("dbDatabase = %s\n" %(Main.dbDatabase))
    session.write("dbTable = %s\n" %(Main.dbTable))
    session.write("sPath = %s\n" %(Main.sPath))
    
    session.close()
    
def loadSession(parent):
    sessionPath = os.getcwd() + "/" + "session.txt"
    try:
        session     = open(sessionPath, "r")
    
        def process(line):
            string = line.split(" = ")[-1]
            string = string.replace(" ", "")
            string = string.strip()
            return string
    
        Main.dbHostname = process(session.readline())
        Main.updateValues(parent)
        Main.dbUsername = process(session.readline())
        Main.updateValues(parent)
        Main.dbDatabase = process(session.readline())
        Main.updateValues(parent)
        Main.dbTable    = process(session.readline())
        Main.updateValues(parent)
        Main.sPath      = process(session.readline())
        Main.updateValues(parent)
    except:
        pass
        

def isDicom(filename):
    try:
        return dicom.read_file(filename) 
    except dicom.filereader.InvalidDicomError:
        return False
        
def popupWindow(message, title="Notice!", parent=None):
    dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.ICON_INFORMATION)
    dlg.CenterOnParent()
    dlg.ShowModal()
    dlg.Destroy()
    
if __name__ == "__main__":
    
    app = wx.App(0)
    main = Main()
    main.Show()
    
    loadSession(main)
    
    app.MainLoop()
