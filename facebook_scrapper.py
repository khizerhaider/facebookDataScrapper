# import time
# import random
# import logging
# import csv
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("hazara_scraper.log"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger()

# class HazaraScraper:
#     def __init__(self, email, password, headless=False):
#         self.email = email
#         self.password = password
        
#         # Configure browser options
#         options = webdriver.ChromeOptions()
#         if headless:
#             options.add_argument("--headless")
        
#         # Add arguments to appear as normal browser
#         options.add_argument("--window-size=1920,1080")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option("useAutomationExtension", False)
        
#         self.driver = webdriver.Chrome(options=options)
#         self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         # Random user agent
#         user_agents = [
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
#         ]
#         self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(user_agents)})
        
#         # Output files
#         self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#     def login(self):
#         """Log in to Facebook"""
#         logger.info("Attempting to login to Facebook")
#         try:
#             self.driver.get("https://www.facebook.com/")
#             time.sleep(random.uniform(2, 4))
            
#             # Handle cookies popup if it appears
#             try:
#                 cookies_button = WebDriverWait(self.driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All') or contains(text(), 'Allow')]"))
#                 )
#                 cookies_button.click()
#                 time.sleep(random.uniform(1, 2))
#             except:
#                 logger.info("No cookies prompt detected or already handled")
            
#             # Enter email
#             email_field = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "email"))
#             )
#             self._human_type(email_field, self.email)
            
#             # Enter password
#             password_field = self.driver.find_element(By.ID, "pass")
#             self._human_type(password_field, self.password)
            
#             # Click login button
#             login_button = self.driver.find_element(By.NAME, "login")
#             login_button.click()
            
#             # Wait for login to complete
#             time.sleep(random.uniform(5, 8))
            
#             # Check if login successful
#             if "login" in self.driver.current_url:
#                 logger.error("Login failed - still on login page")
#                 return False
                
#             logger.info("Successfully logged in to Facebook")
#             return True
            
#         except Exception as e:
#             logger.error(f"Login failed: {str(e)}")
#             return False
    
#     def scrape_group_members(self, group_url):
#         """Scrape all members from a Facebook group"""
#         logger.info(f"Starting to scrape members from group: {group_url}")
#         all_members = []
        
#         # Create a unique filename for this group
#         group_id = group_url.split('/')[-1]
#         members_file = f"group_members_{group_id}_{self.timestamp}.csv"
        
#         try:
#             # First navigate to the group page
#             self.driver.get(group_url)
#             time.sleep(random.uniform(5, 7))
            
#             # Get group name
#             try:
#                 group_name_element = WebDriverWait(self.driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, "//h1"))
#                 )
#                 group_name = group_name_element.text.strip()
#                 logger.info(f"Group name: {group_name}")
#             except:
#                 group_name = "Hazara Group"
#                 logger.warning("Could not find group name, using default")
            
#             # Try to navigate to members tab
#             try:
#                 # Try different ways to find the members link
#                 try:
#                     members_link = WebDriverWait(self.driver, 10).until(
#                         EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/members/')]"))
#                     )
#                 except:
#                     try:
#                         members_link = WebDriverWait(self.driver, 10).until(
#                             EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Members')]/ancestor::a"))
#                         )
#                     except:
#                         # Direct navigation to members page
#                         members_url = f"{group_url}/members"
#                         logger.info(f"Directly navigating to members URL: {members_url}")
#                         self.driver.get(members_url)
#                         time.sleep(random.uniform(3, 5))
                
#                 # If we found a members link, click it
#                 if 'members_link' in locals():
#                     members_link.click()
#                     time.sleep(random.uniform(3, 5))
                
#                 logger.info("Successfully navigated to members page")
                
#                 # Now on the members page, prepare to scrape
#                 group_members = []
#                 previous_height = 0
#                 stall_count = 0
#                 max_stalls = 8  # Increased stall tolerance to ensure we get all members
#                 scroll_count = 0
#                 member_count = 0
#                 last_count = 0
                
#                 # Create and open CSV file for writing
#                 with open(members_file, 'w', newline='', encoding='utf-8') as f:
#                     writer = csv.DictWriter(f, fieldnames=["name", "profile_url", "source_name", "source_url"])
#                     writer.writeheader()
                
#                     # Keep scrolling until we've hit stall limit (no new members loaded)
#                     while stall_count < max_stalls:
#                         # Scroll down
#                         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                         time.sleep(random.uniform(3, 5))
#                         scroll_count += 1
                        
#                         # Get new scroll height
#                         current_height = self.driver.execute_script("return document.body.scrollHeight")
                        
#                         # Find member elements with more specific XPath patterns
#                         member_elements = []
#                         try:
#                             # Try different patterns to find member links
#                             patterns = [
#                                 "//div[contains(@class, 'x1n2onr6')]//a[contains(@href, '/user/') or contains(@href, '/profile.php')]",
#                                 "//div[@role='article']//a[contains(@href, '/user/') or contains(@href, '/profile.php')]",
#                                 "//div[@role='main']//a[contains(@href, '/user/') or contains(@href, '/profile.php')]",
#                                 "//a[contains(@href, '/user/') or contains(@href, '/profile.php')]"
#                             ]
                            
#                             for pattern in patterns:
#                                 elements = self.driver.find_elements(By.XPATH, pattern)
#                                 if elements:
#                                     member_elements = elements
#                                     break
#                         except Exception as e:
#                             logger.error(f"Error finding member elements: {str(e)}")
                        
#                         new_members_found = 0
                        
#                         # Process member elements
#                         for element in member_elements:
#                             try:
#                                 # Try different approaches to get member name and URL
#                                 try:
#                                     member_name = element.text.strip()
#                                     # If name is empty, try to find name in a child element
#                                     if not member_name:
#                                         name_elements = element.find_elements(By.XPATH, ".//span")
#                                         for name_elem in name_elements:
#                                             if name_elem.text.strip():
#                                                 member_name = name_elem.text.strip()
#                                                 break
#                                 except:
#                                     continue  # Skip if can't get name
                                
#                                 member_url = element.get_attribute("href")
                                
#                                 # Clean up member URL to remove parameters
#                                 if member_url and '?' in member_url:
#                                     member_url = member_url.split('?')[0]
                                
#                                 # Skip links that don't look like profile URLs or don't have names
#                                 if not member_name or not member_url or not ('/user/' in member_url or '/profile.php' in member_url):
#                                     continue
                                    
#                                 # Skip if already found this member
#                                 if any(m['name'] == member_name and m['profile_url'] == member_url for m in group_members):
#                                     continue
                                
#                                 # Add member to our list
#                                 member_info = {
#                                     "name": member_name,
#                                     "profile_url": member_url,
#                                     "source_name": group_name,
#                                     "source_url": group_url
#                                 }
#                                 group_members.append(member_info)
#                                 all_members.append(member_info)
#                                 new_members_found += 1
                                
#                                 # Write directly to CSV
#                                 writer.writerow(member_info)
#                                 f.flush()  # Ensure it's written to disk immediately
#                             except Exception as e:
#                                 logger.error(f"Error processing member element: {str(e)}")
#                                 continue
                        
#                         member_count = len(group_members)
#                         logger.info(f"Scroll #{scroll_count}: Found {new_members_found} new members. Total so far: {member_count}")
                        
#                         # Check if we've found new members or the page height has changed
#                         if new_members_found == 0 and current_height == previous_height:
#                             stall_count += 1
#                             logger.info(f"No new members found, stall count: {stall_count}/{max_stalls}")
#                         else:
#                             stall_count = 0  # Reset stall count if we found new members
                        
#                         # Also check if the total member count hasn't changed in several scrolls
#                         if member_count == last_count:
#                             stall_count += 1
#                             logger.info(f"Member count hasn't changed, stall count: {stall_count}/{max_stalls}")
                            
#                         previous_height = current_height
#                         last_count = member_count
                        
#                         # Add periodic longer pauses to avoid detection
#                         if scroll_count % 10 == 0:
#                             logger.info(f"Taking a longer pause after {scroll_count} scrolls")
#                             time.sleep(random.uniform(10, 15))
                
#                 logger.info(f"Completed scraping {len(group_members)} members from group: {group_name}")
#                 logger.info(f"Results saved to {members_file}")
                
#             except Exception as e:
#                 logger.error(f"Error navigating to members page: {str(e)}")
        
#         except Exception as e:
#             logger.error(f"Error scraping group members: {str(e)}")
        
#         logger.info(f"Total members scraped: {len(all_members)}")
#         return all_members
    
#     def scrape_page_followers(self, page_url):
#         """Scrape all followers from a Facebook page"""
#         logger.info(f"Starting to scrape followers from page: {page_url}")
#         all_followers = []
        
#         # Create a unique filename for this page
#         page_id = page_url.split('/')[-1] if page_url[-1] != '/' else page_url.split('/')[-2]
#         followers_file = f"page_followers_{page_id}_{self.timestamp}.csv"
        
#         try:
#             # First navigate to the page
#             self.driver.get(page_url)
#             time.sleep(random.uniform(5, 7))
            
#             # Get page name
#             try:
#                 page_name_element = WebDriverWait(self.driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, "//h1"))
#                 )
#                 page_name = page_name_element.text.strip()
#                 logger.info(f"Page name: {page_name}")
#             except:
#                 page_name = "Hazara Page"
#                 logger.warning("Could not find page name, using default")
            
#             # Try to find or navigate to followers section
#             try:
#                 # Try different ways to find the followers link
#                 followers_found = False
                
#                 # Try direct navigation to followers page
#                 followers_url = f"{page_url}/followers"
#                 logger.info(f"Directly navigating to followers URL: {followers_url}")
#                 self.driver.get(followers_url)
#                 time.sleep(random.uniform(3, 5))
                
#                 # Check if we're on followers page
#                 if "This content isn't available" in self.driver.page_source:
#                     logger.warning("Followers section not accessible. Trying community page instead.")
                    
#                     # Try to navigate to community page which might have followers/members
#                     community_url = f"{page_url}/community"
#                     self.driver.get(community_url)
#                     time.sleep(random.uniform(3, 5))
                
#                 logger.info("Attempting to scrape follower/community data")
                
#                 # Now scrape whatever followers/members are visible
#                 page_followers = []
#                 previous_height = 0
#                 stall_count = 0
#                 max_stalls = 8
#                 scroll_count = 0
#                 follower_count = 0
#                 last_count = 0
                
#                 # Create and open CSV file for writing
#                 with open(followers_file, 'w', newline='', encoding='utf-8') as f:
#                     writer = csv.DictWriter(f, fieldnames=["name", "profile_url", "source_name", "source_url"])
#                     writer.writeheader()
                
#                     # Keep scrolling until we've hit stall limit
#                     while stall_count < max_stalls:
#                         # Scroll down
#                         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                         time.sleep(random.uniform(3, 5))
#                         scroll_count += 1
                        
#                         # Get new scroll height
#                         current_height = self.driver.execute_script("return document.body.scrollHeight")
                        
#                         # Find follower elements with various patterns
#                         follower_elements = []
#                         try:
#                             # Try different patterns to find user links
#                             patterns = [
#                                 "//div[contains(@class, 'x1n2onr6')]//a[contains(@href, '/user/') or contains(@href, '/profile.php')]",
#                                 "//div[@role='article']//a[contains(@href, '/user/') or contains(@href, '/profile.php')]",
#                                 "//div[@role='main']//a[contains(@href, '/user/') or contains(@href, '/profile.php')]",
#                                 "//a[contains(@href, '/user/') or contains(@href, '/profile.php')]"
#                             ]
                            
#                             for pattern in patterns:
#                                 elements = self.driver.find_elements(By.XPATH, pattern)
#                                 if elements:
#                                     follower_elements = elements
#                                     break
#                         except Exception as e:
#                             logger.error(f"Error finding follower elements: {str(e)}")
                        
#                         new_followers_found = 0
                        
#                         # Process follower elements
#                         for element in follower_elements:
#                             try:
#                                 # Get follower name and URL
#                                 try:
#                                     follower_name = element.text.strip()
#                                     # If name is empty, try to find name in a child element
#                                     if not follower_name:
#                                         name_elements = element.find_elements(By.XPATH, ".//span")
#                                         for name_elem in name_elements:
#                                             if name_elem.text.strip():
#                                                 follower_name = name_elem.text.strip()
#                                                 break
#                                 except:
#                                     continue  # Skip if can't get name
                                
#                                 follower_url = element.get_attribute("href")
                                
#                                 # Clean up follower URL to remove parameters
#                                 if follower_url and '?' in follower_url:
#                                     follower_url = follower_url.split('?')[0]
                                
#                                 # Skip links that don't look like profile URLs or don't have names
#                                 if not follower_name or not follower_url or not ('/user/' in follower_url or '/profile.php' in follower_url):
#                                     continue
                                    
#                                 # Skip if already found this follower
#                                 if any(f['name'] == follower_name and f['profile_url'] == follower_url for f in page_followers):
#                                     continue
                                
#                                 # Add follower to our list
#                                 follower_info = {
#                                     "name": follower_name,
#                                     "profile_url": follower_url,
#                                     "source_name": page_name,
#                                     "source_url": page_url
#                                 }
#                                 page_followers.append(follower_info)
#                                 all_followers.append(follower_info)
#                                 new_followers_found += 1
                                
#                                 # Write directly to CSV
#                                 writer.writerow(follower_info)
#                                 f.flush()  # Ensure it's written to disk immediately
#                             except Exception as e:
#                                 logger.error(f"Error processing follower element: {str(e)}")
#                                 continue
                        
#                         follower_count = len(page_followers)
#                         logger.info(f"Scroll #{scroll_count}: Found {new_followers_found} new followers. Total so far: {follower_count}")
                        
#                         # Check if we've found new followers or the page height has changed
#                         if new_followers_found == 0 and current_height == previous_height:
#                             stall_count += 1
#                             logger.info(f"No new followers found, stall count: {stall_count}/{max_stalls}")
#                         else:
#                             stall_count = 0  # Reset stall count if we found new followers
                        
#                         # Also check if the total follower count hasn't changed
#                         if follower_count == last_count:
#                             stall_count += 1
#                             logger.info(f"Follower count hasn't changed, stall count: {stall_count}/{max_stalls}")
                            
#                         previous_height = current_height
#                         last_count = follower_count
                        
#                         # Add periodic longer pauses to avoid detection
#                         if scroll_count % 10 == 0:
#                             logger.info(f"Taking a longer pause after {scroll_count} scrolls")
#                             time.sleep(random.uniform(10, 15))
                
#                 logger.info(f"Completed scraping {len(page_followers)} followers from page: {page_name}")
#                 logger.info(f"Results saved to {followers_file}")
                
#             except Exception as e:
#                 logger.error(f"Error navigating to followers section: {str(e)}")
        
#         except Exception as e:
#             logger.error(f"Error scraping page followers: {str(e)}")
        
#         logger.info(f"Total followers scraped: {len(all_followers)}")
#         return all_followers
    
#     def _human_type(self, element, text):
#         """Type like a human with random delays between keystrokes"""
#         for char in text:
#             element.send_keys(char)
#             time.sleep(random.uniform(0.05, 0.2))
    
#     def close(self):
#         """Close the browser"""
#         self.driver.quit()

# def main():
#     # Facebook credentials
#     email = ""
#     password = ""
    
#     # Target URLs
#     group_url = "https://www.facebook.com/groups/1225720981272765"
#     page_url = "h"
    
#     logger.info("Starting Hazara Facebook Scraper")
    
#     # Initialize scraper
#     scraper = HazaraScraper(email, password, headless=False)
    
#     try:
#         # Login to Facebook
#         if not scraper.login():
#             logger.error("Login failed. Exiting.")
#             return
        
#         # Scrape group members first
#         logger.info(f"Starting to scrape group: {group_url}")
#         group_members = scraper.scrape_group_members(group_url)
#         logger.info(f"Group scraping completed. Found {len(group_members)} members.")
        
#         # Then scrape page followers
#         logger.info(f"Starting to scrape page: {page_url}")
#         page_followers = scraper.scrape_page_followers(page_url)
#         logger.info(f"Page scraping completed. Found {len(page_followers)} followers.")
        
#         # Calculate total unique people
#         all_profiles = {}
#         for member in group_members:
#             profile_url = member['profile_url']
#             if profile_url not in all_profiles:
#                 all_profiles[profile_url] = member
                
#         for follower in page_followers:
#             profile_url = follower['profile_url']
#             if profile_url not in all_profiles:
#                 all_profiles[profile_url] = follower
        
#         logger.info(f"Total unique profiles found: {len(all_profiles)}")
        
#         # Save combined unique profiles
#         combined_file = f"fun_page_hazaratown{scraper.timestamp}.csv"
#         with open(combined_file, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.DictWriter(f, fieldnames=["name", "profile_url", "source_name", "source_url"])
#             writer.writeheader()
#             for profile in all_profiles.values():
#                 writer.writerow(profile)
        
#         logger.info(f"Combined unique profiles saved to: {combined_file}")
        
#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")
    
#     finally:
#         # Close the browser
#         scraper.close()

# if __name__ == "__main__":
#     main()
import time
import random
import logging
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hazara_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

class HazaraScraper:
    def __init__(self, email, password, headless=False):
        self.email = email
        self.password = password
        
        # Configure browser options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        
        # Add arguments to appear as normal browser and improve performance
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.page_load_strategy = 'eager'  # Don't wait for all resources to load
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(user_agents)})
        
        # Output files
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def login(self):
        """Log in to Facebook"""
        logger.info("Attempting to login to Facebook")
        try:
            self.driver.get("https://www.facebook.com/")
            time.sleep(random.uniform(1, 2))  # Reduced wait time
            
            # Handle cookies popup if it appears
            try:
                cookies_button = WebDriverWait(self.driver, 3).until(  # Reduced wait time
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All') or contains(text(), 'Allow')]"))
                )
                cookies_button.click()
                time.sleep(random.uniform(0.5, 1))  # Reduced wait time
            except:
                logger.info("No cookies prompt detected or already handled")
            
            # Enter email
            email_field = WebDriverWait(self.driver, 5).until(  # Reduced wait time
                EC.presence_of_element_located((By.ID, "email"))
            )
            self._human_type(email_field, self.email, fast=True)  # Using faster typing
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "pass")
            self._human_type(password_field, self.password, fast=True)  # Using faster typing
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))  # Reduced wait time
            
            # Check if login successful
            if "login" in self.driver.current_url:
                logger.error("Login failed - still on login page")
                return False
                
            logger.info("Successfully logged in to Facebook")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def scrape_group_members(self, group_url, batch_size=1000, max_members=None):
        """
        Scrape all members from a Facebook group with optimizations for large groups
        - batch_size: Save results in batches to avoid memory issues
        - max_members: Optional limit to stop after certain number (for testing)
        """
        logger.info(f"Starting to scrape members from group: {group_url}")
        all_members = []
        
        # Create a unique filename for this group
        group_id = group_url.split('/')[-1]
        members_file = f"group_members_{group_id}_{self.timestamp}.csv"
        
        try:
            # Direct navigation to members page
            members_url = f"{group_url}/members"
            logger.info(f"Directly navigating to members URL: {members_url}")
            self.driver.get(members_url)
            time.sleep(random.uniform(2, 3))
            
            # Get group name
            try:
                group_name_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//h1"))
                )
                group_name = group_name_element.text.strip()
                logger.info(f"Group name: {group_name}")
            except:
                group_name = "Hazara Group"
                logger.warning("Could not find group name, using default")
            
            # Now on the members page, prepare to scrape
            group_members = []
            previous_height = 0
            stall_count = 0
            max_stalls = 5  # Reduced to improve speed while still being thorough
            scroll_count = 0
            member_count = 0
            last_count = 0
            
            # Create and open CSV file for writing
            with open(members_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["name", "profile_url", "source_name", "source_url"])
                writer.writeheader()
                
                # Keep scrolling until we've hit stall limit or max members
                while stall_count < max_stalls and (max_members is None or member_count < max_members):
                    # Faster scroll method using JavaScript
                    for _ in range(3):  # Multiple small scrolls instead of one big one
                        self.driver.execute_script("window.scrollBy(0, 1000);")
                        time.sleep(0.3)  # Brief pause between scrolls
                    
                    scroll_count += 1
                    
                    # Get new scroll height
                    current_height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    # Find member elements - using more optimized XPath pattern
                    member_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/user/') or contains(@href, '/profile.php')]")
                    
                    new_members_found = 0
                    members_to_process = []
                    
                    # Quickly collect members info first
                    for element in member_elements:
                        try:
                            member_name = element.text.strip()
                            member_url = element.get_attribute("href")
                            
                            # Skip if empty or invalid
                            if not member_name or not member_url:
                                continue
                            
                            # Clean up member URL to remove parameters
                            if '?' in member_url:
                                member_url = member_url.split('?')[0]
                            
                            # Skip links that don't look like profile URLs
                            if not ('/user/' in member_url or '/profile.php' in member_url):
                                continue
                            
                            # Skip if already found this member
                            if member_url in [m.get('profile_url') for m in group_members]:
                                continue
                            
                            # Add to processing list
                            members_to_process.append((member_name, member_url))
                            
                        except Exception as e:
                            continue
                    
                    # Process members in parallel using ThreadPoolExecutor for CPU-bound tasks
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        for member_name, member_url in members_to_process:
                            # Add member to our list
                            member_info = {
                                "name": member_name,
                                "profile_url": member_url,
                                "source_name": group_name,
                                "source_url": group_url
                            }
                            group_members.append(member_info)
                            all_members.append(member_info)
                            new_members_found += 1
                            
                            # Write to CSV
                            writer.writerow(member_info)
                    
                    # Flush the file after processing batch
                    f.flush()
                    
                    member_count = len(group_members)
                    logger.info(f"Scroll #{scroll_count}: Found {new_members_found} new members. Total so far: {member_count}")
                    
                    # Save intermediate results in batches to reduce memory usage
                    if member_count % batch_size == 0:
                        logger.info(f"Reached {member_count} members, saving intermediate results")
                        f.flush()
                        
                        # Optional: pause to avoid detection
                        if scroll_count % 20 == 0:
                            logger.info(f"Taking a short pause after {scroll_count} scrolls")
                            time.sleep(random.uniform(2, 4))
                    
                    # Check for stall conditions
                    if (new_members_found == 0 and current_height == previous_height) or member_count == last_count:
                        stall_count += 1
                        logger.info(f"No new members found, stall count: {stall_count}/{max_stalls}")
                    else:
                        stall_count = 0
                    
                    previous_height = current_height
                    last_count = member_count
                    
                    # Stop if we've reached max_members
                    if max_members is not None and member_count >= max_members:
                        logger.info(f"Reached maximum number of members to scrape: {max_members}")
                        break
                    
                    # Add occasional slightly longer pause to avoid detection but keep speed
                    if scroll_count % 30 == 0:
                        time.sleep(random.uniform(3, 5))
            
            logger.info(f"Completed scraping {len(group_members)} members from group: {group_name}")
            logger.info(f"Results saved to {members_file}")
            
        except Exception as e:
            logger.error(f"Error scraping group members: {str(e)}")
        
        logger.info(f"Total members scraped: {len(all_members)}")
        return all_members
    
    def _human_type(self, element, text, fast=False):
        """Type like a human with random delays between keystrokes"""
        if fast:
            # Faster typing for better performance
            chunk_size = 3  # Type 3 characters at a time
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                element.send_keys(chunk)
                time.sleep(random.uniform(0.01, 0.05))  # Very brief pause
        else:
            # Original slower, more human-like typing
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    # Facebook credentials
    email = ""
    password = ""
    
    # Target URL - group with 61k members
    group_url = "https://www.facebook.com/groups/1225720981272765"
    
    logger.info("Starting Optimized Hazara Facebook Scraper for 61k member group")
    
    # Initialize scraper - using headless for better performance
    # Set to True for production runs where you don't need to see the browser
    scraper = HazaraScraper(email, password, headless=False)
    
    try:
        # Login to Facebook
        if not scraper.login():
            logger.error("Login failed. Exiting.")
            return
        
        # Scrape group members with optimizations
        # Batch size of 2000 members per save to avoid memory issues
        # Uncomment max_members line for testing with smaller sample
        logger.info(f"Starting to scrape large group: {group_url}")
        group_members = scraper.scrape_group_members(
            group_url, 
            batch_size=2000,
            # max_members=5000  # Uncomment to limit scraping for testing
        )
        
        logger.info(f"Group scraping completed. Found {len(group_members)} members.")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    
    finally:
        # Close the browser
        scraper.close()

if __name__ == "__main__":
    main()
