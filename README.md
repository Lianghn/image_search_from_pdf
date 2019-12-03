## Motivation

The goal is to create a serach engine of pdf files with google style:
1. Pdf search page
2. Result page with first potentially associated images in the section above and text below, both linked to pdf files. 


## Tutorial for using the code 
(**Command line mode only, Web interface under developpement**)
##### Create an virtual enviroment:

`conda create -n pdfsearch python=3`

##### Install required pakcages

`pip install --user --requirement requirements.txt`

#####  Pdf extraction 

 - for extraction from one file, example:
   
    `python run_extract.py -f test/CNEWS-20190902-0.pdf`
    
 - for extraction from one folder, example:
   
    `python run_extract.py -d test` 
 
 #####  Pdf search 

 - for search from one file, example:
   
    `python run_search.py -f test/CNEWS-20190902-0.pdf -t france`
    
 - for extraction from one folder, example:
   
    `python run_search.py -d test -t france` 


