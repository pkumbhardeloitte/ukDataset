# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 15:25:00 2019

@author: pkumbhar
"""

#Load modules

from bs4 import BeautifulSoup
import urllib
import pandas as pd

#Global Variables
dfData = pd.read_csv("C:\\Users\\pkumbhar\\Documents\\ContextEdgeRegXplorer\\UK\\AllRegLinksFinal.csv",nrows=5000,header=[0,],sep='\t')
legTypeHardCode = 'UK Public General Acts (4337)'

def extractSectionData(baseLink, eachLegEntry):
    sectionNumberVar = eachLegEntry.find_all('span',{'class':'LegContentsNo'})[0].get_text()
    sectionTitleVar = eachLegEntry.find_all('span',{'class':'LegContentsTitle'})[0].get_text()
    
    sectionLink = baseLink + eachLegEntry.find('a').get('href')
    sectionPage = urllib.request.urlopen(sectionLink)
    sectionSoup = BeautifulSoup(str(sectionPage.read()),"html.parser")
    sectionContents = sectionSoup.find_all('div',{'id':'viewLegSnippet'})[0].find_all('p')
    sectionCompleteText = ''
    for eachsectionContents in sectionContents:
        sectionCompleteText += '\n**' + eachsectionContents.get_text()
    return (sectionNumberVar, sectionTitleVar, sectionLink, sectionCompleteText)

#Extract Data
def extractData(baseLink):
    legTitle = []
    legType = []
    legNo = []
    legDateOfEnactment = []
    
    partNumbers = []
    partName = []
    subPartName = []
    
    sectionNumbers = []
    sectionTitle = []
    sectionLinks = []
    sectionText = []
    
    #Temp variable
    count = 0
    for row in dfData.iterrows():
        if count > 0:
            break
        count += 1
        regType = row[1]['Reg Type']
        regLink = row[1]['Reg Link']
        regFormat = row[1]['Reg Format']
        if regFormat == 'Web' and legTypeHardCode in regType:
            mainPage = urllib.request.urlopen(regLink)
            mainSoup = BeautifulSoup(str(mainPage.read()),"html.parser")
            LegContents = mainSoup.find_all('div',{'class':'LegContents'})
            mainOl = LegContents[0].find_all('ol')[0]
            pageTitle = mainSoup.find_all('h1',{'class':'pageTitle'})
            for eachOl in mainOl:
                print('\n')
                if(eachOl.get_text() == "Introductory Text"):
                    print(eachOl.get_text(),'****Introduction')
                    print(baseLink + eachOl.find('a').get('href'))
                    introPageLink = baseLink + eachOl.find('a').get('href')
                    subPage = urllib.request.urlopen(introPageLink)
                    subSoup = BeautifulSoup(str(subPage.read()),"html.parser")
                    
                    #Update all lists
                    legTitle.append(pageTitle[0].get_text())
                    legType.append(legTypeHardCode)
                    legNo.append(subSoup.find_all('h1',{'class':'LegNo'})[0].get_text())
                    legDateOfEnactment.append(subSoup.find_all('p',{'class':'LegDateOfEnactment'})[0].get_text())
                    partNumbers.append('NA')
                    partName.append('NA')
                    subPartName.append('NA')
                    sectionNumbers.append('NA')
                    sectionTitle.append('Introductory Text')
                    sectionLinks.append(introPageLink)
                    sectionText.append(subSoup.find_all('p',{'class':'LegLongTitle'})[0].get_text() + '\n' + subSoup.find_all('p',{'class':'LegText'})[0].get_text())
                    
                elif 'LegContentsEntry' in eachOl.get('class'):
                    print(eachOl.get_text(),'****Section')
                    
                    sectionNumberVar, sectionTitleVar, sectionLinkVar, sectionCompleteText = extractSectionData(baseLink, eachLegEntry)
                    
                elif 'LegContentsSchedules' in eachOl.get('class'):
                    print(eachOl.get_text(),'****Schedules')
                elif 'LegContentsPart' in eachOl.get('class'):
                    print(eachOl.get_text(),'****PART')
                elif 'LegContentsPblock' in eachOl.get('class'):
                    print(eachOl.get_text(),'****SUB PART')
                    subPartNameVar = eachOl.find_all('p',{'class':'LegContentsTitle'})[0].get_text()
                    subPartOl = eachOl.find_all('ol')[0]
                    for eachLegEntry in subPartOl:
                        sectionNumberVar, sectionTitleVar, sectionLinkVar, sectionCompleteText = extractSectionData(baseLink, eachLegEntry)
                        #Update all lists
                        legTitle.append(pageTitle[0].get_text())
                        legType.append(legTypeHardCode)
                        legNo.append('')
                        legDateOfEnactment.append('')
                        partNumbers.append('NA')
                        partName.append('NA')
                        subPartName.append(subPartNameVar)
                        sectionNumbers.append(sectionNumberVar)
                        sectionTitle.append(sectionTitleVar)
                        sectionLinks.append(sectionLinkVar)
                        sectionText.append(sectionCompleteText)
    
    data = {'sectionText':sectionText,'sectionTitle:':sectionTitle,'sectionNumbers':sectionNumbers,'subPartName':subPartName,'partName':partName,'partNumbers':partNumbers,'legType':legType, 'legNo':legNo, 'legTitle':legTitle, 'legDateOfEnactment':legDateOfEnactment}
    print(data)
    




    
def storeDataToCsv(data):
    try:
        df = pd.DataFrame(data)
        with open('UKDataExtract1.csv', 'a') as f:
            df.to_csv(f, header=False)
        return True
    except:
        return False
    
#Main function
def main():
    #legTypeList = ['http://www.legislation.gov.uk/ukpga', 'http://www.legislation.gov.uk/ukla', 'http://www.legislation.gov.uk/uksi', 'http://www.legislation.gov.uk/ukmo']
    
    #for eachLegType in legTypeList:
    data = extractData('http://www.legislation.gov.uk')
        #break #Testing for UK Public general acts
    if data:    
        result = storeDataToCsv(data)
        if result:
            print('Data Extracted Successfully')
        else:
            print('Error in Wrinting data')

main()
