from django.shortcuts import render
from django.http import JsonResponse
from django import template
import operator
import json

from django.shortcuts import redirect
from django.urls import reverse

from .grassroots_fieldtrial_requests import get_all_fieldtrials
from .grassroots_fieldtrial_requests import get_plot

from .grassroots_plots import dict_phenotypes
from .grassroots_plots import get_trait

# list all studies
def selectStudy(request):
    all_studies  = get_all_fieldtrials()
    all_studies = json.loads(all_studies)
    studiesIDs = []
    names      = []
    ##print("check total: ", len(all_studies['results'][0]['results']))

    for i in range(len(all_studies['results'][0]['results'])):
        uuid  = all_studies['results'][0]['results'][i]['data']['_id']['$oid']
        name = all_studies['results'][0]['results'][i]['data']['so:name']

        if 'phenotypes' in all_studies['results'][0]['results'][i]['data']:
            studiesIDs.append(uuid)
            names.append(name)

    studiesIDs.remove('619e159b87a279348474145b')           # DFW Academic Toolkit RRes, Harvest 2021   
    names.remove('DFW Academic Toolkit RRes, Harvest 2021') # DFW Academic Toolkit RRes, Harvest 2021   
    studiesIDs.remove('6225dfde93b7641e4b5acb85')  #  NIAB CSSL AB Glasshouse exp 
    names.remove('NIAB CSSL AB Glasshouse exp ')   #
    
    studies = dict(zip(studiesIDs, names)) 

    sortedStudies = dict(sorted(studies.items(), key=operator.itemgetter(1)))
    ##print(sortlist)

    if request.method == 'POST':
        selected_study = request.POST.get('study-select')
        if selected_study:
            print("selected study: ", selected_study)
            return redirect('updatePlot', study_id=selected_study)
    
    return render(request, 'select.html', {'options': sortedStudies})

#######################################################
########################################################
def updatePlot(request, study_id):    #plotData.html  second page
    study = get_plot(study_id)
    study = json.loads(study)
    studyName = study['results'][0]['results'][0]['data']['so:name']

    plots = study['results'][0]['results'][0]['data']['plots']       # send only array of 'plots' to plotly

    if  "phenotypes" in study['results'][0]['results'][0]['data']: 
        phenotypes = study['results'][0]['results'][0]['data']['phenotypes']  # Details of all the phenotypes
        dictTraits = dict_phenotypes(phenotypes, plots)  # dictionary to fill dropdown menu
        default_name = list(dictTraits.keys())[0]            
        #print(default_name, list(dictTraits.values())[0])
    else:
        dictTraits = {'No Data':'No data'}  #
        phenotypes = {'No Data': 'No Data'}  
        #print(dictTraits)
        default_name = list(dictTraits.keys())[0]        

    plotIndices = []
    plotIDs      = []
    for j in range(len(plots)):
        if ( 'discard' in plots[j]['rows'][0] ):
            pass
        if ( 'blank' in plots[j]['rows'][0] ):
            pass
        
        if ('rows' in plots[j]):
            plotIndex  = plots[j]['rows'][0]['study_index']
            plotIndices.append(plotIndex)
            plot_ID = plots[j]['_id']['$oid']
            plotIDs.append(plot_ID)

    plotsList    = dict(zip(plotIDs, plotIndices)) 
    # get number of elements in plotIndices
    nPlots = len(plotIndices)
    sortedPlots = dict(sorted(plotsList.items(), key=operator.itemgetter(1)))
    
    
    if request.method == 'POST':
        selected_plot = request.POST.get('plot-select')
        if request.POST.get('load-plot'):
            if selected_plot:
                print("selected plot: ", selected_plot)
                redirect_url = reverse('plotDetails', 
                    kwargs={'plot_id': selected_plot, 'study_id': study_id})
            
                return redirect(redirect_url)
            else:
            # Return the same template with the form
                return render(request, 'plotData.html', {'studyID': study_id, 
                    'studyName': studyName, 'plots':sortedPlots, 
                    'traits':dictTraits, 'nPlots':nPlots })
        
        elif request.POST.get('update-details'):
            if selected_plot:
                redirect_url = reverse('updateDetails', 
                    kwargs={'plot_id': selected_plot, 'study_id': study_id})
            else:
            # Return the same template with the form
                return render(request, 'plotData.html', {'studyID': study_id, 
                    'studyName': studyName, 'plots':sortedPlots, 
                    'traits':dictTraits, 'nPlots':nPlots })    
            
            return redirect(redirect_url)    
    
    return render(request, 'plotData.html', {'studyID': study_id, 
        'studyName': studyName, 'plots':sortedPlots, 
        'traits':dictTraits, 'nPlots':nPlots })

