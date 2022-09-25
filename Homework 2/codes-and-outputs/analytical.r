library(tidyverse)
library(rstudioapi)
library(dplyr)
library(readr)
library(stringr)

#mark current directory
cur_dir = dirname(getSourceEditorContext()$path)
#set directory to data folder
setwd(cur_dir)
setwd("../data")

#file load
accounts <- read.csv("accounts.csv")
cards <- read.csv("cards.csv")
clients <- read.csv("clients.csv")
links <- read.csv("links.csv")
payment_orders <- read.csv("payment_orders.csv")
transactions <- read.csv("transactions.csv")
districts <- read.csv("districts.csv")
loans <- read.csv("loans.csv")

#accounts data type manipulation
accounts$date <- as.Date(accounts$date)

#accounts column rename
accounts$account_id <- accounts$id
accounts$open_date <- accounts$date

accounts$id <- NULL
accounts$date <- NULL

#distircts clean
districts$commited_crimes = gsub("\\[", "", districts$commited_crimes)
districts$commited_crimes = gsub("\\]", "", districts$commited_crimes)
districts$municipality_info = gsub("\\[", "", districts$municipality_info)
districts$municipality_info = gsub("\\]", "", districts$municipality_info)
districts$unemployment_rate = gsub("\\[", "", districts$unemployment_rate)
districts$unemployment_rate = gsub("\\]", "", districts$unemployment_rate)



for(i in c(1:nrow(districts))){
  x = strsplit(districts[i,"municipality_info"], ",")
  districts[i,'pop500'] = x[[1]][1]
  districts[i,'pop500_1999'] = x[[1]][2]
  districts[i,'pop2000_9999'] = x[[1]][3]
  districts[i,'pop10000'] = x[[1]][4]  
}

for(i in c(1:nrow(districts))){
  x = strsplit(districts[i,"unemployment_rate"], ",")
  districts[i,'unemployment95'] = x[[1]][1]
  districts[i,'unemployment96'] = x[[1]][2]
}

for(i in c(1:nrow(districts))){
  x = strsplit(districts[i,"commited_crimes"], ",")
  districts[i,'crime95'] = x[[1]][1]
  districts[i,'crime96'] = x[[1]][2]
}

str(districts)

districts[,9:11] = NULL

for(i in c(9:16)){
  districts[,i] <- as.numeric(districts[,i])
}

districts[is.na(districts$crime95),"crime95"] <- median(districts$crime95, na.rm = T)
districts[is.na(districts$unemployment95),"unemployment95"] <- median(districts$unemployment95, na.rm = T)

#districts join

df = merge(accounts, districts, by.x = "district_id", by.y = "id", all.x = TRUE)

df$district_name = df$name

df = df[,c("account_id", "district_name", "open_date", "statement_frequency")]

#client per account
temp = links %>% count("account_id")

df = merge(df, temp, by.x = "account_id", by.y = "account_id", all.x = TRUE)
df$num_cutomers <- df$freq
df$freq = NULL

#credit card count
temp = merge(links, cards, by.x = "id", by.y = "link_id", all.x = TRUE)
temp = temp[complete.cases(temp),]
temp = temp %>% count("account_id")

df = merge(df, temp, by.x = "account_id", by.y = "account_id", all.x = TRUE)
df$credit_cards <- df$freq
df$freq = NULL
df$credit_cards[is.na(df$credit_cards)] = 0


#loans
#extract column titles of uncleaned data
col_title = c("X24_A"   ,   "X12_B"    ,  "X12_A"    ,  "X60_D"    ,  "X48_C"  ,    "X36_D"  ,   
              "X36_C"   ,   "X12_C"    ,  "X48_A"  ,    "X24_C"   ,   "X60_C"  ,    "X24_B"   ,   "X48_D"  ,    "X24_D"   ,   "X48_B"    ,  "X36_A"  ,    "X36_B" ,    
              "X60_B"    ,  "X12_D"   ,   "X60_A"     )

#split the loan status column titles for cleaning =
x = ""
y = ""

#Erase "X" infront of column titles
temp = gsub("X", "", col_title)

#split the column titles to length and status of loan
for(i in c(1:length(temp))){
  x[i] = strsplit(temp[i], "_")[[1]][1]
  y[i] = strsplit(temp[i], "_")[[1]][2]
}

#mark the rows with respective length and status of loan
for(i in c(1:nrow(loans))){
  for(j in c(1:length(col_title))){
    if(loans[i,col_title[j]] == "X"){
      loans$loan_length[i] = x[j]
      loans$loan_status[i] = y[j]
    }
  }
}

#change ABCD to default and loan status
for(i in c(1:nrow(loans))){
  if (loans$loan_status[i] == "A"){
    loans$loan_status[i] = "expired"
    loans$loan_default[i] = "Flase"
  } else if(loans$loan_status[i] == "B"){
    loans$loan_status[i] = "expired"
    loans$loan_default[i] = "True"
  }else if(loans$loan_status[i] == "C"){
    loans$loan_status[i] = "current"
    loans$loan_default[i] = "False"    
  }else if(loans$loan_status[i] == "D"){
    loans$loan_status[i] = "current"
    loans$loan_default[i] = "True"        
  } else {
    loans$loan_status[i] = NA
    loans$loan_default[i] = NA       
  }
}

#drop pre-existing loans columns
loans[,6:25] = NULL

for(i in c(1:nrow(loans))){
  if(is.na(loans$amount[i]) == TRUE){
    loans$loan[i] <- "True"
  }else{
    loans$loan[i] <- "False"
  }
}

str(loans)

temp = merge(df, loans, by = "account_id", all.x = TRUE)
temp$id = NULL
temp$date = NULL
temp$loan_amount = temp$amount
temp$amount = NULL
temp$loan_payments = temp$payments 
temp$payments = NULL
temp$loan_term = temp$loan_length
temp$loan_length = NULL

df= temp

###cash withdrawal 
temp = transactions[transactions$type == "debit",]
temp = temp[temp$method == "cash",]
temp = temp[,c("account_id","amount")]

temp = temp %>% 
  group_by(account_id) %>% 
    summarize(min_withdrawal = min(amount))

df = merge(df, temp, by = "account_id", all.x = TRUE)

temp = transactions[transactions$type == "debit",]
temp = temp[temp$method == "cash",]
temp = temp[,c("account_id","amount")]

temp = temp %>% 
  group_by(account_id) %>% 
  summarize(max_withdrawal = max(amount))

df = merge(df, temp, by = "account_id", all.x = TRUE)

#cc payments
temp = transactions[transactions$type == "credit",]
temp = temp %>% 
  group_by(account_id) %>% 
  summarize(cc_payments = length(amount))

df = merge(df, temp, by = "account_id", all.x = TRUE)


#balance
temp = transactions[,c("account_id","balance")]

temp = temp %>% 
  group_by(account_id) %>% 
  summarize(min_balance = min(balance))

df = merge(df, temp, by = "account_id", all.x = TRUE)

temp = transactions[,c("account_id","balance")]

temp = temp %>% 
  group_by(account_id) %>% 
  summarize(max_balance = max(balance))

df = merge(df, temp, by = "account_id", all.x = TRUE)

str(df)

write.csv(loans, file = "../codes-and-outputs/analytical_r.csv")
