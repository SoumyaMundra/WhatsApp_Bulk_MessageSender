import pandas as pd
import time
import urllib.parse
import os
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------------
# 🗂️ File picker: Choose attachments
# -----------------------------------
root = tk.Tk()
root.withdraw()  # Hide main window

attachment_paths = filedialog.askopenfilenames(
    title="Select file(s) to send as attachments"
)
ATTACHMENT_PATHS = list(attachment_paths)

# ------------------------
# 🕒 Delay between messages
# ------------------------
DELAY = 5  # Seconds

# --------------------------
# 📋 Load contacts from CSV
# --------------------------
# CSV must have: phone_number,name,message columns
data = pd.read_csv("contacts.csv")

# -------------------------
# 🌐 Launch Chrome with user data (to stay logged in)
# -------------------------
options = Options()
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
os.makedirs(user_data_dir, exist_ok=True)
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://web.whatsapp.com")
input("Scan QR code (if needed), then press Enter to continue...")

# ------------------------------------------
# 📤 Function to send message and attachments
# ------------------------------------------
def send_message(phone, name, message):
    try:
        custom_msg = message.replace("{name}", name)
        encoded_msg = urllib.parse.quote(custom_msg)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"

        driver.get(url)
        time.sleep(DELAY + 2)

        # Wait for send button to appear, then click
        send_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_btn.click()
        print(f"✅ Message sent to {name} ({phone})")

        # Send each attachment
        for attachment_path in ATTACHMENT_PATHS:
            if not os.path.exists(attachment_path):
                print(f"❌ File does not exist: {attachment_path}")
                continue

            print(f"📎 Attaching file: {attachment_path}")

            attach_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span' ))
            )
            attach_btn.click()
            time.sleep(1)

            media_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
            )
            media_input.send_keys(attachment_path)
            time.sleep(2)

# Click the send button for media preview
            send_media_btn = WebDriverWait(driver, 20).until(
                 EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_media_btn.click()
            print(f"📎 Attachment sent to {name} ({phone})")
            time.sleep(2)
    
    except Exception as e:
        print(f"❌ Failed to send to {phone}: {e}")

    time.sleep(DELAY)

# ----------------------
# 🔁 Loop through contacts
# ----------------------
for index, row in data.iterrows():
    send_message(str(row['phone_number']), row['name'], row['message'])

print("\n✅ All messages and attachments sent!")
driver.quit()
