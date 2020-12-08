# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 18:54:13 2020

@author: HP
"""
import pandas as pd
import numpy as np
import joblib
import spacy
from flask import Flask, render_template, request, url_for, redirect


classifier = joblib.load(open('LRmodel.pkl','rb'))
w = {'Item': [],'Qty':[], 'Amount': [], 'Trans_type': []}

def populatetest_DB(text):
   
    s = {} 
    
    x = classifier.predict([text])[0]
    w['Trans_type'].append(x)
    
    interest = ['ITEM', 'QUANTITY', 'PRICE'] 
    nlp2 = spacy.load('./model4')
    doc = nlp2(text)
    r = [(ent.text, ent.label_) for ent in doc.ents]
    
    for i in r:
        if i[1] in interest:    
            s[i[1]] = (i[0]) 
    
    w['Item'].append(s['ITEM'])
    w['Qty'].append(s['QUANTITY'])
    w['Amount'].append(float(s['PRICE']))
        
    df = pd.DataFrame(w)

    income = df[df['Trans_type'] == 'income']
    income_sum = np.sum(income['Amount'])

    expense= df[df['Trans_type'] == 'expense']
    expense_sum = np.sum(expense['Amount'])
    
    Business_Value = income_sum - expense_sum
    
        
    df.to_csv(path_or_buf='./transactions.csv', index=False)

    #render dataframe as html
    html = df.to_html()
    
    #write html to file
    output = open("templates/index.html", "w")
    output.write(html)
    output.close()
       
    return {'Business_Value':Business_Value, 'Income_sum':income_sum, 'Expense_sum':expense_sum }
    


app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    Bus_Val = ""
    Income = ""
    Expense = ""
    if request.method == 'POST':
        ins  = request.form.values()
        ins = list(ins)
        text = ''.join(ins)

        if text == "":
            return redirect(request.url)
        else:
            result = populatetest_DB(text)
            Bus_Val = result['Business_Value']
            Income = result['Income_sum']
            Expense = result['Expense_sum']

    return render_template('nas.html', Business_value = Bus_Val, Income = Income, Expense = Expense)


@app.route('/history')
def hist():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)