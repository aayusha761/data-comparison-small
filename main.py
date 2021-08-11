import sys

import pandas as pd

reload(sys)
sys.setdefaultencoding('utf8')


# Define the diff function to show the changes in each field
def report_diff(x):
    return x[0] if x[0] == x[1] else '{} ---> {}'.format(*x)


# Read in the two files but call the data old and new and create columns to track
old = pd.read_excel('sample-data-1.xlsx', 'Sheet1', na_values=['NA'])
new = pd.read_excel('sample-data-2.xlsx', 'Sheet1', na_values=['NA'])

# map column names
new.rename(
    columns={'Payment ID': 'PAYMENT_ID', 'Contract No': 'CONTRACT_NO', 'IS_PAYMENT_COMPLETE?': 'Is_Payment_Done?',
             'Cost in USD': 'Cost (USD)', 'Cost in Local': 'Cost (Local)'}, inplace=True)

# sequence columns
column_names = ['PAYMENT_ID', 'CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'FX_Rate', 'Cost (USD)',
                'Cost (Local)', 'Payment_due_date', 'Approval_date', 'Approver_Name', 'Is_Payment_Done?',
                'Cash_localAmt', 'Cash_deducted_amt', 'Cash_USDAmt', 'Balance_Payment_Local', 'Balance_Payment_USD',
                'Payment_Received_Date', 'Issue_Date', 'Payment_Status', 'Last_UpdatedDate', 'Payment_Comments',
                'Products']
new = new.reindex(columns=column_names)

# Add extra column 'version' for identifying two excels
old['version'] = "old"
new['version'] = "new"

# Join all the data together and ignore indexes so it all gets added
full_set = pd.concat([old, new], ignore_index=True)

# Update YES to 1 and NO to 0
full_set['Is_Payment_Done?'] = full_set['Is_Payment_Done?'].map({'YES': '1', 'NO': '0', 1: '1', 0: '0'})

# Drop all duplicate columns
changes = full_set.drop_duplicates(
    subset=['PAYMENT_ID', 'CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'FX_Rate', 'Cost (USD)',
            'Cost (Local)', 'Payment_due_date', 'Approval_date', 'Approver_Name', 'Is_Payment_Done?',
            'Cash_localAmt', 'Cash_deducted_amt', 'Cash_USDAmt', 'Balance_Payment_Local', 'Balance_Payment_USD',
            'Payment_Received_Date', 'Issue_Date', 'Payment_Status', 'Last_UpdatedDate', 'Payment_Comments',
            'Products'],
    keep='last')

# print changes

# We want to know where the duplicate columns are, that means there have been changes
dupe_accts = changes.set_index(
    ['CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'Payment_due_date', 'Is_Payment_Done?',
     'Payment_Status']).index.get_duplicates()
dupe_accts_frames = dupe_accts.to_frame().reset_index(drop=True)
# print dupe_accts_frames

# Calling merge() function
dupes = pd.merge(dupe_accts_frames, changes, how='inner')
# print(dupes)

change_new = dupes[(dupes["version"] == "new")]
change_old = dupes[(dupes["version"] == "old")]

# Drop the temp columns - we don't need them now
change_new = change_new.drop(['version'], axis=1)
change_old = change_old.drop(['version'], axis=1)

# print change_old
# print change_new

# Index on the tables
change_new.set_index(
    ['CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'Payment_due_date', 'Is_Payment_Done?',
     'Payment_Status'], inplace=True)
change_old.set_index(
    ['CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'Payment_due_date', 'Is_Payment_Done?',
     'Payment_Status'], inplace=True)

print change_old
print change_new

# Now we can diff because we have two data sets of the same size with the same index
# diff_panel = pd.Panel(dict(df1=change_old, df2=change_new))
# diff_output = diff_panel.apply(report_diff, axis=0)
#
# print diff_output

# writer = pd.ExcelWriter("my-diff-2.xlsx")
# diff_output.to_excel(writer, "changed")
#
# writer.save()
