# SERIOUSLY
# This demo is for EDUCATIONAL purposes ONLY!
# Don't mess with Google
# Don't abuse this code
# Don't do things that might violate Google's T&C
# Use at your own risk!

import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from utils.gcloud_transcript import GCloudTranscript
import unittest
import time
from mock_user import MockUser


class GoogleRegisterSanityTest(unittest.TestCase):
    def get_incognito_caps(self):
        options = Options()
        options.add_argument("--incognito")
        options.add_argument("--disable-popup-blocking")
        return options

    def setUp(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver',
                                       chrome_options=self.get_incognito_caps())
        self.actionchains = webdriver.ActionChains(self.driver)
        self.gcloudTranscriber = GCloudTranscript()

    def tearDown(self):
        self.driver.quit()

    def observe_until_elm_cls_appear(self, class_name, timeout=10):
        print("Observing for class={}".format(class_name))
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    def observe_until_elm_id_appear(self, id_name, timeout=10):
        print("Observing for id={}".format(id_name))
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((By.ID, id_name)))

    def test_login_with_otp(self):
        driver = self.driver

        mock_user = MockUser
        
        # Open Google registration
        driver.get("https://accounts.google.com/SignUp")
        self.observe_until_elm_id_appear("name-form-element", 5)

        # Enter first & last name
        fname_elm = driver.find_element_by_id("FirstName")

        if fname_elm:
            fname_elm.send_keys(mock_user.F_NAME)

        lname_elm = driver.find_element_by_id("LastName")
        if lname_elm:
            lname_elm.send_keys(mock_user.L_NAME)

        username_elm = driver.find_element_by_id("GmailAddress")
        if username_elm:
            username_elm.send_keys(mock_user.USERNAME)

        passwd_elm = driver.find_element_by_id("Passwd")
        if passwd_elm:
            passwd_elm.send_keys(mock_user.PASSWORD)

        passwd2_elm = driver.find_element_by_id("PasswdAgain")
        if passwd2_elm:
            passwd2_elm.send_keys(mock_user.PASSWORD)

        bday_elm = driver.find_element_by_id("BirthDay")
        if bday_elm:
            bday_elm.send_keys(mock_user.BD_DAY)

        # Press month label before month
        month_label_elm = driver.find_element_by_id("BirthMonth")
        if month_label_elm:
            month_label_elm.click()
            time.sleep(1)

        bmonth_elm = driver.find_element_by_id(":{}".format(mock_user.BD_MONTH))
        if bmonth_elm:
            try:
                bmonth_elm.click()
                time.sleep(1)
            except exceptions.WebDriverException:
                pass

        byear_elm = driver.find_element_by_id("BirthYear")
        if byear_elm:
            byear_elm.send_keys(mock_user.BD_YEAR)

        gender_elm = driver.find_element_by_id("Gender")
        if gender_elm:
            gender_elm.click()
            time.sleep(1)
            try:
                female_elm = driver.find_element_by_id(":f")
                if female_elm:
                    female_elm.click()
            except exceptions.WebDriverException:
                pass
            driver.execute_script("document.getElementById(\"HiddenGender\").value=\"MALE\";")

        phone_elm = driver.find_element_by_id("RecoveryPhoneNumber")
        if phone_elm:
            phone_elm.clear()
            phone_elm.send_keys(mock_user.PHONE)

        submit_elm = driver.find_element_by_id("submitbutton")
        if submit_elm:
            submit_elm.click()

        self.observe_until_elm_id_appear("tos-scroll-button", 1)
        # scroll to TOS:
        tos_btn = driver.find_element_by_id("tos-scroll-button")
        if tos_btn:
            for i in range(0, 5):
                try:
                    tos_btn.click()
                    time.sleep(1)
                except exceptions.WebDriverException:
                    continue

        agree_and_send_elm = driver.find_element_by_id("iagreebutton")
        if agree_and_send_elm:
            agree_and_send_elm.click()

        self.observe_until_elm_id_appear("next-button")
        time.sleep(1)

        phone_verification_elm = driver.find_element_by_id("signupidvmethod-voice")
        if phone_verification_elm:
            phone_verification_elm.click()

        next_elm = driver.find_element_by_id("next-button")
        if next_elm:
            self.actionchains.move_to_element(next_elm)
            next_elm.click()

        recording_file_path = os.path.join(
            os.path.dirname(__file__),
            'recordings',
            'latest-record.wav')

        print("Observing for an updated call recording")
        self.assertTrue(self.observe_for_file_ts_change(recording_file_path, 70))
        print("An updated recording was found")

        # transcribe
        # get full transcript
        print("Sending file for transcription...")
        transcripts = self.gcloudTranscriber.transcribe_file(recording_file_path)
        # We need at least one result
        self.assertGreaterEqual(len(transcripts), 1)

        print("Successfully got a transcription: {}".format(transcripts[0]))

        # Extract pin from transcription
        text_to_extract_pin = self.normalize_transcript(transcripts[0])
        matches = re.findall('\d{4,6}', text_to_extract_pin)

        # Check we got the code twice and both are the same to have 100% certain
        # self.assertTrue(len(matches) is 2 and matches[0] == matches[1])
        print("Two codes that were received are matching: " + str(len(matches) is 2 and matches[0] == matches[1]))
        received_pin = (matches[0] if len(matches[0]) == 6 else matches[1])
        print("Got verification code: {}".format(received_pin))

        code_elm = driver.find_element_by_id("verify-phone-input")
        if code_elm:
            code_elm.send_keys(received_pin)

        time.sleep(10)  # this is a demo visual sleep

        finish_elm = driver.find_element_by_name("VerifyPhone")
        if finish_elm:
            finish_elm.click()
            # Done!

        time.sleep(20)
        self.assertIsNotNone(driver.find_element_by_id("profile-arrow"))
        return

    @staticmethod
    def get_file_ts(file_path):
        return os.stat(file_path).st_mtime

    def observe_for_file_ts_change(self, recording_path, ttl):
        if not os.path.isfile(recording_path):
            return None
        cached_stamp = GoogleRegisterSanityTest.get_file_ts(recording_path)
        for i in range(0, ttl):
            stamp = GoogleRegisterSanityTest.get_file_ts(recording_path)
            if stamp != cached_stamp:
                return True
                # File has changed, return true
            else:
                time.sleep(1)
        return False

    def normalize_transcript(self, text):
        numbers = [(".", "0"),
                   ("one", "1"),
                   ("once", "1"),
                   ("two", "2"),
                   ("too", "2"),
                   ("to", "2"),
                   ("three", "3"),
                   ("tree", "3"),
                   ("four", "4"),
                   ("for", "4"),
                   ("five", "5"),
                   ("six", "6"),
                   ("seeks", "6"),
                   ("seven", "7"),
                   ("eight", "8"),
                   ("nine", "9")
                   ]
        for key, val in numbers:
            text = text.replace(key, val)
        text = text.replace(" ", "")
        return text


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(GoogleRegisterSanityTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
