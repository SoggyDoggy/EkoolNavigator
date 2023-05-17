#from kivy.config import Config
#Config.set('graphics', 'resizable', False)
import time
import os.path
import kivy
import kivymd
from kivy.logger import Logger
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView

import multiprocessing
from kivy.properties import ObjectProperty, BooleanProperty

from kivy.lang.builder import Builder
# Logger.setLevel(10) #sets debugger on verbose

KV = '''


<Content>
	adaptive_height: True

	TwoLineIconListItem:
		text: "(050)-123-45-67"
		secondary_text: "Mobile"

		IconLeftWidget:
			icon: 'phone'



MyScreen:
	username: username
	password: password


	MDBoxLayout:
		cols: 2
		md_bg_color: app.theme_cls.bg_light
		MDCard:
			size_hint_x: None
			width: 275
			id: login_box
			md_bg_color: app.theme_cls.bg_dark
			pos_hint: {"center_x": 0.5}
			padding: 20
			spacing: 20
			orientation: 'vertical'
			MDLabel:
				id: login_label
				text: "Log in"
				font_style: 'H3'
				font_size: 40
				halign: 'center'
				size_hint_y: None
				height: self.texture_size[1]
				padding_y: 10
			MDTextField:
				id: username
				hint_text: "username"
				size_hint_x: None
				width: 200
				font_size: 18
				pos_hint: {"center_x": 0.5}
			MDTextField:
				id: password
				hint_text: "password"
				size_hint_x: None
				width: 200
				font_size: 18
				pos_hint: {"center_x": 0.5}
				password: True
			MDRaisedButton:
				id: submit
				text: "LOG IN"
				font_style: "Button"
				font_size: 12
				pos_hint: {"center_x": 0.5}
				on_release: 
					root.SubmitButtonEvent()
			MDRaisedButton:
				id: refresh
				text: "Refresh"
				font_style: "Button"
				font_size: 12
				pos_hint: {"center_x": 0.5}
				on_release: 
					root.RefreshButtonEvent()
			Widget:
				id: spacer
				
		MDCard:
			MDScrollView:
				MDGridLayout:
					id: box
					cols: 1
					size_hint: 1.0, 1.0
					adaptive_height: True
'''
class Content(MDBoxLayout):
	'''Custom content.'''

class MyScreen(MDScreen):
	username = ObjectProperty(None)
	password = ObjectProperty(None)


	def SubmitButtonEvent(self):
		multiprocessing.freeze_support()
		#multiprocessing.Process(target=Ekool.EventLoginCheck, args=(self,self.username.text, self.password.text,), name= "Event_CheckLogin", daemon=True).start()
		Ekool.EventLoginCheck(self,self.username.text, self.password.text)

	def RefreshButtonEvent(self):
		multiprocessing.freeze_support()
		comms1 = multiprocessing.Queue()
		#comms2 = multiprocessing.Queue()
		#multiprocessing.Process(target=Ekool.EventRefreshInfo,args=(self,self.username.text, self.password.text, comms1), name= "EventRefreshInfo", daemon=True).start()
		Ekool.EventRefreshInfo(self,self.username.text, self.password.text, comms1)
		
		GradesStorage:dict = comms1.get(block= True)
		
		for i in GradesStorage:
			self.ids.box.add_widget(
    			MDExpansionPanel(
					size_hint = (1.0, 1.0),
    	    		panel_cls=MDExpansionPanelTwoLine(
    	    	    	text=f"{i}",
    	    	    	secondary_text=f"{GradesStorage[i]}".replace("[","").replace("]","").replace("'","") if f"{GradesStorage[i]}".replace("[","").replace("]","").replace("'","") != "" else "No Grades",
    	    	    	tertiary_text=f"{Ekool.EventMassListAverage(Ekool, GradesStorage[i])}",
    				    )
    				)
					)

	
	

