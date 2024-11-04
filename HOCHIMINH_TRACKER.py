import json
import signal
import sys
import time
from tkinter import *
import tkinter as tk
import customtkinter as ctk
from  tkinter import messagebox
import math
import threading
import pickle
import socket
from threading import Thread
from pymongo import MongoClient


WIDTH = 900
HEIGHT = 600
SERVER_USERNAME = 'admin'
SERVER_PASSWORD = 'admin'
subFileSize= 512*1024 # 512KB

#---------------------------------SERVER_FE----------------------------------------------
class SlidePanel(ctk.CTkFrame):
  def __init__(self,parent,start_pos,end_pos):
      super().__init__(master=parent)
      
      self.start_pos=start_pos
      self.end_pos=end_pos
      self.width = abs(start_pos-end_pos)
      
      self.pos = start_pos
      self.in_start_pos = True
      
      self.place(relx=self.start_pos,rely=0,relwidth=self.width,relheight=0.65)
      
  def animate(self):
      if self.in_start_pos:
          self.animate_forward()
      else:
          self.animate_backward()
  def animate_forward(self):
      if self.pos > self.end_pos:
          self.pos -= 0.008
          self.place(relx=self.pos,rely=0,relwidth=self.width,relheight=0.65)
          self.after(5,self.animate_forward)
      else:
          self.in_start_pos = False
  def animate_backward(self):
      if self.pos < self.start_pos:
          self.pos += 0.008
          self.place(relx=self.pos,rely=0,relwidth=self.width,relheight= 0.65)
          self.after(5,self.animate_backward)
      else:
          self.in_start_pos = True


