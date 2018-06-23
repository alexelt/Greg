from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from random import randint
from multiprocessing.dummy import Pool
from datetime import datetime
import smtplib
import time
import csv
import ast
import json



def email_func(kword):
    # sends emails with the word that couldn't be processed and that this instance closed
    email_content = "The browser with the keyword "+kword+" closed after retries"
    frm = 'your gmail'  # I used my gmail to test it but you can easily use your own smtp, plus if you want to i can set it up for you
    to_m = 'your mail of choice'
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login('username', 'password')
    mail.sendmail(frm, to_m, email_content)
    mail.close()

def error_log(error_word):
    # Writes to the log file the keyword that couldn't be processed
    error_path = output_path1+'errors/'+'logs.csv'
    f = open(error_path, 'a')
    f.write('i am number ' + str(i) + '\n')
    f.close()

    email_func(error_word)


def djson(crnt_result, crnt_word, crnt_rank, crnt_rank_no_ads, desc, cvname):

    stamp_1 = datetime.now()
    stamp_1 = str(stamp_1)
    stamp_1 = stamp_1.replace('-', '_')
    stamp_1 = stamp_1.replace(':', '_')
    stamp_1 = stamp_1.replace(' ', '__')
    sep_1 = '.'
    stamp_1 = stamp_1.split(sep_1, 1)[0]  # The time stamp

    var2 = crnt_result.find('a').get('href')
    var3 = crnt_result.text
    data = {}
    data['title'] = var3
    data['rank'] = crnt_rank+crnt_rank_no_ads
    data['rankExcludingAds'] = crnt_rank_no_ads
    data['search'] = crnt_word
    data['isAd'] = 'False'
    data['timestamp'] = stamp_1
    data['url'] = var2
    data['description'] = desc

    
    output_path1 = output_path1+cvname
    
    with open(output_path1+'/data1.json', 'a', encoding='utf8', newline='') as jsonfile:
        json.dump(data, jsonfile)
        jsonfile.close()

    output_path2 = output_path1+stamp_1

    with open(output_path2+'/data1.json', 'a', encoding='utf8', newline='') as jsonfile:
        json.dump(data, jsonfile)
        jsonfile.close()

def error_retry(driver2, error, counter2):
    print('The keyword '+error+' appeared to have a problem')  #returns the problem, changes the ip and retries 5 times | new options in general
    driver2.quit()
    # opts = Options()
    # opts.add_argument(u_agent)
    driver2.get("https://google.com")  # opens up chrome - google
    driver2.execute_script("return navigator.userAgent")
    try:
        btn = driver2.find_element_by_xpath('//*[@id="lst-ib"]')
        if btn is not None:
            return 'break'
    except:
        driver2.quit()
        if counter2 == 5:
            error_log(error)
            return 'next'
        else:
            z = -1
            return z

def search(word, counter, driver1, cvar):
    button = 'fail'
    srch = True
    raw = 'raw.html'
    raw = word + raw
    final_output = output_path1+raw

    result = None
    resultad = None
    desc_ad = None
    description = None

    while srch == True:
        try:
            driver1.find_element_by_xpath('//*[@id="lst-ib"]')
            button = driver1.find_element_by_xpath('//*[@id="lst-ib"]')
        except NoSuchElementException:
            pass
        if button != 'fail':
            r = randint(5, 9)
            time.sleep(r)
            if counter > 1:
                button.send_keys(Keys.CONTROL + "a")
            button.send_keys(word)
            r = randint(9, 12)
            time.sleep(r)
            button = driver1.find_element_by_xpath('//*[@id="lst-ib"]')
            button.send_keys(u'\ue007')
            r = randint(5, 8)
            time.sleep(r)
            html = driver1.page_source
            soup = BeautifulSoup(html, 'html.parser')
            print("made it \n \n \n \n \n \n")
            file = open(final_output, 'wb')
            file.write(soup.encode('utf-8'))  # Saves the html of the keyword
            file.close()
            results_counter = 0
            ads_counter = 0

            try:
                resultsad = soup.find('div', {"class": 'C4eCVc c'})
                try:
                    resultsad = resultsad.findAll('h3', {'class': 'r'})  # Searches for the ads
                except:
                    resultsad = 'wrong'
                    pass
            except:
                resultsad = 'wrong'
                pass

            if resultsad == 'wrong':
                print(word + " had no ads")
                ads_counter = 0
            else:
                ads_counter = 1  # Counter for the ad results
                for resultad in resultsad:
                    print(resultad.text)
                    print(ads_counter)
                    djson(word, resultad, ads_counter, results_counter, desc_ad, cvar)  # calls the function that passes everything to the json file
                    ads_counter += 1

            try:
                # Searches for the regular results, because of some new google features the results are often split by news etc so it searches for all the regular classes
                results = soup.find('div', {"class": 'srg'})
                testresults = soup.findAll('div', {"class": 'srg'})
                testresults = list(testresults)
                try:
                    results = results.findAll('div', {'class': 'g'})
                except:
                    results = 'wrong'
                    pass

            except:
                results = 'wrong'
                pass

            if results == 'wrong':
                print(word + " problem")
                t = 1
                while t <= 5 or b == 'asdf':
                    b = error_retry(driver1, word, t)  # if the script opens up google it breaks the loop
                    t += 1
            else:
                results_counter = 1  # Counter for the real results
                for result in results:
                    description = result.find('span', {'class': 'st'})
                    result = result.find('h3', {'class': 'r'})
                    print(results_counter)
                    print(result.text)
                    print(result.find('a').get('href'))
                    djson(word, result, ads_counter, results_counter, description, cvar)  # calls the function that passes everything to the json file
                    results_counter += 1

                if len(testresults) > 1:
                    for testresult in testresults[1]:
                        results_counter += 1
                        testresult = testresult.find('h3', {'class': 'r'})
                        print('second group ' + str(results_counter))
                        print(testresult.text)
                        print(testresult.find('a').get('href'))
                        djson(word, testresult, results_counter, description, cvar)  # If for some reason the keywords are correlated to news as i explained there are 2 divs with results so it again calls the function that passes everything to the json file


            srch = False

        else:
            t = 1
            while t <=5 or b=='asdf':
                b = error_retry(driver1, word, t)  # if the script opens up google it breaks the loop
                t += 1

            srch = False  # proceeds to next word





