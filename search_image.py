import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import show
import matplotlib.image as mpimg
import re
import argparse
import os 
import glob
import subprocess

class search_image():
    
    def __init__(self,img_folder, output_csv):
        self.img_folder = img_folder
        self.output_csv = output_csv
        
    def find_image(self, mot_cle):
        res_list = []
      
        df1 = pd.read_csv(self.output_csv)
        df = df1.iloc[:,1:]
        mot_cle1 = ' '+mot_cle.lower()
        tmp = df[df['content'].str.contains(mot_cle)]
        if tmp.shape[0] == 0:
            print('No information found')
        else:
            if tmp[tmp['link-to'].notnull()].shape[0] == 0:
                print('Yop, no related photo, please read text below:')
            else:
                arr_img = tmp[tmp['link-to'].notnull()].iloc[:,8]
                # only first appended image taken 
                li_img = arr_img.apply(lambda x: x.strip().split(' ')[0]).tolist() 
                # delete duplicate image related to key-world
                set_img = set(li_img)
                print(set_img)
                for img in set_img:
                    f = re.search(r'([0-9]+)(Im|im|img)([0-9]+)', img)
                    new_group2 = 'Im' if f.group(2) == 'im' else f.group(2)
                    img_path=mpimg.imread(self.img_folder+'/'+f.group(1)+'_'+new_group2+f.group(3)+'.png')
                    page = f.group(1)
                    print('Legend text from page '+page+' :')
                    img_new    = 'im' if f.group(2) == 'Im' else f.group(2)
                    img_new = f.group(1)+img_new+f.group(3)+'.png'
                    tmp2 = df.iloc[df[df['content']==img_new].index.values.astype(int)[0], 8].strip().split(' ')[0].split('Text')[1]
                    tmp3 = df[(df['page']==int(page)) & (df['class-order-in-page']==int(tmp2)) & (df['class']=='T')]
                    legend = tmp3.iloc[0,7]
                    print(legend)      
                    res_list.append((img_path, page, legend))
            print(' All related text from :')
            for i in range(tmp.shape[0]):
                print('-------')
                print('page '+str(tmp.iloc[i, 0])+' :')
                print('-------')
                print(df.iloc[tmp.index[i], 7])     

        return res_list

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required = False, help = "PDF file to be processed")
    ap.add_argument("-d", "--directory", required = False, help = "folder with pdf files to be processed")
    ap.add_argument("-t", "--text", required = True, help = "text to match")

    args = vars(ap.parse_args())


    if args['file']:
        folder = os.path.dirname(os.path.abspath(args['file']))
        img_folder = folder+'/images_'+os.path.abspath(args['file']).split('/')[-1].split('.')[0]
        output_csv = folder+'/output_'+os.path.abspath(args['file']).split('/')[-1].split('.')[0]+'.csv'
        file = args['file']
        engine = search_image(img_folder, output_csv)
        try: 
            img_page_legend_list = engine.find_image(args['text'])
            num_img = len(img_page_legend_list)
            w = 5*num_img
            h = 5
            fig = plt.figure(figsize=(w,h))
            columns = num_img
            rows = 1
            print(num_img)
            ax = []
            for i in range(num_img):
                
                ax.append(fig.add_subplot(1, num_img, i+1))
                li_str= img_page_legend_list[i][2].split(' ')
                li_str = li_str[:20]
                new_legend = ' '.join([k for k in li_str[:len(li_str)//2]])+'\n'+' '.join([k for k in li_str[len(li_str)//2:]])
                ax[-1].set_title('PATH: Page '+img_page_legend_list[i][1]+' of file '+file+'\n\n LEGEND: '+new_legend, {'fontsize':10})
                plt.imshow(img_page_legend_list[i][0])
        except:
            engine.find_image(args['text'])
            pass
        print('############')
        print('Search done!')
        print('############')
        show()

    if args['directory']:
        folder = os.path.abspath(args['directory'])
        for file in  glob.glob(folder+'/*pdf'):
            print('####################################')
            print('###File '+file.split('/')[-1])
            print('####################################')
            img_folder = folder+'/images_'+file.split('/')[-1].split('.')[0]
            output_csv = folder+'/output_'+file.split('/')[-1].split('.')[0]+'.csv'
            engine = search_image(img_folder, output_csv)
            try: 
                img_page_legend_list = engine.find_image(args['text'])
                num_img = len(img_page_legend_list)
                w = 5*num_img
                h = 5
                fig = plt.figure(figsize=(w,h))
                columns = num_img
                rows = 1
                print(num_img)
                ax = []
                for i in range(num_img):
                
                    ax.append(fig.add_subplot(1, num_img, i+1))
                    li_str= img_page_legend_list[i][2].split(' ')
                    li_str = li_str[:20]
                    new_legend = ' '.join([k for k in li_str[:len(li_str)//2]])+'\n'+' '.join([k for k in li_str[len(li_str)//2:]])
                    ax[-1].set_title('PATH: Page '+img_page_legend_list[i][1]+' of file '+file+'\n\n LEGEND: '+new_legend, {'fontsize':10})
                    plt.imshow(img_page_legend_list[i][0])
            except:
                engine.find_image(args['text'])
                pass
        print('############')
        print('Search done!')
        print('############')
        show()

    if not (args['file'] or args['directory']):
        print('Give at least a file or folder name with -f filename | -d foldername')