class SERVER_FE(ctk.CTk):
    def __init__(self, serverHost, serverPort):
        super().__init__()
        self.username = None
        self.password = None
        
        self.numberOfPeers= 0

        self.serverHost= serverHost
        self.serverPort= serverPort
        
        #---------------Initial frame of several page------------------------------
        self.frameInitialPage= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
        self.frameExecuteLoginButton= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
        self.frameMainPage= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
        self.frameListFilesOnSystem= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
        #--------------------------------------------------------------------------
        
        #-----------initial the text and animation----------------------------------
        self.outputStatusCenter = ctk.CTkTextbox(self.frameMainPage)
        
        self.animate_panel = SlidePanel(self.frameMainPage, 1, 0.72)
        self.outputListPeer = ctk.CTkTextbox(self.animate_panel)
        
        self.outputFileOnSystem = ctk.CTkTextbox(self.frameListFilesOnSystem)
        #-----------------------------------------------------------------------------
        
        self.title("Ho Chi Minh Tracker File Sharing Application")
        self.resizable(False,False) 
        self.geometry("900x600")
        
        self.current_frame = self.initialPage()
        self.current_frame.pack()

    def switch_frame(self, frame):
      self.current_frame.pack_forget()
      self.current_frame = frame()
      self.current_frame.pack(padx = 0) 
      
    # def changeTheme(self):
    #   type = ctk.get_appearance_mode()
    #   if(type=="Light"):
    #       ctk.set_appearance_mode("dark")
    #   else:
    #       ctk.set_appearance_mode("light")
        
    def initialPage(self):

      ctk.set_appearance_mode("light")
    
      frame_label = ctk.CTkLabel(self.frameInitialPage, text="WELCOME TO\n BITTORENT FILE SHARING", font=("Arial",40,"bold"))
      frame_label.place(relx=0.5,rely=0.4,anchor=tk.CENTER)

      button_sign_in = ctk.CTkButton(self.frameInitialPage, text="LOG IN", font= ("Arial", 20, "bold"),
                                      command=lambda:self.switch_frame(self.executeLoginButton))
      button_sign_in.place(relx=0.5,rely=0.7,anchor=tk.CENTER)
      
      # button_sign_up = ctk.CTkButton(self.frameInitialPage, text="CHANGE THEME", font= ("Arial", 20, "bold"), command= self.changeTheme)
      # button_sign_up.place(relx=0.6,rely=0.7,anchor=tk.CENTER)
      
      return self.frameInitialPage

    def executeLoginButton(self):
            
      home_page = ctk.CTkButton(self.frameExecuteLoginButton, text="HOME PAGE", font=("Arial",20,"bold"),
                                command= lambda:self.switch_frame(self.initialPage) )
      home_page.place(relx = 0.5, rely = 0.15, anchor = tk.CENTER)
      
      label_login = ctk.CTkLabel(self.frameExecuteLoginButton, text="LOG IN", font=(("Arial",30,"bold")))
      label_login.place(relx= 0.5,rely= 0.4,anchor = tk.CENTER)

      label_username = ctk.CTkLabel(self.frameExecuteLoginButton, text="Username", font=("Arial",20,"bold"))
      label_username.place(relx = 0.2, rely=0.5, anchor = tk.CENTER)
      
      username_entry = ctk.CTkEntry(self.frameExecuteLoginButton, placeholder_text="Username", width=300, height=4)
      username_entry.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)

      label_password = ctk.CTkLabel(self.frameExecuteLoginButton, text="Password", font=("Arial",20,"bold"))
      label_password.place(relx = 0.2, rely=0.6, anchor = tk.CENTER)
      
      password_entry = ctk.CTkEntry(self.frameExecuteLoginButton, placeholder_text="Password", width=300, height=4, show = "***************")
      password_entry.place(relx = 0.5, rely = 0.6, anchor = tk.CENTER)

      button_sign_in = ctk.CTkButton(self.frameExecuteLoginButton, text="CONFIRM", font= ("Arial", 20, "bold"), 
                                      command= lambda:self.check_login(username_entry, password_entry))
      button_sign_in.place(relx = 0.5, rely = 0.7, anchor = tk.CENTER)
      
      return self.frameExecuteLoginButton

    def check_login(self, username_entry, password_entry):
        username = username_entry.get()
        password = password_entry.get()

        user = tracker_db.find_one({"username": username})

        if user:
           #check password
            if user['password'] == password:
              self.username = username
              self.password = password
              messagebox.showinfo("Successful!", "Log in completed!")
            else:
              messagebox.showerror("Wrong password!", "Log in again!")
              return
        else:
            messagebox.showerror("Error!", "Log in again!")
            return

        self.switch_frame(self.mainPage)
        
    def mainPage(self):  
        
        self.outputListPeer.place(relx=0.5,rely=0.55,anchor=ctk.CENTER,relwidth=0.8,relheight=0.8)
        self.outputListPeer.configure(state=DISABLED)
        
        self.outputStatusCenter.place(relx=0.5,rely=0.58,anchor=tk.CENTER,relwidth=0.4,relheight=0.4)
        self.outputStatusCenter.configure(state=DISABLED)
        
        frame_label = ctk.CTkLabel(self.frameMainPage, text="Table State", font=("Arial", 15))
        frame_label.place(relx=0.5,rely=0.81,anchor=tk.CENTER)

        #------------------------main page server ----------------------------------#
        frame_label = ctk.CTkLabel(self.frameMainPage, text="WELCOME ADMIN", font=("Arial", 40,"bold"))
        frame_label.place(relx=0.5,rely=0.1,anchor=tk.CENTER)
        
        frame_label = ctk.CTkLabel(self.frameMainPage, text="INFORMATION OF TRACKER", font=("Arial",20, "bold"))
        frame_label.place(relx=0.5,rely=0.2,anchor=tk.CENTER)
        
        frame_label = ctk.CTkLabel(self.frameMainPage, text="Server Host: "+ self.serverHost, font= ("Arial", 15))
        frame_label.place(relx=0.5,rely=0.27,anchor=tk.CENTER)
        
        frame_label = ctk.CTkLabel(self.frameMainPage, text="Server Port: "+ str(self.serverPort), font= ("Arial", 15))
        frame_label.place(relx=0.5,rely=0.31,anchor=tk.CENTER)

         #----------------------- display inforpeer----------------------------------#
        
        btn_view_user=ctk.CTkButton(self.frameMainPage,text="LIST PEERS",
                                    font= ("Arial", 20, "bold"),
                                command =lambda:self.animate_panel.animate())
             
        btn_view_user.place(relx=0.3,rely=0.9,anchor=tk.CENTER)

        btn_show_peer = ctk.CTkButton(self.frameMainPage,text="FILES ON SYSTEM",
                               font= ("Arial", 20, "bold"),
                               command=lambda:self.switch_frame(self.listFilesOnSystem))
        btn_show_peer.place(relx=0.7,rely=0.9,anchor=tk.CENTER)

       
        # btn_change_themes = ctk.CTkButton(self.frameMainPage,text="CHANGE THEMES",
        #                        font= ("Arial", 20, "bold"),
        #                         command=self.changeTheme
        #                        )
        # btn_change_themes.place(relx=0.75,rely=0.9,anchor=tk.CENTER)
        list_header=ctk.CTkLabel(self.animate_panel, text = "LIST PEERS", font=("Arial", 30, "bold"))
        list_header.place(relx=0.5,rely= 0.1,anchor=ctk.CENTER)
        # list_header.pack()
        
        return self.frameMainPage
    
    def showPeers(self, state, informPeer):
      if state == "on":
        self.outputListPeer.configure(state=NORMAL)
        self.numberOfPeers+= 1
        self.outputListPeer.insert(ctk.END, f"{self.numberOfPeers}.  PeerHost: {informPeer[0]}, PeerPort: {informPeer[1]}." +"\n\n" )
        self.outputListPeer.see(ctk.END)
        self.outputListPeer.configure(state=DISABLED)
      else:
        self.outputListPeer.configure(state=NORMAL)
        # Lấy toàn bộ nội dung của widget
        peer_list = self.outputListPeer.get("1.0", ctk.END)  # Lấy từ dòng đầu tiên tới cuối
        lines = peer_list.split("\n")  # Chia các dòng thành danh sách
        for i, line in enumerate(lines):
          if f"PeerHost: {informPeer[0]}, PeerPort: {informPeer[1]}" in line:
              start_index = f"{i + 1}.0"  # Dòng bắt đầu
              end_index = f"{i + 2}.0"  # Dòng kết thúc (dòng tiếp theo)
              self.outputListPeer.delete(start_index, end_index)  # Xóa dòng đó
              break
        self.numberOfPeers-= 1
        self.outputListPeer.see(ctk.END)
        self.outputListPeer.configure(state=DISABLED)
    
    def listFilesOnSystem(self):
        
        self.outputFileOnSystem.place(relx=0.5,rely=0.58,anchor=tk.CENTER,relwidth=0.4,relheight=0.4)
        self.outputFileOnSystem.configure(state=DISABLED)

        #------------------------main page server ----------------------------------#
        frame_label = ctk.CTkLabel(self.frameListFilesOnSystem, text="LIST OF FILES ON THE SYSTEM", font=("Arial", 45,"bold"))
        frame_label.place(relx=0.5,rely=0.1,anchor=tk.CENTER)
        
        frame_label = ctk.CTkLabel(self.frameListFilesOnSystem, text="INFORMATION OF TRACKER", font=("Arial",20, "bold"))
        frame_label.place(relx=0.5,rely=0.2,anchor=tk.CENTER)
        
        frame_label = ctk.CTkLabel(self.frameListFilesOnSystem, text="Server Host: "+ self.serverHost, font= ("Arial", 15))
        frame_label.place(relx=0.5,rely=0.27,anchor=tk.CENTER)
        
        frame_label = ctk.CTkLabel(self.frameListFilesOnSystem, text="Server Port: "+ str(self.serverPort), font= ("Arial", 15))
        frame_label.place(relx=0.5,rely=0.31,anchor=tk.CENTER)

        #  #----------------------- display inforpeer----------------------------------#
        
        btn_BACK= ctk.CTkButton(self.frameListFilesOnSystem, text= "BACK", font= ("Arial", 20, "bold"),
                                command= lambda:self.switch_frame(self.mainPage))
        btn_BACK.place(relx= 0.5,rely=0.9,anchor=tk.CENTER)

        return self.frameListFilesOnSystem
      
    def showListFileOnSystem(self):
        self.outputFileOnSystem.configure(state= NORMAL)
        counter= 1
        self.outputFileOnSystem.delete(1.0, ctk.END)
        for fileName in SERVER_BEObject.listFileShared:
            self.outputFileOnSystem.insert(ctk.END, f"{counter}. fileName: \"{fileName}\"." + "\n")
            self.outputFileOnSystem.insert(ctk.END, "\n")
            counter+= 1
        self.outputFileOnSystem.see(ctk.END)
        self.outputFileOnSystem.configure(state= DISABLED)

    def showStatusCenter(self, typeOfStatement, peerHost, peerPort, fileName):
        self.outputStatusCenter.configure(state= NORMAL)
        if typeOfStatement== "Download":
            self.outputStatusCenter.insert(ctk.END, f"PeerHost: {peerHost}, PeerPort: {peerPort} download file \"{fileName}\""+ "\n\n")
        else:
            if typeOfStatement== "Upload":
                self.outputStatusCenter.insert(ctk.END, f"PeerHost: {peerHost}, PeerPort: {peerPort} upload file \"{fileName}\""+ "\n\n")
            else:
                if typeOfStatement== "Join to LAN":
                    self.outputStatusCenter.insert(ctk.END, f"PeerHost: {peerHost}, PeerPort: {peerPort} joined to network"+ "\n\n")
                elif typeOfStatement== "Close the App":
                    self.outputStatusCenter.insert(ctk.END, f"PeerHost: {peerHost}, PeerPort: {peerPort} Closed the App"+ "\n\n")
        self.outputStatusCenter.see(ctk.END)
        self.outputStatusCenter.configure(state= DISABLED)
        
