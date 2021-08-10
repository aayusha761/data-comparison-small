import pandas as pandas
import pandas as pd
import sys

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

# Drop all duplicate columns
changes = full_set.drop_duplicates(
    subset=['PAYMENT_ID', 'CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'FX_Rate', 'Cost (USD)',
            'Cost (Local)', 'Payment_due_date', 'Approval_date', 'Approver_Name', 'Is_Payment_Done?',
            'Cash_localAmt', 'Cash_deducted_amt', 'Cash_USDAmt', 'Balance_Payment_Local', 'Balance_Payment_USD',
            'Payment_Received_Date', 'Issue_Date', 'Payment_Status', 'Last_UpdatedDate', 'Payment_Comments',
            'Products'],
    keep='last')

print changes

# We want to know where the duplicate account numbers are, that means there have been changes
dupe_accts = changes.set_index(
    ['CONTRACT_NO', 'ContractType', 'Payment Type', 'CURRENCY_CODE', 'Payment_due_date', 'Is_Payment_Done?',
     'Payment_Status']).index.get_duplicates()
print dupe_accts

# Get all the duplicate rows
dupes = changes[changes["account number"].isin(dupe_accts)]
print dupes
# writer = pd.ExcelWriter("concat.xlsx")
# full_set.to_excel(writer, "changed")
# writer.save()
