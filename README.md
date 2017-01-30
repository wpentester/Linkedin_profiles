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
