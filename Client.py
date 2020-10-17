import socket
import time
import os


class Client():
    
    
    s=socket.socket()
    
    def __init__(self,ip,port):
        self.s.connect((ip,port))
        print("Connected")
        
                
        
    def authorize(self,password):
        print("Checking message")
        self.s.send(password.encode())
        recvdata=self.s.recv(20)
        print(recvdata)
        if(b'Authorized' in recvdata):
            self.serverroot=(recvdata.split(b"$")[1]).decode().strip()
            return True
        else:
            return False
    def SetErrorEventHandler(self,event):
        self.errorevent=event
    def ErrorEventHandler(self,Message):
        self.errorevent("Error",Message)
        
        
    def shutDown(self):
        self.s.send(b"Shutdown^")

    def deleteFile(self,path):
        self.s.send(b'Delete File $'+(path+"^").encode())
    def deleteFolder(self,path):
        self.s.send(b'Delete Folder $'+(path+"^").encode())       
    def Rename(self,oldpath,newpath):
        self.s.send(('Rename $'+oldpath+"$"+newpath+"^").encode())
    def GetDirList(self,SPath):
        self.s.send(("Get Dir :"+SPath+"^").encode())
        #time.sleep(1)
        Err=self.checkErr()
        #if(Err!="None"):
        if(False):
            print("Error: "+Err)
        else:
            dirstr=self.getServerResponse("^")
            
            dirlist=(dirstr).split(';')
            return dirlist
    
    def SendFile(self,cpath,spath):
        chunk=1024
        cpath=cpath.replace("\\\\","\\")
        FileName=cpath.split("\\")[-1]
        FileSize=os.path.getsize(cpath.replace("\\\\","\\"))
        print("sending file",FileName)
        self.s.send(("Sending File $"+spath+"$"+FileName+"$"+str(FileSize)+"^").encode())
        f=open(cpath,'rb')
        x=True
        ByteCount=0
        while FileSize-ByteCount>=chunk:
            data=f.read(chunk)
            self.s.send(data)
            ByteCount+=chunk
        if(FileSize-ByteCount>0):
            self.s.send(f.read(FileSize-ByteCount))
        f.close()
        
    def getServerResponse(self,enclosebyte):
        payload=b''
        
        byte=self.s.recv(1)
        while byte!=enclosebyte.encode():
            if(byte==enclosebyte.encode()):
                break
            byte=self.s.recv(1)

        byte=self.s.recv(1)
        
        while byte!=enclosebyte.encode():
            #print(byte.decode(),end='')
            payload+=byte
            byte=self.s.recv(1)
            
        return payload.decode("UTF-8")
        
        
    def getFile(self,cpath,fname,spath,size):
        chunks=1024*1024
        recvsize=0
        if(size>0):
            self.s.send(("Get file$"+spath+"^").encode(encoding="UTF-8"))
            Err=self.checkErr()
            if(Err!="None"):
                self.ErrorEventHandler(Err)
                return
        if(not os.path.exists(cpath.replace(fname,""))):
            os.makedirs(cpath.replace(fname,""))
        print("Writing File",cpath+"\\"+fname)
        with open(cpath+"\\"+fname,"w+") as f:
            pass
        with open(cpath+"\\"+fname,"wb") as f:
            
            while size-recvsize>0:
                #print(size-bytecount,chunks)
                data=self.s.recv(chunks)
                recvsize+=len(data)
                #print(data)
                f.write(data)
                #self.ProgressEventHandler("Fetching File "+fname,recvsize*100/size)
