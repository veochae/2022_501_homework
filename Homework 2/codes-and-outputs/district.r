library('tidyverse')
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
districts <- read.csv("districts.csv")

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

write.csv(loans, file = "../codes-and-outputs/district.csv")
