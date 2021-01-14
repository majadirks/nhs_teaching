# -*- coding: utf-8 -*-
'''
Use reports from ALEKS to get a list of all students
who have not completed the Initial Knowledge Check.

Create a file called 'messages.txt'
with messages that a teacher can copy/paste and send to each student
urging them to take the IKC. These messages
include their username and password
(which ALEKS stores in plaintext and makes
visible to teachers, so this isn't a security violation)
'''

import pandas as pd

# Load data from Excel files. Make sure the filenames are correct!
login_data = pd.read_excel('./aleks_logins.xls')
ikc_data = pd.read_excel('./ikc_report.xlsx')
# Join on login_data['Name'] = ikc_data['Student Name']
merged_inner = pd.merge(left=login_data, right=ikc_data, left_on='Name', right_on='Student Name')

# debugging
'''
for index, row in merged_inner.iterrows():
    student_name = row['Student Name']
    time = row['Time in Knowledge Check']
    print(f'{student_name}    "{time}"')
'''

# Select rows corresponding to students who haven't taken IKC
no_time_symbols = ['-', 0]  # Two relevant symbols
no_ikc = merged_inner[merged_inner['Time in Knowledge Check'].isin(no_time_symbols)]

no_ikc_names = []  # Initialize a list to store names of students

# Create text file of messages
with open('./messages.txt', 'w+') as file:
    
    # Iterating over data frame = terrible idea
    # But this is a pretty small data frame, so we're doing it.    
    for index, student_row in no_ikc.iterrows():
        student_name = student_row['Student Name']  # Formatted as 'Last, First'
        first_name = student_name.split(',')[1]
        login = student_row['Login_x']  # i.e. username
        password = student_row['Password']
        message = f'''
        ---------------------------------------------------------------
        (Message for {student_name})
        
        {first_name}, 
        I'm trying to figure out who has and hasn't taken the Initial Knowledge Check on ALEKS. On my end it looks like you haven't  yet. Is that correct? If so, could you please take it some time this week or next? 
       
        Log in at Aleks.com using
        username {login}
        password {password}
        
        Thank you!
        
        
        '''
        file.write(message)  # Append message to the file
        no_ikc_names.append(student_name)  # Add student name to the list

# Display list of student names
no_ikc_count = len(no_ikc_names)
print(f"No ikc found for the following students ({no_ikc_count}):")
print(no_ikc_names)
        