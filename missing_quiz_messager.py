# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 14:55:22 2021

@author: dirksm
"""

import pandas as pd
import regex as re
import os, sys

# Helper functions
# missing list takes a pandas Series
# and returns a string of the index values
# where the record value is 0
def missing_list(record):
    return '\n'.join(list(record[record == 0].index))

# Main code

# Prompt user to choose gradebook file 
# List all .xlsm files in current directory (cd)
# and in parent directory (pd)
excel_files_cd = [file
               for file in os.listdir('.')
               if file.endswith('.xlsm')]
excel_files_pd = [file
               for file in os.listdir('..')
               if file.endswith('.xlsm')]
excel_files = excel_files_cd + excel_files_pd

print("-=Missing Assessment Message Generator=-")
print("")
print("Choose the Excel file that contains your grades:")
for index, file in enumerate(excel_files):
    print(f"\t({index + 1}) {file}")  # list files, 1-indexed
choice = 0
max = len(excel_files)
while (choice <=0 or choice > max):
    try:
        choice = int(input(">"))
    except ValueError:
        choice = int(input(f"Please enter an integer between 1 and {max} > "))

# Read data
max_cd = len(excel_files_cd)
if choice <= max_cd:  # file in current directory
    file = './' + excel_files[choice - 1]  # Adjust for 1-indexed display
else:  # file in parent directory
    file = '../' + excel_files[choice - 1] # Adjust for 1-indexed display

# Read in grades workbook as a dict
# where keys are worksheet names and values are dataframes
try:
    grades = pd.read_excel(file,
                           sheet_name = None,
                           skiprows = 1 # Headers are in row 2
                           )
except PermissionError:
    print("An error occurred. Make sure Excel is closed and try again.")
    input("Press enter...")
    sys.exit()
    
sheets = grades.keys() # Strings of worksheet names

# Pattern for LT column
lt_pattern = 'LT\s?[\d\d?]' #eg 'LT5A', 'LT 5A', ... (Skips 'LT Communication')
# For each class, get a list of missing LTs per student
for sheet in sheets:
    print(f"Processing class {sheet}...")
    period = grades[sheet] # DataFrame for class period
    try:
        lt_columns = [column
                      for column in period.columns
                      if re.match(lt_pattern, column)]
        period['missing'] = period[lt_columns].apply(missing_list, axis=1)
    except TypeError:
        print("\tError: Could not process worksheet {sheet}")
        print("\tI expect column headers in Row 2 of the form 'LT1A', etc.")
        print("\tSkipping worksheet {sheet}")
        continue
    
    
    # Format it into a message
    #period['first_name'] = period['Name'].str.split(',')[1]
#    period['message'] = ("\n\n(Message for " + period['Name'] + ')\n\n' +
#            period['Name'] +
#    "\nAccording to my records you have not yet taken the assessments " +
#    "for the following LTs:\n\n" +
#        period['missing'] +
#        '''\n\nIs that correct? Would you like to take some of those next week?
#        Best,
#        Mr. Dirks\n\n\n''')*(period.missing.str.len() > 0)
    name = period['Name']
    list_of_zeroes = period['missing']
    message_str = r'''\n\n(Message for {period['Name']}
    
    # Create text file of messages
    filename = sheet + '_messages.txt'
    period['message'].to_csv(filename, header = False, index = False)  # Overwrites all but last period!
    print(f"\tWrote '{filename}'")

input("\nPress Enter to exit...")
