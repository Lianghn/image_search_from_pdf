import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', 500)
import nltk
import re
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.corpus import stopwords
import matplotlib.image as mpimg
import argparse
import os 
import glob
import subprocess

class search_engine():
    
    def __init__(self,img_folder, output_csv):
        self.img_folder = img_folder
        self.output_csv = output_csv
        
    def find_image(self, mot_cle):
        df1 = pd.read_csv(self.output_csv)
        df = df1.iloc[:,1:]
        tmp = df[df['content'].str.contains(mot_cle)]
        if tmp.shape[0] == 0:
            print('No information found')
        else:
            if tmp[tmp['link-to'].notnull()].shape[0] == 0:
                print('Yop, no related photo, please read text below:')
                for i in range(tmp.shape[0]):
                    print('----------------------------------------------')
                    print('text from page '+str(tmp.iloc[i, 0])+' :')
                    print(df.iloc[tmp.index[i], 7])           
            else:
                img = tmp[tmp['link-to'].notnull()].iloc[0,8]
                img=mpimg.imread(self.img_folder+img.split(' ')[1].replace('Im', '_Im'))
                imgplot = plt.imshow(img)
                plt.show()
                print('text from page '+str(tmp[tmp['link-to'] !=''].iloc[0,0])+' :')
                print(df.iloc[tmp[tmp['link-to'] !=''].index[0], 7])      
                for i in range(tmp.shape[0]):
                    print('----------------------------------------------')
                    print('text from page '+str(tmp.iloc[i, 0])+' :')
                    print(df.iloc[tmp.index[i], 7])     
engine = search_engine('Test/images_CNEWS-20190903-0/', 'Test/output_CNEWS-20190903-0.csv')
mot_cle = 'étoiles'
engine.find_image(mot_cle)
