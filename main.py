import time, math, random, os
import utils, constants, config
import pickle, hashlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

import json

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=utils.chromeBrowserOptions(),
)


def element_exists(parent, by, selector):
    return len(parent.find_elements(by, selector)) > 0


def applyForJob(offerPage, job_id):
    try:
        driver.get(offerPage + "/" + str(job_id))
        time.sleep(1)
        divbutton = driver.find_element(By.CLASS_NAME, "jobs-apply-button--top-card")
        button = divbutton.find_element(By.TAG_NAME, "button")
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))
        button.click()
        time.sleep(1)
        inputs = driver.find_elements(By.CLASS_NAME, "artdeco-text-input--input")
        print(inputs, len(inputs) - 1)
        if len(inputs) > 1:
            if inputs[2].text != "1212121212":
                inputs[2].clear()
                inputs[2].send_keys("1212121212")  # TODO: Remove static phone number
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@aria-label="Continue to next step"]')
            )
        ).click()
        time.sleep(2)
        try:
            uploaded_file = driver.find_element(By.XPATH, '//input[@type="radio"]')
            if not uploaded_file:
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@name="file"]'))
                )
                time.sleep(1)
                file_input.send_keys(
                    r"C:\Users\arpit\OneDrive\Desktop\js\auto-apply-linkdin\dd12-13_0.pdf"
                )

        except Exception as e:
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="file"]'))
            )
            time.sleep(1)
            file_input.send_keys(
                r"C:\Users\arpit\OneDrive\Desktop\js\auto-apply-linkdin\dd12-13_0.pdf"
            )  # TODO: get this from config
        time.sleep(1)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*aria-label="Continue to next step"]')
                )
            ).click()
        except Exception as e:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@aria-label="Review your application"]')
                )
            ).click()
        time.sleep(3)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@aria-label="Submit application"]')
            )
        ).click()
        return True
    except Exception as e:
        return False


def autoLogin():
    with open("cookies.json", "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

    driver.refresh()


def isLogin():
    return os.path.isfile(os.path.join(os.getcwd(), "cookies.json"))


def main():
    try:
        profile_name = "full stack developer"
        driver.get(
            f"https://www.linkedin.com/jobs/search/?currentJobId=3953024050&f_AL=true&f_E=3&f_WT=2&keywords={profile_name}&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=R"
        )

        if not isLogin():
            utils.prYellow("🔄 Trying to log in Linkedin...")
            time.sleep(5)
            driver.find_element("id", "username").send_keys(config.email)
            driver.find_element("id", "password").send_keys(config.password)
            driver.find_element("xpath", '//button[@type="submit"]').click()
            utils.prYellow("Logged in Linkedin")
            time.sleep(25)
            cookies = driver.get_cookies()
            with open("cookies.json", "w") as file:
                json.dump(cookies, file)
        else:
            autoLogin()

        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        all_jobs = driver.find_element(By.CLASS_NAME, "scaffold-layout__list-container")
        if all_jobs:
            all_jobs = all_jobs.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
            offerIds = []
            for offer in all_jobs:
                if not element_exists(
                    offer, By.XPATH, ".//*[contains(text(), 'Applied')]"
                ):
                    offerId = offer.get_attribute("data-occludable-job-id")
                    offerIds.append(int(offerId.split(":")[-1]))

            for jobID in offerIds:
                result = applyForJob("https://www.linkedin.com/jobs/view", str(jobID))
                if result:
                    print("* 🥳 Just Applied to this job: " + str(jobID))
                else:
                    print("* Failed, skipped!: " + str(jobID))
        else:
            print("No jobs found")

    except Exception as e:
        print(e)
    driver.close()


main()
