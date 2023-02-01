# Springboard Capstone Project: Predicting London Property Prices
### By: Jaye
---
## Background:

My challenge was to be able to predict, as accurately as possible, the price of any property based in London, using publicly available data.

## Process:

### Defining My Project: 
My first step was deciding what I would do as a capstone project. I ultimately decided upon a property prediction process, with the following remit:

**_Idea: A Machine Learning Regressor which can predict London House Prices_**

_A machine learning regressor which can predict London house prices based on features of the house, surrounding area, and other identifiable features._

_Data can be collected from real estate websites, open source datasets, and/or paid data.
Website scraping can be used to collect information._

### Choosing Data Collection techinques
I ultimately decided that I would obtain feature data using a popular estate agent website's property listings and prices.
<br><br>I use three kinds of dataset from the website:
* Basic listings data
  * This is the data that appears in a search results page, and lists basic information about a property, such as number of bedrooms, bathrooms, and property price
  * This data is in the form of a webpage, and requires the data to be scraped, segmented, cleaned, and refined into a dataset for analysis and machine learning ingestion.
* Detailed listing data
  * This is the data for a single property listing. It includes more detailed information than on the basic listings page, and includes information such as proximity to train stations and tenure type (eg freehold vs leasehold).
  * This data is in the form of a webpage, and requires the data to be scraped, segmented, cleaned, and refined into a dataset for analysis and machine learning ingestion.
  * I was able to join this 'detailed' dataset to the 'basic' dataset using the websites unique identifier as a key, using Python Pandas joining functionality.
* Website datalayer model object data
  * From investigation and research, I was able to identify that my chosen website populated their webpage data using a datalayer model.  
  * This data appeared alongside the detailed listing data, but contained far more detailed data that necessarily appeared on the page. Data obtained via this method included property longitude and latitude, and key property information in a structured format.
  * This data is in the form of a datalayer model object. Despite this, it was also possible to obtain this data using standard web scraping techniques, after the necessary adaptations to my web scraping process has been made.
  * I was able to join this 'advanced' dataset to the other datasets using the websites unique identifier as a key, using Python Pandas joining functionality.
<br/><br/>

##### More information about the data collection techniques utilised:<br>[summary of dataset options.md](capstone_steps%2Fstep_02%2Fsummary%20of%20dataset%20options.md)

##### More information about my project proposal:<br>[04_project_proposal.md](capstone_steps%2Fstep_04%2F04_project_proposal.md)

##### More information wrangling and cleaning my data: <br>[05__data_wrangling.md](capstone_steps%2Fstep_05%2F05__data_wrangling.md)


## Running the WebApp
### Running the WebApp Remotely

You can access the running demo of the webapp at:
https://jayportfolio-webapp-capstone-app-0526gb.streamlit.app/

### Running the WebApp Locally

Download this repository and ensure you have the dependencies listed in [requirements.txt](requirements.txt).

To run the Streamlit app, run:<br>
`streamlit run app.py`