''' Data Mining for Carbon Dioxide Hydrogenation
Names: Rachel Calaz, Ben Kahanovitz'''

# Importing required tools
import re
import pandas as pd
import PyPDF2
import os
#import docx

# Function to format strings of data
def format(value):
    value = re.findall(r'\d+(?:[.,]\d+)?', value)
    value = value[-1]
    value = value.replace(',' ,'.')
    value = float(value)
    return value

# Function to classify selectivity
def selectivity(file):
    sel = re.finditer(r'selectivity\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?\s*%?|sel.\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?\s*%?|scx\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?\s*%?', file, re.I)
    if sel:
        for value in sel:
            position = value.start()
            value = value.group()
            if re.search(r'%', value):
                value = format(value) / 100
            else:
                value = format(value)
            input = [value, position]
            select.append(input)

# Function to classify conversion
def conversion(file):
    con = re.finditer(r'conversion\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?\s*%?|conv.\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?\s*%?|xco2\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?\s*%?', file, re.I)
    if con:
        for value in con:
            position = value.start()
            value = value.group()
            if re.search(r'%', value):
                value = format(value) / 100
            else:
                value = format(value)
            input = [value, position]
            conv.append(input)

# Function to classify feed ratio
def feedratio(file):
    ratio = re.finditer(r'feed ratio\s+(\w*\s+){0,10}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|h2/co2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|co2/h2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|h2:co2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?|co2:h2\s+(\w*\s+){0,5}\d+(?:[.,]\d+)?(?:[:/]\d+)?(?:[.,]\d+)?',file, re.I)
    if ratio:
        for value in ratio:
            position = value.start()
            value = value.group()
            if re.search(r'co2/h2|co2:h2', value, re.I):
                value = re.findall(r'\d+(?:[.,]\d+)?', value)
                val1 = value[-1].replace(',','.')
                val2 = value[-2].replace(',','.')
            elif re.search(r'feed ratio|h2/co2|h2:co2', value, re.I):
                value = re.findall(r'\d+(?:[.,]\d+)?', value)
                val1 = value[-2].replace(',','.')
                val2 = value[-1].replace(',','.')
            val1 = float(val1)
            val2 = float(val2)
            value = val1/val2
            input = [value, position]
            Ratio.append(input)

# Function to read in BET Surface Area from text
def BETSA(file):
    bet = re.finditer(r'\s+\d+(?:[.,]\d+)?\s*m2/g|\s+\d+(?:[.,]\d+)?\s*m2/kg|\s+\d+(?:[.,]\d+)?\s*cm2/g|\s+\d+(?:[.,]\d+)?\s*cm2/kg', file, re.I)
    if bet:
        for value in bet:
            position = value.start()
            value = value.group()
            if re.search(r'm2/kg', value, re.I):
                value = format(value)/1000
            elif re.search(r'cm2/g', value, re.I):
                value = format(value)/10000
            elif re.search(r'cm2/kg', value, re.I):
                value = format(value)/10000000
            elif re.search(r'm2/g', value, re.I):
                value = format(value)
            input = [value, position]
            BET.append(input)

# Function to read in Space Velocity from text
def velocity(file):
    vel = re.finditer(r'\s+\d+(?:[.,]\d+)?\s*s-1|\s+\d+(?:\.\d+)?\s*/s|\s+\d+(?:[.,]\d+)?\s*min-1|\s+\d+(?:[.,]\d+)?\s*/min|\s+\d+(?:\.\d+)?\s*h-1|\s+\d+(?:[.,]\d+)?\s*/h|\s+\d+(?:\.\d+)?\s*hr-1|\s+\d+(?:[.,]\d+)?\s*/hr', file, re.I)
    if vel:
        for value in vel:
            position = value.start()
            value = value.group()
            if re.search(r'min', value, re.I):
                value = format(value)/60
            elif re.search(r'h', value, re.I):
                value = format(value)/3600
            elif re.search(r'hr', value, re.I):
                value = format(value)/3600        
            elif re.search(r's', value, re.I):
                value = format(value)
            input = [value, position]
            VEL.append(input)

# Function to read in temperature from text
def temperature(file):
    temp = re.finditer(r'\s+\d+(?:[.,]\d+)?\s*K|\s+\d+(?:\.\d+)?\s*C|\s+\d+(?:\.\d+)?\s*°C|\s+\d+(?:\.\d+)?\s*˙C', file, re.I)
    if temp:
        for value in temp:
            position = value.start()
            value = value.group()
            if re.search(r'c', value, re.I):
                value = format(value) + 273
            elif re.search(r'k', value, re.I):
                value = format(value)
            input = [value, position]
            temps.append(input)
    

# Function to read in pressure from text
def pressure(file):
    press = re.finditer(r'\s+\d+(?:\.\d+)?\s*barg|\s+\d+(?:\.\d+)?\s*bar|\s+\d+(?:\.\d+)?\s*kpag|\s+\d+(?:\.\d+)?\s*kpa|\s+\d+(?:\.\d+)?\s*atm|\s+\d+(?:\.\d+)?\s*mpa', file, re.I)
    if press:
        for value in press:
            position = value.start()
            value = value.group()
            if re.search(r'barg', value, re.I):
                value = format(value) - 1.01
            elif re.search(r'kpag', value, re.I):
                value = (format(value) - 101)/100
            elif re.search(r'kpa', value, re.I):
                value = format(value)/100
            elif re.search(r'mpa', value, re.I):
                value = format(value)/100000
            elif re.search(r'atm', value, re.I):
                value = format(value) * 1.01
            elif re.search(r'bar', value, re.I):
                value = format(value)
            input = [value, position]
            pressures.append(input)

# Function to read in percentages from text

Ratio = []
select = []
conv = []
BET = []
VEL = []
Table = []
temps = []
pressures = []

Path = 'Data'
for file in os.listdir(Path):
    if file.find('.pdf') == -1:
        continue
    Ratio = []
    select = []
    conv = []
    BET = []
    VEL = []
    Table = []
    temps = []
    pressures = []
    with open(Path+"/"+file, "rb") as f:
        pdf = PyPDF2.PdfReader(f)
        for i in range (len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            temperature(text)
            feedratio(text)
            selectivity(text)
            conversion(text)
            BETSA(text)
            velocity(text)
            pressure(text)

print('Temperatures')
print(temps)
print('Feed Ratio')     
print(Ratio)
print('Selectivity')   
print(select)
print('Conversion')   
print(conv)
print('BET')   
print(BET)
print('Space Velocity')   
print(VEL)
print('Pressures')   
print(pressures)