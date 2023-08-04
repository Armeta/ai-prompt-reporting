
# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# html format/time
import time 
from bs4 import BeautifulSoup
import os


# naviagtes to ip.armeta sales oppurtunity
def connect():   
    # Set up options for chrome driver. Detach so the window doesnt close after the session
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.get('https://ip.armeta.com/demo/analytics/sales-opportunity')

    # Setup wait for later
    wait = WebDriverWait(driver, 10)

    # Store the ID of the original window
    original_window = driver.current_window_handle

    # Check we don't have other windows open already
    assert len(driver.window_handles) == 1

    # click azure AD button to make the popup appear
    time.sleep(1)
    AzureADBox = driver.find_element(By.CLASS_NAME, 'login-button-social')
    AzureADBox.click()
    time.sleep(2)

    # Wait for the pop up
    wait.until(EC.number_of_windows_to_be(2))

    # Loop through until we find a new window handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    # Find email box and type in email
    login_box = driver.find_element(By.ID, 'i0116')
    login_box.send_keys("lance.wahlert@armeta.com")

    # Click next
    nextButton = driver.find_element(By.ID, 'idSIButton9')
    nextButton.click()
    time.sleep(1)

    # Find password box and pass in password
    PassWordBox = driver.find_element(By.ID, 'i0118')
    PassWordBox.send_keys("Heads_fever_lead@3")
    time.sleep(1)

    # Find finish button and wait for auth push
    SignInButton = driver.find_element(By.ID, 'idSIButton9')
    SignInButton.click()
    time.sleep(10)

    # click no to stay signed in
    StaySignInButton = driver.find_element(By.ID, 'idBtn_Back')
    StaySignInButton.click()
    time.sleep(2)

    # Switch back to the main window
    driver.switch_to.window(original_window)

    # Wait for the new tab to finish loading content
    wait.until(EC.title_is("Armeta - Demo"))

    #pass the webdriver abck to main    
    return driver

def getOpenAI(soup, driver):

    # Get open AI to sort out the data
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{soup}"}, 
        {"role": "system", "content": "Do not include any extra data or words except the answer"},
        {"role": "system", "content": "Output should be in CSV format."},
        {"role": "system", "content": "Output should be 5 tables with the following schemas:"},
        {"role": "system", "content": "Table1: [Region], [Vol Group], [Product Group]"},
        {"role": "system", "content": "Table2: [Total Opportunity], [Total Sales], [Total Sell Thru]"},
        {"role": "system", "content": "Table3: [Department], [Department Actual Opportunity], [Department Actual Total Sales], [Department Actual Current Inventory]"},
        {"role": "system", "content": "Table4: [District], [District Actual Oppurtunity], [District Actual Total Sales]" },
        {"role": "system", "content": "Table5: [Location], [Location Oppurtunity], [Location Total Sales], [Location Sell Thru]"},
        {"role": "system", "content": "write nulls when you can't find the data."},
        {"role": "system", "content": "Table 1 and table 2 should only contain one row."},
        {"role": "assistant", "content": "Please only reply with the answerReformat/structure this raw data so I can upload it into a database."}
    ]
    )

    # PRint sorted data and url to logging file
    with open('SalesOppurtunityRawData.txt', 'a') as f:
        f.write('\n\n')
        f.write(driver.current_url)
        f.write('\n\n')
        f.write(completion.choices[0].message.content)    

def writeToFile(driver):
    with open('test.html', 'w') as f:
        f.write(driver.page_source)

    with open("test.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    # Find the filter's and their value.
    FilterNames = soup.findAll("label", {"class": "input-group-addon"})
    Filters    = soup.findAll("span", {"class":"ember-power-select-indent-0"})

    if os.stat("test.txt").st_size == 0:
        filterCount = len(FilterNames)
        i = 0
        with open('test.txt', 'a') as f: 
            f.write("URL, ")
            while i < filterCount:
                f.write("Filter" + str(i) + ", ")
                i = i + 1
            f.write("Dasboard")
            f.write("\n")

    # Write Filters
    j = 0
    with open('test.txt', 'a') as f: 
        f.write(driver.current_url + ", ")
        for FilterName in FilterNames:                
            f.write(FilterName.get_text(strip=True) + ": " + Filters[j].get_text(strip=True) + ", ") 
            j += 1
        f.write("Sales Oppurtunity")
        f.write("\n")


def main():
    #Connect to IP
    driver = connect()

    # Write starting page to file
    writeToFile(driver)
   
    # find all the clickable web elements on the page
    buttonElements1 = driver.find_elements(By.XPATH, '//div[@role="button"]')
    i = len(buttonElements1)-1
    for element in buttonElements1:
        
        # Click the button
        buttonElements = driver.find_elements(By.XPATH, '//div[@role="button"]')
        buttonElements[i].click()
        time.sleep(4)

        # Find the options listed after pressing the button. store ogiginal length
        buttonOptions1 = driver.find_elements(By.XPATH, '//li[@role="option"]')
        time.sleep(4)
        j = len(buttonOptions1)-1

        # Go through each option 
        for option in buttonOptions1:
            # on the first go around the menu is open. On the rest we need to find and open it again
            if(j != len(buttonOptions1)-1):
                buttonElements = driver.find_elements(By.XPATH, '//div[@role="button"]')         
                buttonElements[i].click()
                time.sleep(4)       

            # click the new page and wait for it to open
            buttonOptions = driver.find_elements(By.XPATH, '//li[@role="option"]')
            buttonOptions[j].click()
            time.sleep(4) 

            # PRint sorted data and url to logging file
            writeToFile(driver)

            y = i-1
            while y >= 0:

                # Go through all permutation on this option
                buttonElements = driver.find_elements(By.XPATH, '//div[@role="button"]')         
                buttonElements[y].click()
                time.sleep(4)

                # Find the new options 
                buttonOptions2 = driver.find_elements(By.XPATH, '//li[@role="option"]')
                time.sleep(4) 
                x = len(buttonOptions2)-1

                # Go through each option 
                for option2 in buttonOptions2:                
                    # on the first go around the menu is open. On the rest we need to find and open it again
                    if(x != len(buttonOptions2)-1):
                        buttonElements = driver.find_elements(By.XPATH, '//div[@role="button"]')         
                        buttonElements[y].click()
                        time.sleep(4)   
    
                    # click the new page and wait for it to open
                    buttonOptions2 = driver.find_elements(By.XPATH, '//li[@role="option"]')
                    buttonOptions2[x].click()
                    time.sleep(4)              

                    # PRint sorted data and url to logging file
                    writeToFile(driver)
                    x = x-1
                y = y - 1
            j = j-1
        i = i-1


if __name__ == '__main__':  
    main()
