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
