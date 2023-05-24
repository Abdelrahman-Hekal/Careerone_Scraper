from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import time
import csv
import os
from datetime import datetime
import pandas as pd
import warnings
import unidecode
warnings.filterwarnings('ignore')



def initialize_bot():

    ## Setting up chrome driver for the bot
    chrome_options  = webdriver.ChromeOptions()
    #chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("user-data-dir=C:\\Users\\abdel\\AppData\\Local\\Google\\Chrome\\User Data")
    driver_path = ChromeDriverManager().install()
    chrome_options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(driver_path, options=chrome_options)

    return driver


def get_jobs_links(driver):
    links = []
    URL = "https://www.careerone.com.au/jobs/in-australia"
    driver.get(URL)

    for i in range(3195):
        try:
            time.sleep(3)
            div1 = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='discovery']")))
            div = wait(div1, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='SearchJobLoop' and @id='searchJobLoop']")))
            jobs = wait(div, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//a[@class='btn btn-outline-success job__cta']")))
            for job in jobs:
                links.append([job.get_attribute('href')])
                #print(job.get_attribute('href'))

            ul = wait(div1, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination.c1-pagination.b-pagination.justify-content-center")))
            li = wait(ul, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))[-1]
            while True:
                try:
                    wait(li, 60).until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()
                    break
                except:
                    time.sleep(2)
        except:
            return links

    return links

def scrape_jobs(driver, path, start):

    df = pd.read_csv(os.getcwd() + '\\links.csv')
    df = df.drop_duplicates()
    links = df.iloc[:, 0].values[start:]

    n = len(links)
    for i, link in enumerate(links):
        driver.get(link)
        time.sleep(5)
        try:
            title = wait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.jv-title"))).text
            title = unidecode.unidecode(title)
        except:
            title = 'NA'
        try:
            h2 = wait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.jv-subtitle")))
            comp = wait(h2, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))[1].text
            comp = unidecode.unidecode(comp)
        except:
            comp = 'NA'
        try:
            loc = wait(h2, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))[2].text
            loc = unidecode.unidecode(loc)
        except:
            loc = 'NA'
        try:
            work = wait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jv-features-item__text")))[1].text
            work = unidecode.unidecode(work)
        except:
            work = 'NA'
        try:
            contract = wait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jv-features-item__text")))[2].text
            contract = unidecode.unidecode(contract)
        except:
            contract = 'NA'
        try:
            salary = wait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jv-features-item__text")))[0].text
            salary = unidecode.unidecode(salary)
        except:
            salary = 'NA'
        try:
            div = wait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-tags.is-danger")))
            skills = []
            divs = wait(div, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tw-truncate")))
            for tag in divs:
                skills.append(tag.text)
            skills = ', '.join(skills)
            skills = unidecode.unidecode(skills)
        except:
            skills = 'NA'
        try:
            elems = wait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job-details-item__text")))
            try:
                date = elems[0].text
                date = unidecode.unidecode(date)       
            except:
                date = 'NA'
            try:
                cat = elems[1].text
                cat = unidecode.unidecode(cat)  
            except:
                cat = 'NA'
            try:
                ind = elems[2].text
                ind = unidecode.unidecode(ind)    
            except:
                ind = 'NA'
            try:
                sec = elems[-2].text
                sec = unidecode.unidecode(sec) 
            except:
                sec = 'NA'      
        except:
            date = 'NA'
            cat = 'NA'
            ind = 'NA'
            sec = 'NA'
        try:
            # read more button
            try:
                wait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.job-footer__readmore"))).click()
            except:
                button = False

            details = wait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-description"))).text
            details = details.replace("CLOSE", '')
            details = unidecode.unidecode(details) 
        except:
            details = 'NA'

        with open(path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([title, comp, loc, work, contract, skills, date, cat, ind, sec, salary, details])
        print(f'Job {i+1+start} of {n} is scraped successfully!')



def initialize_output():

    # removing the previous output file
    path = os.getcwd()
    files = os.listdir(path)
    for file in files:
        if 'Scraped_Jobs' in file:
            os.remove(file)

    header = ['Job Title', 'Company Name', 'Location', 'Work Type', 'Contract Type', 'Skills', 'Date Posted', 'Category', 'Industry', 'Sector', 'Salary Range', 'Job Description']


    filename = 'Scraped_Jobs_{}.csv'.format(datetime.now().strftime("%d_%m_%Y_%H_%M"))

    if path.find('/') != -1:
        output = path + "/" + filename
    else:
        output = path + "\\" + filename

    with open(output, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)    
        
    return output
  
def resume_output():

    # removing the previous output file
    found = False
    path = os.getcwd()
    files = os.listdir(path)
    start = 0
    for file in files:
        if 'Scraped_Jobs' in file:
            found = True
            if path.find('/') != -1:
                output = path + "/" + file
            else:
                output = path + "\\" + file
            df = pd.read_csv(output)
            start = df.shape[0]

    if found:
        return output, start
    else:
        return 'N/A', start

def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')

def output_data(data):

    path = os.getcwd() + '\\Scraped_Jobs.csv'
    header = ['Job Title', 'Company Name', 'Location', 'Work Type', 'Contract Type', 'Skills', 'Date Posted', 'Category', 'Industry', 'Sector', 'Salary Range']
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
        
def output_links(links):

    path = os.getcwd() + '\\links.csv'
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['link'])
        writer.writerows(links)
        
if __name__ == '__main__':

    start = 0
    output, start  = resume_output()
    if output == 'N/A':
        output= initialize_output()
    start_time = time.time()
    driver = initialize_bot()
    clear_screen()
    print('-'*50)
    print('Getting Jobs Links....')
    print('-'*50)
    links = get_jobs_links(driver)
    output_links(links)
    print('-'*50)
    print('Scraping Jobs....')
    scrape_jobs(driver, output, start)
    driver.quit()
    print('Data is scraped successfully! Total scraping time is {:.1f} mins'.format((time.time() - start_time)/60))
    print('-'*50)




