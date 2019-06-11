# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 18:12:09 2019

@author: adminuser
"""
import csv
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn import linear_model
import geopandas as gpd
import matplotlib.pyplot as plt
from pandas.tools.plotting import table

def data_read():
    const_candidates_votes = pd.read_csv("const_candidates_votes.csv")
    const_margin_party = pd.read_csv("const_margin_party.csv")
    return const_candidates_votes, const_margin_party

def data_merge():
    const_candidates_votes, const_margin_party = data_read()
    const_margin_party['Constituency'] = const_margin_party['Constituency'].str.upper()
    const_candidates_votes['Constituency'] = const_candidates_votes['Constituency'].str.upper()
    print(const_margin_party['Constituency'])
    print(const_candidates_votes['Constituency'])

    election_data_merged = pd.merge(const_candidates_votes, const_margin_party, on='Constituency')
    election_data_merged['Margin Percentage'] = (election_data_merged['Margin']/election_data_merged['Votes'])*100
    print(election_data_merged.head())      
    return(election_data_merged)


def regression():        
    election_data_merged = data_merge()
    x = election_data_merged[['Candidates', 'Votes']]
    y = election_data_merged['Margin']
    x = sm.add_constant(x)
    model_election_data = sm.OLS(y, x).fit()
    print(model_election_data.summary())

#regression()


def chloropleth():
    election_data_merged = data_merge()
    india_shapefile = gpd.read_file("india.shp")
#india_shapefile.plot()
    data_shapefile_merged = india_shapefile.merge(election_data_merged, right_on="Constituency", left_on="PC_NAME", how="inner")
    plot1 = 'Margin'
    plot2 = 'Margin Percentage'
    data_shapefile_merged.plot(plot1, cmap='Reds', legend=True, title = 'Absolute Margin ')
    data_shapefile_merged.plot(plot2, cmap='Reds', legend=True, title = 'Margin as % of votes polled')

#chloropleth()

def charts():
    mean_margin_by_party = election_data_merged.groupby(['Party']).mean()
    seats_by_party = election_data_merged.groupby(['Party']).count()

    seats_by_party.plot.pie(y='Constituency', figsize=(6,6), autopct='%1.1f%%', title = 'Seat Share By Party', labels = None)
    plt.legend(title="Party",loc="best", labels= seats_by_party['Party'],  bbox_to_anchor=(10, 10))
    plt.figure()
    plt.ylabel('')

    plot_bar = mean_margin_by_party['Margin'].plot(kind='bar', title ="Average Victory Margin by Party", figsize=(15, 10), legend=False, fontsize=12)
    plot_bar.set_xlabel("Party", fontsize=12)
    plot_bar.set_ylabel("Number of Votes", fontsize=12)
    plt.figure()
    plt.show()
charts()