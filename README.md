
# GRT Dashboard Grabber

GRT Dashboard Grabber is a Python-based tool designed to scrape data from Power BI dashboards and store the extracted data in a MySQL/MariaDB database. This project leverages Selenium for browser automation and BeautifulSoup for HTML parsing for data manipulation.

## Features

- Automatically open and scrape data from a specified Power BI report URL.
- Extract and clean tabular data from the report.
- Stores or updates the extracted data in a MySQL/MariaDB database.
- Ensure data is not duplicated in the database.

## Requirements

- Python 3.6 or higher
- Google Chrome
- ChromeDriver

## Installation

1. **Clone the repository:**
   
   - git clone https://github.com/vicelikedust/GRT_Dashboard_Grabber.git && cd GRT_Dashboard_Grabber
   

2. **Install the required Python packages:**
   
   - pip install -r requirements.txt
   

3. **Set up your `.env` file:**
   Create a `.env` file in the project directory and add your MySQL/MariaDB credentials:
   
   - MYSQL_USER=your_username
   - MYSQL_PASSWORD=your_password
   - MYSQL_HOST=your_host
   - MYSQL_DATABASE=your_database
   

## Usage

1. **Run the script:**
   
   - python scrape.py
   

2. The script will open the specified Power BI report URL, scrape the data, and insert it into the MySQL/MariaDB database.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Acknowledgments

- [Selenium](https://www.selenium.dev/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
