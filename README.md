# LinkedIn-Scraper
Monolith Code of LinkedIn Scraper

My scraper uses Selenium driver to interact with the website and BeautifulSoup for parsing and scraping the required data. 
First I assign the chromedriver path and and initialize the webdriver
Then the webdriver proceeds to linkedIn and login using the credentials
After landing on the homepage the driver goes to the desired URL provided to it. This URL is created by us by doing a valid search and applying the desired filters
Then the driver proceeds to perform scraping and note it down as a dictionary which is later pasted to the csv file where it ensures that no two items are same 
The scraper can run for as many pages as required and as many conditions given to its code
It scrapes three parameters about a company in this case. They are the company name, industry and no of employees
After the scraping is done the webdriver closes the browser and hence scraping is done successfully
