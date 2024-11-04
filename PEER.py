import re
import bencodepy
import hashlib
import json
import signal
import sys
import time
from tkinter import *
import tkinter as tk
# from customtkinter import CTkButton
import customtkinter as ctk
from tkinter import messagebox
import socket
from threading import Thread
import pickle
import threading
import os
import math

import urllib.parse


WIDTH = 900
HEIGHT = 600
subFileSize= 512*1024 # 512KB

#----------------------------------------Start front end-------------------------------
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
          self.after(10,self.animate_forward)
      else:
          self.in_start_pos = False
  def animate_backward(self):
      if self.pos < self.start_pos:
          self.pos += 0.008
          self.place(relx=self.pos,rely=0,relwidth=self.width,relheight= 0.65)
          self.after(10,self.animate_backward)
      else:
          self.in_start_pos = True

class PEER_FE(ctk.CTk):
  
  def __init__(self, peerHost, peerPort):
    super().__init__()
    self.flagLogIn = False

    self.username = None
    self.password = None
    
    self.numberOfFileUploaded= 0
    self.numberOfFileDownloaded= 0
    
    self.fileUploaded= []
    self.fileDownloaded= []
    self.fileExist= []

    self.peerHost= peerHost
    self.peerPort= peerPort

    self.nameServer= ""

    
    
    #---------------------------initial frame for each page-----------------------------
    self.frameInitialPage= ctk.CTkFrame(self,width= 1020, height=700)
    self.frameAcountPage= ctk.CTkFrame(self,width= 1020, height=700)
    self.frameExecuteSignUpButton= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
    self.frameExecuteLoginButton= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
    self.frameConnectToServer= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
    self.frameMainPage= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
    self.frameExecuteUploadButton= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
    self.frameExecuteDownloadButton= ctk.CTkFrame(self,width=WIDTH,height=HEIGHT)
    
    
    self.textFileExist= ctk.CTkTextbox(self.frameExecuteDownloadButton)
    
    self.animatePanelDownload = SlidePanel(self.frameExecuteDownloadButton, 1,0.7)
    self.outputFileDownload = ctk.CTkTextbox(self.animatePanelDownload)
    
    self.animatePaneUpload = SlidePanel(self.frameExecuteUploadButton, 1,0.7)
    self.outputFileUpload = ctk.CTkTextbox(self.animatePaneUpload)

    self.ServerHost = None
    self.ServerPort = None

    self.resizable(False,False)
    self.title("Bittorrent File Sharing")
    self.geometry("900x600")
    
    # Đặt sự kiện đóng cửa sổ
    self.protocol("WM_DELETE_WINDOW", lambda: self.on_close())
  
    self.current_frame = self.initialPage()
    self.current_frame.pack()

  def on_close(self):
    if self.flagLogIn:
      PEER_BEObject.stateClose()
    #Đóng cửa sổ
    print("Closing window...")
    PEER_BEObject.stopFlag.set()  # Dừng các luồng
    self.destroy()
    
  def switch_frame(self, frame):
    self.current_frame.pack_forget()
    self.current_frame = frame()
    self.current_frame.pack(padx = 0)   
    
  def initialPage(self):

    ctk.set_appearance_mode("light")
    
    frame_label = ctk.CTkLabel(self.frameInitialPage, text="WELCOME TO\n BITTORENT FILE SHARING", font=("Arial",40,"bold"))
    frame_label.place(relx=0.5,rely=0.4,anchor=tk.CENTER)

    button_HaNoi = ctk.CTkButton(self.frameInitialPage, text="Ha Noi Server", font=("Arial", 15, "bold"),
                                    command=lambda:self.executeChooseTrackerButton("HaNoi"))
    button_HaNoi.place(relx=0.4,rely=0.7,anchor=tk.CENTER)
    
    button_HoChiMinh = ctk.CTkButton(self.frameInitialPage, text="Ho Chi Minh Server", font=("Arial", 15, "bold"),
                                        command=lambda:self.executeChooseTrackerButton("HoChiMinh"))
    button_HoChiMinh.place(relx=0.6,rely=0.7,anchor=tk.CENTER)
    
    return self.frameInitialPage
  
  def executeChooseTrackerButton(self, location):
    if location == "HaNoi":
      PEER_BEObject.serverHost = "172.31.0.1"
      PEER_BEObject.serverPort = 85
      self.nameServer = "Ha Noi Server"
    elif location == "HoChiMinh":
      PEER_BEObject.serverHost = "172.31.0.1"
      PEER_BEObject.serverPort = 85
      self.nameServer = "Ho Chi Minh Server"
    self.switch_frame(self.accountPage)
    
  def accountPage(self):
    frame_label = ctk.CTkLabel(self.frameAcountPage, text="WELCOME TO\n BITTORENT FILE SHARING", font=("Arial",40,"bold"))
    frame_label.place(relx=0.5,rely=0.4,anchor=tk.CENTER)

    button_sign_in = ctk.CTkButton(self.frameAcountPage, text="Log in", font=("Arial", 15, "bold"),
                                    command=lambda:self.switch_frame(self.executeLoginButton))
    button_sign_in.place(relx=0.4,rely=0.7,anchor=tk.CENTER)
    
    button_sign_up = ctk.CTkButton(self.frameAcountPage, text="Sign up", font=("Arial", 15, "bold"),
                                        command=lambda:self.switch_frame(self.executeSignUpButton))
    button_sign_up.place(relx=0.6,rely=0.7,anchor=tk.CENTER)

    button_back = ctk.CTkButton(self.frameAcountPage, text="Back", font=("Arial", 15, "bold"),
                                    command=lambda:self.switch_frame(self.initialPage))
    button_back.place(relx=0.5,rely=0.8,anchor=tk.CENTER)    

    return self.frameAcountPage
  
  def executeSignUpButton(self):
    home_page = ctk.CTkButton(self.frameExecuteSignUpButton, text="HOME PAGE", font=("Arial",20,"bold"),
                              command= lambda:self.switch_frame(self.accountPage) )
    home_page.place(relx = 0.5, rely = 0.15, anchor = tk.CENTER)
    
    label_signup = ctk.CTkLabel(self.frameExecuteSignUpButton, text="SIGN UP", font=(("Arial",30,"bold")))
    label_signup.place(relx= 0.5,rely= 0.4,anchor = tk.CENTER)

    label_username = ctk.CTkLabel(self.frameExecuteSignUpButton, text="Username", font=("Arial",20,"bold"))
    label_username.place(relx = 0.2, rely=0.5, anchor = tk.CENTER)
    
    username_entry = ctk.CTkEntry(self.frameExecuteSignUpButton, placeholder_text="Username", width=300, height=4)
    username_entry.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)

    label_password = ctk.CTkLabel(self.frameExecuteSignUpButton, text="Password", font=("Arial",20,"bold"))
    label_password.place(relx = 0.2, rely=0.6, anchor = tk.CENTER)
    
    password_entry = ctk.CTkEntry(self.frameExecuteSignUpButton, placeholder_text="Password", width=300, height=4, show = "***************")
    password_entry.place(relx = 0.5, rely = 0.6, anchor = tk.CENTER)

    label_confirm_password = ctk.CTkLabel(self.frameExecuteSignUpButton, text="Confirm Password", font=("Arial",20,"bold"))
    label_confirm_password.place(relx = 0.2, rely=0.7, anchor = tk.CENTER)
    
    confirm_password_entry = ctk.CTkEntry(self.frameExecuteSignUpButton, placeholder_text="Confirm Password", width=300, height=4, show = "***************")
    confirm_password_entry.place(relx = 0.5, rely = 0.7, anchor = tk.CENTER)

    button_sign_in = ctk.CTkButton(self.frameExecuteSignUpButton, text="CONFIRM", font=("Arial",15,"bold"), 
                                    command= lambda:self.executeConFirmSignUpButton(username_entry, password_entry, confirm_password_entry))
    button_sign_in.place(relx = 0.5, rely = 0.8, anchor = tk.CENTER)
    
    return self.frameExecuteSignUpButton
  
  def executeConFirmSignUpButton(self,usernameEntry, passwordEntry, confirmPassEntry):
    username = usernameEntry.get()
    password = passwordEntry.get()
    confirmPass = confirmPassEntry.get()

    if confirmPass == password:
      new_user = {
        "username": username,
        "password": password
      }
      result = PEER_BEObject.createPEER(new_user)
      if result == 'SUCCESS':
        messagebox.showinfo("Successful", "Your account successfully was created!")
      elif result == 'FAIL':
        messagebox.showerror("ERROR", result)
      else:
        messagebox.showerror("ERROR", "Your username has been existed!")
        return
    else:
      messagebox.showerror("ERROR", "Your password doesn't match with confirm password")
      return
    self.switch_frame(self.accountPage)

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

    button_sign_in = ctk.CTkButton(self.frameExecuteLoginButton, text="CONFIRM", font=("Arial",15,"bold"), 
                                    command= lambda:self.executeConfirmLogInButton(username_entry, password_entry))
    button_sign_in.place(relx = 0.5, rely = 0.7, anchor = tk.CENTER)
    
    return self.frameExecuteLoginButton

  def executeConfirmLogInButton(self, usernameEntry, passwordEntry):
    username = usernameEntry.get()
    password = passwordEntry.get()

    user ={
      "username": username,
      "password": password
    }
    
    result = PEER_BEObject.validationAccount(user)
    if result == 'SUCCESS':
      self.flagLogIn = True
      messagebox.showinfo("Successful", "Login success")
      PEER_BEObject.implementJoinToLAN()
      self.switch_frame(self.mainPage)
    else:
      messagebox.showerror("ERROR", result)
      return

  def signout(self):
    result = messagebox.askyesno("Confirm", "Are you sure?")
    if result:
      PEER_BEObject.stateClose()
      self.switch_frame(self.initialPage)
    else:
      return

  def mainPage(self):
      
    frame_label = ctk.CTkLabel(self.frameMainPage, text=self.nameServer, font=("Arial",40,"bold"))
    frame_label.place(relx=0.5,rely=0.2,anchor=tk.CENTER)
    
    frame_label = ctk.CTkLabel(self.frameMainPage, text="INFORMATION OF PEER", font=("Arial",20, "bold"))
    frame_label.place(relx=0.5,rely=0.4,anchor=tk.CENTER)
    
    frame_label = ctk.CTkLabel(self.frameMainPage, text="Peer Host: "+ self.peerHost, font=("Arial", 15 ))
    frame_label.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
    
    frame_label = ctk.CTkLabel(self.frameMainPage, text="Peer Port: "+ str(self.peerPort), font=("Arial", 15))
    frame_label.place(relx=0.5,rely=0.55,anchor=tk.CENTER)
    
    #----------------Button UPLOAD---------------------------------------------------------
    self.btn_upload = ctk.CTkButton(self.frameMainPage, text="UPLOAD", font=("Arial", 20, "bold"),
                                    command=lambda:self.switch_frame(self.executeUploadButton))
    self.btn_upload.place(relx=0.33,rely = 0.7,anchor =tk.CENTER)
    #---------------------------------------------------------------------------------------
    
    #---------------------------Button DOWNLOAD----------------------------------------------
    self.btn_download = ctk.CTkButton(self.frameMainPage, text="DOWNLOAD", font=("Arial", 20, "bold"),
                                        command=lambda:self.switch_frame(self.executeDownloadButton))
    self.btn_download.place(relx=0.67,rely = 0.7,anchor =tk.CENTER)
    #----------------------------------------------------------------------------------------
    #--------------------------Button SIGNOUT------------------------------------------------
    button_sign_out = ctk.CTkButton(self.frameMainPage, text="SIGN OUT", font=("Arial",15,"bold"), 
                                    command= self.signout)
    button_sign_out.place(relx = 0.9, rely = 0.05, anchor = tk.CENTER)
    #----------------------------------------------------------------------------------------
    #----------------------------Button CHANGE THEME--------------------------------------------------------
    """self.btn_show_listpeer = ctk.CTkButton(self.frameMainPage, text="CHANGE THEME", font=("Arial", 20, "bold"),
                                            command= self.changeTheme)
    self.btn_show_listpeer.place(relx= 0.7,rely=0.7,anchor = tk.CENTER)"""
    #--------------------------------------------------------------------------------------------------
  
    return self.frameMainPage
  
  def executeUploadButton(self):

    header_upload = ctk.CTkLabel(self.frameExecuteUploadButton, text="UPLOAD FILE", font=("Arial", 40,"bold"))
    header_upload.place(relx = 0.5,rely=0.3,anchor = CENTER)
    
    self.outputFileUpload.place(relx=0.5,rely=0.55,anchor=ctk.CENTER,relwidth=0.8,relheight=0.8)
    self.outputFileUpload.configure(state=DISABLED)

    upload_label = ctk.CTkLabel(self.frameExecuteUploadButton, text="Choose the file you want to share", font=("Arial", 20,"bold"))
    upload_label.place(relx = 0.5, rely=0.43,anchor = tk.CENTER)

    upload_entry = ctk.CTkEntry(self.frameExecuteUploadButton, width=200, height= 10, placeholder_text="Enter path to file")
    upload_entry.place(relx = 0.6, rely=0.5,anchor = tk.CENTER)
    # Nút mở cửa sổ chọn file
    btn_browse = ctk.CTkButton(self.frameExecuteUploadButton, text="Browse", font=("Arial", 20,"bold"),
                               command=lambda: self.browseFile(upload_entry))
    btn_browse.place(relx=0.4, rely=0.5, anchor=tk.CENTER)
    
    btn_BACK= ctk.CTkButton(self.frameExecuteUploadButton,text="BACK", font=("Arial", 20,"bold"),
                          command =lambda: self.switch_frame(self.mainPage))
    btn_BACK.place(relx= 0.3, rely= 0.7, anchor= tk.CENTER)
    
    btn_upload = ctk.CTkButton(self.frameExecuteUploadButton, text="UPLOAD", font=("Arial", 20,"bold"),
                                command=lambda:(self.getFileUpload(upload_entry)))      
    btn_upload.place(relx = 0.7,rely=0.7,anchor = CENTER)
  

    # btn_view_repo=ctk.CTkButton(self.frameExecuteUploadButton,text="FILE UPLOADED", font=("Arial", 20,"bold"),
    #                       command =lambda:self.animatePaneUpload.animate())
    # btn_view_repo.place(relx= 0.7, rely= 0.7, anchor= tk.CENTER)
    
    #--------------------------Button SIGNOUT------------------------------------------------
    button_sign_out = ctk.CTkButton(self.frameExecuteUploadButton, text="SIGN OUT", font=("Arial",15,"bold"), 
                                    command= self.signout)
    button_sign_out.place(relx = 0.9, rely = 0.05, anchor = tk.CENTER)
    #----------------------------------------------------------------------------------------
    
    # list_header=ctk.CTkLabel(self.animatePaneUpload, text = " LIST FILES ", font=("Comic Sans",30,"bold"))
    # list_header.place(relx=0.5,rely=0.1,anchor=ctk.CENTER)
    # list_header.pack()

    return self.frameExecuteUploadButton

  def browseFile(self, upload_entry):
    # Tạo cửa sổ chọn file hoặc thư mục
    file_path = tk.filedialog.askopenfilename(title="Select a File",
                                               filetypes=(("All Files", "*.*"),))
    if file_path:  # Nếu chọn file
        upload_entry.delete(0, tk.END)  # Xóa nội dung trước đó của entry
        upload_entry.insert(0, file_path)  # Chèn đường dẫn của file được chọn
    else:  # Nếu không chọn file, kiểm tra xem người dùng có chọn thư mục không
        folder_path = tk.filedialog.askdirectory(title="Select a Folder")
        if folder_path:  # Nếu chọn thư mục
            upload_entry.delete(0, tk.END)  # Xóa nội dung trước đó của entry
            upload_entry.insert(0, folder_path)  # Chèn đường dẫn của thư mục được chọn
  
  def create_torrent(self, path):
    piece_length = 524288  # 512KB cho mỗi piece
    torrent_info = {
        'info': {
            'name': os.path.basename(path),
            'piece length': piece_length,
            'pieces': b'',  # Mảng chứa hash của từng piece (để cập nhật sau)
            'length': 0,  # Tổng kích thước sẽ được cập nhật sau
            'files': []  # Chứa thông tin về các file nếu là thư mục
        },
        'announce': f"tcp://{PEER_BEObject.serverHost}:{PEER_BEObject.serverPort}",
        'creation date': int(os.path.getmtime(path)),
        'comment': 'Created by my torrent application',
        'file_path': os.path.abspath(path)  # Thêm đường dẫn tuyệt đối của thư mục gốc
    }

    # Kiểm tra xem path là file hay thư mục
    if os.path.isfile(path):
        # Nếu là file đơn lẻ, xử lý như bình thường
        file_size = os.path.getsize(path)
        if file_size == 0:
            raise ValueError("File is empty, cannot create torrent.")
        
        pieces = []
        with open(path, 'rb') as f:
            while True:
                piece = f.read(piece_length)
                if not piece:
                    break
                pieces.append(hashlib.sha1(piece).digest())

        # Tính info_hash cho file đơn
        info_hash = hashlib.sha1(b''.join(pieces)).hexdigest()

        torrent_info['info']['pieces'] = b''.join(pieces)
        torrent_info['info']['length'] = file_size
        torrent_info['info']['files'].append({
            'path': [os.path.abspath(path)],  # Lưu đường dẫn tuyệt đối của file đơn
            'length': file_size,
            'piece indices': list(range(len(pieces))),  # Lưu chỉ số của các piece
            'info_hash': info_hash  # Lưu info_hash
        })

    elif os.path.isdir(path):
        # Nếu là thư mục, duyệt qua các file trong thư mục (bao gồm cả thư mục con)
        total_length = 0
        for dirpath, _, filenames in os.walk(path):  # Sử dụng os.walk để duyệt qua tất cả thư mục
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    raise ValueError(f"File '{filename}' is empty, cannot create torrent.")

                pieces = []
                with open(file_path, 'rb') as f:
                    while True:
                        piece = f.read(piece_length)
                        if not piece:
                            break
                        pieces.append(hashlib.sha1(piece).digest())

                # Tính info_hash cho file
                info_hash = hashlib.sha1(b''.join(pieces)).hexdigest()

                # Cập nhật thông tin cho file
                torrent_info['info']['files'].append({
                    'path': [os.path.abspath(file_path)],  # Lưu đường dẫn tuyệt đối của từng file
                    'length': file_size,
                    'piece indices': list(range(len(pieces))),  # Lưu chỉ số của các piece
                    'info_hash': info_hash  # Lưu info_hash
                })
                torrent_info['info']['pieces'] += b''.join(pieces)  # Cập nhật các piece
                total_length += file_size

        torrent_info['info']['length'] = total_length  # Cập nhật tổng kích thước

    else:
        raise ValueError("Path does not exist or is not a file or directory.")

    # Lưu file torrent vào thư mục Downloads
    program_dir = os.path.dirname(os.path.abspath(__file__))
    torrent_folder = os.path.join(program_dir, "Torrent_files")

     # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(torrent_folder):
       os.makedirs(torrent_folder)

    # Đường dẫn file torrent
    torrent_file_path = os.path.join(torrent_folder, f"{os.path.basename(path)}.torrent")

    # Ghi file torrent
    with open(torrent_file_path, 'wb') as torrent_file:
        torrent_file.write(bencodepy.encode(torrent_info))
    
    return torrent_file_path

  def create_magnet_link(self,torrent_file_path):
    # Đọc file torrent để lấy thông tin
    with open(torrent_file_path, 'rb') as torrent_file:
        torrent_info = bencodepy.decode(torrent_file.read())

    # Lấy info_hash
    info_hash = hashlib.sha1(bencodepy.encode(torrent_info[b'info'])).hexdigest()
    
    # Lấy tên file và tracker URL
    file_name = torrent_info[b'info'][b'name']
    file_size = torrent_info[b'info'][b'length']
    tracker_url = torrent_info[b'announce'].decode('utf-8')  # Chuyển đổi từ bytes sang str

    # Tạo magnet link
    magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(file_name)}&tr={tracker_url}&xl={file_size}"
    
    info = [info_hash, magnet_link, file_size]
    return info

  def show_magnet_link(self, magnet_link):
    # Tạo một cửa sổ Toplevel
    top = tk.Toplevel()
    top.title("Magnet Link")
    top.geometry("400x200")  # Thiết lập kích thước cửa sổ dài hơn

    # Thêm nhãn
    label = ctk.CTkLabel(top, text="Your magnet link:",width=300, height=8)
    label.pack(pady=10)

    # Thêm Entry widget để hiển thị magnet link
    entry = ctk.CTkEntry(top, width=300, height=8)  # Thay đổi kích thước Entry
    entry.insert(0, magnet_link)  # Đưa magnet link vào Entry
    entry.pack(pady=10)

    # Hàm sao chép vào clipboard
    def copy_to_clipboard():
        entry.select_range(0, tk.END)  # Chọn toàn bộ nội dung
        entry.focus_set()  # Đặt con trỏ vào Entry
        top.clipboard_clear()  # Xóa clipboard
        top.clipboard_append(entry.get())  # Thêm nội dung vào clipboard
        messagebox.showinfo("Copied", "Magnet link copied to clipboard!")  # Thông báo cho người dùng

    # Khung để chứa nút Copy và Close
    button_frame = tk.Frame(top)
    button_frame.pack(pady=10)

    # Nút Copy
    copy_button = ctk.CTkButton(button_frame, text="Copy", command=copy_to_clipboard, width=15, height=8)
    copy_button.pack(side=tk.LEFT, padx=5)  # Nút Copy nằm bên trái

    # Nút Close
    close_button = ctk.CTkButton(button_frame, text="Close", command=top.destroy, width=15, height=8)
    close_button.pack(side=tk.LEFT, padx=5)  # Nút Close nằm bên phải

  def getFileUpload(self, upload_entry):
    filePathUpload= upload_entry.get()   # file path

    # Loại bỏ dấu ngoặc kép nếu có
    if filePathUpload.startswith('"') and filePathUpload.endswith('"'):
        filePathUpload = filePathUpload[1:-1]

    # Chuyển đổi dấu gạch chéo ngược thành gạch chéo xuôi
    filePathUpload = filePathUpload.replace('/', '\\')

    if not os.path.exists(filePathUpload):
      messagebox.showerror("Error", "File don't exist!")
      return

    torrent_file_path = self.create_torrent(filePathUpload)
    info = self.create_magnet_link(torrent_file_path)

    condition= Thread(target= PEER_BEObject.implementSharing, args= [info[0], filePathUpload, info[1]])
    condition.start()
    self.show_magnet_link(info[1])
    self.switch_frame(self.executeUploadButton)
         
  def showFileUploaded(self, fileName):
    # self.fileUploaded.append(fileName)

    self.outputFileUpload.configure(state=NORMAL)
    self.numberOfFileUploaded+= 1
    self.outputFileUpload.insert(ctk.END, f"{self.numberOfFileUploaded}.   \"{fileName}\"" +"\n\n" )

    self.outputFileUpload.see(ctk.END)
    self.outputFileUpload.configure(state=DISABLED)

  def showMoment(self):
    frame = ctk.CTkFrame(self,width=(WIDTH + 120),height=700)

    header_upload = ctk.CTkLabel(frame, text="WAITING A MOMENT!", font=("Arial", 40,"bold"))
    header_upload.place(relx = 0.5,rely=0.5,anchor = CENTER)
    
    return frame
      
  def executeDownloadButton(self):

    header_upload = ctk.CTkLabel(self.frameExecuteDownloadButton, text="DOWNLOAD FILE", font=("Arial", 40,"bold"))
    header_upload.place(relx = 0.5,rely=0.1,anchor = CENTER)
    
    # listOfFile = ctk.CTkLabel(self.frameExecuteDownloadButton, text="LIST OF FILES", font=("Arial", 20,"bold"))
    # listOfFile.place(relx = 0.5,rely=0.2,anchor = CENTER)
 
    self.textFileExist.place(relx=0.5,rely=0.44,anchor=ctk.CENTER,relwidth=0.3,relheight=0.4)
    self.textFileExist.configure(state=DISABLED)
    self.showFileExist()
    
    self.outputFileDownload.place(relx=0.5,rely=0.55,anchor=ctk.CENTER,relwidth=0.8,relheight=0.8)
    self.outputFileDownload.configure(state=DISABLED)

    upload_label = ctk.CTkLabel(self.frameExecuteDownloadButton, text="Enter your magnet text", font=("Arial", 20,"bold"))
    upload_label.place(relx = 0.5, rely=0.7,anchor = tk.CENTER)

    upload_entry = ctk.CTkEntry(self.frameExecuteDownloadButton, width=300, height= 10, placeholder_text="Enter magnet text")
    upload_entry.place(relx = 0.5, rely=0.75,anchor = tk.CENTER)
    
    btn_BACK= ctk.CTkButton(self.frameExecuteDownloadButton,text="BACK", font=("Arial", 20,"bold"),
                          command =lambda: self.switch_frame(self.mainPage))
    btn_BACK.place(relx= 0.3, rely= 0.85, anchor= tk.CENTER)
    
    btn_upload = ctk.CTkButton(self.frameExecuteDownloadButton, text="DOWNLOAD", font=("Arial", 20,"bold"),
                                command=lambda:(self.getFileDownload(upload_entry)))      
    btn_upload.place(relx = 0.7,rely=0.85,anchor = CENTER)
  
    #--------------------------Button SIGNOUT------------------------------------------------
    button_sign_out = ctk.CTkButton(self.frameExecuteDownloadButton, text="SIGN OUT", font=("Arial",15,"bold"), 
                                    command= self.signout)
    button_sign_out.place(relx = 0.9, rely = 0.05, anchor = tk.CENTER)
    #----------------------------------------------------------------------------------------

    # btn_view_repo=ctk.CTkButton(self.frameExecuteDownloadButton,text="FILE DOWNLOADED", font=("Arial", 20,"bold"),
    #                       command =lambda: self.animatePanelDownload.animate())
    # btn_view_repo.place(relx= 0.75, rely= 0.85, anchor= tk.CENTER)
    
    # list_header=ctk.CTkLabel(self.animatePanelDownload, text = " LIST FILES ", font=("Comic Sans",30,"bold")
    #                           )
    # list_header.place(relx=0.5,rely=0.1,anchor=ctk.CENTER)
    # list_header.pack()

    return self.frameExecuteDownloadButton
  
  def getFileDownload(self, download_entry):
    magnet_text = str(download_entry.get())
    if magnet_text == "":
        messagebox.showerror("Error", "No files specified for download!")
    else:
        listMagnetLinks = magnet_text.split(", ")

        for magnet in listMagnetLinks:
            try:
                # Sử dụng biểu thức chính quy để trích xuất info_hash, server_host, server_port và file_size
                info_hash_match = re.search(r'xt=urn:btih:([a-fA-F0-9]+)', magnet)
                tracker_match = re.search(r'tr=tcp://([^:/]+):(\d+)', magnet)
                file_size_match = re.search(r'xl=(\d+)', magnet)
                file_name_match = re.search(r'dn=([^&]+)', magnet)

                if info_hash_match and tracker_match and file_size_match and file_name_match:
                    info_hash = info_hash_match.group(1)
                    server_host = tracker_match.group(1)
                    server_port = int(tracker_match.group(2))
                    file_size = int(file_size_match.group(1))
                    file_name = urllib.parse.unquote(file_name_match.group(1))

                    # Khởi tạo luồng download với thông tin đã phân tách
                    condition = Thread(
                        target=PEER_BEObject.implementDownload, 
                        args=[info_hash, server_host, server_port, file_size, file_name]
                    )
                    condition.start()
                else:
                    messagebox.showerror("Error", f"Invalid magnet link format: {magnet}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                continue

        self.switch_frame(self.executeDownloadButton)        


    """listFileNameDownload= []
      iteratorLeft= 0
      iteratorRight= 0
      while True:
        if iteratorRight == len(stringFileNameDownload) -1:
          listFileNameDownload.append(stringFileNameDownload[iteratorLeft: (iteratorRight+ 1)])
          break
        else:
          if stringFileNameDownload[iteratorRight]== ",":  # file1.txt, file2.txt
            listFileNameDownload.append(stringFileNameDownload[iteratorLeft: iteratorRight])
            iteratorLeft= iteratorRight+ 2
            iteratorRight= iteratorLeft
          else:
            iteratorRight+= 1
      
      for fileNameDownload in listFileNameDownload:  
        condition= Thread(target= PEER_BEObject.implementDownload, args=[fileNameDownload])
        condition.start()"""
      
      #self.switch_frame(self.executeDownloadButton)
  
  def showFileDownloaded(self, fileName):
    self.outputFileDownload.configure(state=NORMAL)
    self.numberOfFileDownloaded+= 1
    self.outputFileDownload.insert(ctk.END, f"{self.numberOfFileDownloaded}:   \"{fileName}\"" +"\n\n" )
    self.outputFileDownload.see(ctk.END)
    self.outputFileDownload.configure(state=DISABLED)

  def showFileExist(self):
    self.fileExist= PEER_BEObject.implementReceiveListFileExist()
    self.textFileExist.configure(state=NORMAL)
    count=1
    self.textFileExist.delete(1.0, ctk.END)
    for file in self.fileExist:
        self.textFileExist.insert(ctk.END, f"{count}:   {file}" +"\n\n" )
        count +=1
    self.textFileExist.see(ctk.END)
    self.textFileExist.configure(state=DISABLED)

#-------------------------------------End Front end-------------------------------------
        
#-------------------------------Backend-----------------------------------------------

class PEER_BE():
  
  def __init__(self, peerHost, peerPort):
    self.serverHost= None
    self.serverPort= None
    
    self.peerHost= peerHost
    self.peerPort= peerPort
    
    self.subFileSize= 512*1024

    self.running = True  # Biến cờ để kiểm soát vòng lặp
    self.connections = []  # Danh sách các kết nối
    self.peerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.stopFlag = threading.Event()

    self.piece_size = 512 * 1024
    self.download_mapping = {}  # Mapping giữa file và các phần của nó

  def stateClose(self):
    #-------------------- socket initial-------------------
    peerConnectServerSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    peerConnectServerSocket.connect((self.serverHost, self.serverPort))
    #-------------------------------------------------------

    #------------------ send and receive--------------------
    peerConnectServerSocket.send(bytes("Close the App", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    # ----------------------------------------------------

    #-------------------Send inform of peer------------------------
    peerInform= pickle.dumps([self.peerHost, self.peerPort])
    peerConnectServerSocket.sendall(peerInform)
    peerConnectServerSocket.recv(4096) # success
    #--------------------------------------------------------------

    #---------------send cancel command to close the connection---------------------
    peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #-----------------------------------------------------------------------------

    peerConnectServerSocket.close()

  def createPEER(self, new_user):
    #-------------------- socket initial-------------------
    peerConnectServerSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    peerConnectServerSocket.connect((self.serverHost, self.serverPort))
    #-------------------------------------------------------

    #------------------ send and receive--------------------
    peerConnectServerSocket.send(bytes("Creation", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    # --------------------------------------------------------

    #--------------Send new user to server----------------------   
    peerConnectServerSocket.send(json.dumps(new_user).encode("utf-8")) # chuyển từ Object sang Json rồi gửi cho TRACKER
    response = peerConnectServerSocket.recv(4096)  # success
    response_data = response.decode('utf-8') 
    #---------------------------------------------------------

    #---------------send cancel command to close the connection---------------------
    peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #-----------------------------------------------------------------------------

    peerConnectServerSocket.close()
    return response_data

  def validationAccount(self, user):
    try:
      #-------------------- socket initial-------------------
      peerConnectServerSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      peerConnectServerSocket.connect((self.serverHost, self.serverPort))
      #-------------------------------------------------------
      
      #------------------ send and receive--------------------
      peerConnectServerSocket.send(bytes("Valid", "utf-8"))
      peerConnectServerSocket.recv(4096)  # success      
      # --------------------------------------------------------
      
      #--------------Send new user to server----------------------   
      peerConnectServerSocket.send(json.dumps(user).encode("utf-8")) # chuyển từ Object sang Json rồi gửi cho TRACKER
      response_data = str(peerConnectServerSocket.recv(4096), "utf-8")  # success 
      #---------------------------------------------------------
      if response_data == "SUCCESS":
        #-------------------Send inform of peer------------------------
        peerInform= pickle.dumps([self.peerHost, self.peerPort])
        peerConnectServerSocket.sendall(peerInform)
        peerConnectServerSocket.recv(4096) # success
        #--------------------------------------------------------------
      #---------------send cancel command to close the connection---------------------
      peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      #-----------------------------------------------------------------------------
      
      peerConnectServerSocket.close()
      return response_data
    except ConnectionResetError:
      print("Connection was forcibly closed by the remote host.")
      return "ERROR: Connection closed by server."
    except socket.error as e:
      print(f"Socket error: {e}")
      return "ERROR: Socket error occurred."
    
  def seedingFileCompleted(self, filePath):
     #-------------------- socket initial-------------------
    peerConnectServerSocket= socket.socket()
    peerConnectServerSocket.connect((self.serverHost, self.serverPort))
    #-------------------------------------------------------
    
    #------------------ send and receive--------------------
    peerConnectServerSocket.send(bytes("Upload", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    # --------------------------------------------------------
      
    #--------------Send file Name to server----------------------   
    peerConnectServerSocket.send(bytes(filePath, "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #---------------------------------------------------------
      
    #----------------Send peerHost and port--------------------
    peerConnectServerSocket.send(bytes(self.peerHost, "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    peerConnectServerSocket.send(bytes(str(self.peerPort), "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #------------------------------------------------------------
    
    #-------------Send size of file--------------------------------
    sizeOfFile= os.path.getsize(filePath)
    peerConnectServerSocket.send(bytes(str(sizeOfFile), "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #---------------------------------------------------
    
    #---------------send cancel command to close the connection---------------------
    peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #-----------------------------------------------------------------------------
    
    #close the socket
    peerConnectServerSocket.close()
    #-------------------
    
  def implementSharing(self, info_hash, file_path, magnet_text):
    try:
      #-------------------- socket initial-------------------
      peerConnectServerSocket= socket.socket()
      peerConnectServerSocket.connect((self.serverHost, self.serverPort))
      #-------------------------------------------------------
      
      #------------------ send and receive--------------------
      peerConnectServerSocket.send(bytes("Sharing", "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      # --------------------------------------------------------
        
      #--------------Send file Name to server----------------------   
      peerConnectServerSocket.send(bytes(info_hash, "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      #---------------------------------------------------------
        
      #----------------Send peerHost and port--------------------
      peerConnectServerSocket.send(bytes(self.peerHost, "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      peerConnectServerSocket.send(bytes(str(self.peerPort), "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      #------------------------------------------------------------
      
      #----------------Send fileName--------------------
      fileName = os.path.basename(file_path)
      peerConnectServerSocket.send(bytes(str(fileName),"utf-8"))
      peerConnectServerSocket.recv(4096)
      #------------------------------------------------------------
      
      #----------------Send magnet text--------------------
      peerConnectServerSocket.send(bytes(str(magnet_text),"utf-8"))
      peerConnectServerSocket.recv(4096)
      #------------------------------------------------------------        
      
      #---------------send cancel command to close the connection---------------------
      peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      #-----------------------------------------------------------------------------
      
      #close the socket
      peerConnectServerSocket.close()
      #-------------------
      
      """#-----------------get fileName--------------------
      fileName = os.path.basename(filePath)
      #------------------------------------------------
      messagebox.showinfo("Successful", "Upload file "+ str(fileName)+ " completed!")
      PEER_FEObject.fileUploaded.append(fileName)
      PEER_FEObject.showFileUploaded(fileName)"""
    except Exception as e:
      messagebox.showerror("Error", f"Đã xảy ra lỗi: {e}")
  
  def implementReceiveListFileExist(self):
    #-------------------- socket initial-------------------
    peerConnectServerSocket= socket.socket()
    peerConnectServerSocket.connect((self.serverHost, self.serverPort))
    #-------------------------------------------------------
    
    #------------------ send and receive--------------------
    peerConnectServerSocket.send(bytes("fileExist", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    # ----------------------------------------------------
    
    peerConnectServerSocket.send(bytes("SUCCESS", "utf-8"))
    
    #----------------Receive list file exist-----------------------
    listFileExist= pickle.loads(peerConnectServerSocket.recv(10240))
    peerConnectServerSocket.send(bytes("SUCCESS", "utf-8"))
    #---------------------------------------------------------------
    
    peerConnectServerSocket.recv(4096)
    
    #---------------send cancel command to close the connection---------------------
    peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #-----------------------------------------------------------------------------
    
    #close the socket
    peerConnectServerSocket.close()
    #-------------------
    
    return listFileExist
  
  def implementJoinToLAN(self):
    #-------------------- socket initial-------------------
    peerConnectServerSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    peerConnectServerSocket.connect((self.serverHost, self.serverPort))
    #-------------------------------------------------------
    
    #------------------ send and receive--------------------
    peerConnectServerSocket.send(bytes("Join to LAN", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    # ----------------------------------------------------
    
    #-------------------Send inform of peer------------------------
    peerInform= pickle.dumps([self.peerHost, self.peerPort])
    peerConnectServerSocket.sendall(peerInform)
    peerConnectServerSocket.recv(4096) # success
    #--------------------------------------------------------------
    
    peerConnectServerSocket.send(bytes("CONFIRM", "utf-8")) # new insert
    
    #---------------Receive the list of peers-------------------------
    listPeer= pickle.loads(peerConnectServerSocket.recv(4096))
    peerConnectServerSocket.send(bytes("SUCCESS", "utf-8"))  # confirm
    #------------------------------------------------------------------
    
    peerConnectServerSocket.recv(4096)
    
    #---------------send cancel command to close the connection---------------------
    peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    #-----------------------------------------------------------------------------
    
    #close the socket
    peerConnectServerSocket.close()
    #-------------------
       
  def threadListenServerOrPeers(self, conn, addr):
    try:
      while not self.stopFlag.is_set():
        #----------------Receive Type of connect server or peer-----------------------------
        serverOrPeer = str(conn.recv(4096), "utf-8")
        conn.send(bytes("SUCCESS", "utf-8"))  # confirm
        #-----------------------------------------------------------------------------------

        #---------------Classify the serverOrPeer-----------------------------------------
        if serverOrPeer== "SERVER":
          #-----------------Receive FileName-------------------------------------
          filePartPath= str(conn.recv(4096), "utf-8")
          # PEER_FEObject.showFileUploaded(filePartPath)
          conn.send(bytes("SUCCESS", "utf-8"))  # confirm
          #---------------------------------------------------------------------
          
          #-------------------------Receive size of file-----------------------------
          sizeOfFile= int(str(conn.recv(4096), "utf-8"))
          conn.send(bytes("SUCCESS", "utf-8"))  # confirm
          #-------------------------------------------------------------------------

          #--------------Receive the content of file-------------------------------
          with open(filePartPath, "wb") as file:
            content= b''
            while sizeOfFile > 0:
              data= conn.recv(min(10240, sizeOfFile))
              if not data:
                break
              content+= data
              sizeOfFile-= len(data)
            file.write(content)
            file.close()
          conn.send(bytes("SUCCESS", "utf-8"))  # confirm
          #-------------------------------------------------------------------------
          
          #-----------------------Cancel command------------------------------------
          cancelCommand= str(conn.recv(4096), "utf-8")
          conn.send(bytes("SUCCESS", "utf-8"))  # confirm
          self.stopFlag.set()
          #-----------------------------------------------------------------------    
        elif serverOrPeer== "Torrent":
          file_name = str(conn.recv(4096),"utf-8")
          conn.send(bytes("SUCCESS", "utf-8")) #confirm
          # Loại bỏ phần mở rộng hiện tại và thay bằng .torrent
          file_name = file_name + ".torrent"

          #----------------------------------------------
          script_dir = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn đến thư mục chứa chương trình
          torrent_folder = os.path.join(script_dir, "Torrent_files")

          # Xác định đường dẫn đầy đủ của tệp torrent
          torrent_file_path = os.path.join(torrent_folder, file_name)
          # Kiểm tra xem tệp có tồn tại không
          if not os.path.isfile(torrent_file_path):
            raise FileNotFoundError(f"The torrent file '{file_name}' was not found in '{torrent_folder}'.")
          
          # Đọc và giải mã nội dung của tệp torrent
          with open(torrent_file_path, 'rb') as torrent_file:
             torrent_data = bencodepy.decode(torrent_file.read())

          #---------------------------------------------------------------------------------------
          torrent_info = {
              'info': {
                  'name': torrent_data.get(b'info', {}).get(b'name', b'').decode('utf-8'),
                  'piece length': torrent_data.get(b'info', {}).get(b'piece length', 0),
                  'pieces': torrent_data.get(b'info', {}).get(b'pieces', b'').hex(),  # Chuyển sang chuỗi hex
                  'length': torrent_data.get(b'info', {}).get(b'length', 0),
                  'files': [
                      {
                          'path': [p.decode('utf-8') for p in file[b'path']],
                          'length': file[b'length'],
                          'piece indices': file.get(b'piece indices', []),
                          'info_hash': file.get(b'info_hash', b'').decode('utf-8')  # Giải mã thành chuỗi UTF-8
                      } for file in torrent_data.get(b'info', {}).get(b'files', [])
                  ]
              },
              'announce': torrent_data.get(b'announce', b'').decode('utf-8'),
              'creation date': torrent_data.get(b'creation date', 0),
              'comment': torrent_data.get(b'comment', b'').decode('utf-8'),
              'file_path': torrent_data.get(b'file_path', b'').decode('utf-8')
          }

          # Chuyển `torrent_info` thành JSON và gửi qua socket
          torrent_info_serialized = json.dumps(torrent_info, ensure_ascii=False)

          # Gửi dữ liệu qua socket
          conn.sendall(torrent_info_serialized.encode('utf-8'))
          conn.recv(4096) #confirm
          #---------------------------------------------------------------------------------------
        elif serverOrPeer== "PEER":
            #-------------------- recieve info_hash to peer-------------------
            file_name = str(conn.recv(4096), "utf-8")
            conn.send(bytes("SUCCESS", "utf-8"))  # confirm
            #-----------------------------------------------------------------

            #------------------recieve range of index_piece----------------------
            piece_index_start = int(str(conn.recv(4096), "utf-8"))
            conn.send(bytes("SUCCESS", "utf-8"))
            piece_index_end = int(str(conn.recv(4096), "utf-8"))
            conn.send(bytes("SUCCESS", "utf-8"))
            number_of_pieces = int(str(conn.recv(4096), "utf-8"))
            conn.send(bytes("SUCCESS", "utf-8"))
            # Giải mã JSON thành mảng
            data = conn.recv(4096)
            all_piece_indices = json.loads(data.decode()) # Giải mã JSON thành mảng
            conn.send(bytes("SUCCESS", "utf-8")) #confirm
            #-----------------------------------------------------------------

            file_name = file_name + ".torrent"
            #----------------------------------------------
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn đến thư mục chứa chương trình
            torrent_folder = os.path.join(script_dir, "Torrent_files")

            # Xác định đường dẫn đầy đủ của tệp torrent
            torrent_file_path = os.path.join(torrent_folder, file_name)
            # Kiểm tra xem tệp có tồn tại không
            if not os.path.isfile(torrent_file_path):
              raise FileNotFoundError(f"The torrent file '{file_name}' was not found in '{torrent_folder}'.")

            #----------------------------------------------
            # Đọc và giải mã nội dung của tệp torrent
            with open(torrent_file_path, 'rb') as torrent_file:
               torrent_data = bencodepy.decode(torrent_file.read())
               # Trích xuất `torrent_info`
               torrent_info = torrent_data.get(b'info', {})
               # Lấy danh sách tệp từ `torrent_info`
               files = torrent_info.get(b'files', [])
            #-------------------------------------------------------------------
            # Tạo một từ điển để ánh xạ info_hash tới file_path
            file_map = {
                file.get(b'info_hash').decode(): os.path.join(torrent_folder, *[p.decode() for p in file[b'path']])
                for file in files if b'info_hash' in file
            }

            #----------------- Truyền file theo all_piece_indices ----------------
            for info_hash, index in all_piece_indices[piece_index_start:piece_index_end]:  # Sử dụng khoảng từ start đến end-1
               file_path = file_map.get(info_hash)

               if file_path:
                  # Tính toán kích thước của từng phần
                  start = index * subFileSize  # Tính toán vị trí bắt đầu cho phần này

                  # Kiểm tra kích thước tệp để điều chỉnh kích thước phần cuối cùng
                  file_size = os.path.getsize(file_path)  # Lấy kích thước tệp
                  end = min(start + subFileSize, file_size)  # Tính toán vị trí kết thúc cho phần này
                  try:
                     # Mở tệp và đọc phần tương ứng
                     with open(file_path, "rb") as file:
                        file.seek(start)  # Di chuyển con trỏ đến vị trí bắt đầu
                        piece_data = file.read(end - start)  # Đọc dữ liệu cho phần hiện tại

                        if not piece_data:  # Nếu không còn dữ liệu để đọc
                           break
                        
                        conn.sendall(piece_data)  # Gửi dữ liệu qua socket
                        conn.recv(4096)  # Chờ phản hồi từ peer
                  except Exception as e:
                     print(f"Lỗi khi truyền dữ liệu: {e}")
                     conn.send(bytes("ERROR", "utf-8"))  # Thông báo lỗi
               else:
                  print(f"Không tìm thấy file_path cho info_hash {info_hash}")
                  conn.send(bytes("ERROR", "utf-8"))  # Thông báo lỗi khi không tìm thấy file
            #-------------------------------------------------------------------
        elif serverOrPeer== "Cancel":
           self.stopFlag.set()
    except Exception as e:
      print(f"Error occurred: {e}")
    finally:
        # Đảm bảo luôn đóng kết nối
        conn.close()
  
  def listenServerOrPeers(self):
    self.peerSocket.bind((self.peerHost, self.peerPort))
    self.peerSocket.listen(10)
    
    while self.running:
      try:
        conn, addr= self.peerSocket.accept()
        self.connections.append(conn)  # Thêm kết nối vào danh sách
        self.stopFlag.clear()
        #self.stopFlag= threading.Event()
        condition= Thread(target= self.threadListenServerOrPeers, args= [conn, addr])
        condition.start()
      except OSError:
        break # Nếu socket đã bị đóng, thoát vòng lặp
      except Exception as e:
        print(f"Error: {e}")
      time.sleep(0.1)  # Thêm thời gian chờ để tránh CPU sử dụng 100%

  def stop(self):
        self.stateClose()
        self.running = False  # Đặt biến cờ thành False để dừng vòng lặp
        self.peerSocket.close()  # Đóng socket để ngăn chặn kết nối mới
        for conn in self.connections:  # Đóng tất cả các kết nối
            conn.close()
        self.connections.clear()  # Xóa danh sách các kết nối

  def getTorrentInfo(self,file_name, peer):
    peerconn= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
      peerconn.connect((peer['ip_add'], peer['ip_port']))
      #-------------------------------------------------------------------
      peerconn.send(bytes("Torrent", "utf-8"))
      peerconn.recv(4096)
      #--------------------------------------------------------------------

      #--------------------------------------------------------------------
      peerconn.send(bytes(file_name, "utf-8"))
      peerconn.recv(4096) #confirm
      #--------------------------------------------------------------------

      #--------------------------------------------------------------------
      data = peerconn.recv(10*1024).decode('utf-8')
      torrent_info = json.loads(data)
      peerconn.send(bytes("SUCCESS", "utf-8"))
      #--------------------------------------------------------------------

      peerconn.send(bytes("Cancel","utf-8"))
      peerconn.recv(4096)
      peerconn.close()

      return torrent_info

    except (socket.timeout, socket.error) as e:
      print(f"Network error occurred: {e}")
    
  def implementDownload(self, info_hash, serverhost, serverport, size, file_name):
    
    #-------------------- socket initial-------------------
    peerConnectServerSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
      peerConnectServerSocket.connect((self.serverHost, self.serverPort))
      #-------------------------------------------------------
      
      #------------------ send and receive--------------------------------
      peerConnectServerSocket.send(bytes("Download", "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      #---------------------------------------------------------------
      
      #------------------Send info_hash want to down------------------------------
      peerConnectServerSocket.send(bytes(info_hash,"utf-8"))
      peerConnectServerSocket.recv(4096)
      #-------------------------------------------------------------------
      
      #--------------------Send peerHost and peerPort----------------------
      peerConnectServerSocket.send(bytes(serverhost, "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      peerConnectServerSocket.send(bytes(str(serverport), "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      #--------------------------------------------------------------------
      
      peerConnectServerSocket.send(bytes("SUCCESS", "utf-8")) #keep contact

      # Nhận danh sách peer
      data = peerConnectServerSocket.recv(4096).decode('utf-8')
      peerConnectServerSocket.send(bytes("SUCCESS", "utf-8"))
      list_peer = json.loads(data)

      #---------------Close connection--------------------------------------
      peerConnectServerSocket.send(bytes("Cancel", "utf-8"))
      peerConnectServerSocket.recv(4096)  # success
      peerConnectServerSocket.close()
      #---------------------------------------------------------------------
      if len(list_peer) == 0:
        messagebox.showinfo("Not success","Now there are no active peer that has this file/folder!")
        return
      torrent_info = self.getTorrentInfo(file_name, list_peer[0])
      #---------------------------------------------------------------------

      number_of_pieces = 0
      for file in torrent_info["info"]["files"]:
        piece_indices = file["piece indices"]
        number_of_pieces += len(piece_indices)
      
      piece_array = {}
      
      # Lấy số lượng peer tối đa là 5
      num_peer_to_use = min(5, len(list_peer))

      # Chia đều số lượng piece cho từng peer
      pieces_per_peer = number_of_pieces // num_peer_to_use
      remainder = number_of_pieces % num_peer_to_use
      threads = []

      # Lấy danh sách tất cả các piece indices với thông tin tương ứng
      all_piece_indices = []
      for file in torrent_info["info"]["files"]:
         for index in file["piece indices"]:
            all_piece_indices.append((file["info_hash"], index))   
      
      # Khởi tạo chỉ số bắt đầu
      start = 0
      for i in range(num_peer_to_use):
         end = start + pieces_per_peer + (1 if i < remainder else 0)  # Thêm phần dư vào peer
         peer = list_peer[i]  # Chọn peer theo chỉ số
         # Tạo luồng cho từng khoảng phần tệp
         thread = threading.Thread(target=self.download_piece, args=(start, end, all_piece_indices, peer, file_name, number_of_pieces, piece_array))
         threads.append(thread)
         thread.start()
         print(f"Peer {peer}: Tải từ {start} tới {end}")
         start = end  # Cập nhật chỉ số bắt đầu cho peer tiếp the
      # Chờ tất cả các luồng hoàn thành
      for thread in threads:
         thread.join()
      
      # Tạo từ điển để ánh xạ dữ liệu
      piece_map = {}
      for idx, (ih, index) in enumerate(all_piece_indices):
          if ih not in piece_map:
            piece_map[ih] = {}
          piece_map[ih][index] = piece_array[idx]  # Ánh xạ mảnh dữ liệu theo info_hash và index

      # Kiểm tra nếu là file đơn hoặc thư mục
      if "files" in torrent_info["info"] and len(torrent_info["info"]["files"]) > 1:
        # Xử lý thư mục
        # Ghép các mảnh theo thứ tự và ghi vào file cuối cùng
        download_directory = os.path.join(os.path.expanduser("~"), "Downloads", file_name)  # Đường dẫn đến thư mục Downloads
      else:
        download_directory = os.path.join(os.path.expanduser("~"), "Downloads")  # Đường dẫn đến thư mục Downloads
      
      # Tạo thư mục con nếu chưa tồn tại
      os.makedirs(download_directory, exist_ok=True)

      for file in torrent_info["info"]["files"]:
        info_hash = file["info_hash"]
        full_path = os.path.join(*file["path"])
        relative_path = os.path.relpath(full_path, start=torrent_info["file_path"])
        file_path = os.path.join(download_directory, relative_path)

        # Tạo đường dẫn cho file hoặc thư mục
        if len(torrent_info["info"]["files"]) > 1:  # Nếu là thư mục
            file_path = os.path.join(download_directory, relative_path)  # Đường dẫn đến file trong thư mục
        else:  # Nếu là file đơn
            file_path = os.path.join(download_directory, os.path.basename(full_path))  # Chỉ lấy tên file
        
        # Tạo thư mục con nếu chưa tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Ghi từng mảnh vào tệp theo đúng thứ tự
        with open(file_path, "wb") as final_file:
            indices = [idx for ih, idx in all_piece_indices if ih == info_hash]
            for index in indices:
                piece_data = piece_map.get(info_hash, {}).get(index)
                if piece_data is not None:
                    final_file.write(piece_data)  # Ghi dữ liệu vào tệp
                else:
                    print(f"Lỗi: Thiếu dữ liệu cho mảnh {index} của tệp {file_path}")

      print("DOWNLOAD SUCCESS")
      messagebox.showinfo("notification","DOWNLOAD SUCCESS!")
    except (socket.timeout, socket.error) as e:
       print(f"Network error occurred: {e}")
      
  def download_piece(self, start, end, all_piece_indices, peer, file_name, number_of_pieces, piece_array):
    try:
      #-------------------- socket initial-------------------
      peerConnectPeerSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      
      peerConnectPeerSocket.connect((peer['ip_add'], peer['ip_port']))
      #-------------------------------------------------------
      
      #-------------------- socket connect to peer-------------------
      peerConnectPeerSocket.send(bytes("PEER", "utf-8"))
      peerConnectPeerSocket.recv(4096)
      #---------------------------------------------------------------

      #-------------------- send file_name to peer-------------------
      peerConnectPeerSocket.send(bytes(file_name, "utf-8"))
      peerConnectPeerSocket.recv(4096)  # confirm
      #--------------------------------------------------------------

      #---------------------send range of index_piece-------------------
      peerConnectPeerSocket.send(bytes(str(start), "utf-8"))
      peerConnectPeerSocket.recv(4096) #success
      
      peerConnectPeerSocket.send(bytes(str(end), "utf-8"))
      peerConnectPeerSocket.recv(4096) #success
      peerConnectPeerSocket.send(bytes(str(number_of_pieces), "utf-8"))
      peerConnectPeerSocket.recv(4096) #success
      peerConnectPeerSocket.send(json.dumps(all_piece_indices).encode())
      peerConnectPeerSocket.recv(4096) #success
      #------------------------------------------------------------------
      
      #----------------- Truyền file theo all_piece_indices ----------------
      start_point = 0

      for i in all_piece_indices[start:end]:  # Sử dụng khoảng từ start đến end-1
        piece_data = peerConnectPeerSocket.recv(subFileSize)
        peerConnectPeerSocket.send(bytes("SUCCESS", "utf-8"))

        if not piece_data:
          print("KHONG CO DU LIEU")
          break
        piece_array[start_point] = piece_data
        start_point+=1

        
      """#----------------response for each piece which received-------------------
      current_position = start

      while current_position < end:
          # Nhận từng piece có kích thước subFileSize
          piece_data = peerConnectPeerSocket.recv(subFileSize)
          
          if not piece_data:
            break
          piece_array[current_position] = piece_data
          # Xác nhận đã nhận dữ liệu
          peerConnectPeerSocket.send(bytes("SUCCESS", "utf-8"))

          # Cập nhật vị trí hiện tại
          current_position += 1
      print(f"Tải thành công từ {start} tới {end}")"""       
      
    except ConnectionResetError as e:
       print(f"Lỗi kết nối: {e}")
    except Exception as e:
       print(f"Lỗi không xác định: {e}")
    finally:
      peerConnectPeerSocket.send(bytes("Cancel", "utf-8"))
      peerConnectPeerSocket.recv(4096)
      peerConnectPeerSocket.close()
     
  def sendStatusToTracker(self, file_path, piece_number):
    # Gửi trạng thái tới tracker (cần được định nghĩa cụ thể)
    peerConnectServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerConnectServerSocket.connect((self.serverHost, self.serverPort))
    peerConnectServerSocket.send(bytes("STATUS", "utf-8"))
    peerConnectServerSocket.recv(4096)  # success
    peerConnectServerSocket.send(bytes(file_path, "utf-8"))
    peerConnectServerSocket.send(bytes(str(piece_number), "utf-8"))
    peerConnectServerSocket.close()
     
#------------------------------End back end-----------------------------------------------
        
# Hàm xử lý tín hiệu Ctrl+C
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Closing application...')
    PEER_BEObject.stop()  # Gọi phương thức stop của PEER_BE
    sys.exit(0)
      
if __name__ == "__main__":
    peerHost= socket.gethostbyname_ex(socket.gethostname())[2][1]
    # print(peerHost)
    peerPort= 2000
    
    PEER_BEObject= PEER_BE(peerHost, peerPort)

    # Đăng ký tín hiệu Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    condition1= Thread(target= PEER_BEObject.listenServerOrPeers)
    condition1.daemon = True  # Đặt daemon flag để luồng tự kết thúc khi chương trình chính kết thúc
    condition1.start()
    
    PEER_FEObject = PEER_FE(peerHost, peerPort)
    PEER_FEObject.mainloop()
    