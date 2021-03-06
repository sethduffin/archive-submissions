# Archive Canvas Student Submissons

## Overview
This small script uses Canvas assignment links to save student submissions as PDF's while keeping them organized in a Canvas like folder structure! This project requires Python 3 and Selenium to gather submissions, make sure both are correctly installed beforehand using the steps below.

## Installing Selenium
1. Install Chrome Driver:
	1. Go to: https://sites.google.com/a/chromium.org/chromedriver/home.
	2. Download chrome driver.
	3. Unzip chromedriver.
	4. Move file to usr/local/bin. 
    ```
    mv /Downloads/chromedriver /usr/local/bin
    ```
2. Install Brew (or make sure you have brew installed).
	1. Go to: https://brew.sh
3. Install Python 3. 
	```
	brew install python3
	```
4. Install Selenium.
	```
	pip3 install selenium
	```

Note: On the first launch it will ask you to verify chromedriver. To do this, go to System Preferences > Security & Privacy > General > chomedriver: Allow anyways.

## Archiving Submissions
First, download or clone this repository

Paste assignment links inside "assignments.txt".  
Execute "run" to archive student submissons!

	./run 
The first time you execute the script, it will have you enter your Canvas credentials.
