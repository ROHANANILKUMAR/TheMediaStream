
import tkinter as tk
from tkinter import messagebox
import Client as cl
from tkinter import ttk
import os
import shutil

client=None
serveraddr=''
clientroot=''
serverport=''
class Login:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Login")
        self.root.geometry('510x240+500+500')
        self.root.config(bg="#827b96")
        self.root.resizable(False,False)

        self.IPVar=tk.StringVar()
        self.PortVar=tk.StringVar()
        self.PassVar=tk.StringVar()
        self.ClRootVar=tk.StringVar()
        
        
        lbl=tk.Label(self.root,text="Login to Media Stream",anchor='center',width=60,pady=10,font=('Helvica',10),fg='black',bg="#827b96")
        lbl.grid(row=1,columnspan=3)
        iplbl=tk.Label(self.root,text="Server IP:",width=11,fg="black",anchor='w',pady=10,bg="#827b96")
        portlbl=tk.Label(self.root,text="Server Port:",width=11,anchor='w',pady=10,bg="#827b96")
        passlbl=tk.Label(self.root,text="Password:",width=11,anchor='w',pady=10,bg="#827b96")
        clrootlbl=tk.Label(self.root,text="Client Root:",width=11,anchor='w',pady=10,bg="#827b96")
        iplbl.grid(row=2)
        portlbl.grid(row=3)
        passlbl.grid(row=4)
        clrootlbl.grid(row=5)
        
        ip=tk.Entry(self.root,width=60,textvariable=self.IPVar)
        port=tk.Entry(self.root,width=60,textvariable=self.PortVar)
        passwd=tk.Entry(self.root,width=60,textvariable=self.PassVar)
        clroot=tk.Entry(self.root,width=60,textvariable=self.ClRootVar)
        ip.grid(row=2,column=2,columnspan=2)
        port.grid(row=3,column=2,columnspan=2)
        passwd.grid(row=4,column=2,columnspan=2)
        clroot.grid(row=5,column=2,columnspan=2)
        
        btn=tk.Button(self.root,text="Login",command=self.Log,width=20)
        btn.grid(row=6,columnspan=3,pady=10)
        self.root.mainloop()

        
        
    def Log(self):
        global serveraddr
        global serverport
        global client
        global clientroot
        try:
            client=cl.Client(self.IPVar.get(),int(self.PortVar.get()))
            if(client.authorize(self.PassVar.get())):
                serveraddr=self.IPVar.get()
                serverport=self.PortVar.get()
                messagebox.showinfo("Success","Successfully Logged in!")
                serveraddr=self.IPVar.get()
                serverport=self.PortVar.get()
                clientroot=self.ClRootVar.get()
                self.root.destroy()
                MainWindow()
            else:
                self.PassVar.set("")
                messagebox.showerror("Error","Wrong Password")
        except:
            messagebox.showerror("Error","Could not connect to "+self.IPVar.get()+"... Is the IP and port valid?")
        
            
