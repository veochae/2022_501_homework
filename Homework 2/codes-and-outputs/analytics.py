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

accounts['date'] = pd.to_datetime(accounts['date'])

accounts = accounts.rename(columns = {"id": "account_id", "district_id": "district_id", "date": "open_date", "statement_frequency": "statement_frequency"})

#### DISTRICT #####

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

df = accounts.merge(districts, left_on = "district_id", right_on = "id", how = "left" )
df = df.rename(columns = {'name': 'district_name'})

df = df[['account_id', 'district_name', 'open_date', 'statement_frequency']]

##### links

temp = pd.DataFrame(links.groupby("account_id")['client_id'].count())
temp = temp.rename(columns = {"client_id": "num_customers"})

column_extract = temp.T
temp['account'] = column_extract.columns

temp

df= df.merge(temp, left_on = "account_id", right_on = "account", how = "left")

df = df.drop("account", axis = 1)

temp = links.merge(cards, left_on = "id", right_on = "link_id", how = "left")
temp

temp = pd.DataFrame(temp.groupby("account_id")['id_y'].count())
temp = temp.rename(columns = {"id_y": "credit_cards"})

temp

column_extract = temp.T

column_extract
temp['account'] = column_extract.columns
temp.info()

pd.unique(temp['credit_cards'])

df = df.merge(temp, left_on = "account_id", right_on="account", how = "left")
df.drop("account", axis = 1)

#### loans
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


temp = pd.DataFrame.copy(df)
loans = loans.rename(columns = {"account_id": "account"})
temp = temp.merge(loans, left_on="account_id", right_on= "account", how = "left")
temp['loan_amount'] = temp['amount']
temp['loan_payments'] = temp['payments']
temp['loan_term'] = temp['loan_length']

x = []
for i in range(0,len(temp)):
    if pd.isnull(temp.loc[i,"loan_amount"]) == True:
        x.append("False")
    else: x.append("True")

temp['loan'] = x

for i in range(0,len(temp)):
    if temp.loc[i,"loan_status"] == "A":
        temp.loc[i,"loan_status"] = "expired"
        temp.loc[i,"loan_default"] = "False"
    elif temp.loc[i,"loan_status"] == "B":
        temp.loc[i,"loan_status"] = "expired"
        temp.loc[i,"loan_default"] = "True"
    elif temp.loc[i,"loan_status"] == "C":
        temp.loc[i,"loan_status"] = "current"
        temp.loc[i,"loan_default"] = "False"
    elif temp.loc[i,"loan_status"] == "D":
        temp.loc[i,"loan_status"] = "current"
        temp.loc[i,"loan_default"] = "True"
    else: temp.loc[i,["loan_status", "loan_default"]] = np.nan

df = temp[["account_id", "district_name","open_date", "statement_frequency", "num_customers", "credit_cards", "loan", "loan_amount",
            "loan_payments", "loan_term", "loan_status", "loan_default"]]


#transactions

xx =transactions[transactions['type'] =="debit"]
xx =xx[xx['method'] == "cash"]

min = pd.DataFrame(xx.groupby("account_id")["amount"].min())
max = pd.DataFrame(xx.groupby("account_id")["amount"].max())

column_extract = max.T
max['account'] = column_extract.columns
max = max.rename(columns = {"amount": "max_withdrawal"})

df = df.merge(max, left_on="account_id", right_on="account", how = "left")

df = df.drop("account", axis = 1)


column_extract = min.T
min['account'] = column_extract.columns
min = min.rename(columns = {"amount": "min_withdrawal"})

df = df.merge(min, left_on="account_id", right_on="account", how = "left")

df = df.drop("account", axis = 1)

xx = transactions[transactions['type'] =="credit"]
xx = pd.DataFrame(xx.groupby("account_id")["amount"].count())
column_extract = xx.T
xx['account'] = column_extract.columns
xx = xx.rename(columns = {"amount": "cc_payments"})

df = df.merge(xx, left_on="account_id", right_on="account", how = "left")

df = df.drop("account", axis = 1)

min = pd.DataFrame(transactions.groupby("account_id")["balance"].min())
max = pd.DataFrame(transactions.groupby("account_id")["balance"].max())

column_extract = max.T
max['account'] = column_extract.columns
max = max.rename(columns = {"balance": "max_balance"})

df = df.merge(max, left_on="account_id", right_on="account", how = "left")

df = df.drop("account", axis = 1)


column_extract = min.T
min['account'] = column_extract.columns
min = min.rename(columns = {"balance": "min_balance"})

df = df.merge(min, left_on="account_id", right_on="account", how = "left")

df = df.drop("account", axis = 1)

os.chdir('../codes-and-outputs')
districts.to_csv(os.getcwd()+ "/analytical_py.csv",index = False, header = True)
