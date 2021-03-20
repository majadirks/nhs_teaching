# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 14:55:22 2021

@author: dirksm
"""

import pandas as pd
import regex as re
import os, sys

MESSAGE_TEMPLATE_FILE = 'message_template.txt'

# Helper functions
# missing list takes a pandas Series
# and returns a string of the index values
# where the record value is 0, 'M', or 'm'
def missing_list(record):
    missing_codes = ['M', 'm', 'Z', 'z', 0]
    return '\n'.join(list(record[record.isin(missing_codes)].index))

# This function takes a filename and two series (columns)
# It returns a series with a message for each student
# based on the text in the file
def message_column(template, name_series, missing_series):
    with open(template, 'r',) as file:
        lines = file.readlines()
        # Ignore all commented lines
        # The first meaningful lines get stored as starting_line
        # Once we hit another comment, we are done with starting_line
        # and all subsequent non-comment lines are stored as closing_line
        starting_line = ''
        closing_line = ''
        phase = 0  # 0 = opening comments, 1 = starting lines, 2 = closing lines
        for line in lines:
            if line.startswith('#'):
                               if phase == 1: # If we're in starting lines
                                   phase = 2 # Switch to ending lines
                               continue
            elif phase == 0: # If we're in opening comments
                phase = 1 # switch to starting lnes
                starting_line += '\n' + line
            elif phase == 2:
                closing_line += '\n' + line
        
        # Format it into a message
        message = pd.Series(("\n\n(Message for " + name_series + ')\n\n' +
                          name_series + ',\n\n' + 
                          starting_line + '\n\n' +
                          missing_series + '\n\n' +
                          closing_line + '\n\n\n')*(missing_series.str.len() > 0))
        return message
    
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
print("Choose the Excel file that contains your grades, or (Q)uit:")
for index, file in enumerate(excel_files):
    print(f"\t({index + 1}) {file}")  # list files, 1-indexed
choice = 0
max = len(excel_files)
while (choice <=0 or choice > max):
    try:
        choice = input(">")
        if choice.strip().upper()[:1] == 'Q':
            sys.exit(0)
        choice = int(choice)
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
    sys.exit(0)

print(f"\nFile accepted. I will write messages based on the file '{MESSAGE_TEMPLATE_FILE}'\n")
    
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
        print(f"\tError (TypeError): Could not process worksheet '{sheet}'")
        print("\tI expect column headers in Row 2 of the form 'LT1A', etc.")
        print(f"\tSkipping '{sheet}'")
        continue
    
    
    # Format it into a message
    period['message'] = message_column(MESSAGE_TEMPLATE_FILE,
                                      period.Name,
                                      period.missing)

    
    # Create text file of messages
    filename = sheet + '_messages.txt'
    period['message'].to_csv(filename, header = False, index = False)  # Overwrites all but last period!
    print(f"\tWrote '{filename}'")

input("\nPress Enter to exit...")
