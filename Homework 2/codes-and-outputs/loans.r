library(tidyverse)
library(rstudioapi)
library(plyr)
library(readr)
library(stringr)
library(hash)

#mark current directory
cur_dir = dirname(getSourceEditorContext()$path)
#set directory to data folder
setwd(cur_dir)
setwd("../data")

#file load
loans <- read.csv("loans.csv")

#changing date column to fit date format
loans$date = as.Date(loans$date)

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

#drop pre-existing loans columns
loans[,6:25] = NULL

write.csv(loans, file = "../codes-and-outputs/loans_r.csv")