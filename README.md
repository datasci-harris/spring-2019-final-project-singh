# Intro to Programming for Public Policy
# PPHA 30550


## Final Project: Reproducible Research
## Spring 2019


## Due: Monday, June 10th on GitHub Classrooms

#the project's intention is to scrape data from Indian election 2019 for each of the 542 constituencies, and regress margin of victory in each constituency on a few different independent variables. 
#the independent variables are: total number of votes cast in each constituency, total number of candidates in each constituency

#there are two sets of URLs from which data has been scraped: 1. http://results.eci.gov.in/pc/en/trends/statewiseU011.htm; 2. http://results.eci.gov.in/pc/en/constituencywise/ConstituencywiseS033.htm
#the above two URLs change their numbers to show data for different constituencies 

import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import statsmodels.formula.api as sm
from sklearn import linear_model
import geopandas as gpd
import matplotlib.pyplot as plt
from pandas.tools.plotting import table


#declaring empty lists for each of the variables to be scraped
#the first variable to be scraped is number of candidates in each constituency
number_of_candidates = []

#declaring lists of code of state and page numbers to deal with changing URLs
#code_of_state deals with different states whereas page_number deals with constituencies within each state
page_number = ['1', '2', '3']
code_of_state = ['01', '02']

#'S' is for states whereas 'U' is for Union Territories
state_ut = ['S', 'U']


#this method scrapes three variables - number of candidates, total votes polled and name of constituency - for each constituency
def scrape1():
    tentative1_name_of_const = []
    tentative2_name_of_const = []
    name_of_const = []
    number_of_candidates = []
    total_votes = []
    td_list = []

    for j in (code_of_state):
        for i in (page_number):
            for k in (state_ut):  
                page = requests.get('http://results.eci.gov.in/pc/en/constituencywise/Constituencywise' + k + j + i +'.htm')
                soup = BeautifulSoup(page.content, 'html.parser')
                full_table = soup.find_all(attrs={"style":"font-size:12px;"})
                if (len(full_table) is not 0):
                    number_of_candidates.append(len(full_table))
                vote_row = soup.find(attrs={"style":"color: #fff; background: #105980; border-color:#673033; border-width:1px;border-style:Solid;font-family:Calibri;"})
                if (vote_row is not None):
                        td_list = vote_row.find_all("td")
                        total_votes.append(td_list[5].get_text())
                name_row = soup.find(class_="table-party")
                if (name_row is not None):
                    tentative1_name_of_const.append(name_row.find("tr").get_text())
                    tentative2_name_of_const.append(tentative1_name_of_const[-1].strip().split("-"))    
    temporary_tuple = tuple(tentative2_name_of_const)
    name_of_const = [t[1] for t in temporary_tuple] 
    combined_list = list(zip(name_of_const, number_of_candidates, total_votes))
    df_const_candidates_votes = pd.DataFrame(np.array(combined_list), columns = list("abc"))
    df_const_candidates_votes.columns = ['Constituency', 'Candidates', 'Votes']
    df_const_candidates_votes['Constituency'] = df_const_candidates_votes['Constituency'].str.upper()
    return(df_const_candidates_votes)

#this method scrapes three variables - margin of victory of winning candidate, party of winning candidate and name of constituency - for each constituency
def scrape2():
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
            
    combined = list(zip(name_of_const, margin, party_name))
    df_const_margin_party = pd.DataFrame(np.array(combined), columns = list("abc"))
    df_const_margin_party.columns = ['Constituency', 'Margin', 'Party']
    df_const_margin_party['Constituency'] = df_const_margin_party['Constituency'].str.upper()
    df_const_margin_party['Margin'] = pd.to_numeric(df_const_margin_party['Margin'])
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #    print(df_const_margin_party)
    return(df_const_margin_party)        
        
#this function merges the above two dataframes            
def merge_df():
    df_const_candidates_votes = scrape1()
    df_const_margin_party = scrape2()
    election_data_merged = pd.merge(df_const_candidates_votes, df_const_margin_party, on='Constituency')
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(dummy)
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df_merged)
   
    return (election_data_merged)


def regression():
    election_data_merged = merge_df()
    reg = linear_model.LinearRegression()
    reg.fit(election_data_merged[['Candidates', 'Votes']], election_data_merged['Margin'])
    print(reg.coef_)

regression()

#this function merges the merged dataframe with the shapefile on the columns "Constituency" and "PC_NAME"; it then plots the merged shapefile
def chloropleth():
    merged_df = merge_df()
    india_shapefile = gpd.read_file("india.shp")
    #print(india_shapefile.dtypes)
    #print(merged_df.dtypes)
    df_shapefile_merged = merged_df.merge(india_shapefile, left_on="Constituency", right_on="PC_NAME", how="inner")
    variable = 'Margin'
    #print(df_shapefile_merged.head())
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df_shapefile_merged.head())
    df_shapefile_merged.plot(variable, cmap='Reds', legend=True)
    
chloropleth()


def charts():
    merged_df = merge_df()
    mean_margin_by_party = merged_df.groupby(['Party']).mean()
    seats_by_party = merged_df.groupby(['Party']).count()
    plot_pie = seats_by_party.plot.pie(y='Constituency', figsize=(4,4), autopct='%1.1f%%')
    plot_pie.legend(title="Party",loc="best", bbox_to_anchor=(1, 0, 0.5, 1))
    print(mean_margin_by_party)
    plot_bar = mean_margin_by_party['Margin'].plot(kind='bar', title ="Average Victory Margin by Party", figsize=(15, 10), legend=False, fontsize=12)
    plot_bar.set_xlabel("Party", fontsize=12)
    plot_bar.set_ylabel("Number of Votes", fontsize=12)
    plt.show()

charts()
