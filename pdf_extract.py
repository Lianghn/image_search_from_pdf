import os 
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize
from nltk.corpus import stopwords
import argparse
import glob
import subprocess
from layout_scanner import get_pages

class text_image():

    def __init__(self,file, outputfile, img_folder, output_csv):
        """
        file       : pdf file to scan
        outputfile : output containing text & image layout and text information
        img_folder : folder to save images from pdf
        """
        self.file = file
        self.outputfile = outputfile
        self.img_folder = img_folder
    
    def file_scan(self):
        """use pdfminer to scan pdf and save to outputfile and img_folder"""
        get_pages(self.file, '',  self.outputfile, self.img_folder)
 
    def output_to_df(self):
        """
        convert output txt file to dataframe
        df  : dataframe
        """
        with open(outputfile, 'r') as f:
            lines = f.readlines()
        # array of text/image line
        arr_li = []
        #convert  a line of box/images informations to a list.
        for li in lines:
            if 'START-PAGE' in li:
                page = li.split(' ')[1]
            elif  'TextBoxH' in li:
                arr_li.append([page, 'T',li.split(' ')[0].split('(')[1].split(')')[0], \
                               li.split(',')[0].split(' ')[1],li.split(',')[1], \
                              li.split(',')[2],li.split(',')[3].split(' ')[0], ' '.join([i for i in li.split(' ')[2:]]), ''])
            elif 'LTImage' in li:
                arr_li.append([page, 'I',li.split(' ')[0].split('(')[1].split(')')[0][2:], \
                               li.split(',')[0].split(' ')[1],li.split(',')[1], \
                               li.split(',')[2],li.split(',')[3].split(' ')[0], page+ \
                               li.split(' ')[0].split('(')[1].split(')')[0]+'.png', ''])
        arr_li = np.asarray(arr_li)
        df = pd.DataFrame(arr_li, columns=['page', 'class', 'class-order-in-page','xmin', 'ymin', 'xmax', 'ymax', 'content','link-to'])
        df['content'] = df['content'].apply(lambda x:  None if re.match(r"^\'(.\\n|CNEWS.FR)", x) else x).tolist()
        df = df.dropna().reset_index(drop=True)
        df['content'] = df['content'].apply(lambda x: re.sub(r'(\\n|\>\s|\')', ' ', x))
        df[['page', 'class-order-in-page']] = df[['page', 'class-order-in-page']].astype('int')
        df[[ 'xmin', 'ymin', 'xmax', 'ymax']] = df[['xmin', 'ymin', 'xmax', 'ymax']].astype('float')
        return df

    def image_legend_association(self, df):
        for page in df['page'].unique():
            df_page = df[df['page']==page]       
            df_box = df_page[df_page['class']=='T']
            df_img = df_page[df_page['class']=='I']
            for ord_img in df_img['class-order-in-page'].unique():
                for ord_box in  df_box['class-order-in-page'].unique():
                    img_ymin = df_img[df_img['class-order-in-page']==ord_img].iloc[0,4]
                    box_ymax = df_box[df_box['class-order-in-page']==ord_box].iloc[0,6]
                    img_xmin = df_img[df_img['class-order-in-page']==ord_img].iloc[0,3]
                    box_xmin = df_box[df_box['class-order-in-page']==ord_box].iloc[0,3]
                    if  ( (abs(img_ymin - box_ymax) < 10) and (abs(img_xmin - box_xmin) < 10)) :
                        df.iloc[df_box[df_box['class-order-in-page']==ord_box].index.values.astype(int)[0],8] =  \
                        df.iloc[df_box[df_box['class-order-in-page']==ord_box].index.values.astype(int)[0],8]+' '+ \
                        df.iloc[df_img[df_img['class-order-in-page']==ord_img].index.values.astype(int)[0],7]
                        df.iloc[df_img[df_img['class-order-in-page']==ord_img].index.values.astype(int)[0],8] =  \
                        df.iloc[df_img[df_img['class-order-in-page']==ord_img].index.values.astype(int)[0],8]+' '+\
                        str(page)+'Text'+str(ord_box)
        return df
        
    def text_preprocessing(self, df):
        tokenizer = RegexpTokenizer(r'\w+')
        df['content_processed'] = df['content'].apply(lambda x: tokenizer.tokenize(x))
        #.apply(lambda x: [nltk.stem.snowball.FrenchStemmer().stem(i) for i in x])
        a = set(stopwords.words('french'))
        new_stopwords = ['a', 'être', 'avoir']
        a = a.union(set(new_stopwords))
        df['content_processed'] = df['content_processed'].apply(lambda x: [nltk.stem.snowball.FrenchStemmer().stem(i) for i in x]) \
        .apply(lambda x: [i for i in x if i not in a])
        return df

    def image_text_association(self, df, asso):
        """
        asso  : variable for image-textbox association type
        = 1   : image with textbox on its left
        = 2   : image with textbox on its right
        = 3   : image with textbox below
        = 4   : image with textbox above 
        = 5   : image with textbox wiht cross-section
        """
        for page in df['page'].unique():
            df_page = df[df['page']==page]       
            df_box = df_page[df_page['class']=='T']
            df_img1 = df_page[df_page['class']=='I']
            df_img = df_img1[df_img1['link-to']!='']
            for ord_img in df_img['class-order-in-page'].unique():
                # ord_box2 is the lengend text box order.
                ord_box2 = int(df_img[df_img['class-order-in-page']==ord_img].iloc[0,8].split("Text")[1])
                for ord_box in  df_box['class-order-in-page'].unique():
                    # box_xmin is the box compared to image
                    img_ymin = np.squeeze(df_img[df_img['class-order-in-page']==ord_img].iloc[:,4])
                    img_xmin = np.squeeze(df_img[df_img['class-order-in-page']==ord_img].iloc[:,3])
                    img_xmax = np.squeeze(df_img[df_img['class-order-in-page']==ord_img].iloc[:,5])
                    img_ymax = np.squeeze(df_img[df_img['class-order-in-page']==ord_img].iloc[:,6])
                    box_xmin = np.squeeze(df_box[df_box['class-order-in-page']==ord_box].iloc[:,3])
                    box_ymin = np.squeeze(df_box[df_box['class-order-in-page']==ord_box].iloc[:,4])
                    box_xmax = np.squeeze(df_box[df_box['class-order-in-page']==ord_box].iloc[:,5])
                    box_ymax = np.squeeze(df_box[df_box['class-order-in-page']==ord_box].iloc[:,6])
                    if asso == 1:
                        condition = ( ( ((img_xmin - box_xmax) < 20) and ((img_xmin - box_xmax) > 0) )  \
                         and (not ( (img_ymax<box_ymin) or (img_ymin > box_ymax) ) ) )
                    elif asso == 2:
                        condition = ( ( ((box_xmin - img_xmax) < 20) and ((box_xmin - img_xmax) > 0) ) \
                        and (not ( (img_ymax<box_ymin) or (img_ymin > box_ymax) ) ) )
                    elif asso == 3:
                        condition = ( ( ((box_ymin - img_ymax) < 20) and ((box_ymin - img_ymax) > 0) ) \
                        and (not ( (img_xmax<box_xmin) or (img_xmin > box_xmax) ) ) )
                    elif asso == 4:
                        condition = ( ( ((img_ymin - box_ymax) < 40) and ((img_ymin - box_ymax) > 20) ) \
                        and (not ( (img_xmax<box_xmin) or (img_xmin > box_xmax) ) ) )
                    elif asso == 5:
                        condition = ((not ( ((img_ymin - box_ymax) > 0) or ((box_ymin - img_ymax) > 0) \
                        or ((img_xmin - box_xmax) > 0) or ((box_xmin - img_xmax) > 0))) and (ord_box != ord_box2))
                        
                    if  condition:
                        match = set(df_box[df_box['class-order-in-page']==ord_box].iloc[0,9]) \
                         .intersection(set(df_box[df_box['class-order-in-page']==ord_box2].iloc[0, 9]))
                        if (len(list(match)) >=1):
                            if len(list(match))==1 :
                                if not re.match(r'[a-zA-Z0-9]', list(match)[0]) :
                                        df.iloc[df_box[df_box['class-order-in-page']==ord_box2].index.values.astype(int)[0],8] =  \
                                        df.iloc[df_box[df_box['class-order-in-page']==ord_box2].index.values.astype(int)[0],8]+' '+ \
                                        ' '.join([i for i in df.iloc[df_img[df_img['class-order-in-page']==ord_img] \
                                                                     .index.values.astype(int)[0],9]])
                            else:
                                        df.iloc[df_box[df_box['class-order-in-page']==ord_box2].index.values.astype(int)[0],8] =  \
                                        df.iloc[df_box[df_box['class-order-in-page']==ord_box2].index.values.astype(int)[0],8]+' '+ \
                                        ' '.join([i for i in df.iloc[df_img[df_img['class-order-in-page']==ord_img]\
                                                                     .index.values.astype(int)[0],9]])
        return df                


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required = False, help = "PDF file to be processed")
    ap.add_argument("-d", "--directory", required = False, help = "folder with pdf files to be processed")
    args = vars(ap.parse_args())

    if args['file']:
        folder = os.path.dirname(os.path.abspath(args['file']))
        img_folder = folder+'/images_'+os.path.abspath(args['file']).split('/')[-1].split('.')[0]
        file = args['file']
        outputfile = folder+'/output_'+os.path.abspath(args['file']).split('/')[-1].split('.')[0]+'.txt'
        output_csv = folder+'/output_'+os.path.abspath(args['file']).split('/')[-1].split('.')[0]+'.csv'
        try:
            subprocess.call('mkdir -p '+img_folder, shell=True)
        except:
            pass

        engine = text_image(file, outputfile, img_folder, output_csv)
        print('-------------------')
        print('Start extraction...')
        engine.file_scan()
        print('txt file generated.')
        df = engine.output_to_df()
        df = engine.image_legend_association(df)
        df = engine.text_preprocessing(df)
        print('text preprocessing done.')
        for i in range(1,6):
            df = engine.image_text_association(df,i)
        df.to_csv(output_csv)
        print('csv file saved')
        print('Extraction done')

    if args['directory']:
        folder = os.path.abspath(args['directory'])
        for file in  glob.glob(folder+'/*pdf'):    
            img_folder = folder+'/images_'+file.split('/')[-1].split('.')[0]
            outputfile = folder+'/output_'+file.split('/')[-1].split('.')[0]+'.txt'
            output_csv = folder+'/output_'+file.split('/')[-1].split('.')[0]+'.csv'
            try:
                subprocess.call('mkdir -p '+img_folder, shell=True)
            except:
                pass
            engine = text_image(file, outputfile, img_folder, output_csv)
            print('-------------------')
            print('Start extraction...')
            engine.file_scan()
            print('txt file generated.')
            df = engine.output_to_df()
            df = engine.image_legend_association(df)
            df = engine.text_preprocessing(df)
            print('text preprocessing done.')
            for i in range(1,6):
                df = engine.image_text_association(df,i)   
            df.to_csv(output_csv)
            print('csv file saved')
            print('Extraction done')
 
    if not (args['file'] or args['directory']):
        print('Give at least a file or folder name by -i xx | -d xx !!')
