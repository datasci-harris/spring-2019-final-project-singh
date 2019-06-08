# Intro to Programming for Public Policy
# PPHA 30550


## Final Project: Reproducible Research
## Spring 2019


## Due: Monday, June 10th on GitHub Classrooms

#the project's intention is to scrape data from Indian election 2019 for each of the 542 constituencies, and regress margin of victory in each constituency on a few different independent variables. 
# the independent variables are: total number of votes cast in the constituency, total number of candidates in the constituency
# there are two sets of URLs from which data has been scraped: 1. http://results.eci.gov.in/pc/en/trends/statewiseU011.htm; 2. http://results.eci.gov.in/pc/en/constituencywise/ConstituencywiseS033.htm

import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

#declaring empty lists for each of the variables to be scraped
#the first variable to be scraped is number of candidates in each constituency
number_of_candidates = []

#declaring lists of code of state and page numbers to deal with changing URLs
# code_of_state deals with different states whereas page_number deals with constituencies within each state
page_number = ['1', '2', '3']
code_of_state = ['01', '02']

# 'S' is for states whereas 'U' is for Union Territories
state_ut = ['S', 'U']


for j in (code_of_state):
    for i in (page_number):
        for k in (state_ut): 
          # page iterates over the changing URLs
          page = requests.get('http://results.eci.gov.in/pc/en/constituencywise/Constituencywise' + k + j + i +'.htm')
          soup = BeautifulSoup(page.content, 'html.parser')
          full_table = soup.find_all(attrs={"style":"font-size:12px;"})
          for td in full_table:
            candidates.append(td.find(attrs={"align":"center"}).get_text())
          number_of_candidates = number_of_candidates + [candidates[-1]]          
          vote_row = soup.find(attrs={"style":"color: #fff; background: #105980; border-color:#673033; border-width:1px;border-style:Solid;font-family:Calibri;"})
          if (vote_row is not None):
            td_list = vote_row.find_all("td")
            total_votes.append(td_list[5].get_text())
          name_row = soup.find(class_="table-party")
          if (name_row is not None):
            tentative1_name_of_const.append(name_row.find("tr").get_text())
            tentative2_name_of_const.append(tentative1_name_of_const[-1].strip().split("-"))  
 
 
 
for j in (code_of_state):
    for i in (page_number):
        for k in (state_ut):   
            page = requests.get('http://results.eci.gov.in/pc/en/trends/statewise' + k + j + i + '.htm')
            soup = BeautifulSoup(page.content, 'html.parser')
            full_table = soup.find_all(attrs={"style":"font-size:12px;"})
            for td in full_table:
                name_of_const.append(td.find('td').get_text())
                margin.append(td.find(attrs={"align":"right"}).get_text())
                party_name.append(td.find("tbody").find("td").get_text())

combined = zip(name_of_const, margin, party_name)
df_const_margin_party = pd.DataFrame(np.array(combined), columns = list("abc"))
df_const_margin_party.columns = ['Constituency', 'Margin', 'Party']
   
      
