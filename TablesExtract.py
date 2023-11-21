import tabula
#from PyPDF2 import PdfReader
import PyPDF2
import re
import os
import pandas as pd
import numpy as np

def GetTables(pdf, tables):
    for i in range (len(pdf.pages)):
            global data
            start = False
            digit = False
            Finish = False
            data = []
            heading = []
            counter = 0
            page = pdf.pages[i]
            text = page.extract_text()
            if re.findall(r'table\s*\d+', text, re.I) or re.findall(r'table\s*:\s*\d+', text, re.I):
                lines = text.split('\n')
                for line in lines:
                    row = line.split()
                    for point in row:
                        if re.findall(r'^\s*table\s*\d+', line, re.I) or re.findall(r'^\s*table\s*:\s*\d+', line, re.I):
                            start = True
                        if start:
                            if re.search(r'\w+\s+(\d+\s*)?\w+\s+(\d+\s*)?\w+', line, re.I) and digit:
                                counter += 1
                                if counter > 2:
                                    Finish = True
                            if re.findall(r'\s*\d+\s+(\w+\s*)?\d*\s+(\w+\s*)?\d*', line, re.I):
                                digit = True
                            tables.append(point)
                    if tables != [] and start:
                        data.append(tables)
                        tables = []
                    if data != [] and digit and Finish:
                        CleanTables(data)
                        data = []
                        digit = False
                        start = False
                        Finish = False

      
def CleanTables(data):
    start = True
    global heading
    column_headings = [] 
    columns = []
    Heading = [] 
    Data = []
    broke = False
    for i in data:
        points = ' '.join(i)
    react = ''.join(points)
    for i in reversed(data):
        for j in i:
            if re.findall(r'table', j, re.I):
                Data.insert(0,i)
                broke = True
        if broke:
            break
        Data.insert(0,i)
    for i in range(len(Data)):
        for j in range(i):
            try:
                Data[i][j] = Data[i][j].replace(',' ,'.')
                Data[i][j] = float(Data[i][j])
            except:
                i = i
    for line in Data:
        for i in line:
            columns.append(i)
            try: 
                if re.findall(r'%|\)|ratio|others|C4|C5|CH4|α|catalyst|number|reactors', i, re.I) and not re.findall(r'hydrocarbon|^/|^%', i, re.I):
                    columns = ' '.join(columns)
                    if re.findall(r'distribution', columns):
                        break
                    column_headings.append(columns)
                    columns = []
            except:
                ToPanda(Data, column_headings, react)
        try:
            if columns != []:  
                columns = []
        except:
            i = i       

def format(value):
    value = re.findall(r'\d+(?:[.,]\d+)?', value)
    value = value[-1]
    value = value.replace(',' ,'.')
    value = float(value)
    return value

def ToPanda(Data, column_headings, react):
    dict = {'Base': [], 'Promoter': [], 'Temperature (K)': [], 'Pressure (bar)': [], 'Feed Ratio': [], 'Conversion': [], 'Selectivity C1': [], 'Selectivity C2-C4': [], 'Selectivity C5+': [], ' Rate': [], 'Probability Chain Growth': [], 'BET': []} 
    digit = False
    counter = 0
    for line in Data:
        dict = {'Base': [], 'Promoter': [], 'Temperature (K)': [], 'Pressure (bar)': [], 'Feed Ratio': [], 'Conversion': [], 'Selectivity C1': [], 'Selectivity C2-C4': [], 'Selectivity C5+': [], ' Rate': [], 'Probability Chain Growth': [], 'BET': []}
        for i in line:
            try:
                value = i
                header = column_headings[line.index(i)]
                if re.findall(r'Temp|T/', header, re.I) and dict['Temperature (K)'] == []:
                    dict['Temperature (K)'].append(Temp(value, header))
                elif re.findall(r'Pres', header, re.I) and dict['Pressure (bar)'] == []:
                    dict['Pressure (bar)'].append(Press(value, header))
                elif re.findall(r'feed ratio', header, re.I) and dict['Feed Ratio'] == []:
                    dict['Feed Ratio'].append(ratio(value, header))
                elif re.findall(r'conv|sion', header, re.I) and dict['Conversion'] == []:
                    dict['Conversion'].append(conv(value, header))
                elif re.findall(r'sel|CH4', header, re.I) and dict['Selectivity C1'] == []:
                    dict['Selectivity C1'].append(select(value, header))
                elif re.findall(r'sel|C2|C4', header, re.I) and dict['electivity C2-C4'] == []:
                    dict['Selectivity C2-C4'].append(select(value, header))
                elif re.findall(r'sel|C5', header, re.I) and dict['Selectivity C5+'] == []:
                    dict['Selectivity C5+'].append(select(value, header))
                elif re.findall(r'Probability chain growth|α', header, re.I) and dict['Probability Chain Growth'] == []:
                    dict['Probability Chain Growth'].append(float(value))
                elif re.findall(r'bet', header, re.I) and dict['BET'] == []:
                    dict['BET'].append(bet(value, header))
                    
            except:
                i = i
        if re.findall(r'React', react, re.I):
            temp = re.findall(r'\d+\s*K|.°C|\d+\s*˙C|\d+\s*◦C', react, re.I)
            press = re.findall(r'\s+\d+(?:\.\d+)?\s*barg|\s+\d+(?:\.\d+)?\s*bar|\s+\d+(?:\.\d+)?\s*kpag|\s+\d+(?:\.\d+)?\s*kpa|\s+\d+(?:\.\d+)?\s*atm|\s+\d+(?:\.\d+)?\s*mpa', react, re.I)
            feedratio = re.findall(r'feed ratio\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|h2/co2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|co2/h2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|h2:co2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|co2:h2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?',react, re.I)
            try:
                if temp:
                    dict['Temperature (K)'].append(Temp(temp[-1], temp[-1]))
                if press:
                    dict['Pressure (bar)'].append(Press(press[-1], press[-1]))
                if feedratio:
                    dict['Feed Ratio'].append(ratio(feedratio[-1], feedratio[-1]))
            except:
                i = i

        present = False
        for item in dict:
            if dict[item] == []:
                dict[item].append(0)
            else:
                present = True
        global df
        if present:
            data_points = pd.DataFrame(dict,columns=['Base', 'Promoter', 'Temperature (K)', 'Pressure (bar)', 'Feed Ratio', 'Conversion', 'Selectivity C1', 'Selectivity C2-C4', 'Selectivity C5+', ' Rate', 'Probability Chain Growth', 'BET'], index = [file])
            df = pd.concat([data_points, df])
            df.drop_duplicates(inplace = True)
    

