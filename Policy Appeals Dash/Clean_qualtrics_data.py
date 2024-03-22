#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install QualtricsAPI
from QualtricsAPI.Setup import Credentials
from QualtricsAPI.Survey import Responses
import pandas as pd
import numpy as np


# In[2]:


Credentials().qualtrics_api_credentials(token='AR7WLgm3j2koGWHEmF7dpb9VByMY91P0AUhaSukQ',data_center='ca1',directory_id='POOL_2YrDmsCtkrAw2Aj')
df = Responses().get_survey_responses(survey="SV_3a4CkoBg7BQhXRr", useLabels = True)


# In[3]:


df.columns = df.iloc[0]
df.drop(df.index[[0,1]], inplace=True)
df.drop(['Start Date', 'End Date', 'Distribution Channel', 'User Language', 'Response Type', 'IP Address', 'Progress', 'External Data Reference', 'Location Latitude', 'Location Longitude', \
         'Duration (in seconds)', 'Finished', 'Response ID', 'Recipient Last Name', 'Recipient First Name', 'Recipient Email', \
         'By clicking the button below, I certify that this petition is being completed by the student making the request.', \
         'Please fill in the following information: - First name (Preferred)', 'Please fill in the following information: - Last name', 'Please fill in the following information: - Wisc email address', \
         'The Wisconsin School of Business has a concurrent enrollment policy for the fall and spring terms that is detailed here. Exceptions to this policy are rare and will be reviewed on an individual basis based on extenuating circumstances.', \
         'You can upload supporting documentation here as needed - Id', 'You can upload supporting documentation here as needed - Name', 'You can upload supporting documentation here as needed - Size', \
         'Courses may not be dropped after the 9th week except in extremely unusual circumstances, and only with the approval of the BBA Director of Academic Advising and Affairs or Assistant Dean of WSB Undergraduate Program. Please note that the summer term drop deadlines are usually within the first week or two of a particular summer session. See the Summer Key Deadlines for more specific details.\n\n\n\nEarning a poor grade in a course, not being aware of deadlines, or not receiving feedback on an examination until after the deadline are a few examples that are not considered strong reasons for obtaining permission to drop a course after the deadline.', \
         'You can upload supporting documentation here as needed - Type'], axis=1, inplace=True)

df.columns = df.columns.str.replace('Please fill in the following information for the course you would like to take through UW Independent Learning or through another institution. (example: Spanish, First Semester Spanish, U912-101, 4 credits)', 'Fill in the information for the course you would like to take through UW Independent Learning or another institution.')
df.columns = df.columns.str.replace('Most exceptions require consultation with an advisor prior to submitting a petition. ','')
df.columns = df.columns.str.replace('International students on F-1/J-1 visas and student athletes must maintain full-time status (a minimum of 12 credits) during the fall and spring semesters. ', '')
df.columns = df.columns.str.replace('You can learn more about the Disruption Grading Option at https://registrar.wisc.edu/disruptiongrades/.  \n \n\n', '')
df.columns = df.columns.str.replace('The modality for School of Business online degree program courses are online only.  Exceptions are rare and will be considered on an individual basis.\n \n\n', '')


# In[4]:


#Create a row per students major
df.drop('Declared Major(s) and Certificate(s) - Selected Choice - Other/non-business majors and certificates:', axis=1, inplace=True)
id_vars = ['Please fill in the following information: - Student ID number']
value_vars = [col for col in df.columns if col.startswith('Declared Major(s) and Certificate(s) - Selected Choice -')]
df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='MajorColumn', value_name='Major')
df_melted = df_melted.dropna(subset=['Major'])
result_df = df_melted.merge(df, on=id_vars, how='left')
result_df = result_df.drop(columns=value_vars)
result_df.drop("MajorColumn", axis=1, inplace=True)

result_df["Term Date"] = result_df["Recorded Date"].apply(lambda x: "Spring  {}".format(x.split("-")[0][:4]) if int(x.split("-")[1])<6 \
                                       else ("Summer {}".format(x.split("-")[0][:4]) if (int(x.split("-")[0])>=6 and int(x.split("-")[1])<9) \
                                           else "Fall {}".format(x.split("-")[0][:4]) ) )

result_df["For which academic policy or requirement are you requesting an exception?"] = np.where(result_df["For which academic policy or requirement are you requesting an exception?"].isnull(), result_df["For which academic rule, regulation or requirement are you requesting an alternative or exception?"], result_df["For which academic policy or requirement are you requesting an exception?"])
result_df.drop("For which academic rule, regulation or requirement are you requesting an alternative or exception?", axis=1, inplace=True)
result_df = result_df.drop_duplicates()

#TESTING
#result_df["For which academic policy or requirement are you requesting an exception?"].unique()
#result_df["For which academic policy or requirement are you requesting an exception?"].value_counts()

#result_df[result_df['Please fill in the following information: - Student ID number']=='9082038788']
#result_df.loc[(result_df["cata"] == "Other") & (result_df["For which academic policy or requirement are you requesting an exception?"] == "Remove DR notation, post Wednesday deadline for Marketing 300")]


