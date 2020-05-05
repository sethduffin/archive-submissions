from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import extensions,local
import os,sys,json,string,time,signal

dir_path = os.path.dirname(os.path.realpath(__file__))

settings = {
    "appState": {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local"
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }  
}
prefs = {'printing.print_preview_sticky_settings': json.dumps(settings)}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')

driver = webdriver.Chrome(options=chrome_options)
action = ActionChains(driver)
driver.implicitly_wait(3)

extensions.set_driver(driver,action)

def signal_handler(sig, frame):
    error("Manual Exit",False)

signal.signal(signal.SIGINT, signal_handler)

def error(e="Unkown",line=True):
	if line:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("Error: %s (%s %s)" % (e,fname,exc_tb.tb_lineno))
	else:
		print("Error: %s" % (e))
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
	if slash
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
		output_path = "%s/%s/" % (dir_path,local.output_folder)
		
		# Clear output folder
		os.system("rm -rfv %s/*" % (output_path))

		for assignment in assignments:

			# Get assignment information
			driver.get(assignment.url)
			assignment.course_name = driver.find("class","assignmentDetails__Info").find("tag","a").wait_until("element.text != ''").text
			assignment.name = driver.find("class","assignmentDetails__Title").wait_until("element.text != ''").text
			print(driver.find("id","x_of_x_students_frd").text)
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
				driver.find("class","c-grading",wait=5).click()
				time.sleep(0.1)
				driver.execute_script("print()")
				driver.send_keys(Keys.ENTER)
				input("student_name")

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