def Temp(value, search):
    if re.search(r'c', search, re.I):
        value = format(value) + 273
    elif re.search(r'k', search, re.I):
        value = format(value)
    return(value)

def Press(value, search):
    if re.search(r'barg', search, re.I):
        value = format(value) - 1.01
    elif re.search(r'kpag', search, re.I):
        value = (format(value) - 101)/100
    elif re.search(r'kpa', search, re.I):
        value = format(value)/100
    elif re.search(r'mpa', search, re.I):
        value = format(value)*10
    elif re.search(r'atm', search, re.I):
        value = format(value) * 1.01
    elif re.search(r'bar', search, re.I):
        value = format(value)
    return(value)

def ratio(value, search):
    if re.search(r'co2/h2|co2:h2', search, re.I):
        value = re.findall(r'\d+(?:[.,]\d+)?', search)
        val1 = value[-1].replace(',','.')
        val2 = value[-2].replace(',','.')
    elif re.search(r'feed ratio|h2/co2|h2:co2', search, re.I):
        value = re.findall(r'\d+(?:[.,]\d+)?', search)
        val1 = value[-2].replace(',','.')
        val2 = value[-1].replace(',','.')
    val1 = float(val1)
    val2 = float(val2)
    value = val1/val2
    if re.search(r'feed ratio', search, re.I):
        value = value = re.findall(r'\d+(?:[.,]\d+)?', search)
        value = float(value)
    return(value)

def conv(value, search):
    value = float(value)
    if value > 1:
        value = value / 100
    else:
        value = value
    return(value)

def select(value, search):
    value = float(value)
    if value > 1:
        value = value / 100
    else:
        value = value
    return(value)

def bet(value, search):
    if re.search(r'm2/kg', search, re.I):
        value = format(value)/1000
    elif re.search(r'cm2/g', search, re.I):
        value = format(value)/10000
    elif re.search(r'cm2/kg', search, re.I):
        value = format(value)/10000000
    elif re.search(r'm2/g', search, re.I):
        value = format(value)
    value = float(value)
    return(value)

df = pd.DataFrame(columns=['Base', 'Promoter', 'Temperature (K)', 'Pressure (bar)', 'Feed Ratio', 'Conversion', 'Selectivity C1', 'Selectivity C2-C4', 'Selectivity C5+', ' Rate', 'Probability Chain Growth', 'BET'])

dict = {'Base': [], 'Promoter': [], 'Temperature (K)': [], 'Pressure (bar)': [], 'Feed Ratio': [], 'Conversion': [], 'Selectivity C1': [], 'Selectivity C2-C4': [], 'Selectivity C5+': [], ' Rate': [], 'Probability Chain Growth': [], 'BET': []}      
data = []
panda = []

Path = 'Data'
#Path = 'Iron-based literature'
for file in os.listdir(Path):
    tables = []
    if file.find('.pdf') == -1:
        continue
    with open(Path+"/"+file, "rb") as f:
        pdf = PyPDF2.PdfReader(f)
        GetTables(pdf, tables)

df.to_excel('output.xlsx')