class Ekool(MDApp):
	GradeValueStorage = {}
	GradesStorage = {}
	ScanFrequency:timedelta = timedelta(minutes = 10) #
	chromedriverpath:Path = f"{Path(f'{os.path.dirname(os.path.abspath(__file__))}') / 'chromedriver.exe'}"

	#Set up Selenium instance with default arguments
	chrome_options = Options()
		#Remove argument '--headless' if debugging is enabled
	if Logger.level != 10:
		chrome_options.add_argument('--headless')
	else:
		Logger.debug(f"Ekool:" +" Logger level DEBUG! Chrome --headless launch switch automatically disabled")
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')
	chrome_options._binary_location = f"{Path(f'{os.path.dirname(os.path.abspath(__file__))}') /'GoogleChromePortable64'/ 'App' / 'Chrome-bin' / 'chrome.exe'}"
		#Define default Chrome Service object
	try:
		chrome_service = Service(chromedriverpath)
		ChromeBrowser = webdriver.Chrome(options=chrome_options, service=chrome_service)
		Logger.info("Ekool:" + " Login backend initialized")
	except selenium.common.exceptions.WebDriverException as e:
		Logger.fatal(f"No version of Google Chrome installed! Please install Google Chrome and run again... \n {e}")
	
	def build(self):
		self.theme_cls.theme_style = "Dark"
		self.theme_cls.primary_palette = "Purple"
		return Builder.load_string(KV)

	def EventRefreshInfo(self, username:str, password:str, queue:multiprocessing.Queue, ):
		if Ekool.Loggedin(Ekool):
			Ekool.RetrieveGrades(Ekool)
			queue.put(Ekool.GradesStorage)
			#queue2.put(Ekool.LessonAverage)
		else:
			Logger.info("Ekool:" +"Session expired! Attempting reconnect...")
			Ekool.Login(Ekool, username, password)


	def EventLoginCheck(self, username:str, password:str) -> bool:
		Ekool.Login(Ekool, username, password)
		


	def Loggedin(self) -> bool:
		"""Checks if the current session is logged in."""
		#Go to userlogin page, which redirects to main page if session is already logged in
		Logger.debug(f"Ekool:" +" logged_in() called")
		self.ChromeBrowser.get("https://login.ekool.eu/#/en")
		cookie = self.ChromeBrowser.get_cookie('logged_in')
		try:
			if cookie['domain'] == '.ekool.eu' and cookie['value'] == 'true':
				Logger.debug(f"Ekool:" +" logged_in returned True")
				return True
		except TypeError:
			Logger.debug(f"Ekool:" +" logged_in returned False ")
			return False
		else:
			return False

	def Login(self, User:str, Pass:str):
		self.Username:str = User
		self.Password:str = Pass
		"""Basic login onto the eKool site"""
		#usernamebox = WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-45")))
		#passwordbox = WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-48")))
			#Go to login page
		Logger.info(f"Ekool:" +" Attempting login...")
		self.ChromeBrowser.get("https://login.ekool.eu/#/en")
			#Check if user is logged in
		if not self.Loggedin(self=self):
				#if not enter account info to the login prompt
			try:
				WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-45"))).clear()
				WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-45"))).send_keys(self.Username)
				WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-48"))).clear()
				WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-48"))).send_keys(self.Password)
				WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.ID, "input-48"))).send_keys(Keys.RETURN)
			except (selenium.common.exceptions.TimeoutException):
				Logger.error(f"Ekool:" +" Attempt timed out!")
				raise LoginTimeoutError(pagesource=self.ChromeBrowser.page_source)
			#Check if login was successful and if not, wether it had errors
			time.sleep(3)
			if not self.Loggedin(self=self):
				Logger.warn(f"Ekool:" +" Exception occurred during login!")
				try:
					self.ChromeBrowser.find_element(By.CSS_SELECTOR, "#app > div > div > div > div.px-4.col-lg-6.col-12 > div > div > div:nth-child(2)")
				except (selenium.common.exceptions.NoSuchElementException):
					Logger.info(f"Ekool:" +" No errors during login")
					pass
				else:
					
					Logger.error(f"Ekool:" +" Login failed!")
					raise LoginError(pagesource=self.ChromeBrowser.page_source)
			else:
				Logger.info(f"Ekool:" +" Login successful!")
		else:
			Logger.debug(f"Ekool:" +" Login not needed. Skipping login...")

	def MainPage(self):
		"Navigates to the Main user view page"
		Logger.debug(f"Ekool:" +" Navigating to Main Page...")	
		#Check if session is logged in, if not raise NotLoggedInError() exception
		if self.Loggedin(self=self):
			self.ChromeBrowser.get("https://family.ekool.eu/index_et.html")
		else:
			Logger.error(f"Ekool:" +" Session not logged in!")
			raise NotLoggedInError()
		
	def RetrieveGrades(self, trimester:int = None):
		"""Retrive most recent grades from the gradepage. """
		"""Leaving 'trimester' empty will autoselect the ongoing trimester"""
		Logger.info(f"Ekool:" +" Retrieving grades for all lessons...")
			#Check if session is logged in, if not raise NotLoggedInError() exception
		if not self.Loggedin(Ekool):
			Logger.error(f"Ekool:" +" Session not logged in!")
			raise NotLoggedInError()
		#Go to main page and then navigate to gradesheet menu
		self.MainPage(self=Ekool)
		WebDriverWait(self.ChromeBrowser, 20).until(EC.visibility_of_element_located((By.ID, "dash_page_menu_reports"))).click()
		WebDriverWait(self.ChromeBrowser, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="appnav_scroll"]/ul/li[1]'))).click()
			#Switch to requested trimester's page
		WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#gradeReportContentDiv > div.tagfilter')))
		if (trimester == 1):
			Logger.debug(f"Ekool:" +" Selected trimester 1")
			WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#gradeReportContentDiv > div.tagfilter > dl > dd:nth-child(3)'))).click()
		elif (trimester == 2):
			Logger.debug(f"Ekool:" +" Selected trimester 2")
			WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#gradeReportContentDiv > div.tagfilter > dl > dd:nth-child(4)'))).click()
		elif (trimester == 3):
			Logger.debug(f"Ekool:" +" Selected trimester 3")
			WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#gradeReportContentDiv > div.tagfilter > dl > dd:nth-child(5)')))
		elif trimester == None:
			Logger.debug(f"Ekool:" +" No trimester provided. Selecting the ongoing trimester...")
			#Remove previous saved grades
			self.GradesStorage = {}
			Logger.debug(f"Ekool:" +" Grade storage cleared...")
			#Go through the elements onto the grade's table
		for i in range(1, len(self.ChromeBrowser.find_element(By.CSS_SELECTOR, '#gradeReportContentDiv > table.fulltable.gradesheet.velvet-table.gray-headers.kov > tbody').find_elements(By.TAG_NAME, 'tr'))):
			Logger.debug(f"Ekool:" +f" Ongoing grade retrival for tab {i}")
				#Select a column
			Column = WebDriverWait(self.ChromeBrowser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'#gradeReportContentDiv > table.fulltable.gradesheet.velvet-table.gray-headers.kov > tbody > tr:nth-child({i})')))
				#Get the lesson name from the tab header
			LessonName = Column.find_element(By.CLASS_NAME, "name").text
				#define a temporary storage to append only grades, not tardy and absence indicators
			tempListStorage = []
			for i in Column.find_elements(By.CLASS_NAME, "assessmentGrade"):
				tempListStorage.append(f"{i.text}".replace(" ", "").replace("*", ""))
			for i in Column.find_elements(By.CLASS_NAME, "lessonGrade"):
				tempListStorage.append(f"{i.text}".replace(" ", "").replace("*", ""))
				#Store gathered grades in a intance wide storage variable
			self.GradesStorage[f'{LessonName}'] = tempListStorage
				#Save the last time that the grades were checked
		Logger.info(f"Ekool:" +" Grades retrieved")

	def LessonAverage(self, lesson:str) -> float:
		"""Returns requested lesson's average"""
		"""percentGrades=[]
		for g in self.GradesStorage[lesson]:
			if(g=="IGNORE"):
				continue
			else:
				tmp:str=self.GradeEquivalent(g)
				if(tmp=="IGNORE"):
					continue
				else:
					percentGrades.append(tmp)"""
			#Take the grades and convert them into their equivalents in percent, make sure that grades marked "IGNORE" are left out of the equation
		Logger.debug(f"Ekool:" +" Calculating lesson average for {lesson}")
		percentGrades=[self.GradeEquivalent(g) for g in self.GradesStorage[lesson] if(g!="IGNORE")]
		percentGrades=[x for x in percentGrades if(x!="IGNORE")]
			#return the lesson grade average percent
		return round(sum(percentGrades)/len(percentGrades), 2)
	
	def EventMassListAverage(self,list:list, trimester:int = None):
		x = self.ListAverage(self, list, trimester)
		return x if (isinstance(x, str)) else f"Lesson average percent is: {int(x)}%"

	def ListAverage(self, list:list, trimester:int = None):
		"""Returns requested lesson's average"""
			#make a quick swap from argument variable to a local one to avoid any unstability
		self.SetGradeValue(self,"A", 1.00)
		self.SetGradeValue(self,"B", 0.90)
		self.SetGradeValue(self,"C", 0.75)
		self.SetGradeValue(self,"D", 0.60)
		self.SetGradeValue(self,"E", 0.50)
		self.SetGradeValue(self,"F", 0.00)
		self.SetGradeValue(self,"AR", "IGNORE")
		self.SetGradeValue(self,"0", "IGNORE")
		self.SetGradeValue(self,"MA", "IGNORE")
			#A representation of the more complex two-liner for easier debugging
		"""percentGrades=[]
		for g in self.GradesStorage[lesson]:
			if(g=="IGNORE"):
				continue
			else:
				tmp:str=self.GradeEquivalent(g)
				if(tmp=="IGNORE"):
					continue
				else:
					percentGrades.append(tmp)"""
			#Take the grades and convert them into their equivalents in percent, make sure that grades marked "IGNORE" are left out of the equation
		Logger.debug(f"Ekool:" +" Calculating lesson average for list")
		percentGrades=[self.GradeEquivalent(self=self,Grade=g) for g in list if(g!="IGNORE")]
		percentGrades=[x for x in percentGrades if(x!="IGNORE")]
			#return the lesson grade average percent
		return round(sum(percentGrades)/len(percentGrades)*100, 2) if (len(percentGrades) > 0) else "Not enough info to calculate lesson average"
	
	def SetGradeValue(self, Grade:str, value):
		"""Defines a grade value.
		The value passing format can only be float (0.12 for 12 percent, 0.50 for 50 percent, 0.90 for 90 percent) or string 'IGNORE' to ignore to set the grade as non valuable grade. 
		Raises FormatError() if the fed format was wrong."""
			#Check if the 'value' argument is a string
		if isinstance(value, str):
				#if it's a string, make sure if the value is "IGNORE", and if it is, set the grade to be ignored
			if value.upper() == "IGNORE":
				newvalue = "IGNORE"
			else:
				raise FormatError(Grade)
			#Set the grade value in instance grade value definition storage variable
			self.GradeValueStorage[f"{Grade}"] = newvalue
			#Check if the 'value' argument is a float instead
		elif isinstance(value, float):
				#If its a float, make sure that is in the bounds of 1 to 100% in float
			if value > 1.0 or value < 0:
				FormatError(Grade)
			else:
				newvalue = value
				#Set the grade value in instance grade value definition storage variable
			self.GradeValueStorage[f"{Grade}"] = newvalue
		else: 
			raise TypeError(Grade)
		Logger.debug(f' New grade value "{newvalue}" set for grade "{Grade}"')

	def GradeEquivalent(self, Grade:str):
		"""Returns the percent equivalent of passed grade. Raises exception GradeValueNotDefined() if the value of such grade hasn't been defined"""
			#If such grade definition exists, return the value of it		
		try:
			Logger.debug(f' GradeEquivalent() called for Grade "{Grade}"')
			equivalent = self.GradeValueStorage[f"{Grade}"]
		except KeyError:
			Logger.error(f'Grade value not defined for grade "{Grade}"')
			raise GradeValueNotDefined(Grade)
		else:
			return equivalent
	
	
