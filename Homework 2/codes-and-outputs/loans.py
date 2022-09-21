import pandas as pd
import numpy as np
import os
import glob

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
for i in range(len(loans.columns)):
    print((loans.columns[i], sum(loans.iloc[:,i].isna())) if sum(loans.iloc[:,i].isna()) != 0 else "")

#extract column title containing loan info
col_title = ['24_A', '12_B',
       '12_A', '60_D', '48_C', '36_D', '36_C', '12_C', '48_A', '24_C', '60_C',
       '24_B', '48_D', '24_D', '48_B', '36_A', '36_B', '60_B', '12_D', '60_A']

#split column titles into length and type
x = []
y = []

for i in range(len(col_title)):
    x.append(col_title[i].split("_")[0])
    y.append(col_title[i].split("_")[1])

#create new column loan_length and loan_status
for row in range(0,len(loans)):
    for col in range(0,len(col_title)):
        if loans.loc[row,col_title[col]] == "X":
            loans.loc[row,"loan_length"] = x[col]
            loans.loc[row,"loan_status"] = y[col]


#loans['loan_length'].fillna(value = "no_loan", inplace = True)
#loans['loan_status'].fillna(value = "no_loan", inplace = True)
 
#drop unnecessary columns
loans = loans.drop(loans.columns[5:25], axis =1)

#change to correct datatype
loans['date'] = pd.to_datetime(loans['date'])

#export
os.chdir('../codes-and-outputs')
districts.to_csv(os.getcwd()+ "/loans.csv",index = False, header = True)