#---------------------------FINISH SERVER_FE------------------------------------------------


#---------------------------------SERVER_BE-------------------------------------------------
class fileShared:
  def __init__(self, fileName, filePath, peerHost, peerPort, size):
    self.fileName= fileName
    self.numberOfPeer= 1
    self.size= size
    self.informPeerLocal= [[filePath, peerHost, peerPort]]
    
class SERVER_BE:
  
  def __init__(self, serverHost, serverPort):
    self.listPeer= []
    self.listFileExist= []
    self.listFileShared= set()
    
    self.serverHost= serverHost
    self.serverPort= serverPort

    self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.stopFlag = threading.Event()
    self.running = True
    self.connections = []

  def implementValidSignUp(self, new_user):
     username = new_user['username']
     password = new_user['password']

     if username == "" or password == "":
        return 'You must fill the infomation!'

     user = client_db.find_one({"username": username})
     if user is None:
        result = client_db.insert_one(new_user)
        return 'SUCCESS'
     else:
        return 'FAIL'
  
  def implementValidLogIn(self, user):
     username = user['username']
     password = user['password']

     user = client_db.find_one({"username":username})
     if user:
        #check password
        if user['password'] == password:
           return "SUCCESS"
        else:
          return "wrong password"
     else:
        return "user doesn't exist!"

  def seekListOfPeers(self,serverhost,serverport):
    #---------------------------------
    print()
  
  def implementDownload(self, conn):  
    #--------------------Receive the info_hash want to down----------------------------
    info_hash= str(conn.recv(4096), "utf-8")
    conn.send(bytes("SUCCESS", "utf-8"))  # confirm
    #------------------------------------------------------------------------------------
    
    #-----------------------Receive serverHost and serverPort----------------------------------
    serverhost= str(conn.recv(4096), "utf-8")
    conn.send(bytes("SUCCESS", "utf-8"))
    serverport= int(str(conn.recv(4096), "utf-8"))
    conn.send(bytes("SUCCESS", "utf-8"))
    #---------------------------------------------------------------------------------------
    
    conn.recv(4096) #kepp contact

    #----------------implement find list of peers--------------------------------------------------
    documents = client_db.find(
      {
        "info_hash":info_hash,
        "state": { "$ne": "off" }
      },
      {
        "ip_add":1,
        "ip_port":1,
        "_id":0
      }
    )
    list_peer = list(documents)

    json_data = json.dumps(list_peer) # Chuyển đổi mảng thành chuỗi JSON
    
    # Gửi dữ liệu qua socket
    conn.sendall(json_data.encode('utf-8'))
    conn.recv(4096) #success
    #----------------------------------------------------------------------------------------------
    
    """#-----------------Using for loop to down each of file in list------------------------
    fileShareObject = None
    for iterator in self.listFileShared:
      if iterator.fileName== fileNameDownload:
        fileShareObject= iterator
        break
    if fileShareObject!= None:
      conn.send(bytes("File exist!", "utf-8"))
      conn.recv(4096) # Success
      pieces= math.ceil(fileShareObject.size / subFileSize)

      #-----------Send list filePath and peer------------------------
      conn.sendall(pickle.dumps(fileShareObject.informPeerLocal))
      conn.recv(4096)
      #--------------------------------------------------------------
      
      #------------Send pieces of fileName---------------------------
      conn.send(bytes(str(pieces), "utf-8"))
      conn.recv(4096)
      #--------------------------------------------------------------
      SERVER_FEObject.showStatusCenter("Download", peerHost, peerPort, fileNameDownload)
      
    else:
      conn.send(bytes("File not exist!", "utf-8"))
      conn.recv(4096) # Success
      
    conn.send(bytes("SUCCESS", "utf-8"))"""
    
  def updateState(self, state, PeerHost):
     client_db.update_one({"ip_add": PeerHost},{"$set": {"state": state}})

  def implementListenPeer(self):
    self.serverSocket.bind((self.serverHost, self.serverPort))
    # serverSocket.bind(("", self.serverPort))
    self.serverSocket.listen(10)
  
    while self.running:
      try:
        conn, addr= self.serverSocket.accept()
        #stopFlag= threading.Event()
        self.stopFlag.clear()
        condition= Thread(target= self.threadListenPeer, args=[conn])
        condition.start()
      except OSError:
        break
      except Exception as e:
        print(f"Error: {e}")
      time.sleep(0.1)

  def stop(self):
    self.running = False
    self.serverSocket.close()
    for conn in self.connections:
      conn.close()
    self.connections.clear()
    
  def implementSharing(self, filePath, peerHost, peerPort, size):
    #----------------get fileName from filePath----------------------
    iterator= -1
    while True:
      if filePath[iterator]== "\\":
        break
      else:
        iterator-= 1
    fileName= filePath[(iterator+ 1): ]
    #-----------------------------------------------------------------
    
    #---------------Add inform to listFileShared----------------------
    flagFileExist= False
    for fileSharedObject in self.listFileShared:   # fileShared is the object
      if fileSharedObject.fileName== fileName:
        for informPeerLocal in fileSharedObject.informPeerLocal:  # informPeerLocal is the list
          if informPeerLocal[1]== peerHost and informPeerLocal[2]== peerPort:  # path equal or not
            flagFileExist= True
            break
        if flagFileExist== True:
          break
        else:
          flagFileExist= True
          fileSharedObject.numberOfPeer+= 1
          fileSharedObject.informPeerLocal.append([filePath, peerHost, peerPort])
          SERVER_FEObject.showListFileOnSystem()
          break
            
            
    if flagFileExist== False:
      fileShareObject= fileShared(fileName, filePath, peerHost, peerPort, size)
      self.listFileShared.append(fileShareObject)
      self.listFileExist.append(fileName)
      SERVER_FEObject.showListFileOnSystem()
    #------------------------------------------------------------------------------
    
    SERVER_FEObject.showStatusCenter("Upload", peerHost, peerPort, fileName)
    # print("-------------------Inform List----------------------------")
    # for iterator in self.listFileShared:
    #   print(iterator.fileName)
    #   print(iterator.size)
    #   print(iterator.informPeerLocal)
    # print("------------------Finish------------------------------------\n")

  def threadListenPeer(self, conn):
    try:
      while not self.stopFlag.is_set():
        # ---------------------Receive the type of request-----------
        typeOfRequest = str(conn.recv(4096), "utf-8")
        conn.send(bytes("SUCCESS", "utf-8"))  # confirm
        #-------------------------------------------------------------
        
        #-------------Classify the type request-----------------------
        if typeOfRequest== "Join to LAN":
          #----------------Receive inform of peer-----------------------
          peerInform= pickle.loads(conn.recv(4096))
          conn.send(bytes("SUCCESS", "utf-8"))  # confirm
          #------------------------------------------------------------
          
          #----------------Add inform of peer to list----------------------
          self.listPeer.append(peerInform)
          #---------------------------------------------------------------
          SERVER_FEObject.showPeers("on", peerInform)
          conn.recv(4096)  # new insert
          
          #-----------------Send the list of peers------------------------
          conn.sendall(pickle.dumps(self.listPeer))
          conn.recv(4096)  # success
          #---------------------------------------------------------------
          
          conn.send(bytes("SUCCESS", "utf-8"))
          
          SERVER_FEObject.showStatusCenter(typeOfRequest, peerInform[0], peerInform[1], "")
        elif typeOfRequest== "Cancel":
            self.stopFlag.set()         
        elif typeOfRequest== "Upload":
              #--------------------Receive upload filePath--------------------
              filePath = str(conn.recv(4096), "utf-8")
              conn.send(bytes("SUCCESS", "utf-8"))  # confirm
              #----------------------------------------------------------------

              #----------------Receive peerHost and peerPort-----------------------
              peerHost= str(conn.recv(4096), "utf-8")
              conn.send(bytes("SUCCESS", "utf-8"))  # confirm
              peerPort= int(str(conn.recv(4096), "utf-8"))
              conn.send(bytes("SUCCESS", "utf-8"))  # confirm
              #--------------------------------------------------------------------
              
              #--------------------Receive size of file-----------------------------
              size= int(str(conn.recv(4096), "utf-8"))
              conn.send(bytes("SUCCESS", "utf-8"))  # confirm
              #-----------------------------------------------------------------------
              
              #------------------add inform File to listFileShared--------------------
              self.implementSharing(filePath, peerHost, peerPort, size)
              #------------------------------------------------------------------------            
        elif typeOfRequest== "Sharing":
               #--------------------Receive upload filePath--------------------
               info_hash = str(conn.recv(4096), "utf-8")
               conn.send(bytes("SUCCESS", "utf-8"))  # confirm
               #----------------------------------------------------------------

               #----------------Receive peerHost and peerPort-----------------------
               peerHost= str(conn.recv(4096), "utf-8")
               conn.send(bytes("SUCCESS", "utf-8"))  # confirm
               peerPort= int(str(conn.recv(4096), "utf-8"))
               conn.send(bytes("SUCCESS", "utf-8"))  # confirm
               #--------------------------------------------------------------------

               #----------------Receive fileName-----------------------
               fileName= str(conn.recv(4096), "utf-8")
               conn.send(bytes("SUCCESS", "utf-8"))  # confirm
               self.listFileShared.add(fileName)
               SERVER_FEObject.showListFileOnSystem()
               #--------------------------------------------------------------------
                
               #----------------Receive magnet text-----------------------
               magnet_text= str(conn.recv(4096), "utf-8")
               conn.send(bytes("SUCCESS", "utf-8"))  # confirm
               #--------------------------------------------------------------------
                
                
               # Cập nhật hoặc thêm info_hash vào mảng trong cơ sở dữ liệu
               client_db.update_one(
                 {"ip_add": peerHost, "ip_port": peerPort},
                 {"$addToSet": {"info_hash": info_hash,"files": {"fileName": fileName, "magnet_text":magnet_text}}}  # Sử dụng $addToSet để thêm mà không trùng lặp
               )                     
        elif typeOfRequest== "Download":
                  self.implementDownload(conn)             
        elif typeOfRequest== "fileExist":
                      conn.recv(4096)
                      conn.sendall(pickle.dumps(self.listFileExist))
                      conn.recv(4096)
                      conn.send(bytes("SUCCESS", "utf-8"))              
        elif typeOfRequest == "Creation":
                        raw_data = conn.recv(4096);
                        json_data = raw_data.decode('utf-8') #chuyển BYTES thành chuỗi
                        data = json.loads(json_data)
                        result = self.implementValidSignUp(data)
                        conn.send(bytes(result,"utf-8"))
        elif typeOfRequest == "Valid":
                        raw_data = conn.recv(4096)
                        json_data = raw_data.decode('utf-8') #chuyển BYTES thành chuỗi
                        data = json.loads(json_data)
                        result = self.implementValidLogIn(data)
                        
                        if result == 'SUCCESS':
                          conn.send(bytes("SUCCESS","utf-8"))
                          #----------------Receive inform of peer-----------------------
                          peerInform= pickle.loads(conn.recv(4096))
                          client_db.update_one({"username":data['username']},{"$set": {"ip_add": peerInform[0],
                                                                                        "ip_port": peerInform[1]}})
                          self.updateState("on", peerInform[0])
                          conn.send(bytes("SUCCESS", "utf-8"))  # confirm
                          
                          #------------------------------------------------------------
                        else:
                          conn.send(bytes(result,"utf-8"))
        elif typeOfRequest == "Close the App":
                        #conn.send(bytes("SUCCESS", "utf-8"))
                        peerInform= pickle.loads(conn.recv(4096))
                        self.updateState("off", peerInform[0])
                        SERVER_FEObject.showPeers("off",peerInform)
                        SERVER_FEObject.showStatusCenter(typeOfRequest, peerInform[0], peerInform[1], "")
                        conn.send(bytes("SUCCESS", "utf-8"))
    except Exception as e:
      print(f"Error occurred: {e}")
    finally:
      conn.close()                                         
            
#----------------------FINISH SERVER_BE----------------------------------------------------           

# Hàm xử lý tín hiệu Ctrl+C
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Closing application...')
    SERVER_BEObject.stop()  # Gọi phương thức stop của PEER_BE
    sys.exit(0)
        
if __name__ == '__main__':
    serverHost= socket.gethostbyname_ex(socket.gethostname())[2][0]
    serverPort= 85
    print(socket.gethostbyname_ex(socket.gethostname())[2]);

    # Kết nối đến MongoDB sử dụng URI
    uri = "mongodb+srv://sharingFile-bitTorren:Hieu28282828@bittorent.yohyp.mongodb.net/"
    mongo = MongoClient(uri)
    database_name = mongo['test']
    client_db = database_name['Client']
    tracker_db = database_name['Tracker']

    client_db.create_index([("info_hash", 1)])
    
    SERVER_BEObject= SERVER_BE(serverHost, serverPort)

    signal.signal(signal.SIGINT, signal_handler)
    
    condition= Thread(target= SERVER_BEObject.implementListenPeer)
    condition.daemon = True
    condition.start()

    SERVER_FEObject = SERVER_FE(serverHost, serverPort)
    SERVER_FEObject.mainloop()