##            if(size-bytecount>0):
##                  
##                print(size-bytecount)
##                f.write(self.s.recv(size-bytecount))
        print(recvsize,size)
        if(recvsize!=size):
            self.ErrorEventHandler("Some Error Occured")
        
                
    def getFolderMetaData(self,spath,cpath):
        self.s.send(("Get Folder$"+spath+"^").encode())
        Err=self.checkErr()
        if(Err=="None"):
            print("FurtherInfo")
            FileNameStr=self.getServerResponse("^")
            print(FileNameStr)
            Dirs=[]
            Files={}
            sep_string=";*&#%@"

            for i in FileNameStr.split(sep_string):
                #print("Determining")
                if(i!=""):
                    data=i.split("$")
                    if(len(data)==1):
                        Dirs.append(i.replace("\\\\","\\"))
                    else:
                        Files[data[0].replace("\\\\","\\")]=int(data[1])
            return Dirs,Files
        else:
            self.ErrorEventHandler(Err)
            
    def getFolder(self,spath,cpath):
        self.s.send(("Get Folder$"+spath+"^").encode())
        Err=self.checkErr()
        if(Err=="None"):
            print("FurtherInfo")
            FileNameStr=self.getServerResponse("^")
            print(FileNameStr)
            Dirs=[]
            Files={}
            sep_string=";*&#%@"

            for i in FileNameStr.split(sep_string):
                #print("Determining")
                if(i!=""):
                    data=i.split("$")
                    if(len(data)==1):
                        Dirs.append(i.replace("\\\\","\\"))
                    else:
                        Files[data[0].replace("\\\\","\\")]=int(data[1])
            for i in Dirs:
                newcpath=cpath+"\\"+i.replace("\\".join(spath.split("\\")[:-1]),"").lstrip("\\")
                print(newcpath)
                print(newcpath,os.path.exists(newcpath))
                if(not os.path.exists(newcpath)):
                    os.makedirs(newcpath)
                    print("Making Dir",i)
                    
            for i in Files:
                #xprint(i.replace("\\".join(spath.split("\\")[:-1]),"").lstrip("\\"))
                newcpath=cpath+"\\"+(i.replace("\\".join(spath.split("\\")[:-1]),"").lstrip("\\")).replace(i.split("\\")[-1],"")
                print("requesting ",i)
                self.getFile(newcpath,i.split("\\")[-1],i,Files[i])
        else:
            self.ErrorEventHandler(Err)
            
    def checkErr(self):
        Err=self.getServerResponse("^")
        if Err=="None":
            return "None"
        else:
            return Err
          
    def createDir(self,path):
        self.s.send(b"Create Dir $"+(path+"^").encode())
        
    def createFile(self,path):
        self.s.send(b"Create file $"+(path+"^").encode())
        
    def getLayeredDir(self,path):
        dirs=[]
        try:
            indirs=os.listdir(path)
        except:
            return
        for i in indirs:
                
                if(os.path.isdir(path+"\\"+i)):
                        templist=self.getLayeredDir(path+"\\"+i)
                        if templist!=None:  
                                dirs.extend(templist)
                        dirs.append(path+"\\"+i)
        return dirs
    
    def getFileSize(self,spath):
        self.s.send(("Get File Size$"+spath+"^").encode())
        Err=self.checkErr()
        if(Err=='None'):
            return int(self.getServerResponse("^"))
        else:
            self.ErrorEventHandler(Err)
            return None
    
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

    def SendFolder(self,cpath,spath):
        print(f"Sending {cpath} to {spath}")
        Files=self.fileLayeredSearch(cpath)
        SendStr="Sending Folder $"+spath+"$"+cpath.split("\\")[-1]+"$"
        FileCode=''
        DirCode=''
        for i in Files:
            sdata=i.replace("\\".join(cpath.split("\\")[:-1]),spath)
            print(f"sdata={sdata}")
            #print(f"{i}.replace({cpath},{spath})={sdata}")
            if(os.path.isfile(i)):
                FileCode+=sdata.replace("\\\\","\\")+";"+str(os.path.getsize(i))+"|"
            else:
                DirCode+=sdata.replace("\\\\","\\")+"|"
        SendStr+=DirCode
        SendStr+="$"
        SendStr+=FileCode
        self.s.send((SendStr+"^").encode())

        rsps=self.getServerResponse("^")
        while rsps!="$$$$$$$$":
            FileName=rsps
            print("Getting ",FileName)
            c_get_path=FileName.replace(spath,cpath.replace(cpath.split("\\")[-1],""))
            f_get_path='\\'.join(FileName.split("\\")[:-1])
            print(f'send ing file {c_get_path} to {f_get_path}')
            self.SendFile(c_get_path,f_get_path)
            rsps=self.getServerResponse("^")
            
        #print(FileCode,DirCode)

    def main(self):
        while True:
            cmd=input(">>> ")
            if(cmd.startswith("get file")):
                self.getFile(cmd.split('-')[2],(cmd.split('-')[1]).split("\\")[-1],cmd.split('-')[1],self.getFileSize(cmd.split('-')[1]))
            elif(cmd.startswith("get dir")):
                print(self.GetDirList(cmd.split('-')[1]))
            elif(cmd.startswith("shutdown")):
                self.shutDown()
            elif(cmd.startswith("send file")):
                self.SendFile(cmd.split('-')[1],cmd.split('-')[2])
            elif(cmd.startswith("send folder")):
                self.SendFolder(cmd.split('-')[1],cmd.split('-')[2])
            elif(cmd.startswith("delete file")):
                self.deleteFile(cmd.split('-')[1])
            elif(cmd.startswith("get folder")):
                self.getFolder(cmd.split('-')[1],cmd.split('-')[2])
            else:
                self.s.send(cmd.encode())
##client=Client('192.168.1.2',12347)
##client.main()

