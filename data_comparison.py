##############################################################
# File Name : data_comparison.py
# Inputs : Source File Name, Target File Name, Table_Type
# The configuration will have the Key value pair as Table_Type_<Key>
# So when we pass the Table Type we will append that and search and then
# put in generic variables, By doing this we can configure as many 
# tables as we want but pass them
##############################################################
# Version   Date            Author              Comments
#  1.0      10-Aug-2021     Aayush  Arora       Initial File
#  1.0      10-Aug-2021     Krishna Vaddadi     Made file more generic 
##############################################################

from posixpath import split, splitdrive
import pandas as pandas
import pandas as pd
from datetime import datetime
import sys
import os

#reload(sys)
#sys.setdefaultencoding('utf8')


# Define the diff function to show the changes in each field
def report_diff(x):
    return x[0] if x[0] == x[1] else '{} ---> {}'.format(*x)

def main(args):
    # Read in the two files but call the data old and new and create columns to track
    source_file = args[0]
    target_file = args[1]
    # This should have the Table/Comparison Object and Date and Time stamp attached, So we don't override the
    # previous data. For now leaving it as is.
    final_diff_file = "final_diff.xlsx"

    if os.path.isfile(source_file):
        print("File Exists")
    else:
        print ("File " + source_file + " Does not exist, Exiting.")
        sys.exit(1)
    # Check if file exists or not!! If not simply exit
    if os.path.isfile(target_file):
        print("File Exists")
    else:
        print ("File " + target_file + " Does not exist, Exiting.")
        sys.exit(1)

    #config_file_dir = "/configs/" # To be used later
    #Config File name
    config_file_name = "data_comparison.cfg"
    # Check if the file exists at the location or not

    # First check if the configuration file exists or not, If not then exit
    if os.path.isfile(config_file_name):
        print("File Exists")
    else:
        print ("File " + config_file_name + " Does not exist, Exiting.")
        sys.exit(1)   
    cfg_file=open(config_file_name,"r")
    remap_field = ''
    for line in cfg_file:
        if line[0]!= '#':
            # First is not a # so continue processing
            split_line=line.split("=")
            #print ("Length of the split_line " + str(len(split_line)))
            #print(split_line[0] + "::LHS")
            first_set = split_line[0]
            #print (split_line[1] + "::RHS")
            if first_set.strip() == "source_file_columns":
                # Set the Source column Names
                src_column_names = split_line[1]
            elif first_set.strip() == "target_file_column_mapping":
                tgt_column_mapping = split_line[1].replace('\n','')
            elif first_set.strip() == "index_columns":
                index_columns = split_line[1].replace('\n','')
            elif first_set.strip() == "subset_columns":
                subset_cols = split_line[1].replace('\n','')
            elif first_set.strip() == "map_field":
                remap_field == split_line[1].replace('\n','')

    # Now load the configuration file They will be placed under configs/data_comparison.cfg (For now kept under same location as Main!!)
    
    # Open the files
    print ("Opening both files...")
    print ("Start time to Open Source File :" + source_file + " : " + str(datetime.now()))
    source = pd.read_excel(source_file, 'Sheet1', na_values=['NA'])
    print ("Start time to Open Target File :" + target_file + " : " + str(datetime.now()))
    target = pd.read_excel(target_file, 'Sheet1', na_values=['NA'])

    #print ("Src Column Names : " + src_column_names)
    #print ("Target Column Names : " + tgt_column_mapping)
    #print ("Index Column Names : " + index_columns)
    #print ("Subset Column Names : " + subset_cols)
    # map column names
    target.index.rename(tgt_column_mapping, inplace=True)

    # sequence columns
    source_column_names = [src_column_names]
    target = target.reindex(columns=source_column_names)

    # Add extra column 'version' for identifying two excels
    source['version'] = "source"
    target['version'] = "target"

    # Join all the data together and ignore indexes so it all gets added
    full_set = pd.concat([source, target], ignore_index=True)
    if remap_field:
        full_set[remap_field] = full_set[remap_field].map({'YES': '1', 'NO': '0', 1: '1', 0: '0'})

    # Drop all duplicate columns
    changes = full_set.drop_duplicates(keep='last')
    print (changes)

    #print ("Listing Changes :") 
    #print (changes)

    # We want to know where the duplicate account numbers are, that means there have been changes
    dupe_records = changes.set_index(index_columns)#.get_duplicates()
    #print (dupe_records)
    dupe_record_frames = dupe_records.to_frame().reset_index(drop=True)
    # print dupe_accts_frames
    # Calling merge() function
    
    dupes = pd.merge(dupe_record_frames, changes, how='inner')
 
    change_new = dupes[(dupes["version"] == "source")]
    change_old = dupes[(dupes["version"] == "target")]

    # Drop the temp columns - we don't need them now
    change_new = change_new.drop(['version'], axis=1)
    change_old = change_old.drop(['version'], axis=1)

    # Index on the tables
    change_new.set_index([index_columns], inplace=True)
    change_old.set_index([index_columns], inplace=True)

    print ("Printing Old Changes: ") 
    print (change_old)
    print ("Pringing New Changes:")
    print (change_new)

    # Now we can diff because we have two data sets of the same size with the same index
    try:
        diff_panel = pd.Panel(dict(df1=change_old, df2=change_new))
        diff_output = diff_panel.apply(report_diff, axis=0)

        writer = pd.ExcelWriter(final_diff_file)
        diff_output.to_excel(writer, "changed")
        writer.save()
    except Exception:
        print ("No Unique Key matches this criteria.")

if __name__ == "__main__":
    if len(sys.argv[1:]) != 2:
        print ("Invalid Call Should be compare_data.py <file1> <file2>")
    else:
        main (sys.argv[1:])