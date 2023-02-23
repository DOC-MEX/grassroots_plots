import requests
import json

import numpy as np
#import matplotlib.pyplot as plt
from io import BytesIO
import base64


from functools import reduce


          

###################################################################
def searchPhenotypeTrait(listPheno, value):

    name = listPheno[value]['definition']['trait']['so:name']

    return name

###################################################################
def searchPhenotypeUnit(listPheno, value):

    name = listPheno[value]['definition']['unit']['so:name']

    return name

###################################################################
###############NEW FUNCTION FOR MINIMAL DJANGO######################
###################################################################
def get_trait(variable, phenotypes):
    
    for key in phenotypes:
        if key == variable:
            trait = phenotypes[key]['definition']['trait']['so:name']
            unit = phenotypes[key]['definition']['unit']['so:name']
    return trait, unit
    
    


#########################################################################################################
'''
create treatments array for plotly text 
'''
def treatments(arraysJson, rows, columns):

    dt= np.dtype(('U', 80))
    matrix = np.zeros((rows,columns), dtype=dt)
    matrix[:] = "N/A"

    for r in range(len(arraysJson)):
        if  ( 'discard' in arraysJson[r]['rows'][0] ):
            i = int( arraysJson[r]['row_index']    )
            j = int( arraysJson[r]['column_index'] )
            i=i-1
            j=j-1
            matrix[i][j] = 'N/A'
        elif  ( 'blank' in arraysJson[r]['rows'][0] ):
            i = int( arraysJson[r]['row_index']    )
            j = int( arraysJson[r]['column_index'] )
            i=i-1
            j=j-1
            matrix[i][j] = 'N/A'
    

        elif ( 'treatments' in arraysJson[r]['rows'][0] ):
            i = int( arraysJson[r]['row_index']    )
            j = int( arraysJson[r]['column_index'] )
            i=i-1
            j=j-1
            value = []
            label = []
            treat = []
            for k in range(len(arraysJson[r]['rows'][0]['treatments'])):
                    value  = np.append(value, arraysJson[r]['rows'][0]['treatments'][k]["so:sameAs"] )
                    label  = np.append(label, arraysJson[r]['rows'][0]['treatments'][k]["label"] )

            for m in range(len(value)):
                v1 = value[m]
                v2 = label[m]
                t  = v1 +' (' + v2 +')'        # combine name and label
                treat  = np.append(treat, t)  # to create single matrix that contains all the treatment(s) info.  
        
            #string = ', '.join(value)
            string = ', '.join(treat)
            matrix[i][j] = string

        ##else:
        ##    matrix[i][j] = np.inf.  Possible Warning? No treatment saved in plots...

    matrix  = matrix.flatten()
    return matrix


###################################################################
def dict_phenotypes(pheno, plots):

    names  = []
    traits = []
    
    for key in pheno:
        names.append(key)
        traits.append(pheno[key]['definition']['trait']['so:name'])

    phenoDict = dict(zip(names, traits))    # dictionary for the dropdown menu options

    for j in range(len(plots)):
        if ( 'discard' in plots[j]['rows'][0] ):
            pass
        if ( 'blank' in plots[j]['rows'][0] ):
            pass
        
        if ('observations' in plots[j]['rows'][0]):
            for k in range(len(plots[j]['rows'][0]['observations'])):
                if ('raw_value' in plots[j]['rows'][0]['observations'][k]):
                    rawValue = plots[j]['rows'][0]['observations'][k]['raw_value']
                if ('corrected_value' in plots[j]['rows'][0]['observations'][k]):
                    rawValue = plots[j]['rows'][0]['observations'][k]['corrected_value']
                if ( type(rawValue) == str):                # Remove values that are strings,e.g., dates. 
                    name = plots[j]['rows'][0]['observations'][k]['phenotype']['variable']
                    if ( name in phenoDict.keys() ):
                        #print("check", phenoDict[name])
                        del phenoDict[name]

            #break

    return phenoDict