class LoginError(Exception):
	"""Raised on any error in the Login() process. 
	Most of the time, the login credentials were wrong...
	"""
	"""Provides a pagesource upon raising, useful for finding the problem on login"""

	def __init__(self, pagesource):
		self.pagesource = pagesource
		self.message = f"An Exception occurred on login. Page source: {pagesource}"
		super().__init__(self.message)

class NotLoggedInError(Exception):
	"""Raised on any occurrence where the client has't logged in with the current instance or has been automatically logged out due to session timeout
	"""
	def __init__(self):
		self.message = f"Client is not logged on"
		super().__init__(self.message)

class LoginTimeoutError(Exception):
	"""Raised on any occurrence where the client has't logged in with the current instance or has been automatically logged out due to session timeout
	"""
	def __init__(self, pagesource):
		self.message = f"Login prompt timeout exceeded. Page source for debugging: {pagesource}"
		super().__init__(self.message)
	
class GradeValueNotDefined(Exception):
	"""Raised if the requested grade has no defined value"""
	def __init__(self, rgrade:str):
		self.message = f"Requested grade '{rgrade}' has no value defined for it."
		super().__init__(self.message)

class FormatError(Exception):
	"""Raised if the format in which the argument was passed, was wrong."""
	def __init__(self, rgrade:str):
		self.message = f"Value in wrong format."
		super().__init__(self.message)

if __name__ == '__main__':
	Ekool().run()
	Ekool.ChromeBrowser.close()