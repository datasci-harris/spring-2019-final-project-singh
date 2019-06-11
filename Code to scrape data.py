# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 20:41:32 2019

@author: adminuser
"""
#the project's intention is to scrape data from Indian election 2019 for each of the 542 constituencies, and regress
#margin of victory in each constituency on a few different independent variables. 
#the independent variables are: total number of votes cast in each constituency, total number of candidates in each constituency

#there are two sets of URLs from which data has been scraped: 1. http://results.eci.gov.in/pc/en/trends/statewiseU011.htm; 
#2. http://results.eci.gov.in/pc/en/constituencywise/ConstituencywiseS033.htm
#the above two URLs change their numbers to show data for different constituencies 


import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#page_number, code_of_state and state_ut are to access different URLs from which scraping has to be done
#max value of page_number = 80 and max value of code_of_state = 29
#code_of_state = 09 has been dropped from this analysis because of the anomalous structure of the page (its additional column 'migrant votes' makes scraping difficult)
page_number = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44','45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80']
code_of_state = ['01', '02', '03', '04', '05', '06', '07', '08', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29']
#'S' is for states, and 'U' is for Union Territories
state_ut = ['S', 'U']

#this method scrapes three variables - number of candidates, total votes polled and name of constituency - for each constituency
def scrape_name_candidates_votes():
    #declaring empty lists for each of the variables to be scraped
    #the first variable to be scraped is name of constituency
    name_of_const = []
    #the tentative variables for name of constituency are used to get to the final name 
    tentative1_name_of_const = []
    tentative2_name_of_const = []
    #the second variable to be scraped is number of candidates in each constituency
    number_of_candidates = []
    #the third variable to be scraped is total votes polled in each constituency
    total_votes = []
    #td_list is used to scrape td tags, in order to append total_votes 
    td_list = []

    for j in (code_of_state):
        for i in (page_number):
            for k in (state_ut):  
                #the variable page goes to each URL
                page = requests.get('http://results.eci.gov.in/pc/en/constituencywise/Constituencywise' + k + j + i +'.htm')
                soup = BeautifulSoup(page.content, 'html.parser')
                #the next three lines of code scrape number of candidates in each constituency
                #full_table scrapes the HTML code for each row except the last; each row is depicted by the tr tag "font-size:12px;" 
                #the first column of each row contains the serial number of candidate; number of candidates is equal to 
                #the final serial number, which is equal to length of full_table
                full_table = soup.find_all(attrs={"style":"font-size:12px;"})
                #the if condition below is to deal with the fact that full_table will take null values for all URLs that don't exist
                #for example, the URL with code_of_state = 02 and page_number = 3 does not exist
                if (len(full_table) is not 0):
                    number_of_candidates.append(len(full_table))
                # the next 4 lines scrape total votes polled in each constituency
                vote_row = soup.find(attrs={"style":"color: #fff; background: #105980; border-color:#673033; border-width:1px;border-style:Solid;font-family:Calibri;"})
                if (vote_row is not None):
                        td_list = vote_row.find_all("td")
                        total_votes.append(td_list[5].get_text())
                name_row = soup.find(class_="table-party")
                #the if condition used below is used to deal with the issue of null values, as done above
                if (name_row is not None):
                    tentative1_name_of_const.append(name_row.find("tr").get_text())
                    # the name is split on "-" because it's initially scraped as <Name of State-Name of Constituency>
                    tentative2_name_of_const.append(tentative1_name_of_const[-1].strip().split("-"))     
    #the tuple is used to extract Name of Constituency after splitting on "-"
    temporary_tuple = tuple(tentative2_name_of_const)
    name_of_const = [t[1] for t in temporary_tuple]
    combined_name_candidates_votes = list(zip(name_of_const, number_of_candidates, total_votes))
    #print(combined_name_candidates_votes)
    return (combined_name_candidates_votes)

#this function writes name of constituency, number of candidates and total votes polled to a CSV file
def write_first_csv_file():
    combined_name_candidates_votes = scrape_name_candidates_votes()
    
    with open('const_candidates_votes.csv', 'w') as csvFile:
       w = csv.writer(csvFile)
       w.writerow(['Constituency', 'Candidates', 'Votes'])
       for data in combined_name_candidates_votes:
           if data:
               w.writerow(data)
write_first_csv_file()

#this method scrapes three variables - margin of victory of winning candidate, party of winning candidate and name of constituency - for each constituency

def scrape_name_margin_party():
    name_of_const = []
    margin = []
    party_name = []

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
            
    combined_name_margin_party = list(zip(name_of_const, margin, party_name))
    #print(combined_name_margin_party)        
    return(combined_name_margin_party)

#this function writes name of constituency, margin of victory and party of winning candidate to a CSV file
def write_second_csv_file():
    combined_name_margin_party = scrape_name_margin_party
    with open('const_margin_party.csv', 'w') as csvFile:
       w = csv.writer(csvFile)
       w.writerow(['Constituency', 'Margin', 'Party'])
       for data in combined_name_margin_party:
           if data:
               w.writerow(data)
    
write_second_csv_file    
