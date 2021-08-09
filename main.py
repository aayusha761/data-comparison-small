import pandas as pd


# Define the diff function to show the changes in each field
def report_diff(x):
    return x[0] if x[0] == x[1] else '{} ---> {}'.format(*x)


# Read in the two files but call the data old and new and create columns to track
old = pd.read_excel('sample-address-old.xlsx', 'Sheet1', na_values=['NA'])
new = pd.read_excel('sample-address-new.xlsx', 'Sheet1', na_values=['NA'])
old['version'] = "old"
new['version'] = "new"

# Join all the data together and ignore indexes so it all gets added
full_set = pd.concat([old, new], ignore_index=True)

# Let's see what changes in the main columns we care about
changes = full_set.drop_duplicates(subset=["account number", "name", "street", "city", "state", "postal code"],
                                   keep='last')

print changes

# We want to know where the duplicate account numbers are, that means there have been changes
dupe_accts = changes.set_index(['account number']).index.get_duplicates()
print dupe_accts

# Get all the duplicate rows
dupes = changes[changes["account number"].isin(dupe_accts)]
print dupes

# Pull out the old and new data into separate dataframes
change_new = dupes[(dupes["version"] == "new")]
change_old = dupes[(dupes["version"] == "old")]

# Drop the temp columns - we don't need them now
change_new = change_new.drop(['version'], axis=1)
change_old = change_old.drop(['version'], axis=1)

print change_old
print change_new

# Index on the account numbers
change_new.set_index('account number', inplace=True)
change_old.set_index('account number', inplace=True)

# Now we can diff because we have two data sets of the same size with the same index
diff_panel = pd.Panel(dict(df1=change_old, df2=change_new))
diff_output = diff_panel.apply(report_diff, axis=0)

print diff_output
# Diff'ing is done, we need to get a list of removed items

writer = pd.ExcelWriter("my-diff-2.xlsx")
diff_output.to_excel(writer, "changed")

writer.save()
