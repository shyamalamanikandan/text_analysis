# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 14:57:26 2018

@author: dura1
"""

import PyPDF2
import docx2txt
import os
from pathlib import Path



# Reading Docx file
def docReader(fileName):
    text = docx2txt.process(fileName)
    text = text.replace("\n","")
    return text

# Reading text file
def textReader(fileName):
    text =Path(fileName).read_text()
    text = text.replace("\n","")
    return text

def pdfReader(fileName):

    # creating a pdf file object
     pdfFileObj = open(fileName,'rb')

    # creating a pdf reader object
     pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    #Getting  number of pages in pdf file
     num_pages = pdfReader.numPages

     count = 0
     text = ""
    #The while loop will read each page
     while count < num_pages:
      pageObj = pdfReader.getPage(count)
      count +=1
      text += pageObj.extractText()

    # closing the pdf file object
     pdfFileObj.close()
     text = text.replace("\n","")
     return text
 
def fileReaderMethod(fileName):

    result =""
    extension = os.path.splitext(fileName)
    
    if extension[1].lower() == ".docx" :
       result = docReader(fileName)
    elif extension[1].lower() == ".pdf" :
       result = pdfReader(fileName)
    elif extension[1].lower() == ".txt" :
       result = textReader(fileName)   
       
    return result
    




