import socket
import os
from multiprocessing.dummy import Pool
import shutil


class Server:
    pwd="0000"
    s=socket.socket()
    clients=[]
    authorizedclients=[]
    busyclients=[]
    new_Client=None
    def __init__(self,root,pwd='0000'):
        self.pwd=pwd
        port=12346
        self.serverroot=root
        hn=socket.gethostname()
        #self.s.bind((socket.gethostbyname(hn),port))
        self.s.bind(('0.0.0.0',port))
        self.s.listen(5)
        
        print("Server running at",'137.97.52.117',":",port)#socket.gethostbyname(hn),":",port)

    def getClient(self):
        global new_Client
        while True:
            c=self.s.accept()[0]
            self.clients.append(c)
            self.new_Client=c
            print("Connected")
            self.authorize(c)
            if(c in self.authorizedclients):
                print("Successfully authorized")
                p=Pool(processes=1)
                p.apply_async(self.getRequest)
                
                #self.getRequest()
            else:
                print("Client removed")
            
    def authorize(self,c):
        try:
            while c not in self.authorizedclients:
                password=c.recv(100)
                print(password)
                if(password==self.pwd.encode()):
                    self.authorizedclients.append(c)
                    print("Done")
                    c.send(b"Authorized $ "+(self.serverroot).encode())
                else:
                    c.send(b"Nope")
        except:
            try:
                self.clients.remove(c)
                new_client=None
            except:
                pass
    def waitbusy(self,c):
        while c in self.busyclients:
            pass

    def deleteFile(self,c,path):
        os.remove(path)
    def deleteFolder(self,c,path):
        shutil.rmtree(path)
    def Rename(self,c,oldpath,newpath):
        os.rename(oldpath,newpath)
    def returnError(self,c,Err):
        c.send("Error")

    def createFile(self,c,path):
        dir='\\'.join(path.split('\\')[:-1])
        fName=path.split('\\')[-1]
        print(f"Creating File {fName} on {dir}")
        f=open(dir+'\\'+fName,'w+')
        f.close()

    def createDir(self,c,path):
        dircheck=path.split('\\')[0]+"\\"
        dir=path.split('\\')[1:]
        
        print(dir,dircheck,path)
        for i in dir:
            if(i!=''):
                if(i not in os.listdir(dircheck) ):
                    print("creating dir",i,'on',dircheck)
                    os.mkdir(dircheck+"\\"+i)
                dircheck+=(i)
                dircheck+='\\'

    def getRequest(self):
        c=self.new_Client
        while True:
            self.waitbusy(c)
            try:
                byte=c.recv(1)
                request=b''
                while byte!=b"^":
                    request+= byte
                    #print(byte)
                    byte=c.recv(1)
            except:
                self.clients.remove(c)
                break
            #print("waiting for request")
            print(request.decode())
            if(b'Get file' in request):
                print((request.partition(b"$")[2]))
                self.sendFile(c,(request.partition(b"$")[2]).decode())
            if(b'Get Dir' in request):
                self.sendDirectoryList(c,(request.partition(b":")[2]).decode())
            if(b'Create File' in request):
                print("File create request",(request.split(b'$')[1]).decode())
                self.createFile(c,(request.split(b'$')[1]).decode())
            if(b'Create Dir' in request):
                print("Dir create request",(request.split(b'$')[1]).decode())
                self.createDir(c,(request.split(b'$')[1]).decode())
            if(b'Sending File' in request):
                RecieveData=request.split(b'$')
                print("Recieving File",(request.split(b'$')[1]).decode(),'\nCommand=',RecieveData)
                self.GetFile(c,(RecieveData[1]).decode(),RecieveData[2].decode(),int(RecieveData[3].decode()))
            if(b'Sending Folder' in request):
                RecieveData=request.split(b'$')
                print("Recieving Folder",(request.split(b'$')[1]).decode())
                self.GetFolder(c,(RecieveData[1]).decode(),RecieveData[2].decode(),RecieveData[3].decode(),RecieveData[4].decode())
            if(b'Delete File' in request):
                print("Deleting File",(request.split(b'$')[1]).decode())
                self.deleteFile(c,(request.split(b'$')[1]).decode())
            if(b'Delete Folder' in request):
                print("Deleting Folder",(request.split(b'$')[1]).decode())
                self.deleteFolder(c,(request.split(b'$')[1]).decode())
            if(b'Get Folder' in request):
                print("Folder request",(request.split(b'$')[1]).decode())
                self.sendFolder(c,(request.split(b'$')[1]).decode())
            if(b'Get File Size' in request):
                print("FileSize request",(request.split(b'$')[1]).decode())
                self.sendFileSize(c,(request.split(b'$')[1]).decode())
            if(b'Rename' in request):
                print("Rename request",(request.split(b'$')[1]).decode(),"to",(request.split(b'$')[2]).decode())
                self.Rename(c,(request.split(b'$')[1]).decode(),(request.split(b'$')[2]).decode())
            if(b'Shutdown' in request):
                self.clients.remove(c)
                break
    def fileLayeredSearch(self,path):
        #print("f "+path)
        try:
            if(path[-1]!="\\"):
                path=path.rstrip()+"\\"
            files=os.listdir(path)
            temp=[]
            for i in files: temp.append(path+"\\"+i)
            files=temp
            #print("asdfad")
        except:
            return
        for i in files:
            if os.path.isdir(i):
                morefiles=self.fileLayeredSearch(i)
                if(morefiles!=None):
                    files.extend(morefiles)
        return files

    def sendErr(self,c,ErrMsg):
        c.send((f"^{ErrMsg}^").encode())

        
    def sendFolder(self,c,path):
        sep_string=";*&#%@"
        self.waitbusy(c)
        try:
            print(path)
            FileNames=self.fileLayeredSearch(path)
            if(FileNames==None):
                self.sendErr(c,"Directory not found")
                return
            self.sendErr(c,"None")
            FileSizes={}
            FileSendStr='^'
            for i in FileNames:
                print("packing",i)
                if(os.path.isfile(i)):
                    FileSizes[i]=os.path.getsize(i)
            for i in FileNames:
                if(os.path.isfile(i)):
                    FileSendStr+=(i+"$"+str(FileSizes[i])+sep_string)
                else:
                    FileSendStr+=(i+sep_string)
            FileSendStr+="^"
            c.send(FileSendStr.encode())
            print("File metadata sent")
        except(FileNotFoundError):
            self.sendErr(c,"FileNotFound")
    
    def sendDirectoryList(self,c,DPath):
        self.waitbusy(c)
        self.busyclients.append(c)
        
        print("Requestind Dir")
        try:
            dirs=os.listdir(DPath)
            self.sendErr(c,"None")
            c.send(b"^")
            for i in dirs:
                if(os.path.isfile(DPath+"\\"+i)):
                    c.send((i+"f;").encode())
                else:
                    c.send((i+"d;").encode())
                    
                
            c.send(b"^")
            
            self.busyclients.remove(c)
        except:
            self.sendErr(c,"FileNotFound")
            print("SomeErr")
    def sendFileSize(self,c,path):
        self.waitbusy(c)
        self.busyclients.append(c)
        try:
            size=str(os.path.getsize(path))
            self.sendErr(c,"None")
            stream=("^"+size+"^").encode()
            c.send(stream)
        except:
            self.sendErr(c,"FileNotFound")
        self.busyclients.remove(c)
        
    def sendFile(self,c,path):
        self.waitbusy(c)
        self.busyclients.append(c)
        try:
            chunk=1024*1024*1024
            print("sending file")
            FileName=path.replace("\\\\","\\")
            FileSize=os.path.getsize(path.replace("\\\\","\\"))
            self.sendErr(c,"None")
            print(f"File size ",FileSize)
            f=open(FileName,'rb')
            x=True
            ByteCount=0
            while FileSize-ByteCount>=chunk:
                data=f.read(chunk)
                print("Loop")
                c.send(data)
                ByteCount+=chunk
            if(FileSize-ByteCount>0):
                c.send(f.read(FileSize-ByteCount))
            print("File sent")
        except:
            self.sendErr(c,"FileNotFound")
        self.busyclients.remove(c)
        
    def GetFile(self,c,path,fname,size):
        print("Geting file start")
        self.waitbusy(c)

        self.busyclients.append(c)
        
        chunks=1024*1024
        if(not os.path.exists(path.replace(fname,""))):
            os.makedirs(path.replace(fname,""))
        print("Writing File",path+"\\"+fname)
        with open(path+"\\"+fname,"w+") as f:
            pass
        if(size>0):
            recvsize=0
            with open(path+"\\"+fname,"wb") as f:
                
                while size-recvsize>0:
                    if(size-recvsize<chunks):
                        data=c.recv(size-recvsize)
                        f.write(data)
                        recvsize+=len(data)
                    else:
                        data=c.recv(chunks)
                        f.write(data)
                        recvsize+=len(data)
                if(size-recvsize>0):
                    f.write(c.recv(size-recvsize))
                
        self.busyclients.remove(c)
        print("Getting file stop")
                
    def GetFolder(self,c,path,FolderName,DirCode,FileCode):
        
        self.waitbusy(c)
        
        Dirs=[]
        Files={}
        for i in DirCode.split("|"):
            if(i!=""):
                Dirs.append(i)
                #print("Dir",i)
        for i in FileCode.split("|"):
            if(i!=""):
                Files[i.split(";")[0]]=i.split(";")[1]
                #print("File",i)
        for i in Dirs:
            if(not os.path.exists(i)):
                os.makedirs(i)
                
        for i in Files:
            self.waitbusy(c)
            c.send(("^"+i+"^").encode())
        c.send("^$$$$$$$$^".encode())

        
                

#p=Pool(processes=1)
#p.apply_async(getClient)
s=Server(input('Server Root Directory: '),input("Server Password: "))
s.getClient()
#print(s.FileLayeredSearch("E:\\"))

