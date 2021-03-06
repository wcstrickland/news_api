## Phase 1
Created a web scraping program that requests html from a major news outlet and then parses the request return via tags. The result is a json like object that includes:
* the date and time the article was printed in UTC
* The single word topic
* The main headline
* The one sentence sub headline
* And the URL for the article.
 
This information is then compared against a data base and if any of the scraped articles are not currently in the database they are added.
I created a batch file that executes automatically through windows scheduler (or chron for mac) every hour to constantly update the database.

![alt text](https://github.com/wcstrickland/news_api/blob/main/example2.png)

## Phase 2
Created a front facing API that allows users to search the data base with high level of specificity through a series of endpoints. The API supports programmatic access via endpoints or simple query string search.
## Phase 3 
Created a simple static html page with a brief description of the API’s endpoints and provided examples on how to properly use them. 

![alt text](https://github.com/wcstrickland/news_api/blob/main/home_page_img.png)
