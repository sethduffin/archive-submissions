from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import extensions,local
import os,sys,json,string,time,signal

implicit_wait = 3

dir_path = os.path.dirname(os.path.realpath(__file__))
output_path = "%s/%s/" % (dir_path,local.output_folder)
temp_path = "%s/temp/" % (dir_path)

settings = {
    "appState": {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local"
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isHeaderFooterEnabled": False
    }  
}
prefs = {
	'printing.print_preview_sticky_settings': json.dumps(settings),
	'savefile.default_directory': temp_path,
	#'C:%s' % (temp_path),
	'download.directory_upgrade': True
}
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', prefs)
options.add_argument('--kiosk-printing')

driver = webdriver.Chrome(options=options)
action = ActionChains(driver)
driver.implicitly_wait(implicit_wait)

extensions.set_driver(driver,action)

def signal_handler(sig, frame):
    error("Manual Exit",False,False)

signal.signal(signal.SIGINT, signal_handler)

def error(e="Unkown",line=True,pause=True):
	if line:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("Error: %s (%s %s)" % (e,fname,exc_tb.tb_lineno))
	else:
		print("Error: %s" % (e))
	if pause:
		input(" -- Quit -- ")
	driver.quit()
	quit()

# Remove path unsported characters
def path_ready(text,slash=False):
	allowed = [
		string.ascii_lowercase,
		string.ascii_uppercase,
		range(10),
		[" ","-","_"]
	]
	fixed = ""
	for char in text:
		clean = True
		for a in allowed:
			if char in a:
				fixed += char
				break	
		else:
			fixed += "_"
	if slash:
		fixed +="/"
	return fixed

courses = []
assignments = []

class Assignment:
	def __init__(self,url,assignment_id):
		self.url = url
		self.assignment_id = assignment_id

def import_urls():
	try:
		with open("assignments.txt","r") as file:
			lines = file.read().splitlines()
			if len(lines) == 0:
				error("No assignment urls provided",False)
			for line in lines:
				assignment_id = line.split("assignments/")[1]
				url = "%sgradebook/speed_grader?assignment_id=%s" % (line.split("assignments/")[0],assignment_id)
				assignments.append(Assignment(url,assignment_id))
	except Exception as e:
		error(e)

def login():
	try:
		driver.get(assignments[0].url)
		driver.find("name","pseudonym_session[unique_id]").send(local.username)
		driver.find("name","pseudonym_session[password]").send(local.password)
		driver.find("class","Button--login")[0].send_keys(Keys.RETURN)
	except Exception as e:
		error(e)

def save_pdfs():
	try:
		# Clear output folder
		os.system("rm -r %s/*" % (output_path))

		if "temp" in os.listdir(dir_path):
			os.system("rm -r %s/*" % (temp_path))
		os.system("mkdir %s" % (temp_path))

		for assignment in assignments:

			# Get assignment information
			driver.get(assignment.url)
			assignment.course_name = driver.find("class","assignmentDetails__Info").find("tag","a").wait_until("element.text != ''").text
			assignment.name = driver.find("class","assignmentDetails__Title").wait_until("element.text != ''").text
			assignment.student_count = int(driver.find("id","x_of_x_students_frd").text.split("/")[1])

			# Create file structure
			course_path = output_path+path_ready(assignment.course_name,True)
			assignment.path = course_path+path_ready(assignment.name,True)

			if not assignment.course_name in courses:
				os.system('mkdir "%s"' % (course_path))
			os.system('mkdir "%s"' % (assignment.path))
		
			# Save each student pdf
			for i in range(assignment.student_count):
				student_name = driver.find("id","students_selectmenu-button").find("class","ui-selectmenu-item-header").text
				
				driver.implicitly_wait(0.5)

				if len(driver.find("id","speedgrader_iframe",True)) > 0:
					driver.switch_to.frame(driver.find("id","speedgrader_iframe",wait=5))
					new_path = assignment.path+path_ready(student_name)+'.pdf'
					driver.find("class","c-grading",wait=5).wait_until("element.clickable()").click()
				else:
					new_path = assignment.path+path_ready(student_name)+' (Not Submitted).pdf'

				driver.implicitly_wait(implicit_wait)

				driver.execute_script('document.getElementsByTagName("head")[0].insertAdjacentHTML("afterbegin",\'<style type="text/css" media="print"> @page {margin: 0;} </style>\')')
				time.sleep(0.1)
				driver.execute_script("print()")
				time.sleep(0.1)

				old_path = temp_path+os.listdir(temp_path)[0]

				os.system('mv "%s" "%s" ' % (old_path,new_path))
				
				driver.switch_to.default_content()
				driver.find("id","next-student-button").click()

		os.system("rm -r %s" % (temp_path))

	except Exception as e:
		error(e)

def run():
	import_urls()
	login()
	save_pdfs()
	
try:
	run()
except Exception as e:
	error(e)
else:
	driver.quit()