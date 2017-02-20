# -*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from pprint import pprint
from time import sleep
import sys
from urllib import urlencode
import traceback
import json
import argparse
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

reload(sys)
sys.setdefaultencoding('utf8')

class LinkedinProfiles():
    def __init__(self, company):
        self.base_url = "https://www.linkedin.com"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.employees = []
        self.company = company
        self.scompany = company.replace(" ", "_")
        if not os.path.isdir(self.scompany):
            os.mkdir(self.scompany)

    def init_driver(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.username = raw_input('linkedin username:')
        self.password = raw_input('linkedin password:')

    # This function will open the browser, login to linkedin, then save all search results for the company
    # specified in the company variable
    def get_linkedin_profiles(self):
        self.init_driver()
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_id("login-email").clear()
        driver.find_element_by_id("login-email").send_keys(self.username)
        driver.find_element_by_id("login-password").clear()
        driver.find_element_by_id("login-password").send_keys(self.password)
        driver.find_element_by_id("login-submit").click()

        # wait until the class appears
        driver.implicitly_wait(5)

        #a = driver.find_elements_by_xpath(//*[contains(@id, 'a11y-ember')]""")
        targetElement = driver.find_element_by_xpath("//input[contains(@id, \"a11y-ember\")]").clear()
        targetElement = driver.find_element_by_xpath("//input[contains(@id, \"a11y-ember\")]").send_keys(self.company)  
        targetElement
        # driver.find_element_by_name("submit").click()
        #driver.find_element_by_class_name('ember-text-field ember-view').clear()
        #driver.find_element_by_class_name('ember-text-field ember-view').send_keys(self.company)


        # Create the search URL
        search = "https://www.linkedin.com/ta/federator"
        params = {'orig': 'GLHD',
                  'verticalSelector': 'all',
                  'query': self.company}
        # search = "https://www.linkedin.com/ta/federator?orig=GLHD&verticalSelector=all&query={}&tracking=true&refTarId=1468332198550"
        search_url = "{}?{}".format(search, urlencode(params))
        driver.get(search_url)
        # Parse the results from our search
        soup = BeautifulSoup(driver.page_source)
        j = json.loads(soup.find("pre").text)
        # Results look like: {"meta":{"tarId":"1468332203875"},"resultList":[{"sourceID":"autocomplete","displayName":"cottingham butler","subLine":"","rank":0,"id":"1","url":"","headLine":"cottingham butler"},{"sourceID":"company","displayName":"Cottingham &amp; Butler","imageUrl":"https://media.licdn.com/mpr/mpr/shrink_100_100/p/5/000/226/18c/395b088.png","subLine":"Insurance; 501-1000 employees","rank":1,"id":"54611","url":"https://www.linkedin.com/company/54611","headLine":"Cottingham &amp; Butler"},{"sourceID":"group","displayName":"Cottingham &amp; Butler Transportation Summit","imageUrl":"https://media.licdn.com/mpr/mpr/shrink_100_100/p/6/005/049/120/046d523.png","subLine":"","rank":2,"id":"6641194","url":"https://www.linkedin.com/groups?gid=6641194&mostPopular=","headLine":"Cottingham &amp; Butler Transportation Summit"},{"sourceID":"mynetwork","displayName":"Cottingham Butler","subLine":"Sales Executive at Cottingham and Butler","rank":3,"id":"471545431","url":"https://www.linkedin.com/profile/view?id=AAkAABwbNlcBBLH-e2KL__V9-v0Z3h6Aiflxec0&authType=NAME_SEARCH&authToken=mhR4&locale=en_US","headLine":"Cottingham Butler","misc":{"degree":""}}]}
        comp_id = None
        for item in j['resultList']:
            # Select the first company in the results list
            if item['sourceID'] == 'company':
                comp_id = item['id']
                print "Found company ID"
                break
        if comp_id:
            # Create the URL for getting the company's employee page
            employees_page = "https://www.linkedin.com/vsearch/p?f_CC={}&trk=rr_connectedness".format(comp_id)
        else:
            print "Couldn't find a company link with that name! Quitting..."
            quit()
        driver.get(employees_page)
        # driver.find_element_by_xpath('//*[@id="results"]/li[1]/div/h3/a').click()
        # driver.find_element_by_link_text("See all").click()
        previous = ""
        for i in range(0, 99):
            print "Processing Page: %d" % i

            #driver.find_elements_by_xpath('//div[contains(@class, \"search-is-loading\")]')
            while driver.find_elements_by_xpath('//div[contains(@class, \"search-is-loading\")]'):
                sleep(50.0/1000.0)

            f = open("{}/{}{}_source.html".format(self.scompany, self.scompany, i), 'wb')
            source = driver.page_source
            # The source will be different every time even if it is the same page
            # Need to figure out a way to check if the employees on the 'next' page are actually different
            # or if it's just loading the same page over and over again
            if previous == source:
                break
            previous = source
            encoded = source.encode('utf-8').strip()
            f.write(source)
            f.close()
            # self.parse_source(source)
            # TODO: if there is no "Next" button, end the loop
            try:
                driver.find_element_by_class_name("next").click()


            except Exception, e:
                # traceback.print_exc(e)
                print "Pulled {} pages".format(i+1)
                break
        # driver.find_element_by_link_text("Next >").click()
        # driver.find_element_by_link_text("Next >").click()

class ParseProfiles():
    def __init__(self, suffix, prefix, ignore, company):
        self.employees = []
        self.prefix = prefix
        self.suffix = suffix
        self.ignore = ignore
        self.company = company.replace(" ", "_")

    def parse_source(self, path):
        try:
            source = open(path)
            soup = BeautifulSoup(source, 'html.parser')
            results = soup.find('ul','results-list')


            #print results
            
            try:
            	links = results.find_all("li", {"class": "search-result search-entity search-result--person search-result--blue-hover ember-view"})
            except:
            	pass
            	links = []

            for person in links:
                link = person.find('img', {"class": "lazy-image loaded"})
                ind = {'name': "Not Found",
                       'picture': "Not Found",
                       'email': "Not Found",
                       'job': "Not Found"}
                img = ""
                if link:
                    # img = link.img
                    img = link
                    #print img
                if img:
                    # ind['picture'] = img.get('src')
                    ind['picture'] = img
                else:
                	ind['picture'] = ""
                #name = person.find('a', {"class": "title main-headline"})
                name = person.find('span',{"class": "name"})
                if name:
                    name = name.text#name.text
                    ind['name'] = name
                job = person.find('p', {"class": "search-result__snippets mt2 Sans-13px-black-55% ember-view"})
                if not job:
                    job = person.find('p', {"class": "subline-level-1 Sans-15px-black-85% search-result__truncate"})
                    #print "Description"
                    #print job.text
                    jobval = job.text
                else:
                	jobval = job.text.split("\n")[1]
                if job:
                    ind['job'] = jobval
                    #print "Job text"
                    #print job.text
                # print ind['name']
                self.employees.append(ind)
        except Exception, e:
            print "Encountered error parsing file: {}".format(path)
            traceback.print_exc(e)

    def print_employees(self):
        # pprint(self.employees)
        body = ""
        csv = []
        css = """<style>
		#employees {
		    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
		    border-collapse: collapse;
		    width: 100%;
		}

		#employees td, #employees th {
		    border: 1px solid #ddd;
		    padding: 8px;
		}

		#employees tr:nth-child(even){background-color: #f2f2f2;}

		#employees tr:hover {background-color: #ddd;}

		#employees th {
		    padding-top: 12px;
		    padding-bottom: 12px;
		    text-align: left;
		    background-color: #4CAF50;
		    color: white;
		}
		</style>

		"""

        header = """<center><table id=\"employees\">          
                 <tr>
                 <th>Name</th>
                 <th>Possible Email:</th>
                 <th>Job</th>
                 </tr>
                 """
        for emp in self.employees:
        	# Get rid of stupid people with brackets
            #if '(' in emp['name']:
            #    if ')' in emp['name']:
            #        continue
            if ',' in emp['name']:
                print "user's name contains a comma, might not display properly: {}".format(emp['name'])
            name = emp['name'].split(',')[0]
            emp['name'] = name

            parts = name.split()
            if emp['name'] != 'LinkedIn Member':
                if len(parts) == 2:
                    fname = parts[0]
                    mname = '?'
                    lname = parts[1]
                elif len(parts) == 3:
                    fname = parts[0]
                    mname = parts[1]
                    lname = parts[2]
                else:
                	fname = parts[0]
                	lname = parts[1]
                fname = re.sub('[^A-Za-z]+', '', fname)
                emp['fname'] = fname
                mname = re.sub('[^A-Za-z]+', '', mname)
                lname = re.sub('[^A-Za-z]+', '', lname)
                emp['lname'] = lname
                if self.prefix == 'full':
                    user = '{}{}{}'.format(fname, mname, lname)
                if self.prefix == 'firstlast':
                    user = '{}{}'.format(fname, lname)
                if self.prefix == 'firstmlast':
                    user = '{}{}{}'.format(fname, mname[0], lname)
                if self.prefix == 'flast':
                    user = '{}{}'.format(fname[0], lname)
                if self.prefix == 'first.last':
                    user = '{}.{}'.format(fname, lname)
                if self.prefix == 'fmlast':
                    user = '{}{}{}'.format(fname[0], mname[0], lname)

                emp['email'] = '{}@{}'.format(user, self.suffix)

            # Only add the employee if we're not ignoring it
            if not self.ignore or (self.ignore and emp['name'] != 'LinkedIn Member'):
                body += "<tr>" \
                        "<td>{name}</td>" \
                        "<td>{email}</td>" \
                        "<td>{job}</td>" \
                        "<a>".format(**emp)
                csv.append('"{fname}","{lname}","{name}","{email}","{job}"'.format(**emp))
            else:
                print "ignoring user: {} - {}".format(emp['name'], emp['job'])
        foot = "</table></center>"
        f = open('{}/employees.html'.format(self.company), 'wb')
        f.write(css)
        f.write(header)
        f.write(body)
        f.write(foot)
        f.close()
        f = open('{}/employees.csv'.format(self.company), 'wb')
        f.writelines('\n'.join(csv))
        f.close()


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

def main():
    parser = argparse.ArgumentParser(description='Scrape Linkedin profiles for a specified company', formatter_class=SmartFormatter)
    parser.add_argument('--company', help='The name of the company on Linkedin', required=True)
    parser.add_argument('--email_suffix', help='The company email suffix ex: user@<email_suffix>', required=True)
    parser.add_argument('--email_prefix', choices=['firstlast', 'firstmlast','flast', 'fmlast', 'full', 'first.last'],
                        help='R|The email prefix format ex: <email_prefix>@company.com\n'
                             ' full   - ex: johntimothydoe@company.com\n'
                             ' firstmlast - ex: johntdoe@company.com\n'
                             ' flast  - ex: jdoe@company.com\n'
                             ' fmlast - ex: jtdoe@company.com\n'
                             ' firstlast - ex: johndoe@company.com\n'
                             ' first.last - ex: john.doe@company.com', required=True)
    parser.add_argument('--function', choices=['get', 'create'],
                        help='R| Function to perform:\n'
                             ' get - Logs into Linkedin and saves the employee html pages\n'
                             ' create - Parses the html pages to create employee lists', required=True)
    parser.add_argument('--ignore', help='Ignore profiles without a name', action='store_true', required=True)
    args = parser.parse_args()
    company = args.company.replace(" ", "_")

    if args.function == 'create':
        # Parse the downloaded page sources
        pp = ParseProfiles(args.email_suffix, args.email_prefix, args.ignore, args.company)
        for i in range(0, 99):
            print "Parsing Page: %d" % i
            filename = "{}{}_source.html".format(company, i)
            file_path = "{}/{}".format(company, filename)
            if os.path.isfile(file_path):
                pp.parse_source(file_path)
            else:
                print "file {} not found, stopping...".format(file_path)
                break
        pp.print_employees()

    elif args.function == 'get':
        lip = LinkedinProfiles(args.company)
        # Start the web driver and download the company's employee pages
        lip.get_linkedin_profiles()


if __name__ == "__main__":
    main()
    # test()
