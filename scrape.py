from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

def timestamped_print(message):
    print(f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) - {message}")

def connect_to_mysql():
    try:
        cnx = mysql.connector.connect(user=os.getenv('MYSQL_USER'), 
                                      password=os.getenv('MYSQL_PASSWORD'),
                                      host=os.getenv('MYSQL_HOST'), 
                                      database=os.getenv('MYSQL_DATABASE'),
                                      charset='utf8mb4',
                                      collation='utf8mb4_general_ci')
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            timestamped_print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            timestamped_print("Database does not exist")
        else:
            timestamped_print(err)
        return None

def ensure_table_exists(cursor):
    table_description = """
    CREATE TABLE IF NOT EXISTS PowerBIData (
        Year INT PRIMARY KEY,
        Jan VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Feb VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Mar VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Apr VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        May VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Jun VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Jul VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Aug VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Sep VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Oct VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Nov VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        `Dec` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
        Total VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
    )"""
    try:
        timestamped_print("Creating table PowerBIData...")
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        timestamped_print(f"Failed creating table: {err}")

def data_exists(cursor, year):
    query = "SELECT * FROM PowerBIData WHERE Year = %s"
    cursor.execute(query, (year,))
    return cursor.fetchone()

def update_data(cursor, existing_data, new_data):
    update_query = """
    UPDATE PowerBIData
    SET Jan = %s,
        Feb = %s,
        Mar = %s,
        Apr = %s,
        May = %s,
        Jun = %s,
        Jul = %s,
        Aug = %s,
        Sep = %s,
        Oct = %s,
        Nov = %s,
        `Dec` = %s,
        Total = %s
    WHERE Year = %s
    """
    
    # Update only if the new data is not None and the existing data is None or empty
    updated_data = []
    for i in range(1, len(new_data)):
        if new_data[i] is not None and (existing_data[i] is None or existing_data[i].strip() == ''):
            updated_data.append(new_data[i])
        else:
            updated_data.append(existing_data[i])
        timestamped_print(f"Field {i} update: Existing: {existing_data[i]}, New: {new_data[i]}, Update to: {updated_data[-1]}")  # Debug print for each field
    
    cursor.execute(update_query, updated_data + [new_data[0]])

def insert_data(cursor, data):
    add_data = ("INSERT INTO PowerBIData "
                "(Year, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, `Dec`, Total) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(add_data, data)

def scrape_powerbi_table():
    try:
        timestamped_print("Setting up the Selenium WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver_service = ChromeService()
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)

        timestamped_print("Opening the Power BI report URL...")
        url = "https://app.powerbi.com/view?r=eyJrIjoiMzJjOTA2MjYtNjA0My00ZGU4LWE5MDktYWQyODRhZWNiM2MyIiwidCI6IjlkMGRjYTFlLTAzODQtNGRhNS1hNWMwLWQxNGI5YWExZDk5ZCIsImMiOjN9&wmode=transparent"
        driver.get(url)

        timestamped_print("Waiting for the table to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/report-embed/div/div/div[1]/div/div/div/exploration-container/div/div/docking-container/div/div/div/div/exploration-host/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[10]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div[1]/div[2]/div"))
        )
        timestamped_print("Table loaded successfully.")

        timestamped_print("Getting the page source...")
        page_source = driver.page_source

        timestamped_print("Parsing the page source with BeautifulSoup...")
        soup = BeautifulSoup(page_source, 'html.parser')

        timestamped_print("Finding the table element...")
        table = soup.select_one("div[role='row']")
        if table is None:
            timestamped_print("Error: Table element not found.")
            return

        headers = ["Year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Total"]

        timestamped_print("Extracting the rows...")
        rows = []
        table_rows = soup.select("div[role='row']")
        if not table_rows:
            timestamped_print("Error: No table rows found.")
            return

        for row in table_rows:
            row_header = row.find("div", {"role": "rowheader"})
            if row_header:
                row_data = [int(row_header.text)]
                grid_cells = row.find_all("div", {"role": "gridcell"})
                row_data.extend([cell.text if cell.text.strip() != '\xa0' else None for cell in grid_cells])
                timestamped_print(f"Extracted row data: {row_data}")
                rows.append(row_data)
            else:
                timestamped_print("No rowheader found in row.")

        timestamped_print("Connecting to MySQL...")
        cnx = connect_to_mysql()
        if cnx is None:
            return

        cursor = cnx.cursor()
        ensure_table_exists(cursor)

        timestamped_print("Inserting or updating data in MySQL...")
        for row_data in rows:
            year = row_data[0]
            existing_data = data_exists(cursor, year)
            timestamped_print(f"Existing data for year {year}: {existing_data}")
            if existing_data:
                update_data(cursor, existing_data, row_data)
                timestamped_print(f"Updated data for year {year}")
            else:
                insert_data(cursor, row_data)
                timestamped_print(f"Inserted data for year {year}")
            cnx.commit()

        cursor.close()
        cnx.close()
        timestamped_print("Data insertion complete.")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_powerbi_table()
