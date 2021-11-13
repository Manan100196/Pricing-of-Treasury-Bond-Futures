#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''
Treasury Bond Futures Pricing Project
'''

import datetime
from datetime import date
import numpy as np
import pandas as pd
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as td

class Bond_Futures_Pricing():
    
    def __init__(self, settlement_price, discount_rate, maturity_date):
        
        self.settlement_price = settlement_price
        self.discount_rate = discount_rate
        self.maturity_date = datetime.datetime.strptime(maturity_date,'%Y-%m-%d')
    
    '''Calculating conversion factor for each bond from the imported excel data'''
    def Conversion_Factor(self):
    
        '''importing bond data available in the market from excel'''
        bond_data = pd.read_csv(r'E:\Career Development\Project\Bond_Futures_Data.csv')
        
        bond_data['Issue Date'] = pd.to_datetime(bond_data['Issue Date'])
        bond_data['Maturity'] = pd.to_datetime(bond_data['Maturity'])
        y = []
        
        '''Converting time into the factor of quarter(0.25)'''
        for i in range(bond_data.shape[0]):
            t = bond_data.iloc[i,2] - bond_data.iloc[i,1]
            t = t.days/360
            t= t - t%0.25
            j = 0

            x = 0
            '''Calculation of PV of future cashflow if time period is a factor of semiannualy(0.5) in if statement 
            and below for quarterly (0.25) in else statement'''
            if t%0.5 == 0:
                while j in range(0, int(t*2)):
                    x = x + ((bond_data.iloc[i,3]/2 * bond_data.iloc[i,4]) / (1 + self.discount_rate/2) ** ((j+1)/2))
                    j += 1
                x = x + (bond_data.iloc[i,4] / ((1 + self.discount_rate/2) ** ((j+1)/2)))

            #'''Calculation of PV of future cashflow if time period is a factor of quarterly(0.25)'''
            else:
                while j in range(0, int((t-0.25)*2)):
                    x = x + ((bond_data.iloc[i,3]/2 * bond_data.iloc[i,4]) / (1 + self.discount_rate/2) ** ((j+1)/2))
                    j += 1
                x = x + (bond_data.iloc[i,4] / ((1 + self.discount_rate/2) ** ((j+1)/2)))
                x = x/((np.sqrt(1.03)-1)*100)
                x = x - (bond_data.iloc[i,3] * bond_data.iloc[i,4]/2)
            
            '''added CF for each bond in the list y'''
            y.append(x/bond_data.iloc[i,4])
        
        '''updated bond data with new column conversion factor'''
        bond_data['Conv_Fac'] = y
        
        return bond_data
    
    '''Selecting the bond which is cheapest to deliver'''
    def CTD_Bond(self, bond_data):
        
        x = []
        '''Calculating cost of delivering each bond and adding it in the index x'''
        for i in range(bond_data.shape[0]):
            x.append(bond_data.iloc[i, 5] - bond_data.iloc[i, 6] * self.settlement_price)
        
        '''Updating bond_data table with chepest to deliver price'''
        bond_data['CTD_Price'] = x
        
        '''Selecting the index position which is cheapest to deliver'''
        y = [i for i,z in enumerate(x) if z == min(x)]
        y = y[0] + 1
        #print(f"The cheapest to deliver bond is Bond {y}")
        
        '''Output is the bond number'''
        return y
    
    '''Calculating quoted future price of the bond which is cheapest to deliver'''
    def Bond_Futures(self, bond_data, y):
        
        '''Adding the coupon dates in the list cpn_date'''
        cpn_date = []
        i = (bond_data.iloc[y-1,1]).date()
        while i < (bond_data.iloc[y-1,2]).date():
            i = i + td(months = 12 /2)
            cpn_date.append(i)
        #print(cpn_date)
        
        '''Finding index position of a coupon date which is just after todays date'''
        i = 0
        while cpn_date[i] < dt.today().date():
            i = i + 1
        #print(cpn_date[i])
    
        '''Taking last coupon date and next coupon date for accrued interest calculation'''
        prev_coupon = cpn_date[i-1]
        next_coupon = cpn_date[i]
        
        '''Accrued interest calculation'''
        AI_1 = bond_data.iloc[y-1,3]*bond_data.iloc[y-1,4]*((dt.today().date()-prev_coupon)/(next_coupon - prev_coupon))/2
        
        '''Adding accrued interest'''
        price = bond_data.iloc[y-1,5] + AI_1
        
        '''Calculating present value of future coupon pv_fut_cpn'''
        #maturity_date = datetime.datetime(2024,7,15)
        pv_fut_cpn = 0
        while cpn_date[i] < self.maturity_date.date():
            #print((cpn_date[i]- dt.today().date()).days)
            pv_fut_cpn = pv_fut_cpn + bond_data.iloc[y-1,3]*bond_data.iloc[y-1,4]/2* np.exp(-self.discount_rate*((cpn_date[i]- dt.today().date()).days)/360)
            i = i + 1
        
        '''Subracting present valur of future coupon from price. 
        Later, the future value at maturity of bond future is calculated'''
        price = (price - pv_fut_cpn)*np.exp(self.discount_rate*((self.maturity_date.date() - dt.today().date()).days)/360)

        '''Accrued interest between maturity date and the last coupon date before maturity date is subracted'''
        price = price - bond_data.iloc[y-1,3]*bond_data.iloc[y-1,5]/2*((self.maturity_date.date()-cpn_date[i-1]).days)/((cpn_date[i]-cpn_date[i-1]).days)

        '''The price arrived at last step is divided by the conversion factor'''
        price = price/bond_data.iloc[y-1,6]
        
        return price
    
    def final(self):
        print(self.Conversion_Factor())
        print('\n')
        print(f'The cheapest to deliver bond is Bond {self.CTD_Bond(self.Conversion_Factor())}')
        print('\n')
        print(f'The quoted future price is {self.Bond_Futures(self.Conversion_Factor(), self.CTD_Bond(self.Conversion_Factor())):.2f}')


# In[2]:


Price = Bond_Futures_Pricing(95,0.06,'2024-07-15')
Price.final()

