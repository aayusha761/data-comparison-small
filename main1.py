import pandas as pd
import numpy as np
import sys

reload(sys)
sys.setdefaultencoding('utf8')


# Define the diff function to show the changes in each field
def report_diff(x):
    return x[0] if x[0] == x[1] else '{} ---> {}'.format(*x)


# Read in the two files but call the data old and new and create columns to track
old = pd.read_excel('sample-data-1.xlsx', 'Sheet1', na_values=['NA'])
new = pd.read_excel('sample-data-2.xlsx', 'Sheet1', na_values=['NA'])
old['version'] = "old"
new['version'] = "new"

# Join all the data together and ignore indexes so it all gets added
full_set = pd.concat([old, new], ignore_index=True, sort=True)

# Let's see what changes in the main columns we care about
changes = full_set.drop_duplicates(subset=["PAYMENT_ID", "CONTRACT_NO", "ContractType",
                                           "Payment Type", "CURRENCY_CODE", "FX_Rate", "Cost (USD)",
                                           "Cost (Local)", "Payment_due_date", "Approver_Name",
                                           "Is_Payment_Done?", "Cash_localAmt", "Cash_deducted_amt",
                                           "Cash_USDAmt", "Balance_Payment_Local",
                                           "Balance_Payment_USD", "Payment_Received_Date",
                                           "Issue_Date", "Payment_Status", "Last_UpdatedDate",
                                           "Payment_Comments", "Products"], keep='last')

# We want to know where the duplicate account numbers are, that means there have been changes
dupe_accts = changes.set_index('PAYMENT_ID').index.get_duplicates()
# dupe_accts = changes.index.get_level_values('PAYMENT_ID').duplicated(keep=False)

# Get all the duplicate rows
dupes = changes[changes["PAYMENT_ID"].isin(dupe_accts)]

# Pull out the old and new data into separate dataframes
change_new = dupes[(dupes["version"] == "new")]
change_old = dupes[(dupes["version"] == "old")]

# Drop the temp columns - we don't need them now
change_new = change_new.drop(['version'], axis=1)
change_old = change_old.drop(['version'], axis=1)

# Index on the account numbers
change_new.set_index('PAYMENT_ID', inplace=True)
change_old.set_index('PAYMENT_ID', inplace=True)

# Now we can diff because we have two data sets of the same size with the same index
diff_panel = pd.Panel(dict(df1=change_old, df2=change_new))
diff_output = diff_panel.apply(report_diff, axis=0)


# Diff'ing is done, we need to get a list of removed items

# Flag all duplicated account numbers
changes['duplicate'] = changes["PAYMENT_ID"].isin(dupe_accts)

# Identify non-duplicated items that are in the old version and did not show in the new version
removed_accounts = changes[(changes["duplicate"] == False) & (changes["version"] == "old")]

# We have the old and diff, we need to figure out which ones are new

# Drop duplicates but keep the first item instead of the last
new_account_set = full_set.drop_duplicates(subset=["PAYMENT_ID", "CONTRACT_NO", "ContractType",
                                                   "Payment Type", "CURRENCY_CODE", "FX_Rate", "Cost (USD)",
                                                   "Cost (Local)", "Payment_due_date", "Approver_Name",
                                                   "Is_Payment_Done?", "Cash_localAmt", "Cash_deducted_amt",
                                                   "Cash_USDAmt", "Balance_Payment_Local",
                                                   "Balance_Payment_USD", "Payment_Received_Date",
                                                   "Issue_Date", "Payment_Status", "Last_UpdatedDate",
                                                   "Payment_Comments", "Products"],
                                           keep='first')

# Identify dupes in this new dataframe
new_account_set['duplicate'] = new_account_set["PAYMENT_ID"].isin(dupe_accts)

# Identify added accounts
added_accounts = new_account_set[(new_account_set["duplicate"] == False) & (new_account_set["version"] == "new")]

# Save the changes to excel but only include the columns we care about
writer = pd.ExcelWriter("my-diff-3.xlsx")
diff_output.to_excel(writer, "changed")
removed_accounts.to_excel(writer, "removed", index=False, columns=["PAYMENT_ID", "CONTRACT_NO", "ContractType",
                                                                   "Payment Type", "CURRENCY_CODE", "FX_Rate",
                                                                   "Cost (USD)",
                                                                   "Cost (Local)", "Payment_due_date", "Approver_Name",
                                                                   "Is_Payment_Done?", "Cash_localAmt",
                                                                   "Cash_deducted_amt",
                                                                   "Cash_USDAmt", "Balance_Payment_Local",
                                                                   "Balance_Payment_USD", "Payment_Received_Date",
                                                                   "Issue_Date", "Payment_Status", "Last_UpdatedDate",
                                                                   "Payment_Comments", "Products"])
added_accounts.to_excel(writer, "added", index=False, columns=["PAYMENT_ID", "CONTRACT_NO", "ContractType",
                                                               "Payment Type", "CURRENCY_CODE", "FX_Rate", "Cost (USD)",
                                                               "Cost (Local)", "Payment_due_date", "Approver_Name",
                                                               "Is_Payment_Done?", "Cash_localAmt", "Cash_deducted_amt",
                                                               "Cash_USDAmt", "Balance_Payment_Local",
                                                               "Balance_Payment_USD", "Payment_Received_Date",
                                                               "Issue_Date", "Payment_Status", "Last_UpdatedDate",
                                                               "Payment_Comments", "Products"])
writer.save()