# In[5]:


# Auto group free response answers
def fill_cat(row):
    if not pd.isna(row.iloc[9]): #ADD/DROP
        return 'Add/drop'
    elif pd.notnull(row.iloc[[10, 11, 12, 13, 14, 16, 17, 18, 19]]).any(): #CONCURR
        return 'Concurrent'
    elif pd.notnull(row.iloc[[20, 21, 23]]).any(): #OVERLOAD
        return 'Overload'
    elif pd.notnull(row.iloc[[30, 31]]).any(): #SUBSTITU
        return 'Substitution'
    elif not pd.isna(row.iloc[29]): #WAIVE
        return 'Waive'
    elif pd.notnull(row.iloc[[25, 26, 27]]).any(): #WITHDRAWL
        return 'Late withdrawl'
    elif pd.notnull(row.iloc[[32, 33]]).any(): #COVID
        return 'SD/UD request'
    elif pd.notnull(row.iloc[[34, 35]]).any(): #MODALITY
        return 'Modality change'
    else:
        return 'Other'

result_df["Catagory"] = result_df.apply(fill_cat, axis=1)



result_df["For which academic policy or requirement are you requesting an exception?"] = result_df["For which academic policy or requirement are you requesting an exception?"].astype(str)
def text_cat(response):
    cates = {
        'Add/drop': ["Add or drop a class after the deadline", "drop a c"],
        'Overload': ["Enroll for a credit overload", "75 ", "75."],
        'Concurrent': ["Concurrent enrollment during a fall or spring term", "concurrently", "concurrent", "Winter"],
        'SD/UD request': ["SD/UD"],
        'Modality change' : ["Online courses enrollment", "modality"],
        'Late withdrawl': ["withdraw"],
        'Remove DR': ["Remove DR notation", "DR "],
        'Waive': ["Waive a requirement", "waive", "lift", "requisite class with its pre-requisite class"],
        'Study abroad': ["region", "Study abroad", "Studying abroad", "abroad"],
        'Substitution': ["Meet a requirement with a substitution", "substitute", "count"]}
    for key, value in cates.items():
        if key == 'Remove DR':
            if ('transcript' in response.lower() and 'dr' in response.lower()) or ('drop' in response.lower() and 'waive' in response.lower()):
                return key
        if key == 'Modality change':
            if 'online' in response.lower() and ('course' in response.lower() or 'degree' in response.lower()):
                return key
        if key == 'Concurrent':
            if 'another' in response.lower() and ('institution' in response.lower() or 'college' in response.lower() or 'university' in response.lower()):
                return key
        if key == 'Substitution':
            if 'fulfill' in response.lower() and ('requirement' in response.lower() or 'elective' in response.lower()):
                return key
        if isinstance(value, list):
            for element in value:
                if element.lower() in response.lower():
                    return key
    return 'Other'

result_df.loc[result_df["Catagory"] == "Other", "Catagory"] = result_df.loc[result_df["Catagory"] == "Other", "For which academic policy or requirement are you requesting an exception?"].apply(text_cat)

#result_df["Catagory"].value_counts()


# In[6]:


result_df.to_excel("policy_appeal_data_clean.xlsx")


# In[7]:


# ANOTHER IDEA
#from difflib import get_close_matches

#result_df["For which academic policy or requirement are you requesting an exception?"] = result_df["For which academic policy or requirement are you requesting an exception?"].astype(str)
# add_drop = ["Add or drop a class after the deadline", "deadline past", "after deadline", "add", "drop"]
# concurrent = ["Concurrent enrollment during a fall or spring term", "concurrent", "same time", "together"]
# overload = ["overload", "75", "limit", "maximum"]
# req_subs = ["Meet a requirement with a substitution","substitution", "replace", "instead of", "fulfill", "exception"]
# req_waiv = ["waive", "requirement", "requisite"]
# withdrawl = ["Withdraw from all classes after the deadline", "leave", "drop", "withdrawl"]
# sdud_cov = ["Request SD/UD grading option post-deadline (Spring 2020 and Spring 2021 terms only)", "Spring 2020", "Spring 2021", "covid", "UD", "SD"]
# modality = ["modality", "online"]
# trans_dr = ["remove", "drop", "DR", "transcript"]
# stu_ab = ["region", "Study abroad", "Studying abroad"]
# other = ["nan"] #anything else goes here
                                                                                             
# def find_best_match(response):
#     categories = {"add_drop": add_drop, "concurrent": concurrent, "overload": overload, \
#         "req_subs": req_subs, "req_waiv": req_waiv, "withdrawl": withdrawl, \
#         "sdud_cov": sdud_cov, "modality": modality, "trans_dr": trans_dr, \
#         "other": other}
#     best_match = max(categories.keys(), \
#         key=lambda category: len(get_close_matches(response, categories[category], n=1, cutoff=0.6)) > 0)
#     return best_match

# result_df["For which academic policy or requirement are you requesting an exception?"] = result_df["For which academic policy or requirement are you requesting an exception?"].apply(find_best_match)

