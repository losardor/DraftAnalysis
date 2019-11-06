import os
from datetime import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import re
import io
import HuffmanEncode as HE

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

def crosswithinlist(filename, window_lenght = 300, slideW = 50):
    df = pd.DataFrame()
    with open(filename, 'r') as f:
        listfile = list(f.read()) # random_text(10000)#
    
    textlen = (len(listfile)   // slideW ) * slideW
    if len(listfile)   // window_lenght < 2:
        return pd.DataFrame({0:[]})
    ind=0
    while ind <= textlen-(window_lenght*2):    
        #df.append
        crssntrpy = crossentropy(listfile[ind:ind+window_lenght],listfile[ind+window_lenght:ind+(window_lenght*2)])
        df = df.append([crssntrpy])
        #print(crossentropy(listfile[ind:ind+window_lenght],listfile[ind+window_lenght:ind+(window_lenght*2)]))
        ind += 50
    df.reset_index(inplace=True)
    df.drop(axis=0, columns=['index'], inplace=True)
    #df.index=list(range(len(listfile)   // slideW )-1)
    
    return df

def crossentropy(t1,t2):

    C12=crossCompress(t1,t2)
    h = HE.HuffmanCoding(C12)
    Cbits12 = h.BitsCompressed()
    #C2=compress(t2)
    #h = HE.HuffmanCoding(C2)
    #Cbits2 = h.BitsCompressed()
    #C1 = compress(t1)
    #h = HE.HuffmanCoding(C1)
    #Cbits1 = h.BitsCompressed()
    
    return Cbits12/(len(t1)+len(t2))

def twinLength(text,d,i):
    t=0
    if i<d:
        print("indexes in wrong order")
        return -1
    if i==d:
        return 0
    for j in range(0,min(i-d,len(text)-i)):
        #print(str(d+j)+" -- "+ str(j+i))
        if text[d+j]==text[j+i]:
            t=t+1
        else:
            return t
        
    return t

#------

def twinStart_N_length(text,i):
    d_t_max=i
    t_max=0
    
    for j in range(0,i+1):
        #print(str(text[j])+"=="+str(text[i]))
        if text[j]==text[i]:
            d=j
            t=twinLength(text,d,i)
            
            if t>t_max:
                t_max = t
                d_t_max = d
                
    return (d_t_max,t_max)

#------

def compress(text):
    j=0
    i = 0
    text_new = []
    while(i<len(text)):
        d,l = twinStart_N_length(text, i)
        if l == 0:
            elem = text[i]
        else:
            elem = (i-d,l)
        text_new.append(elem)
        i+=max(l,1)
        j+=1
    return text_new


#--------

def crossCompress(text1,text2):
    j=0
    i = 0
    text_new = []
    text = text1+text2
    while(i<len(text)):
        d,l = brotherStart_N_length(text, i, len(text1))
        if l == 0:
            elem = text[i]
        else:
            elem = (i-d,l)
        text_new.append(elem)
        i+=max(l,1)
        j+=1
    return text_new

#------

def brotherStart_N_length(text,i,L):
    d_t_max=i
    t_max=0
    
    for j in range(0,min(i+1,L)):
        #print(str(text[j])+"=="+str(text[i]))
        if text[j]==text[i]:
            d=j
            t=twinLength(text,d,i)
            if t+d > L:
                t = L-d

            if t>t_max:
                t_max = t
                d_t_max = d
                
    return (d_t_max,t_max)

#-------

def size_compresse(text):
    siz = 0
    for elem in text:
        if type(elem) is str:
            #print(str(elem)+' is a string')
            siz+=8
        elif type(elem) is tuple:
            #print(str(elem)+' is a tuple')
            siz+=32
        else:
            print('unrecognised element error')
            return None
    return siz

class sliding:
    def __init__(self, data):
        self.data = data
        self.avg = data.mean()
        self.var = data.var()
        self.var1 = np.var(np.diff(data[0]))

class draft:
    Cname = []
    contig = []
    Ccontig = []
    tag = []
    contigData = []
    sliding = []
    wordnumber = np.nan
    CharCount = np.nan

    def __str__(self):
        return "Cname: "+ Cname + "Ccontig: " + Ccontig + "tag: " + tag

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
    
    def Sliding(self, C=False):
        with io.open(self.filepath+"START/"+self.Cname,'r', encoding='utf-8') as f:
            text = f.read()
        if len(text)<600:
            self.sliding = sliding(pd.DataFrame(index = [], columns=["0"]))
        else:
            if C==False:
                slid = crosswithinlist(self.filepath+"START/"+self.Cname)
            else:
                if os.path.exists('ContigSliding.csv'):
                    os.remove("ContigSliding.csv")
                    #print("removed")
                os.system("bash runningWindow.sh "+self.filepath+"START/"+self.Cname)
                time.sleep(2)
                slid = pd.read_csv("ContigSliding.csv", sep="\t", header=None, skipfooter=1)
                slid = slid.drop(axis =1, columns=[0])
                slid[0] = slid[1]
                slid = slid.drop(axis =1, columns=[1])
            self.sliding = sliding(slid)
    
    def CountWords(self):
        with open(self.filepath+"START/"+self.Cname, 'r', encoding='utf-8') as f:
            text = f.read()
        wordnumber = len(re.findall(r'\w+', text))
        self.wordnumber = wordnumber
    
    def CharacterCount(self):
        with open(self.filepath+"START/"+self.Cname,'r', encoding='utf-8') as f:
            text = f.read()
        self.CharCount = len(text)


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
    
    def slide(self,C=False):
        for Draft in self.drafts:
            Draft.Sliding(C)
            self.drafts[Draft.index] = Draft

    
    def FindLastMacro(self):
        count1 = dt.strptime('01_01_01_01_2019', '%d_%m_%H_%M_%Y')
        count2 = dt.strptime('01_01_01_01_2019', '%d_%m_%H_%M_%Y')
        count3 = dt.strptime('01_01_01_01_2019', '%d_%m_%H_%M_%Y')
        count4 = dt.strptime('01_01_01_01_2019', '%d_%m_%H_%M_%Y')
        lastMacro1=0
        lastMacro2=0
        lastMacro3=0
        lastMacro4=0
        for i,draft in enumerate(self.drafts):
            if draft.Cname.split("_")[4] == '1':
                if count1<dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y'):
                    count1 = dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y')
                    lastMacro1 = i
            elif draft.Cname.split("_")[4] == '2':
                if count2<dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y'):
                    count2 = dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y')
                    lastMacro2 = i
            elif draft.Cname.split("_")[4] == '3':
                if count3<dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y'):
                    count3 = dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y')
                    lastMacro3 = i
            elif draft.Cname.split("_")[4] == '4':
                if count4<dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y'):
                    count4 = dt.strptime(str(draft.tag)+'_2019', '%d_%m_%H_%M_%Y')
                    lastMacro4 = i
            else:
                print('weird data input ad: '+draft.Cname)
        if lastMacro1 == 0:
            print(draft.Cname + " is last edit of draft 1")
        if lastMacro2 == 0:
            print(draft.Cname + " is last edit of draft 2")
        if lastMacro3 == 0:
            print(draft.Cname + " is last edit of draft 3")
        if lastMacro4 == 0:
            print(draft.Cname + " is last edit of draft 4")
        self.Last1 = lastMacro1
        self.Last2 = lastMacro2
        self.Last3 = lastMacro3
        self.Last4 = lastMacro4

def resetFolder(directory):
    os.system("rm -rf "+directory+"/*")
