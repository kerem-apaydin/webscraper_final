**This project was finalized earlier than originally.**

# Web Scraper Final Project

This is a Python-based web scraping project developed to extract supplier-based product data from the official website of the Turkish State Supply Office (DMO). It uses `requests` and `BeautifulSoup4` for scraping and provides a clean Flask-based web interface for displaying the results.

## Features

- Supplier-based product data extraction
- Price change tracking and historical data logging
- Product and price history stored in JSON format
- Modern card-based grid layout with search and sort options
- Filter products by supplier via sidebar
- Old price display if any change is detected
- Daily automatic updates using APScheduler
- Fast and retry-safe scraping with fallback logic



Web scraping is inherently site-specific. The logic, structure, and parsing strategy used in this project are tailored to the current HTML layout of the DMO website. If the target site changes its structure or if the scraper is adapted to a different website, significant modifications to the scraping code may be necessary.

## Possible Future Extensions

##### Important Note on Web Scraping

Web scraping is inherently site-specific. The logic, structure, and parsing strategy used in this project are tailored to the current HTML layout of the DMO website. If the target site changes its structure or if the scraper is adapted to a different website, significant modifications to the scraping code may be necessary.

##
The architecture of this project was significantly simplified during development. As a result, certain features originally planned were not implemented because they became unnecessary. 
However, if the scraping logic is changed again or extended to different websites, the following additions may become relevant:


- Handling complex multi-supplier comparisons dynamically
- Integration with a relational database (e.g., PostgreSQL) instead of JSON files
- Per-product historical charting (price over time)
- Pagination control for very large datasets
- Authentication for admin-level manual edits
- Exporting filtered results as PDF or Excel


## Installation

1. Clone the repository:

```bash
git clone https://github.com/kerem-apaydin/webscraper_final.git
cd webscraper_final
