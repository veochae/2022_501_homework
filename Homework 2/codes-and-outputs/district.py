import pandas as pd
import numpy as np
import os
import glob

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
os.chdir(path)
os.chdir('../data')

path = os.getcwd() #current working directory
files = glob.glob(path + "/*.csv") #all csv file names

name = [] #empty list for csv file name extraction
#csv file name extraction - .csv
for i, file_name in enumerate(files):
    name.append(os.path.basename(files[i]).removesuffix('.csv')) 

d = {}   #dictionary to store all csv as df

#input into dictionary d 
for i, file_name in enumerate(files): 
    d[name[i]] = pd.read_csv(file_name)

for i,x in enumerate(name):
    vars()[x] = pd.DataFrame(d[x])

#checking for missing values --> none
for i in range(len(districts.columns)):
    print((districts.columns[i], sum(districts.iloc[:,i].isna())) if sum(districts.iloc[:,i].isna()) != 0 else "")

rep = {"[": "", "]": ""}

for key, value in rep.items():
    for row in range (0,len(districts)):
        districts.loc[row,'municipality_info'] = districts.loc[row,'municipality_info'].replace(key, value)
        districts.loc[row,'unemployment_rate'] = districts.loc[row,'unemployment_rate'].replace(key, value)
        districts.loc[row,'commited_crimes'] = districts.loc[row,'commited_crimes'].replace(key, value)
        
    

for row in range (0,len(districts)):
        x = districts.loc[row,'municipality_info'].split(",")
        districts.loc[row,'pop500'] = x[0]
        districts.loc[row,'pop500_1999'] = x[1]
        districts.loc[row,'pop2000_9999'] = x[2]
        districts.loc[row,'pop10000'] = x[3]

for row in range (0,len(districts)):
        x = districts.loc[row,'unemployment_rate'].split(",")
        districts.loc[row,'unemployment95'] = x[0]
        districts.loc[row,'unemployment96'] = x[1]


for row in range (0,len(districts)):
        x = districts.loc[row,'commited_crimes'].split(",")
        districts.loc[row,'crime95'] = x[0]
        districts.loc[row,'crime96'] = x[1]



districts = districts.drop(['municipality_info','unemployment_rate','commited_crimes'], axis =1)

for i in range(8,16):
    districts.iloc[:,i] = pd.to_numeric(districts.iloc[:,i], errors = "coerce")

districts['crime95']= districts['crime95'].fillna(districts['crime95'].median())
districts['unemployment95']= districts['unemployment95'].fillna(districts['unemployment95'].median())    

os.chdir('../codes-and-outputs')
districts.to_csv(os.getcwd()+ "/district_py.csv",index = False, header = True)
