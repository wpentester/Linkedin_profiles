This script uses selenium to scrape linkedin employee details from a specified company.  If the script isn't working, you can always browse to the desired company's employee page and paste in the link on line 69 like this: "employees_page = url"

The trick is to run the script with the "--function get" flag first.  When the browser has opened and run through it's tests, and the files have been successfully saved on disk, then re-run the script using the "--function create" flag.  

```sh
# Linkedin_profiles  
scrapes Linkedin for company employee profiles  
  
usage: linkedin_profiles.py [-h] --company COMPANY --email_suffix EMAIL_SUFFIX  
                            --email_prefix  
                            {firstlast,firstmlast,flast,fmlast,full,first.last}  
                            --function {get,create} --ignore  
  
Scrape Linkedin profiles for a specified company  
  
optional arguments:  
  -h, --help            show this help message and exit  
  --company COMPANY     The name of the company on Linkedin  
  --email_suffix EMAIL_SUFFIX  
                        The company email suffix ex: user@<email_suffix>  
  --email_prefix {firstlast,firstmlast,flast,fmlast,full,first.last}  
                        The email prefix format ex: <email_prefix>@company.com  
                         full   - ex: johntimothydoe@company.com  
                         firstmlast - ex: johntdoe@company.com  
                         flast  - ex: jdoe@company.com  
                         fmlast - ex: jtdoe@company.com  
                         firstlast - ex: johndoe@company.com  
                         first.last - ex: john.doe@company.com  
  --function {get,create}  
                         Function to perform:    
                         get - Logs into Linkedin and saves the employee html pages  
                         create - Parses the html pages to create employee lists  
  --ignore              Ignore profiles without a name 
```