def start(keywords):  # Takes each list and starts looping through the keywords
    opts = Options()  # Gives chrome basic settings and opens it
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36")
    driver = webdriver.Chrome("", chrome_options=opts)
    driver.get("https://google.com")  # opens up chrome - google
    agent = driver.execute_script("return navigator.userAgent")
    print(agent)
    i = 1
    for keyword in keywords:  # The part that it starts looping through keywords
        if i == 1:  # The first time it takes the time and parses it to a var to create 1 json per instance
            sepc = '.'
            csvar = datetime.now()
            csvar = str(csvar)
            csvar = csvar.split(sepc, 1)[1]
        search(keyword, i, driver, csvar)
        i += 1





userlist = []
with open('', 'r') as userfile:  # Reads from the csv the main list with all the keywords
    userfilereader = csv.reader(userfile)
    for col in userfilereader:
        userlist.append(col)

with open('', 'r') as userfile1:  # Reads from the csv the number of instances
    reader = csv.reader(userfile1)
    num_of_instances = [row for idx, row in enumerate(reader) if idx == 1]

with open('', 'r') as userfile2:  # Reads from the csv the path that you want the program to save the main json file
    reader = csv.reader(userfile2)
    output_path = [row for idx, row in enumerate(reader) if idx == 2]

actual_list = ast.literal_eval(str(userlist[0]))
output_path1 = str(output_path[0])

x = num_of_instances[0]
x = ''.join(x)
number_of_instances = int(x)  # The number of chrome instances

stamp = datetime.now()
stamp = str(stamp)
stamp = stamp.replace('-', '_')
stamp = stamp.replace(':', '_')
stamp = stamp.replace(' ', '__')
sep = '.'
stamp = stamp.split(sep, 1)[0] # The time stamp


output_path1 = str(output_path1)[2:-2]  # The path tha you want the main json to be stored
print(output_path1+stamp)  # for each new json and raw html


divider = len(actual_list)//number_of_instances
actual_list1 = []
actual_list2 = []
actual_list3 = []
for i in range(0, len(actual_list)):
    if i < divider:
        actual_list1.append(actual_list[i])
        #print('actual_list1 '+str(i))
    elif i >= (divider-1) and (i <= (divider*2)-1):  # It creates 7 lists in this variation but you can st as many as you'd want
        actual_list2.append(actual_list[i])
        #print('actual_list2 '+str(i))
    elif (i >= 5):
        actual_list3.append(actual_list[i])
        #print('actual_list3 '+str(i))




#pool = Pool(3)
#pool.map(start, (actual_list1, actual_list2, actual_list3))  # opens up 7 instances of chrome
#pool.close()
#pool.join()


userfile.close()
userfile1.close()
userfile2.close()



'''



proxy = "00.00.00.00:7899" 

chr_options = Options()
chr_options.add_argument('--proxy-server=%s' % PROXY)


'''
