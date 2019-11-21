#### DRAFT ANALYSIS 2.0


import pandas as pd
import os
from datetime import datetime as dt
import time
import numpy as np
import subprocess


def initialize(PATH, verbose = False):
    '''Creates a copy if the input folder. Walks through the copy folder and creates an author entry for each folder in the input path and populates a datafrane
    with info names, IDs and workshopIDs and empty fields for drafts'''
    os.system("rm -rf ./Data/WORKING/*")
    os.system("cp -r "+PATH+"* ./Data/WORKING/")
    PATH_new = './Data/WORKING/'
    

    Data = pd.DataFrame()
    authors = []
    dirs = []
    workshopID = []

    
    for i, directory in enumerate(next(os.walk(PATH_new))[1]):
        if verbose:
            print(directory)
        cleanFilenames(PATH_new+directory+'/START/')
        authors.append(directory.title())
        dirs.append(PATH_new + directory)
        workshopID.append(os.listdir(PATH_new+directory+'/START/')[0].split('_')[2][3])

    Data["Name"] = authors

    Data["ID"] = list(range(len(authors)))

    Data["workshopID"] = workshopID
    Data["Path"] = dirs

    return Data

def fill_drafts(Data, verbose=False):
    ''' Compiles table for each author and creates dictionary to access them using the name of the author in title case '''
    draft_dic = {}
    for index, row in Data.iterrows():
        drafts = author_draft(row['Path']+"/START/", verbose)
        if verbose:
            print(drafts.head)
        draft_dic.update({row['Name']:drafts})
    return draft_dic


def run_bcl(Data, verbose=False):
    ''' creates a temporary folder in which the bcl code computes cross entropy between drafts, computes said CE and puts the info back in the original folder '''
    for index, row in Data.iterrows():
        if verbose:
            print(row['Name'])

        if os.path.exists("./START"):
            os.system("rm -r ./START")
        os.rename(row['Path']+"/START", "./START")
        os.system("./bcl3pezza")
        os.rename("./START", row['Path']+"/START")
        
def import_contigs(Data, draft_dic, verbose=False):
    ''' imports the data computed by the run_bcl function into tables for each draft. Returns updated draft tables'''
    for index, row in Data.iterrows():
        contigs = []
        if verbose:
            print(row['Name'])
        for draft in draft_dic[row['Name']]['path']:
            author_path = "/".join(draft.split('/')[0:-2])
            contig_path = author_path+"/START/ris_bcl+10000-10000/Contig."+draft.split('/')[-1]
            df = pd.read_csv(contig_path, header=None)
            df = df[0].str.split("_", n=10, expand = True)
            df = df.drop([0,1,5,8], axis=1)
            new = df[10].str.split("\t", n=2, expand = True)
            df[10]=new[0]
            df['distance'] = new[1]
            months = {'January': 1, 'February': 2,  "March":3, "April":4, "May": 5,
                    "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, 
                    "November": 11, "December": 12}
            df = df.replace(months)
            df['date'] = df[6].astype('str')+'-'+df[7].astype('str')+'-'+'2019'
            df['time'] = df[9].astype('str')+':'+df[10].astype('str')
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], dayfirst = True)
            df = df.drop([6,7,9,10, 'date', 'time'], axis=1)
            df = df.rename(index=str, columns={2:'WorkshopEd', 3:'Username', 4:'MacroRev'})
            df.merge(draft_dic[row['Name']][['ID', 'TimeStamp']], left_on='datetime', right_on='TimeStamp').drop('datetime', axis=1)
            df['distance'] = pd.to_numeric(df['distance'])
            df = df.sort_values(by='datetime').reset_index(drop=True)
            df['Edit']=df.index
            df = df.set_index('datetime')
            df['Edit_norm'] = (df['Edit']-df['Edit'].min())/(df['Edit'].max()-df['Edit'].min())
            contigs.append(df)
        draft_dic[row['Name']]['Contig'] = contigs
    return draft_dic

def Slide(Data, draft_dic, verbose = False):
    for _, author in Data.iterrows():
        if verbose:
            print(author['Name'])
        Slides = []
        sl_mn = []
        sl_dev = []
        for draft in draft_dic[author['Name']]['path']:
            #print(draft)
            if os.path.exists('ContigSliding.csv'):
                os.remove("ContigSliding.csv")
            # process = subprocess.Popen(['bash runningWindow', draft],
            #          stdout=subprocess.PIPE, 
            #          stderr=subprocess.PIPE,
            #          shell = True)
            # stdout, stderr = process.communicate()
            # print(stdout)
            os.system("bash runningWindow.sh "+draft)
            time.sleep(2)
            slid = pd.read_csv("ContigSliding.csv", sep="\t", header=None, skipfooter=1)
            slid = slid.drop(axis =1, columns=[0])
            slid[0] = slid[1]
            slid = slid.drop(axis =1, columns=[1])
            Slides.append(slid[0].to_list())
            sl_mn.append(np.mean(slid))
            sl_dev.append(np.std(slid))
        draft_dic[author['Name']]['Sliding_X'] = Slides
        draft_dic[author['Name']]['Sliding_mn'] = sl_mn
        draft_dic[author['Name']]['Sliding_dev'] = sl_dev
        draft_dic[author['Name']]
    return draft_dic


def author_draft(PATH, verbose = False):
    ''' creates summary table for drafts from one author. ''' 
    Drafts = pd.DataFrame()

    tags = []
    MEdit = []
    path=[]

    months = {'January': 1, 'February': 2,  "March":3, "April":4, "May": 5,
        "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, 
        "November": 11, "December": 12}

    for filename in os.listdir(PATH):
        if verbose:
            print(filename)
        dateTime = filename.split("_")[6:]
        MEdit.append(filename.split("_")[4])
        dateTime = [months[i] if i in months.keys() else i for i in dateTime ]
        try:
            date = str(dateTime[0])+'-'+str(dateTime[1])+'-'+'2019'
        except:
            print(filename+ " is not in the correct format for this analysis")
        time = dateTime[3]+':'+dateTime[4]
        tag = dt.strptime(date + ' ' + time, '%d-%m-%Y %H:%M')
        tags.append(tag)
        path.append(PATH+filename)

    Drafts["ID"] = list(range(len(tags)))
    Drafts["TimeStamp"] = tags
    Drafts["path"] = path
    Drafts["MacroEdit"] = MEdit
    Drafts["Contig"] = [[] for i in range(len(tags))]
    Drafts=Drafts.sort_values(by='TimeStamp').reset_index(drop=True)
    Drafts['Edit']=Drafts.index
    Drafts['Edit_norm'] = (Drafts['Edit']-Drafts['Edit'].min())/(Drafts['Edit'].max()-Drafts['Edit'].min())
    return Drafts

def cleanFilenames(directory):
    '''Renames files in the directory by putting underscores in place of commas
     and columns'''
    for filename in os.listdir(directory):
        filenameold = filename
        filename2 = "_".join(filename.replace(",", " ")
                             .replace(":", " ").split(" "))
        os.rename(directory+filenameold, directory+filename2)