class MainWindow:
    def __init__(self):
        self.root=tk.Tk()
        self.root.resizable(False, False)
        self.root.geometry("1150x770")
        self.root.title("MainWindow")
        self.root.config(bg="#827b96")
        self.CurServerPath=client.serverroot
        self.CurClientPath=clientroot
        self.CurServerDirs=[]
        self.CurServerFiles=[]
        self.CurClientDirs=[]
        client.SetErrorEventHandler(self.ErrorEventHandler)
        self.LoadWidgets()
        self.root.mainloop()
        
 
    def ErrorEventHandler(self,Title,Message):
        messagebox.showerror(Title,Message)
    
        
    def LoadMainFrames(self):
        lbl=tk.Label(self.root,text="Connected to Server "+serveraddr+" on Port "+serverport,bg="#827b96",font=("Helvica",16))
        lbl.grid(row=1,columnspan=2)
        
        self.ServerFrame=tk.Frame(self.root,bg='#ababab',height=500,width=450)
        self.ServerFrame.grid(row=2,column=1,padx=5,pady=5)
        self.ClientFrame=tk.Frame(self.root,bg='#ababab',height=500,width=450)
        self.ClientFrame.grid(row=2,column=2,padx=5,pady=5)

        self.ProgressFrame=tk.Frame(self.root,height=10,width=1129)
        self.ProgressFrame.grid(row=3,columnspan=3)
        
        self.ProgressList=tk.Listbox(self.ProgressFrame,height=5,width=185)
        self.ProgressList.pack(fill='x',side='left')

        self.ProgressScroll=tk.Scrollbar(self.ProgressFrame,orient='vertical')
        self.ProgressScroll.config(command=self.ProgressList.yview)
        self.ProgressScroll.pack(side='right',fill='y')
        self.ProgressList.config(yscrollcommand=self.ProgressScroll.set)
    
    def AddProgress(self,data):
        self.ProgressList.insert(tk.END,data)
        
    def LoadSubFrames(self):
        self.CNameLbl=tk.Label(self.ClientFrame,text="Client Directory",font=('Helvica',10),bg='#5e5e5e',fg='white')
        self.CNameLbl.pack(fill='x')
        self.SNameLbl=tk.Label(self.ServerFrame,text="Server Directory",font=('Helvica',10),bg='#5e5e5e',fg='white')
        self.SNameLbl.pack(fill='x')
        
        self.SDirFrame=tk.Frame(self.ServerFrame)
        self.SDirFrame.pack()
        self.CDirFrame=tk.Frame(self.ClientFrame)
        self.CDirFrame.pack()
        
        self.SDir=tk.StringVar()
        self.CDir=tk.StringVar()
        self.ServerDir=tk.Label(self.SDirFrame,textvariable=self.SDir,bg='#a3a3a3',anchor='w',width=67)#74)
        self.ClientDir=tk.Label(self.CDirFrame,textvariable=self.CDir,bg='#a3a3a3',anchor='w',width=67)
        self.ServerDir.grid(row=1,column=1)
        self.ClientDir.grid(row=1,column=1)
        
        self.CDir.set(self.CurClientPath)
        self.SDir.set(self.CurServerPath)

        self.SBackDir=tk.Button(self.SDirFrame,text="back",command=self.BackDirServer)
        self.CBackDir=tk.Button(self.CDirFrame,text="back",command=self.BackDirClient)
        self.SBackDir.grid(row=1,column=3)
        self.CBackDir.grid(row=1,column=3)

        self.SRefreshDir=tk.Button(self.SDirFrame,text="Refresh",command=self.LoadServerBrowser)
        self.CRefreshDir=tk.Button(self.CDirFrame,text="Refresh",command=self.LoadClientBrowser)
        self.SRefreshDir.grid(row=1,column=2)
        self.CRefreshDir.grid(row=1,column=2)
        
        self.SBrowseFrame=tk.Frame(self.ServerFrame,height=500)
        self.CBrowseFrame=tk.Frame(self.ClientFrame,height=500)
        self.SBrowseFrame.pack(fill='x')
        self.CBrowseFrame.pack(fill='x')
        
    def LoadBrowseFrames(self):
        self.SBrowse=tk.Listbox(self.SBrowseFrame,width=90,height=30)
        self.SBrowse.pack(side='left')
        self.CBrowse=tk.Listbox(self.CBrowseFrame,width=90,height=30)
        self.CBrowse.pack(side='left')
        
        self.CBrowseScroll=tk.Scrollbar(self.CBrowseFrame,orient='vertical')
        self.CBrowseScroll.config(command=self.CBrowse.yview)
        self.CBrowseScroll.pack(side='right',fill='y')
        self.SBrowseScroll=tk.Scrollbar(self.SBrowseFrame,orient='vertical')
        self.SBrowseScroll.config(command=self.SBrowse.yview)
        self.SBrowseScroll.pack(side='right',fill='y')

        self.SBrowse.config(yscrollcommand=self.SBrowseScroll.set)
        self.CBrowse.config(yscrollcommand=self.CBrowseScroll.set)

        self.SBrowse.bind('<<ListboxSelect>>',self.SBrowseSelectionChanged)
        self.CBrowse.bind('<<ListboxSelect>>',self.CBrowseSelectionChanged)
        self.SBrowse.bind('<Double-Button>',self.SBrowseDClick)
        self.CBrowse.bind('<Double-Button>',self.CBrowseDClick)

        self.CControl=tk.Frame(self.ClientFrame,bg='#bdbdbd',height=60)
        self.SControl=tk.Frame(self.ServerFrame,bg='#bdbdbd',height=60)
        self.CControl.pack(side='bottom',fill='x',pady=5)
        self.SControl.pack(side='bottom',fill='x',pady=5)
        
    def LoadControlFrames(self):
        self.SFolderFrame=tk.LabelFrame(self.SControl,text="Folder Options")
        self.CFolderFrame=tk.LabelFrame(self.CControl,text="Folder Options")
        self.SFolderFrame.pack(side='left',padx=5,pady=5)
        self.CFolderFrame.pack(side='left',padx=5,pady=5)

        self.SFileFrame=tk.LabelFrame(self.SControl,text="File Options")
        self.CFileFrame=tk.LabelFrame(self.CControl,text="File Options")
        self.SFileFrame.pack(side='right',padx=5,pady=5)
        self.CFileFrame.pack(side='right',padx=5,pady=5)
        
        self.S2CFile=tk.Button(self.SFileFrame,text="Get File From Server",command=self.S2CFileEvent)
        self.C2SFile=tk.Button(self.CFileFrame,text="Send File To Server",command=self.C2SFileEvent)
        self.S2CFile.grid(row=1,column=1,padx=5,columnspan=2)
        self.C2SFile.grid(row=1,column=1,padx=5,columnspan=2)

        self.S2CFolder=tk.Button(self.SFolderFrame,text="Get Folder From Server",command=self.S2CFolderEvent)
        self.C2SFolder=tk.Button(self.CFolderFrame,text="Send Folder To Server",command=self.C2SFolderEvent)
        self.S2CFolder.grid(row=1,column=1,padx=5,columnspan=2)
        self.C2SFolder.grid(row=1,column=1,padx=5,columnspan=2)

        self.SFileDelete=tk.Button(self.SFileFrame,text="Delete File",command=self.SFileDeleteEvent)
        self.CFileDelete=tk.Button(self.CFileFrame,text="Delete File",command=self.CFileDeleteEvent)
        self.SFileDelete.grid(row=1,column=3,padx=5)
        self.CFileDelete.grid(row=1,column=3,padx=5)

        self.SFolderDelete=tk.Button(self.SFolderFrame,text="Delete Folder",command=self.SFolderDeleteEvent)
        self.CFolderDelete=tk.Button(self.CFolderFrame,text="Delete Folder",command=self.CFolderDeleteEvent)
        self.SFolderDelete.grid(row=1,column=3,padx=5)
        self.CFolderDelete.grid(row=1,column=3,padx=5)

        self.SFileRenameLbl=tk.Label(self.SFileFrame,text="Rename:")
        self.SFileRenameLbl.grid(row=2,column=1,pady=5)
        self.CFileRenameLbl=tk.Label(self.CFileFrame,text="Rename:")
        self.CFileRenameLbl.grid(row=2,column=1,pady=5)

        self.SFolderRenameLbl=tk.Label(self.SFolderFrame,text="Rename:")
        self.SFolderRenameLbl.grid(row=2,column=1,pady=5)
        self.CFolderRenameLbl=tk.Label(self.CFolderFrame,text="Rename:")
        self.CFolderRenameLbl.grid(row=2,column=1,pady=5)

        self.SFileRename=tk.StringVar()
        self.CFileRename=tk.StringVar()
        self.SFolderRename=tk.StringVar()
        self.CFolderRename=tk.StringVar()
        
        self.SFileRenameEntry=tk.Entry(self.SFileFrame,textvariable=self.SFileRename)
        self.SFileRenameEntry.grid(row=2,column=2)
        self.CFileRenameEntry=tk.Entry(self.CFileFrame,textvariable=self.CFileRename)
        self.CFileRenameEntry.grid(row=2,column=2)

        self.SFolderRenameEntry=tk.Entry(self.SFolderFrame,textvariable=self.SFolderRename)
        self.SFolderRenameEntry.grid(row=2,column=2)
        self.CFolderRenameEntry=tk.Entry(self.CFolderFrame,textvariable=self.CFolderRename)
        self.CFolderRenameEntry.grid(row=2,column=2)

        self.SFileRenameBtn=tk.Button(self.SFileFrame,text="Apply",command=self.SFileRenameEvent)
        self.SFileRenameBtn.grid(row=2,column=3)
        self.CFileRenameBtn=tk.Button(self.CFileFrame,text="Apply",command=self.CFileRenameEvent)
        self.CFileRenameBtn.grid(row=2,column=3)

        self.SFolderRenameBtn=tk.Button(self.SFolderFrame,text="Apply",command=self.SFolderRenameEvent)
        self.SFolderRenameBtn.grid(row=2,column=3)
        self.CFolderRenameBtn=tk.Button(self.CFolderFrame,text="Apply",command=self.CFolderRenameEvent)
        self.CFolderRenameBtn.grid(row=2,column=3)

    
    def LoadWidgets(self):
        self.LoadMainFrames()
        self.LoadSubFrames()
        self.LoadBrowseFrames()
        self.LoadControlFrames()

        self.LoadClientBrowser()
        self.LoadServerBrowser()
        self.SFolderFrameLockDown()
        self.SFileFrameLockDown()
        self.CFolderFrameLockDown()
        self.CFileFrameLockDown()
        
    def SFileRenameEvent(self):
        oldName=self.FullCurSelectedPathServer()
        ext=oldName.split(".")[-1]
        newName=self.CurServerPath+"\\"+self.SFileRename.get()+'.'+ext
        client.Rename(oldName,newName)
        self.SFileRename.set("")
        self.LoadServerBrowser()
        self.AddProgress(f"rename {oldName} to {newName} on Server")
        messagebox.showinfo("Success","The File name was changed successfully")
        
    def CFileRenameEvent(self):
        oldName=self.FullCurSelectedPathClient()
        ext=oldName.split(".")[-1]
        newName=self.CurClientPath+"\\"+self.CFileRename.get()+"."+ext
        os.rename(oldName,newName)
        self.CFileRename.set("")
        self.LoadClientBrowser()
        self.AddProgress(f"rename {oldName} to {newName} On Client")
        messagebox.showinfo("Success","The File name was changed successfully")
        
        
    def SFolderRenameEvent(self):
        oldName=self.FullCurSelectedPathServer()
        newName=self.CurServerPath+"\\"+self.SFolderRename.get()
        client.Rename(oldName,newName)
        self.SFolderRename.set("")
        self.LoadServerBrowser()
        self.AddProgress(f"rename {oldName} to {newName} on Server")
        messagebox.showinfo("Success","The Directory name was changed successfully")
        
    def CFolderRenameEvent(self):
        oldName=self.FullCurSelectedPathClient()
        newName=self.CurClientPath+"\\"+self.CFolderRename.get()
        os.rename(oldName,newName)
        self.LoadClientBrowser()
        self.AddProgress(f"rename {oldName} to {newName} on Client")
        messagebox.showinfo("Success","The Directory name was changed successfully")
        


    def S2CFileEvent(self):
        #self.ProgressData.set("Fetching file "+self.SBrowse.get(self.SBrowse.curselection()))
        client.getFile(self.CurClientPath,self.SBrowse.get(self.SBrowse.curselection()),self.FullCurSelectedPathServer(),client.getFileSize(self.FullCurSelectedPathServer()))
        self.AddProgress(f"Fetch {self.SBrowse.get(self.SBrowse.curselection())}")
        self.LoadClientBrowser()
        
    def C2SFileEvent(self):
        client.SendFile(self.FullCurSelectedPathClient(),self.CurServerPath)
        self.AddProgress(f"Send {self.FullCurSelectedPathClient()}")
        self.LoadServerBrowser()
        
        
        
    def S2CFolderEvent(self):
        client.getFolder(self.FullCurSelectedPathServer(),self.CurClientPath)
        self.AddProgress(f"Fetch {self.FullCurSelectedPathServer()}")
        self.LoadClientBrowser()
    def C2SFolderEvent(self):
        #print(f"SendFolder({self.FullCurSelectedPathClient()},{self.CurServerPath})")
        client.SendFolder(self.FullCurSelectedPathClient(),self.CurServerPath)
        self.AddProgress(f"Send {self.FullCurSelectedPathClient()}")
        self.LoadServerBrowser()
        
    def SFileDeleteEvent(self):
        client.deleteFile(self.FullCurSelectedPathServer())
        self.AddProgress(f"Delete {self.FullCurSelectedPathServer()} on Server" )
        self.LoadServerBrowser()
        
    def CFileDeleteEvent(self):
        os.remove(self.FullCurSelectedPathClient())
        self.AddProgress(f"Delete {self.FullCurSelectedPathClient()} on Client" )
        self.LoadClientBrowser()
        
    def SFolderDeleteEvent(self):
        client.deleteFolder(self.FullCurSelectedPathServer())
        self.AddProgress(f"Delete {self.FullCurSelectedPathServer()} on Server" )
        self.LoadServerBrowser()
        
    def CFolderDeleteEvent(self):
        shutil.rmtree(self.FullCurSelectedPathClient())
        self.AddProgress(f"Delete {self.FullCurSelectedPathClient()} on Client" )
        self.LoadClientBrowser()

    def SetServerPath(self,path):
        self.SDir.set(path)
        self.CurServerPath=path
        self.LoadServerBrowser()
        
    def SetClientPath(self,path):
        self.CDir.set(path)
        self.CurClientPath=path
        self.LoadClientBrowser()
        
    def SBrowseDClick(self,evt):
        lb=evt.widget
        if(lb.get(lb.curselection()) in self.CurServerDirs):
            self.SetServerPath(self.FullCurSelectedPathServer())
    def CBrowseDClick(self,evt):
        lb=evt.widget
        if(os.path.isdir(self.FullCurSelectedPathClient())):
            self.SetClientPath(self.FullCurSelectedPathClient())
            

    def FullCurSelectedPathServer(self):
        if(self.CurServerPath[:-1]=='\\'):
            return self.CurServerPath+self.SBrowse.get(self.SBrowse.curselection())
        return self.CurServerPath+"\\"+self.SBrowse.get(self.SBrowse.curselection())
    def FullCurSelectedPathClient(self):
        if(self.CurClientPath[:-1]=='\\'):
            return self.CurClientPath+self.CBrowse.get(self.CBrowse.curselection())
        return self.CurClientPath+"\\"+self.CBrowse.get(self.CBrowse.curselection())
    
    def SBrowseSelectionChanged(self,evt):
        lb=evt.widget
        try:
            data=lb.get(lb.curselection())
            if(data in self.CurServerDirs):
                self.SFileFrameLockDown()
                self.SFolderFrameRevive()
            else:
                self.SFolderFrameLockDown()
                self.SFileFrameRevive()
        except:
            pass
    def CBrowseSelectionChanged(self,evt):
        lb=evt.widget
        try:
            data=lb.get(lb.curselection())
            if(os.path.isfile(self.CurClientPath+"\\"+data)):
                self.CFileFrameRevive()
                self.CFolderFrameLockDown()
            else:
                self.CFileFrameLockDown()
                self.CFolderFrameRevive()
        except:
            pass
        
    def SFileFrameLockDown(self):
        self.S2CFile.config(state='disabled')
        self.SFileDelete.config(state='disabled')
        self.SFileRenameBtn.config(state='disabled')
        self.SFileRenameEntry.config(state='disabled')
        self.SFileRenameLbl.config(state='disabled')
    def SFolderFrameLockDown(self):
        self.S2CFolder.config(state='disabled')
        self.SFolderDelete.config(state='disabled')
        self.SFolderRenameBtn.config(state='disabled')
        self.SFolderRenameEntry.config(state='disabled')
        self.SFolderRenameLbl.config(state='disabled')
    def SFileFrameRevive(self):
        self.S2CFile.config(state='normal')
        self.SFileDelete.config(state='normal')
        self.SFileRenameBtn.config(state='normal')
        self.SFileRenameEntry.config(state='normal')
        self.SFileRenameLbl.config(state='normal')
    def SFolderFrameRevive(self):
        self.S2CFolder.config(state='normal')
        self.SFolderDelete.config(state='normal')
        self.SFolderRenameBtn.config(state='normal')
        self.SFolderRenameEntry.config(state='normal')
        self.SFolderRenameLbl.config(state='normal')
    def CFileFrameLockDown(self):
        self.C2SFile.config(state='disabled')
        self.CFileDelete.config(state='disabled')
        self.CFileRenameBtn.config(state='disabled')
        self.CFileRenameEntry.config(state='disabled')
        self.CFileRenameLbl.config(state='disabled')
    def CFolderFrameLockDown(self):
        self.C2SFolder.config(state='disabled')
        self.CFolderDelete.config(state='disabled')
        self.CFolderRenameBtn.config(state='disabled')
        self.CFolderRenameEntry.config(state='disabled')
        self.CFolderRenameLbl.config(state='disabled')
    def CFileFrameRevive(self):
        self.C2SFile.config(state='normal')
        self.CFileDelete.config(state='normal')
        self.CFileRenameBtn.config(state='normal')
        self.CFileRenameEntry.config(state='normal')
        self.CFileRenameLbl.config(state='normal')
    def CFolderFrameRevive(self):
        self.C2SFolder.config(state='normal')
        self.CFolderDelete.config(state='normal')
        self.CFolderRenameBtn.config(state='normal')
        self.CFolderRenameEntry.config(state='normal')
        self.CFolderRenameLbl.config(state='normal')
        
    
        
    def BackDirServer(self):
        CurDir=self.CurServerPath
        if(len(CurDir.split("\\"))>1):
            CurDir='\\'.join(CurDir.split("\\")[:-1])
            self.SetServerPath(CurDir)
    def BackDirClient(self):
        CurDir=self.CurClientPath
        if(len(CurDir.split("\\"))>1):
            CurDir='\\'.join(CurDir.split("\\")[:-1])
            self.SetClientPath(CurDir)

    def LoadServerBrowser(self):
        self.SFolderFrameLockDown()
        self.SFileFrameLockDown()
        self.SBrowse.delete(0,tk.END)
        self.CirServerFiles=[]
        self.CirServerDirs=[]
        serverdata=client.GetDirList(self.CurServerPath)
        for i in serverdata:
            if(i!=''):
                if(i[-1]=="f"):
                    self.CurServerFiles.append(i[:-1])
                else:
                    self.CurServerDirs.append(i[:-1])
        
        for i in serverdata:
            if(i!=''):
                self.SBrowse.insert(tk.END,i[:-1])
            
    def LoadClientBrowser(self):
        self.CFolderFrameLockDown()
        self.CFileFrameLockDown()

        self.CBrowse.delete(0,tk.END)
        #print(self.CurClientPath)
        self.CurClientDirs=[x for x in os.listdir(self.CurClientPath) if x!='']
        for i in self.CurClientDirs:
            if(i!=''):
                #sprint(i)
                self.CBrowse.insert(tk.END,i)
        
Login()

