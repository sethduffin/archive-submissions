from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import extensions
import os,sys,json,string,time,signal
from getpass import getpass

iw = 3 # Default implicit wait

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
code_dir = "%s/code/" % (dir_path)
temp_path = "%s/code/temp/" % (dir_path)
local_path = code_dir+'local.py'

local_template = '''username = ""					# Canvas username that has access to all assginment links
password = ""					# Canvas password to username
output_folder = "submissions"	# Folder name to save archived submissons to
clear_output_folder = True 		# Removes all files in output folder when script is executed 
'''

print_style = '''
<style type="text/css" media="print"> 
	@page {
		margin: 10px;
	} 
	@media print {
		.speedgrader-stats {
		    display: flex;
		    flex-direction: column;
		    align-items: center;
		    justify-content: center;
		    padding: 1.6rem;
		    background-color: #f5f5f5 !important;
		    border: #d6d6d6;
		    border-style: solid;
		    border-width: 1px;
		    border-radius: .3rem;
		    margin-bottom: 1rem;
		    text-align: center;
		    height: 60px;
		}
		.speedgrader-stats span {
		    margin-bottom: .4rem;
		    font-size: 10px;
		    color: #595959;
		}
		.speedgrader-stats div {
		    font-size: 15px;
		    color: #333;
		}
		.u-fifth {
		    width: 20%!important;
		}
		.c-row {
		    display: flex;
		    align-items: center;
		}
		.c-label, .c-text {
		    font-family: Lato,sans-serif;
		    font-weight: 400;
		    color: #333;
		    margin-top: 40px;
		}
		.c-column {
    		padding: .1rem 1rem .1rem 1rem;
		}
		.speedgrader-actions {
		    display: none;
		}
	} 
</style>
'''.replace('\n', ' ').replace('\r', '')


# Make sure local file is created
if not 'local.py' in os.listdir(code_dir):
	with open(local_path, "w") as file:
		file.writelines(local_template)

import local

output_path = "%s/%s/" % (dir_path,local.output_folder)

settings = {
   "recentDestinations": [{
        "id": "Save as PDF",
        "origin": "local",
        "account": "",
    }],
    "selectedDestinationId": "Save as PDF",
    "version": 2
}
prefs = {
	'printing.print_preview_sticky_settings.appState': json.dumps(settings),
	'savefile.default_directory': temp_path,
	'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    "printing.default_destination_selection_rules": {
        "kind": "local",
        "namePattern": "Save as PDF",
    },
}
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', prefs)
options.add_argument('--kiosk-printing')

driver = None
action = None

def signal_handler(sig, frame):
    print("")
    print("Manual Exit")
    if driver:
    	driver.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def error(e="Unkown",line=False):
	if line:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("%s (%s %s)" % (e,fname,exc_tb.tb_lineno))
	else:
		print(e)
	if driver:
		driver.quit()
	sys.exit(0)

def start_driver():
	global driver,action
	driver = webdriver.Chrome(options=options)
	action = ActionChains(driver)
	driver.implicitly_wait(iw)

	extensions.set_driver(driver,action)

