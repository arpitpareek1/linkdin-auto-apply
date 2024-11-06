import time, math, random, os
import utils, constants, config
import pickle, hashlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


class Linkedin:
    def __init__(self):
        utils.prYellow(
            "🤖 Thanks for using Easy Apply Jobs bot, for more information you can visit our site - www.automated-bots.com"
        )
        utils.prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=utils.chromeBrowserOptions(),
        )
        self.cookies_path = (
            f"{os.path.join(os.getcwd(),'cookies')}/{self.getHash(config.email)}.pkl"
        )
        self.driver.get("https://www.linkedin.com")
        self.loadCookies()

        if not self.isLoggedIn():
            self.driver.get(
                "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
            )
            utils.prYellow("🔄 Trying to log in Linkedin...")
            try:
                self.driver.find_element("id", "username").send_keys(config.email)
                time.sleep(2)
                self.driver.find_element("id", "password").send_keys(config.password)
                time.sleep(2)
                self.driver.find_element("xpath", '//button[@type="submit"]').click()
                time.sleep(5)
                print("j")
            except Exception:
                utils.prRed(
                    "❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8."
                )

            # self.saveCookies()
        # start application
        self.linkJobApply()

    def getHash(self, string):
        return hashlib.md5(string.encode("utf-8")).hexdigest()

    def loadCookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def saveCookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def isLoggedIn(self):
        self.driver.get("https://www.linkedin.com/feed")
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember14"]')
            return True
        except Exception:
            pass
        return False

    def generateUrls(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        try:
            with open("data/urlData.txt", "w", encoding="utf-8") as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            utils.prGreen(
                "✅ Apply urls are created successfully, now the bot will visit those urls."
            )
        except Exception:
            utils.prRed(
                "❌ Couldn't generate urls, make sure you have editted config file line 25-39"
            )

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            totalJobs = self.driver.find_element(By.XPATH, "//small").text
            totalPages = utils.jobsToPages(totalJobs)

            urlWords = utils.urlToKeywords(url)
            lineToWrite = (
                "\n Category: "
                + urlWords[0]
                + ", Location: "
                + urlWords[1]
                + ", Applying "
                + str(totalJobs)
                + " jobs."
            )
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url + "&start=" + str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(
                    By.XPATH, "//li[@data-occludable-job-id]"
                )
                offerIds = [
                    (offer.get_attribute("data-occludable-job-id").split(":")[-1])
                    for offer in offersPerPage
                ]
                time.sleep(random.uniform(1, constants.botSpeed))

                for offer in offersPerPage:
                    if not self.element_exists(
                        offer, By.XPATH, ".//*[contains(text(), 'Applied')]"
                    ):
                        offerId = offer.get_attribute("data-occludable-job-id")
                        offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    offerPage = "https://www.linkedin.com/jobs/view/" + str(jobID)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1

                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties:
                        lineToWrite = (
                            jobProperties
                            + " | "
                            + "* 🤬 Blacklisted Job, skipped!: "
                            + str(offerPage)
                        )
                        self.displayWriteResults(lineToWrite)

                    else:

                        # Wait for the "Apply" button to be clickable and click it
                        apply_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(
                                (
                                    By.CLASS_NAME,
                                    "jobs-apply-button artdeco-button artdeco-button--3 artdeco-button--primary ember-view",
                                )
                            )
                        )
                        apply_button.click()

                        # Wait for the phone number input field to be visible and send keys
                        phone_number_field = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located(
                                (
                                    By.ID,
                                    "single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-3955402927-1198923481-phoneNumber-nationalNumber",
                                )
                            )
                        )
                        phone_number_field.send_keys(
                            "1212123434"
                        )  # TODO: get this from configuration

                        # Wait for the next button to be clickable and click it
                        next_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(
                                (
                                    By.CLASS_NAME,
                                    "artdeco-button artdeco-button--2 artdeco-button--primary ember-view",
                                )
                            )
                        )
                        next_button.click()

                        # Wait for the file input to be visible and send keys (upload file)
                        file_input = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located(
                                (
                                    By.ID,
                                    "jobs-document-upload-file-input-upload-resume-urn:li:fsu_jobApplicationFileUploadFormElement:urn:li:jobs_applyformcommon_easyApplyFormElement:(3955402927,1198923465,document)",
                                )
                            )
                        )
                        file_input.send_keys(
                            "/Users/arpit/OneDrive/Desktop/js/auto-apply-linkdin/dd12-13_0.pdf"
                        )  # TODO: get this from config

                        # Wait for the final submit button to be clickable and click it
                        final_submit_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(
                                (
                                    By.CLASS_NAME,
                                    "artdeco-button artdeco-button--2 artdeco-button--primary ember-view",
                                )
                            )
                        )
                        final_submit_button.click()
                        questions = self.driver.find_element(
                            By.CLASS_NAME, "t-16 t-bold"
                        )
                        if questions and questions.text == "Additional Questions":
                            all_ques = self.driver.find_elements(
                                By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"
                            )
                            if len(all_ques):
                                for ques in all_ques:
                                    ques.find_element(
                                        By.CLASS_NAME, " artdeco-text-input--input"
                                    ).send_keys("2")

                        submit_application = self.driver.find_element(
                            By.CLASS_NAME,
                            "artdeco-button artdeco-button--2 artdeco-button--primary ember-view",
                        )
                        if submit_application:
                            submit_application.click()
                            lineToWrite = (
                                jobProperties
                                + " | "
                                + "* 🥳 Just Applied to this job: "
                                + str(offerPage)
                            )
                            self.displayWriteResults(lineToWrite)
                            countApplied += 1
                            return
                        else:
                            easyApplybutton = self.easyApplyButton()

                        if easyApplybutton is not False:
                            easyApplybutton.click()
                            time.sleep(random.uniform(1, constants.botSpeed))

                            try:
                                self.chooseResume()
                                self.driver.find_element(
                                    By.CSS_SELECTOR,
                                    "button[aria-label='Submit application']",
                                ).click()
                                time.sleep(random.uniform(1, constants.botSpeed))

                                lineToWrite = (
                                    jobProperties
                                    + " | "
                                    + "* 🥳 Just Applied to this job: "
                                    + str(offerPage)
                                )
                                self.displayWriteResults(lineToWrite)
                                countApplied += 1

                            except Exception:
                                try:
                                    self.driver.find_element(
                                        By.CSS_SELECTOR,
                                        "button[aria-label='Continue to next step']",
                                    ).click()
                                    time.sleep(random.uniform(1, constants.botSpeed))
                                    self.chooseResume()
                                    comPercentage = self.driver.find_element(
                                        By.XPATH,
                                        "html/body/div[3]/div/div/div[2]/div/div/span",
                                    ).text
                                    percenNumber = int(
                                        comPercentage[0 : comPercentage.index("%")]
                                    )
                                    result = self.applyProcess(percenNumber, offerPage)
                                    lineToWrite = jobProperties + " | " + result
                                    self.displayWriteResults(lineToWrite)

                                except Exception:
                                    self.chooseResume()
                                    lineToWrite = (
                                        jobProperties
                                        + " | "
                                        + "* 🥵 Cannot apply to this Job! "
                                        + str(offerPage)
                                    )
                                    self.displayWriteResults(lineToWrite)
                        else:
                            lineToWrite = (
                                jobProperties
                                + " | "
                                + "* 🥳 Already applied! Job: "
                                + str(offerPage)
                            )
                            self.displayWriteResults(lineToWrite)

            utils.prYellow(
                "Category: "
                + urlWords[0]
                + ","
                + urlWords[1]
                + " applied: "
                + str(countApplied)
                + " jobs out of "
                + str(countJobs)
                + "."
            )

        utils.donate(self)

    def chooseResume(self):
        try:
            self.driver.find_element(
                By.CLASS_NAME, "jobs-document-upload__title--is-required"
            )
            resumes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]"
            )
            if (
                len(resumes) == 1
                and resumes[0].get_attribute("aria-label") == "Select this resume"
            ):
                resumes[0].click()
            elif (
                len(resumes) > 1
                and resumes[config.preferredCv - 1].get_attribute("aria-label")
                == "Select this resume"
            ):
                resumes[config.preferredCv - 1].click()
            elif type(len(resumes)) != int:
                utils.prRed(
                    "❌ No resume has been selected please add at least one resume to your Linkedin account."
                )
        except Exception:
            pass

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobLocation = ""

        try:
            jobTitle = (
                self.driver.find_element(
                    By.XPATH, "//h1[contains(@class, 'job-title')]"
                )
                .get_attribute("innerHTML")
                .strip()
            )
            res = [
                blItem
                for blItem in config.blackListTitles
                if (blItem.lower() in jobTitle.lower())
            ]
            if len(res) > 0:
                jobTitle += "(blacklisted title: " + " ".join(res) + ")"
        except Exception as e:
            if config.displayWarnings:
                utils.prYellow("⚠️ Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            time.sleep(5)
            jobDetail = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div"
            ).text.replace("·", "|")
            res = [
                blItem
                for blItem in config.blacklistCompanies
                if (blItem.lower() in jobTitle.lower())
            ]
            if len(res) > 0:
                jobDetail += "(blacklisted company: " + " ".join(res) + ")"
        except Exception as e:
            if config.displayWarnings:
                print(e)
                utils.prYellow("⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(
                By.XPATH,
                "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]",
            )
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text

        except Exception as e:
            if config.displayWarnings:
                print(e)
                utils.prYellow("⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        textToWrite = str(count) + " | " + jobTitle + " | " + jobDetail + jobLocation
        return textToWrite

    def easyApplyButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class, 'jobs-apply-button')]",
            )
            EasyApplyButton = button
        except Exception:
            EasyApplyButton = False

        return EasyApplyButton

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) - 2
        result = ""
        for pages in range(applyPages):
            self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Continue to next step']"
            ).click()

        self.driver.find_element(
            By.CSS_SELECTOR, "button[aria-label='Review your application']"
        ).click()
        time.sleep(random.uniform(1, constants.botSpeed))

        if config.followCompanies is False:
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, "label[for='follow-company-checkbox']"
                ).click()
            except Exception:
                pass

        self.driver.find_element(
            By.CSS_SELECTOR, "button[aria-label='Submit application']"
        ).click()
        time.sleep(random.uniform(1, constants.botSpeed))

        result = "* 🥳 Just Applied to this job: " + str(offerPage)

        return result

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            utils.prRed("❌ Error in DisplayWriteResults: " + str(e))

    def element_exists(self, parent, by, selector):
        return len(parent.find_elements(by, selector)) > 0


start = time.time()
Linkedin().linkJobApply()
end = time.time()
utils.prYellow("---Took: " + str(round((time.time() - start) / 60)) + " minute(s).")
