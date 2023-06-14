from django.shortcuts import render
from django.http import JsonResponse
from django import template
from django.conf import settings
import operator
import json, os
from datetime import datetime, date

from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.urls import reverse

from .grassroots_fieldtrial_requests import get_all_fieldtrials
from .grassroots_fieldtrial_requests import get_plot
#from .grassroots_fieldtrial_requests import updateRequest
from .grassroots_fieldtrial_requests import interact_backend

from .grassroots_plots import dict_phenotypes
from .grassroots_plots import get_trait

from .grassroots_csv import create_CSV

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

    

    plotIndices = []
    plotIDs      = []
    for j in range(len(plots)):                
        if ('rows' in plots[j]):
            if ( 'discard' in plots[j]['rows'][0] ):
                pass
            elif ( 'blank' in plots[j]['rows'][0] ):
                pass
            else:
                plotIndex  = plots[j]['rows'][0]['study_index']            
                plotIndices.append(plotIndex)
                plot_ID = plots[j]['_id']['$oid']             # plot ID, change to row ID!
                rows_ID = plots[j]['rows'][0]['_id']['$oid']  # plot ID, change to row ID!
                #print("ID OF PLOT:",plot_ID, rows_ID)
                plot_ID = rows_ID
                plotIDs.append(plot_ID)

    plotsList    = dict(zip(plotIDs, plotIndices)) 
    # get number of elements in plotIndices
    nPlots = len(plotIndices)
    sortedPlots = dict(sorted(plotsList.items(), key=operator.itemgetter(1)))
    
    
    if request.method == 'POST':
        selected_plot = request.POST.get('plot-select')
        ###################################################       
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
                     'nPlots':nPlots })
        ###################################################       
        elif request.POST.get('update-details'):
            if selected_plot:
                redirect_url = reverse('updateDetails', 
                    kwargs={'plot_id': selected_plot, 'study_id': study_id})
            else:
            # Return the same template with the form
                return render(request, 'plotData.html', {'studyID': study_id, 
                    'studyName': studyName, 'plots':sortedPlots, 
                     'nPlots':nPlots })    
            
            return redirect(redirect_url)    
        ###################################################       
        elif request.POST.get('download-file'):
            #if selected_plot:             
                print("create csv of study:", studyName)
                phenotypes        = study['results'][0]['results'][0]['data']['phenotypes']
                treatment_factors = study['results'][0]['results'][0]['data']['treatment_factors']
                file_name = f"data-{study_id}.csv"
                file_path = os.path.join(settings.BASE_DIR, 'CSVs', file_name)
                create_CSV(plots, phenotypes, treatment_factors, study_id)                
                # Open the file and read its contents into the HttpResponse object
                with open(file_path, 'rb') as csv_file:
                    response = HttpResponse(csv_file.read(), content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                
                return response
            
    
    
    return render(request, 'plotData.html', {'studyID': study_id, 
        'studyName': studyName, 'plots':sortedPlots, 
         'nPlots':nPlots })

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
        ##if (plot_id in plots[j]['_id']['$oid']):  # FIND PLOT
        if (plot_id in plots[j]['rows'][0]['_id']['$oid']):  # FIND ROW_ID INSTEAD?
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
        
        matrix=[rawValues, traits]
        matrix=list(zip(traits, rawValues, units))

    if len(phenoVariables)==0:
        matrix = None
        rawValues = None
        traits = None
        units = None

    csrf_token = get_token(request)
    #print("TOKEN", csrf_token)
    if request.method == 'POST':        
        my_input_value = request.POST.get('my-input')
        selected_phenotype = request.POST.get('selected-trait')
        selected_date = request.POST.get('my-date')
        if len(selected_date) == 0:
             selected_date = str(date.today().strftime('%Y-%m-%d'))
        print(f"New observation is: {my_input_value} for {selected_phenotype}")        
        print(selected_date)
        #result = updateRequest(plot_id, study_id, selected_phenotype, my_input_value, selected_date)

        return render(request, 'updateDetails.html', {'plotID': plot_id, 'studyID': study_id,
                'studyName': studyName, 'row':row, 'column':column, 'accession':accession,
                'plotIndex':plotIndex, 'matrix':matrix, 'csrf_token':csrf_token,  
                'rawValues':rawValues, 'traits':traits, 'traits':dictTraits})
    
    

    return render(request, 'updateDetails.html', {'plotID': plot_id, 'studyID': study_id,
        'studyName': studyName, 'row':row, 'column':column, 'accession':accession,
        'plotIndex':plotIndex, 'matrix':matrix, 'csrf_token':csrf_token, 
        'rawValues':rawValues, 'traits':traits, 'traits':dictTraits})

########################################################
def interact_with_apache(request):
    data = request.body    
    response_json = interact_backend(data)
    return HttpResponse(response_json)


########################################################
def plotDetails(request, plot_id, study_id):    # third page. plotDetails.html
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
    row     = None
    column  = None
    dates   = []
    notes   = []

    for j in range(len(plots)):
        ##if (plot_id in plots[j]['_id']['$oid']):  # FIND PLOT
        if (plot_id in plots[j]['rows'][0]['_id']['$oid']):  # FIND ROW_ID INSTEAD?
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

                        if ('notes' in plots[j]['rows'][0]['observations'][k]):
                            note = plots[j]['rows'][0]['observations'][k]['notes']
                            notes.append(note)
                        else:
                            notes.append('')      # add empty note


                        if ('raw_value' in plots[j]['rows'][0]['observations'][k]):
                            raw_value = plots[j]['rows'][0]['observations'][k]['raw_value']
                            rawValues.append(raw_value)
                            if ('date' in plots[j]['rows'][0]['observations'][k]):    
                                date = plots[j]['rows'][0]['observations'][k]['date']
                                date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                                date_only = date.strftime('%Y-%m-%d')
                                if('end_date' in plots[j]['rows'][0]['observations'][k]):
                                    endDate = plots[j]['rows'][0]['observations'][k]['end_date']
                                    endDate = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S')
                                    dates.append("From "+date_only+" to "+endDate.strftime('%Y-%m-%d'))
                                else:
                                    dates.append(date_only)   
                            
                            else:
                                dates.append('')  
                            
                            
                        elif ('corrected_value' in plots[j]['rows'][0]['observations'][k]):
                            raw_value = plots[j]['rows'][0]['observations'][k]['corrected_value']
                            rawValues.append(raw_value)
                            if ('date' in plots[j]['rows'][0]['observations'][k]):    
                                date = plots[j]['rows'][0]['observations'][k]['date']
                                date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                                date_only = date.strftime('%Y-%m-%d')
                                dates.append(date_only)
                                if('end_date' in plots[j]['rows'][0]['observations'][k]):
                                    endDate = plots[j]['rows'][0]['observations'][k]['end_date']
                                    endDate = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S')
                                    dates.append("From "+date_only+" to "+endDate.strftime('%Y-%m-%d'))
                                else:
                                    dates.append(date_only)
                            else:
                                dates.append('')                          

                        #print("dates: ", len(rawValues),len(dates))
                        #print("NOTES: ", len(notes),len(notes))
                        
            row    = plots[j]['row_index'] 
            column = plots[j]['column_index'] 

            if accession == None:                
                accession = 'No accession'

    if  "phenotypes" in study['results'][0]['results'][0]['data']: 
        phenotypes = study['results'][0]['results'][0]['data']['phenotypes']  # Details of all the phenotypes
    else:
        phenotypes = {'No Data': 'No Data'}  
    
    # Get trait and unit data from each phenotype in current plot
    for i in range(len(phenoVariables)): 
        trait, unit = get_trait(phenoVariables[i], phenotypes)
        traits.append(trait)
        units.append(unit)
        #print(rawValues)
        #print(units)

    #combined = [f'{rawValue} ({date})' for rawValue, date in zip(rawValues, dates)]
    combined = [f'{rawValue} ({date})' if date else str(rawValue) for rawValue, date in zip(rawValues, dates)]
    
    matrix=list(zip(traits, rawValues, units, dates, notes))

    if len(phenoVariables)==0:
        matrix = None
        rawValues = None
        traits = None
        units = None
    
    

    return render(request, 'plotDetails.html', {'plotID': plot_id, 'studyID': study_id,
        'studyName': studyName, 'row':row, 'column':column, 'accession':accession,
        'plotIndex':plotIndex, 'matrix':matrix,  
        'rawValues':rawValues, 'traits':traits, 'dates':dates})