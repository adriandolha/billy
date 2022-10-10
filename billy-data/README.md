# Billy Data
Does the heavy work, consumes events and triggers jobs to process, transform and load data. 
It uses tabula to extract data from bank statements pdf, then pandas for data cleansing and transformations.
The final data frame (category, date, desc, amount) is saved in the data bucket where it's consumed by the API.

## Deployment
It uses AWS SAM for deployment. 