# Remove path unsported characters
def path_ready(text,slash=False):
	allowed = [
		string.ascii_lowercase,
		string.ascii_uppercase,
		['0','1','2','3','4','5','6','7','8','9'],
		[' ','-','_']
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
new_credentials = False
successfull_archives = 0

class Assignment:
	def __init__(self,url,assignment_id,source):
		self.url = url
		self.assignment_id = assignment_id
		self.source = source

def save_credentials():
	local_file = None
	with open(local_path, "r") as file:
		local_file = file.readlines()
	local_file[0] = ('username = "%s"			# Canvas username that has access to all assginment links\n' % (local.username))
	local_file[1] = ('password = "%s"			# Canvas password to username\n' % (local.password))
	with open(local_path, "w") as file:
		file.truncate()
		file.writelines(local_file)

def check():
	global new_credentials
	with open("assignments.txt","r") as file:
		lines = file.read().splitlines()
		if len(lines) == 0:
			error('No assignment urls provided in "assignment.txt"',False)
	if not local.username or not local.password:
		print("\033[4m"+"Set Canvas Credentials"+"\033[0m")
		local.username = input("Username: ")
		local.password = getpass("Password: ")
		os.system('clear')
		new_credentials = True
	if not local.username or not local.password:
		error("Invalid credentials")
	
def import_urls():
	try:
		with open("assignments.txt","r") as file:
			lines = file.read().splitlines()
			for i,line in enumerate(lines):
				assignment_id = line.split("assignments/")[1]
				source = "Line %s: %s" % (i+1,line)
				url = "%sgradebook/speed_grader?assignment_id=%s" % (line.split("assignments/")[0],assignment_id)
				assignments.append(Assignment(url,assignment_id,source))
	except Exception as e:
		error(e)

def login():
	driver.get(assignments[0].url)
	driver.implicitly_wait(0.5)
	if len(driver.find("name","pseudonym_session[unique_id]",True)) > 0:
		driver.find("name","pseudonym_session[unique_id]").send(local.username)
		driver.find("name","pseudonym_session[password]").send(local.password)
		driver.find("class","Button--login")[0].send_keys(Keys.RETURN)
	elif len(driver.find("name","UserName",True)) > 0:
		driver.find("name","UserName").send_keys(local.username)
		driver.find("name","Password").send_keys(local.password)
		time.sleep(0.3)
		driver.find("id","submitButton").click()
	else:
		error("Unrecognized Canvas, unable to login")

	if len(driver.find("text+","Invalid username or password",True)) > 0 or len(driver.find("id","errorText",True)) > 0:
		local.username = ""
		local.password = ""
		save_credentials()
		error("Unable to login with current Canvas credentials. \nRun script again to set new credentials.")
	elif new_credentials:
		save_credentials()
	driver.implicitly_wait(iw)

def save_pdfs():
	try:
		# Clear output folder
		if local.clear_output_folder:
			if "submissions" in os.listdir(dir_path):
				os.system("rm -r %s" % (output_path))
			os.system("mkdir %s" % (output_path))

		if "temp" in os.listdir(code_dir):
			os.system("rm -r %s" % (temp_path))
		os.system("mkdir %s" % (temp_path))

		for assignment in assignments:

			# Get assignment information
			driver.get(assignment.url)

			if len(driver.find("class","assignmentDetails__Info",True)) > 0:

				try:

					assignment.course_name = driver.find("class","assignmentDetails__Info").find("tag","a").wait_until("element.text != ''").text
					assignment.name = driver.find("class","assignmentDetails__Title").wait_until("element.text != ''").text
					assignment.student_count = int(driver.find("id","x_of_x_students_frd").text.split("/")[1])

					# Create file structure
					course_path = output_path+path_ready(assignment.course_name,True)
					assignment.path = course_path+path_ready(assignment.name,True)

					if not assignment.course_name in os.listdir(output_path):
						os.system('mkdir "%s"' % (course_path))
					os.system('mkdir "%s"' % (assignment.path))
				
					# Save each student pdf
					for i in range(assignment.student_count):
						try:
							student_name = driver.find("id","students_selectmenu-button").find("class","ui-selectmenu-item-header").text
							
							driver.implicitly_wait(0.5)

							if len(driver.find("id","speedgrader_iframe",True)) > 0:
								driver.switch_to.frame(driver.find("id","speedgrader_iframe",wait=5))
								new_path = assignment.path+path_ready(student_name)+'.pdf'
								driver.find("class","c-grading",wait=8).wait_until("element.clickable()",8).click()
							else:
								new_path = assignment.path+path_ready(student_name)+' (No Submission).pdf'

							driver.implicitly_wait(iw)

							driver.execute_script('document.getElementsByTagName("head")[0].insertAdjacentHTML("afterbegin",\'%s\')' % (print_style))
							time.sleep(0.1)
							driver.execute_script("print()")
							time.sleep(0.1)

							old_path = temp_path+os.listdir(temp_path)[0]

							os.system('mv "%s" "%s" ' % (old_path,new_path))
							global successfull_archives
							successfull_archives += 1
						except Exception as e:
							#error(e,True)
							print("[Error] Unable to archive student (%s) submission for assignment: \n        %s)" % (i+1,assignment.source))

						driver.switch_to.default_content()
						driver.find("id","next-student-button").click()

				except:
					print("[Error] Unable to archive assignment submissions for: \n        %s" % (assignment.source))
			else:
				print("[Invalid URL] "+assignment.source)

		os.system("rm -r %s" % (temp_path))

	except Exception as e:
		error(e)

def done():
	if successfull_archives > 0:
		print("Successfully archived %s student submissions!" % (successfull_archives))

def run():
	check()
	start_driver()
	import_urls()
	login()
	save_pdfs()
	done()
	
try:
	run()
except Exception as e:
	error(e)
else:
	driver.quit()
