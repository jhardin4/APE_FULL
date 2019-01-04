# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 15:56:21 2018

@author: jhardin
"""
testlist = [1,2,3,4]
for n in range(len(testlist)):
    print(testlist[n])
    testlist.append(testlist[n])
    