########################################################
########################################################
def updateDetails(request, plot_id, study_id):    # 3rd page. updateDetails.html
    study = get_plot(study_id)
    study = json.loads(study)
    studyName = study['results'][0]['results'][0]['data']['so:name']

    plots = study['results'][0]['results'][0]['data']['plots'] 
    accession = None
    phenotype = None


    if  "phenotypes" in study['results'][0]['results'][0]['data']: 
        phenotypes = study['results'][0]['results'][0]['data']['phenotypes']  # Details of all the phenotypes
        dictTraits = dict_phenotypes(phenotypes, plots)  # dictionary to fill dropdown menu
        default_name = list(dictTraits.keys())[0]            
    else:
        dictTraits = {'No Data':'No data'}  #
        phenotypes = {'No Data': 'No Data'}  
        #print(dictTraits)
        default_name = list(dictTraits.keys())[0]   

    rawValues = []
    phenoVariables = [] 
    traits     = []
    units      = []
    row     = []
    column  = []
    
    for j in range(len(plots)):
        if (plot_id in plots[j]['_id']['$oid']):  # FIND PLOT
            if ('rows' in plots[j]):
                plotIndex  = plots[j]['rows'][0]['study_index']
                print("found plot ", plotIndex)
                if ('material' in plots[j]['rows'][0]):
                    accession = plots[j]['rows'][0]['material']['accession']
                if ('observations' in plots[j]['rows'][0]):
                    # Get data from particular plot. phenotypes and raw values
                    for k in range(len(plots[j]['rows'][0]['observations'])):
                        phenotype = plots[j]['rows'][0]['observations'][k]['phenotype']['variable']
                        phenoVariables.append(phenotype)
                        if ('raw_value' in plots[j]['rows'][0]['observations'][k]):
                            raw_value = plots[j]['rows'][0]['observations'][k]['raw_value']
                            rawValues.append(raw_value)
                        if ('corrected_value' in plots[j]['rows'][0]['observations'][k]):
                            raw_value = plots[j]['rows'][0]['observations'][k]['corrected_value']
                            rawValues.append(raw_value)

                        #print("phenotype: ", phenotype, raw_value)
                        
            row    = plots[j]['row_index'] 
            column = plots[j]['column_index'] 

            if accession == None:                
                accession = 'No accession'

    if  "phenotypes" in study['results'][0]['results'][0]['data']: 
        phenotypes = study['results'][0]['results'][0]['data']['phenotypes']  # Details of all the phenotypes
    else:
        phenotypes = {'No Data': 'No Data'}  
    
    # Get trait data from each phenotype in current plot
    for i in range(len(phenoVariables)): 
        trait, unit = get_trait(phenoVariables[i], phenotypes)
        traits.append(trait)
        units.append(unit)

        #print(rawValues)
        #print(units)
        matrix=[rawValues, traits]
        matrix=list(zip(traits, rawValues, units))

    if len(phenoVariables)==0:
        matrix = None
        rawValues = None
        traits = None
        units = None
    
    

    return render(request, 'updateDetails.html', {'plotID': plot_id, 'studyID': study_id,
        'studyName': studyName, 'row':row, 'column':column, 'accession':accession,
        'plotIndex':plotIndex, 'matrix':matrix,  
        'rawValues':rawValues, 'traits':traits, 'traits':dictTraits})

########################################################
########################################################
def plotDetails(request, plot_id, study_id):    # thirs page. plotDetails.html
    study = get_plot(study_id)
    study = json.loads(study)
    studyName = study['results'][0]['results'][0]['data']['so:name']

    plots = study['results'][0]['results'][0]['data']['plots'] 
    accession = None
    phenotype = None

    rawValues = []
    phenoVariables = [] 
    traits     = []
    units      = []
    row  = []
    column  = []
    for j in range(len(plots)):
        if (plot_id in plots[j]['_id']['$oid']):  # FIND PLOT
            if ('rows' in plots[j]):
                plotIndex  = plots[j]['rows'][0]['study_index']
                print("found plot ", plotIndex)
                if ('material' in plots[j]['rows'][0]):
                    accession = plots[j]['rows'][0]['material']['accession']
                if ('observations' in plots[j]['rows'][0]):
                    # Get data from particular plot. phenotypes and raw values
                    for k in range(len(plots[j]['rows'][0]['observations'])):
                        phenotype = plots[j]['rows'][0]['observations'][k]['phenotype']['variable']
                        phenoVariables.append(phenotype)
                        if ('raw_value' in plots[j]['rows'][0]['observations'][k]):
                            raw_value = plots[j]['rows'][0]['observations'][k]['raw_value']
                            rawValues.append(raw_value)
                        if ('corrected_value' in plots[j]['rows'][0]['observations'][k]):
                            raw_value = plots[j]['rows'][0]['observations'][k]['corrected_value']
                            rawValues.append(raw_value)

                        #print("phenotype: ", phenotype, raw_value)
                        
            row    = plots[j]['row_index'] 
            column = plots[j]['column_index'] 

            if accession == None:                
                accession = 'No accession'

    if  "phenotypes" in study['results'][0]['results'][0]['data']: 
        phenotypes = study['results'][0]['results'][0]['data']['phenotypes']  # Details of all the phenotypes
    else:
        phenotypes = {'No Data': 'No Data'}  
    
    # Get trait data from each phenotype in current plot
    for i in range(len(phenoVariables)): 
        trait, unit = get_trait(phenoVariables[i], phenotypes)
        traits.append(trait)
        units.append(unit)

        #print(rawValues)
        #print(units)
        matrix=[rawValues, traits]
        matrix=list(zip(traits, rawValues, units))

    if len(phenoVariables)==0:
        matrix = None
        rawValues = None
        traits = None
        units = None
    
    

    return render(request, 'plotDetails.html', {'plotID': plot_id, 'studyID': study_id,
        'studyName': studyName, 'row':row, 'column':column, 'accession':accession,
        'plotIndex':plotIndex, 'matrix':matrix,  
        'rawValues':rawValues, 'traits':traits, 'iterator':range(1,2)})