# Step 4: Project Proposal
### Overview of Capstone Proposal
The project I’m planning to solve is being able to predict what the asking price will be for a property placed on the market.

I believe that it should be possible to identify key criteria associated with a London property, and use that criteria as data which can be used to train a machine learning model (or series/ensemble of models) in order to make astute predictions about the price of properties which the model has never seen. 

I will be testing this hypothesis over the course of my capstone project, while additionally creating an overall engineering solution which creates a deployable solution which could be used in a productionised manner. I will use best practice commercial tools which will enable me to provide an end-to-end tool which is usable by an end user to make predictions on the expected asking price of a London property, by supplying my system with the necessary input data.


I will be analysing properties being solved in London, and identifying key features of those properties to create a model which is capable of predicting newer properties which come onto the market.

As a prospective property buyer in London, this project is interesting to me because I would like to get a deeper understanding of what features and traits of properties are important in what makes a property valuable, and which are less so.

To create my model, I will need to acquire feature data about existing properties in order to train my model. I expect the bulk of my data collection will be acquired by interrogating estate agent websites (using web scraping technology) for both the target data (asking price) and feature data for properties. 

The predictors, or features, will be constrained by two main factors:
* What informational datasets it is possible to gain, in relation to the properties I will be analysing. Reasons it may not be possible to gain information which may be relevant include:
  * The data does not exist
  * The data does not exist in an electronic form, or an electronic form which is feasible to capture or use
  * The data is not publicly available
  * The data is publicly available but not possible to capture in a batch-usable form
* Whether it is possible to obtain that data within the time available for the project

Over the course of the project, I will discover which of these limitations apply for my project, and devise how to mitigate these restrictions to produce a model and machine learning product which remains usable and provides valuable insight.
### Collecting Data
I believe that I should be able to get many of the following data about properties in order to train my model:
* Number of bedrooms
* Number of bathrooms
* Location of property (either borough, postcode, or latitude/longitude)
* Whether property is new or resale
* Type of property (House, Apartment)
* Ownership type (Leasehold or Freehold)
* Distance to public transport
* Anecdotal information about key features of the property (Garden)
* Property age
* Property size

I will augment and enrich this data with other sources as and when necessary to refine the model. Potential options for additional data include historical prices paid for property, crime figures for London boroughs, proximity to good and outstanding schooling, property age records, and access to green space.

### Defining the problem type
This will be a supervised regression problem. The project will be geared towards minimising the error when predicting the asking price of a property, given the associated features for that property.

(The data will ultimately be sufficient to re-model as a classification problem, such as predicting whether a property is more or less than a particular price point. This may pose an additional challenge for the capstone project should time permit.)

I will use traditional machine learning approaches initially, and may delve into deep learning approaches if deemed appropriate.

### Architecting the solution
I anticipate that my final deliverable will be an API and/or webapp. The aim is to create a self-contained product which is capable of being consumed by a computational/human third-party.

I will use GitHub for the storage and publication of this project. 
Whether the entire project will be a single repository or a series of repositories is yet to be determined, but the overall github account is available at https://github.com/jayportfolio.
