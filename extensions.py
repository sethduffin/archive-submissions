# Selenium for Python extentions by Seth Duffin
# Version: 2.0
# Updated: 5/5/2020

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import sys


driver = None
action = None

def set_driver(driver_value,action_value=None):
    global driver,action
    driver = driver_value
    action = action_value


def find(self,method,selector,force_list=False,**kwargs):
    content = self
    elements = []
    if method == 'class':
        elements = content.find_elements_by_class_name(selector)
    elif method == 'text':
        elements = content.find_elements_by_link_text(selector)
    elif method == 'text*':
        elements = content.find_elements_by_partial_link_text(selector)
    elif method == 'text+':
        elements = content.find_elements_by_xpath('//*[text()[contains(., "'+selector+'")]]')
    elif method == 'text~':
        elements = content.find_elements_by_xpath('.//*[text()[contains(., "'+selector+'")]]')
    elif method == 'tag':
        elements = content.find_elements_by_tag_name(selector)
    elif method == 'name':
        elements = content.find_elements_by_name(selector)
    elif method == 'id':
        elements = content.find_elements_by_id(selector)
    elif method == 'xpath':
        elements = content.find_elements_by_xpath(selector)
    else:
        elements = content.find_elements_by_xpath(".//*[@"+method+"='"+selector+"']")

    if len(elements) == 0:
        if force_list:
            return elements
        else:
            if "wait" in kwargs:
                time = 0
                while time <= kwargs["wait"]:
                    try:
                        return content.find(method,selector)
                    except Exception as e:
                        pass
                    time += 1
                else:
                    raise Exception("No element matching criteria: %s = '%s'" % (method,selector)) 
                    return None
            else:
                raise Exception("No element matching criteria: %s = '%s'" % (method,selector)) 
                return None
    elif len(elements) == 1:
        if force_list:
            return elements
        else:
            return elements[0]
    else:
        return elements

def strong_click(self,method,selector):
    try:
        if method == 'text':
            xpath = ".//*[text()='"+selector+"']"
        if method == 'xpath':
            xpath = selector
        else:
            xpath = ".//*[@"+method+"='"+selector+"']"
        if self.__class__.__name__ == 'WebDriver':
            driver.execute_script("document.evaluate(\""+xpath+"\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
        else:    
            driver.execute_script("document.evaluate(\""+xpath+"\", arguments[0], null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()",self)
    except Exception as e:
        print(e)
        raise Exception('Error while strong_click "%s" = "%s"' % (method,selector))

def flag(self,color='lightgreen'):
    driver.execute_script("arguments[0].style += 'background: "+color+";'", self) 
    return self

def send(self,text):
    self.clear()
    self.send_keys(text)

def delete(self):
    driver.execute_script('arguments[0].parentNode.removeChild(arguments[0]);', self)

def up(self,num=1):
    elem = self
    for i in range(num):
        elem = elem.find_element_by_xpath('..')
    return elem

def wait_until(self,condition,time=5):
    element = self
    wait = 0
    while wait < time:
        try:
            if eval(condition,None,locals()):
                return element
        except:
            pass
        sleep(.1)
        wait += 0.1
    else:
        error('Couldn\'t find element matching condition "%s"' % (num))
    
exts = ['find','flag','send','up','delete','strong_click',"wait_until"]

for ext in exts:
    exec('WebDriver.'+ext+' = '+ext)
    exec('WebElement.'+ext+' = '+ext)

# -------- Action Chains -------

def do(self):
    self.perform()
    action.reset_actions()

ActionChains.do = do


    
