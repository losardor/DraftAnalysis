import os
from datetime import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time

def plot_sliding_prop(Data, prop):
    x = np.linspace(0, 5, 100)
    cmap = plt.get_cmap('jet')
    fig = plt.figure(figsize=(14,6))
    ax = fig.add_axes([1,1,1,1])
    N = len(Data)
    for i,author in enumerate(Data):
        color = cmap(float(i)/N)
        plot_df = pd.DataFrame()
        x = [dt.strptime(draft.tag, '%d_%m_%H_%M') for draft in author.drafts]
        sliding_avg = [float(getattr(draft.sliding,prop)) for draft in author.drafts]
        plot_df['x']  = x
        plot_df['y'] = sliding_avg
        plot_df.sort_values(by='x')
        plot_df.reset_index()
        plot_df['Edit_norm'] = plot_df.index/plot_df.index.max()
        plot_df.plot(ax =ax,x='Edit_norm',y='y',c=color, label=author.name)
    plt.ylabel(prop)

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def cleanFilenames(directory):
    '''Renames files in the directory by putting underscores in place of commas
     and columns'''
    for filename in os.listdir(directory):
        filenameold = filename
        filename2 = "_".join(filename.replace(",", " ")
                             .replace(":", " ").split(" "))
        os.rename(directory+filenameold, directory+filename2)
        return filename2

def cleanFilename(filename, directory):
    '''Renames a single file to fit in the filename convention'''
    filename2 = "_".join(filename.replace(",", " ")
        .replace(":", " ").split(" "))
    os.rename(directory+filename, directory+filename2)
    return filename2

def cleanContig(directory, filename, output = False):
    #print(filename)
    if not os.path.exists(directory):
        print(directory+filename)
        raise NameError('Missing Data')
    months = {'January': 1, 'February': 2, 	"March":3, "April":4, "May": 5,
        "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, 
        "November": 11, "December": 12}
    dateTime = filename.split("_")[6:]
    dateTime = [months[i] if i in months.keys() else i for i in dateTime ]
    try:
        date = str(dateTime[0])+'-'+str(dateTime[1])+'-'+'2019'
    except:
        print(filename+ " is not in the correct format for this analysis")
    time = dateTime[3]+':'+dateTime[4]
    tag = dt.strptime(date + ' ' + time, '%d-%m-%Y %H:%M').strftime("%d_%m_%H_%M")
    df = pd.read_csv(directory+filename, header=None)
    
    df = df[0].str.split("_", n=10, expand = True) 
    if output:
        print(filename)
        print(tag)
    df = df.drop([0,1,5,8], axis=1)
    new = df[10].str.split("\t", n=2, expand = True)
    df[10]=new[0]
    df['distance'] = new[1]
    df = df.replace(months)
    #print(df.head())
    df['date'] = df[6].astype('str')+'-'+df[7].astype('str')+'-'+'2019'
    df['time'] = df[9].astype('str')+':'+df[10].astype('str')
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], dayfirst = True)
    df = df.drop([6,7,9,10, 'date', 'time'], axis=1)
    df = df.rename(index=str, columns={2:'WorkshopEd', 
                                       3:'Username', 4:'MacroRev'})
    df['distance'] = pd.to_numeric(df['distance'])
    df = df.sort_values(by='datetime').reset_index(drop=True)
    df['Edit']=df.index
    df = df.set_index('datetime')
    df['Edit_norm'] = (df['Edit']-df['Edit'].min())/(df['Edit']
                                                     .max()-df['Edit'].min())
    savepath = directory+'../CleanContigs/Contig'+tag+'.csv'
    df.to_csv(savepath)
    return tag, df, savepath

class sliding:
    def __init__(self, data):
        self.data = data
        self.avg = data.mean()
        self.var = data.var()
        self.var1 = np.var(np.diff(data[1]))

class draft:
    Cname = []
    contig = []
    Ccontig = []
    tag = []
    contigData = []
    sliding = []

    def __init__(self, filename, index, author):
        self.author = author
        self.filename = filename
        self.index = index
        self.filepath = "./Data/WORKING/"+author+"/"
    
    def CleanContig(self):
        if not os.path.exists(self.filepath+'START/CleanContigs'):
            os.makedirs(self.filepath+'START/CleanContigs')
        self.contig = "Contig."+self.Cname
        tag_temp, contigData, savepath = cleanContig(self.filepath+"START/ris_bcl+10000-10000/", self.contig)
        self.tag = tag_temp
        self.Ccontig = savepath
        self.contigData = contigData
    
    def Sliding(self):
        if os.path.exists("./ContigSlinding"):
            os.system("rm ContigSlinding")
        print("bash runningWindow.sh "+self.filepath+"START/"+self.Cname)
        os.system("bash runningWindow.sh "+self.filepath+"START/"+self.Cname)
        time.sleep(2)
        slid = pd.read_csv("ContigSliding", sep="\t", header=None)
        slid = slid.drop([0], axis =1)
        self.sliding = sliding(slid)

def Hello():
    print("Helloworld")

class author:

    def __init__(self, name):
        self.name = name
        self.directory = name.upper()
        print(self.directory)
        self.originpath = "./Data/INPUT/"+name.upper()+"/"
        self.workingpath = "./Data/WORKING/"+name.upper()+"/"
        os.system("cp -r "+self.originpath+" "+self.workingpath)
        filenames = [file for file in files(self.workingpath+"START/")]
        try:
            filenames.remove('.DS_Store')
        except:
            pass

        drafts = list()
        for i, filename in enumerate(filenames):
            #print(filename)
            drafts.append(draft(filename, i, self.directory))
        self.drafts = drafts

    def cleanfilenames(self):
        for Draft in self.drafts:
            self.drafts[Draft.index].Cname =  cleanFilename(Draft.filename,
                self.workingpath+"START/")

    def createContigs(self):
        if os.path.exists("./START"):
            os.system("rm -r ./START")
        os.rename(self.workingpath+"START", "./START")
        #os.system("cp ./bcl3pezza ./temp/bcl3pezza")
        os.system("./bcl3pezza")
        os.rename("./START", self.workingpath+"START")
        #os.system("rm "+self.path+"START/bcl3pezza")
        for Draft in self.drafts:
            Draft.CleanContig()
            self.drafts[Draft.index] = Draft
    
    def slide(self):
        for Draft in self.drafts:
            Draft.Sliding()
            self.drafts[Draft.index] = Draft

def resetFolder(directory):
    os.system("rm -rf "+directory+"/*")
