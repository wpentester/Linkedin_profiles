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

        # driver.find_element_by_name("submit").click()
        driver.find_element_by_id("main-search-box").clear()
        driver.find_element_by_id("main-search-box").send_keys(self.company)
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
            sleep(5)
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
                driver.find_element_by_link_text("Next >").click()
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
            results = soup.find(id='results')
            links = results.find_all("li", {"class": "mod"})
            for person in links:
                link = person.find('a', {"class": "result-image"})
                ind = {'name': "Not Found",
                       'picture': "Not Found",
                       'email': "Not Found",
                       'job': "Not Found"}
                if link:
                    # img = link.img
                    img = link
                if img:
                    # ind['picture'] = img.get('src')
                    ind['picture'] = img
                name = person.find('a', {"class": "title main-headline"})
                if name:
                    ind['name'] = name.text
                job = person.find('p', {"class": "title"})
                if not job:
                    job = person.find('div', {"class": "description"})
                if job:
                    ind['job'] = job.text
                # print ind['name']
                self.employees.append(ind)
        except Exception, e:
            print "Encountered error parsing file: {}".format(path)
            traceback.print_exc(e)

    def print_employees(self):
        # pprint(self.employees)
        body = ""
        csv = []
        header = "<table>" \
                 "<thead>" \
                 "<tr>" \
                 "<td>Picture</td>" \
                 "<td>Name</td>" \
                 "<td>Possible Email:</td>" \
                 "<td>Job</td>" \
                 "</tr>" \
                 "</thead>"
        for emp in self.employees:
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
                fname = re.sub('[^A-Za-z]+', '', fname)
                mname = re.sub('[^A-Za-z]+', '', mname)
                lname = re.sub('[^A-Za-z]+', '', lname)
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
                        "<td>{picture}</td>" \
                        "<td>{name}</td>" \
                        "<td>{email}</td>" \
                        "<td>{job}</td>" \
                        "<td>".format(**emp)
                csv.append('{name},{email},"{job}"'.format(**emp))
            else:
                print "ignoring user: {} - {}".format(emp['name'], emp['job'])
        foot = "</table>"
        f = open('{}/employees.html'.format(self.company), 'wb')
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
