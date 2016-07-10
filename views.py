import ipdb

import pprint

from persistent.mapping import PersistentMapping as PM
from persistent.list    import PersistentList    as PL

from pyramid.config import Configurator

from pyramid.view import view_config
from pyramid.events import subscriber


from .models import *

import transaction, json

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors

@view_config(route_name = "initialise", renderer='templates/initialise.pt')
def initalise(request):
  toReturn = {"stauts": "fail"}
  if "initialiseAppConfig" in request.root:
    toReturn['status'] = "alreadyConfigured"
    toReturn['currentConfig'] = request.root['initialiseAppConfig']
  else:
    toReturn['status'] = "newConfigStarted"


  return toReturn


@view_config(renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'thisEqualsThat'}

@view_config(route_name='thisEqualsThat',             renderer='templates/thisEqualsThat.pt')
def thisEqualsThat(request):
    return {'project': 'thisEqualsThat'}

@view_config(route_name='thisEqualsThat_iframe',      renderer='templates/thisEqualsThat_iframe.pt')
def thisEqualsThat_iframe(request):
    return {'project': 'thisEqualsThat'}

@view_config(route_name='thisEqualsThat_bertonbeil',  renderer='templates/thisEqualsThat_bertonbeil.pt')
def thisEqualsThat_bertonbeil(request):
    return {'project': 'thisEqualsThat'}

@view_config(route_name='getModelClasses', renderer="json")
def getModelClasses(request):
  modelClasses  = request.root['modelClasses']
  ##ipdb.set_trace()
  jsonOutput    = modelClasses.keys()
  #user = request.root['user']['CPS']
  return jsonOutput
  
@view_config(route_name='getClassInstance', renderer="json")
def getClassInstance(request):
  ##ipdb.set_trace()
  modelClassName                = request.params['modelClassName']
  modelClass                    = request.root['modelClasses'][modelClassName]

  modelInstance                 = modelClass.getModelInstance(request.root['modelInstances'])
  modelInstanceInterface        = modelInstance.getJSInterface()
  
  ##ipdb.set_trace()
  jsonOutput                    = [ modelInstanceInterface ]
  transaction.commit()
  return jsonOutput
  
@view_config(route_name="inputFieldAltered", renderer="json")
def inputFieldAltered(request):
  print request.path_qs
  
  modelInstanceID   = request.params['modelInstanceID']
  modelInstance     = request.root['modelInstances'][modelInstanceID]
  modelClass        = modelInstance['modelClass']
  
  valueFromInstance = []
  try:
    inputField      = tuple(json.loads(request.params['inputField']))
    fieldDataType   = modelInstance.getInputSetter(inputField)['path'][-1]['field']['fieldType']
    if fieldDataType == "text" or fieldDataType == "select":
      inputFieldValue = request.params['newValue']
    else:    
      inputFieldValue = float(request.params['newValue'])
    
    print "Set Input Value from Interface: %s: %s" % (inputField, inputFieldValue)
    modelInstance.getInputSetter(inputField).setValue(modelInstance, inputFieldValue)
  except KeyError as e:
    print "Exception in setting input value: %s" % e
    valueFromInstance.append("inputField")
    valueFromInstance.append("newValue")
  try:
    outputField     = tuple(json.loads(request.params['outputField']))
    modelInstance.getOutputSetter(outputField)
  except Exception as e:
    print repr(e)
    valueFromInstance.append("outputField")
    outputField = modelInstance['lastAlteredOutput']
  try:
    visualisationField = tuple(json.loads(request.params['visualisationField']))
    modelInstance['lastAlteredVisualisation'] = visualisationField
  except Exception as e:
    print repr(e)
    valueFromInstance.append("visualisationField")
    if "lastAlteredVisualisation" not in modelInstance:
      modelInstance['lastAlteredVisualisation'] = outputField
    visualisationField = modelInstance['lastAlteredVisualisation']

  print "valuesPreListing: \n  inputField: %s, fieldValue: %s\n  outputField: %s\nvisualisationField: %s\n filledFromInstance: %s" \
      % ( modelInstance['inputSetter'], 
          modelInstance['inputSetter'].getValue(modelInstance), 
          modelInstance['outputSetter'], 
          visualisationField, 
          valueFromInstance,
        )
  
  #if modelInstance['isBottomModel'] == True:
  #  ipdb.set_trace()
  
  originalInputFieldAddress = modelInstance['inputFieldAddress']
  #All that is needed to allow as many models as you like in a row is to have the top and bottom models store ID's for each other so they can tell what is going on. 
  #The front end just neesd to have the overflow set for the container
  if modelInstance['isBottomModel']:
    modelInstance.getInputSetter(modelInstance['boundInputField'])
  newOutputValue = modelInstance.process()
  modelInstance.getInputSetter(originalInputFieldAddress)  

  #ipdb.set_trace()
  choosableFields = []
  bottomModelData = {}
  if not modelInstance['isBottomModel']:
    #ipdb.set_trace()
    #if not (outputField == modelInstance.currentOutputField):
    #else:
      outputUnit      = modelInstance['outputSetter']['path'][-1]['field']['unit']
      matchingFields  = request.root['fieldUnitIndex'][outputUnit]

      bottomModel = modelInstance['bottomModel']
      if bottomModel is None:
        for field in matchingFields:
          bottomModelLinkFieldItem = \
              { "boundOutputField": modelInstance['outputFieldAddress'],
                "boundInputField" : field['classData'].getValue(field['modelClass'], "fieldAddress"), 
                "bottomModelClass": field['modelClass']['name']
              }
          choosableFields.append(bottomModelLinkFieldItem)

      elif bottomModel is not None:
        #ipdb.set_trace()
        

        matchUnit             = False
        matchFieldByFieldName = False
        if not outputField == modelInstance['lastAlteredOutput']:
          outputFieldName = modelInstance['outputSetter']['path'][-1]['field']['name']
          if outputFieldName in bottomModel['modelClass']['fields']:
            matchFieldByFieldName = bottomModel['modelClass']['fields'][outputFieldName]
            bottomModel['boundInputField'] = matchFieldByFieldName['classData'].getValue(matchFieldByFieldName['modelClass'], "fieldAddress")
          else:
            matchUnit = True

        for field in matchingFields:
          bottomModelLinkFieldItem = \
              { "boundOutputField": modelInstance['outputFieldAddress'],
                "boundInputField" : field['classData'].getValue(field['modelClass'], "fieldAddress"), 
                "bottomModelClass": field['modelClass']['name']
              }
          if      (matchUnit is False  and matchFieldByFieldName is not False and field is matchFieldByFieldName) \
              or  (matchUnit is True   and field['modelClass']['name'] == bottomModel['modelClass']['name']):
            bottomModelLinkFieldItem['selected'] = "selected"
            bottomModel['boundInputField'] = bottomModelLinkFieldItem['boundInputField']
            matchUnit  = "matched"
          choosableFields.append(bottomModelLinkFieldItem)
      
        bottomModel.getInputSetter(bottomModel['boundInputField']).setValue(bottomModel, newOutputValue)
        #if there is no outputField set, set it to the inputField. Simple.
        if "lastAlteredOutput" not in bottomModel:
          bottomModel['lastAlteredOutput'] = bottomModel['bountInputField']
        print "Bound InputField %s "    % (bottomModel['boundInputField'], )
        print "currentOutputField: %s"  % (bottomModel['lastAlteredOutput'], )
        bottomModelOutputValue = \
          bottomModel['modelClass'].getProcessPath(bottomModel['boundInputField'], bottomModel['lastAlteredOutput']).process(bottomModel)
        bottomModelSVG3dDisplayJSON = bottomModel['modelClass']['svgDisplayDefs'].process(bottomModel)
        bottomModelData = { "fieldName": bottomModel['lastAlteredOutput'], "newValue": bottomModelOutputValue,
                            "svg3dDisplayJSON": bottomModelSVG3dDisplayJSON
                          }

  modelInstance['lastAlteredInput']  = originalInputFieldAddress
  modelInstance['lastAlteredOutput'] = modelInstance['outputFieldAddress']

  svg3dDisplayJSON = modelClass['svgDisplayDefs'].process(modelInstance)

  transaction.commit()
  
  return {    "fieldName": modelInstance['outputFieldAddress'], 
              "newValue": newOutputValue, 

              "fieldValues": modelInstance.getJSInterface()['fieldValues'],

              "choosableFields":    choosableFields,
              "svg3dDisplayJSON":   svg3dDisplayJSON,
              "bottomModelData":    bottomModelData,
              "lastAlteredInput":   modelInstance['lastAlteredInput'],
              "lastAlteredInputValue": modelInstance['inputSetter'].getValue(modelInstance),
              "lastAlteredOutput":  modelInstance['lastAlteredOutput'],
              "lastAlteredOutputValue": modelInstance['outputSetter'].getValue(modelInstance),
          }

@view_config(route_name="setBottomModel", renderer="json")
def setBottomModel(request):
  print request.path_qs

  topModelID        = request.params['topModelID']
  bottomModelClass  = request.params['bottomModelClass']
  #ipdb.set_trace()
  boundOutputField  = tuple(json.loads(request.params['boundOutputField']))
  boundInputField   = tuple(json.loads(request.params['boundInputField']))
  
  topModelInstance  = request.root['modelInstances'][topModelID]
  if bottomModelClass in topModelInstance['bottomModelHistory']:
    bottomModelInstance = topModelInstance['bottomModelHistory'][bottomModelClass]
  else:
    bottomModelInstance = request.root['modelClasses'][bottomModelClass].getModelInstance(topModelInstance['bottomModelHistory'])
    bottomModelInstance['isBottomModel'] = True
    request.root['modelInstances'][bottomModelInstance['uuid']] = bottomModelInstance
  
  topModelInstance['bottomModel'] = bottomModelInstance

  topModelInstance['boundOutputField']   = boundOutputField
  bottomModelInstance['boundInputField'] = boundInputField
  
  bottomModelInstance.getInputSetter(boundInputField).setValue(bottomModelInstance, topModelInstance.getOutputSetter(boundOutputField).getValue(topModelInstance))
  bottomModelInstance.getOutputSetter(bottomModelInstance['lastAlteredOutput'])
  bottomModelInstance.getProcessPath().process(bottomModelInstance)
  
  #jsonOutput = bottomModelInstance.getJSInterface(boundInputField=boundInputField)
  #remove input field binding. Destructive and Irrelevant
  jsonOutput = bottomModelInstance.getJSInterface()
  jsonOutput['__modelClass'] = bottomModelInstance['modelClass']['name'];
  
  print "setBottomModel: \n  boundFields: %s, %s" % (boundOutputField, boundInputField)
  
  transaction.commit()
  
  return jsonOutput

import pyramid_google_login


@view_config(route_name="googleConnect/login", renderer="json")
def googleConnect_login(context, request):
  #ipdb.set_trace()
  emailAddress = request.params['emailAddress']
  if emailAddress in request.root['users']:
    del request.root['users'][emailAddress]
    print ("deleted credentials %s" % emailAddress)


  transaction.commit()

  return pyramid_google_login.redirect_to_signin(request, url="/googleConnect/credentialsCheck?emailAddress=%s" % (emailAddress, ))
  

@subscriber(pyramid_google_login.events.UserLoggedIn)
def googleConnect_login_happened(googleConnect_loginEvent):

  users         = googleConnect_loginEvent.request.root['users']

  userID        = googleConnect_loginEvent.userid
  loggingIn     = \
      { "id":           userID, 
        "userData":     googleConnect_loginEvent.userinfo,
        "oauth2_token": googleConnect_loginEvent.oauth2_token,

      }
  
  users[userID] = loggingIn
  
  localUserData = users[loggingIn["id"]]

  print "google connect log in event completed"
  
  transaction.commit()

@view_config(route_name="googleConnect/credentialsCheck", renderer="templates/googleCredentialsCheck.pt")
def googleConnect_waitingForCredentials(context, request):
  return {"emailAddress": request.params['emailAddress']}


@view_config(route_name="googleConnect/gotCredentials", renderer="json")
def googleConnect_gotCredentials(context, request):
  emailAddress = request.params['emailAddress']
  if emailAddress in request.root['users']:
    toReturn = {"gotCredentials": True}
  else:
    toReturn = {"gotCredentials": False}
  print "gotCredentials: %s" % (toReturn['gotCredentials'],)
  return toReturn;


@view_config(route_name="googleConnect/getSheets", renderer="json")
def googleConnect_getSheets(context, request):

  try:
    emailAddress    = request.params['emailAddress']
    spreadsheetURL  = request.params['spreadsheetURL']

    credentials = client.AccessTokenCredentials(request.root["users"][emailAddress]["oauth2_token"]["access_token"], "ThisEqualsThat")

    http = credentials.authorize(httplib2.Http())

    scriptID_directoryListing = "MZ7tLcHX3wZ083vtBstxR_yxJyIsVAxIO"

    service = discovery.build('script', 'v1', http=http)

    # Create an execution request object.
    googleConnect_request = {"function": "getSheets", "parameters": [spreadsheetURL], "devMode": True}

    toReturn = {"Fail"}

    try:
        # Make the API request.
        googleConnect_response = service.scripts().run(body=googleConnect_request,
                scriptId=scriptID_directoryListing).execute()


        if 'error' in googleConnect_response:
            # The API executed, but the script returned an error.

            # Extract the first (and only) set of error details. The values of
            # this object are the script's 'errorMessage' and 'errorType', and
            # an list of stack trace elements.
            error = googleConnect_response['error']['details'][0]
            print "Script error message: {0}".format(error['errorMessage'])

            if 'scriptStackTraceElements' in error:
                # There may not be a stacktrace if the script didn't start
                # executing.
                print "Script error stacktrace:"
                for trace in error['scriptStackTraceElements']:
                    print("\t{0}: {1}".format(trace['function'],
                        trace['lineNumber']))
        else:
            # The structure of the result will depend upon what the Apps Script
            # function returns. Here, the function returns an Apps Script Object
            # with String keys and values, and so the result is treated as a
            # Python dictionary (folderSet).
            sheetNames = googleConnect_response['response'].get('result', {})
            if not sheetNames:
                toReturn =  {"status":'No sheet names returned!', "sheetNames":[]}
            else:
                toReturn = {"status": 'Folders under your root folder:', "sheetNames": sheetNames}
        return toReturn

    except errors.HttpError as e:
        # The API encountered a problem before the script started executing.
        print e.content
    except client.AccessTokenCredentialsError as e:
      ipdb.set_trace()
      print('An exception occurred: {}'.format(e))
  except BaseException as exception:
    print('An exception occurred: {}'.format(exception))

@view_config(route_name="googleConnect/getCellRange", renderer="json")
def googleConnect_getCellRange(context, request):

  try:
    emailAddress    = request.params['emailAddress']      or "christopherreay@gmail.com"
    spreadsheetURL  = request.params['spreadsheetURL']    or "https://docs.google.com/spreadsheets/d/1HIhmZMCHDRaiCQYogvsBSb1C5hzEOuIhIivvLb5eEBY/edit?pref=2&pli=1#gid=1562621115"
    sheetName       = request.params['sheetName']         or 1.0
    cellRange       = request.params['cellRange']         or "a76:b76"

    credentials = client.AccessTokenCredentials(request.root["users"][emailAddress]["oauth2_token"]["access_token"], "ThisEqualsThat")

    http = credentials.authorize(httplib2.Http())

    scriptID_directoryListing = "MZ7tLcHX3wZ083vtBstxR_yxJyIsVAxIO"

    service = discovery.build('script', 'v1', http=http)

    # Create an execution request object.
    googleConnect_request = {"function": "getCellRange", "parameters": [spreadsheetURL, sheetName, cellRange], "devMode": True}

    toReturn = {"Fail"}

    try:
        # Make the API request.
        googleConnect_response = service.scripts().run(body=googleConnect_request,
                scriptId=scriptID_directoryListing).execute()


        if 'error' in googleConnect_response:
            # The API executed, but the script returned an error.

            # Extract the first (and only) set of error details. The values of
            # this object are the script's 'errorMessage' and 'errorType', and
            # an list of stack trace elements.
            error = googleConnect_response['error']['details'][0]
            print "Script error message: {0}".format(error['errorMessage'])

            if 'scriptStackTraceElements' in error:
                # There may not be a stacktrace if the script didn't start
                # executing.
                print "Script error stacktrace:"
                for trace in error['scriptStackTraceElements']:
                    print("\t{0}: {1}".format(trace['function'],
                        trace['lineNumber']))
        else:
            # The structure of the result will depend upon what the Apps Script
            # function returns. Here, the function returns an Apps Script Object
            # with String keys and values, and so the result is treated as a
            # Python dictionary (folderSet).
            cellRangeData = googleConnect_response['response'].get('result', {})
            if not cellRangeData:
                toReturn =  {"status":'No sheet names returned!', "cellRangeData":[]}
            else:
                toReturn = {"status": 'Folders under your root folder:', "cellRangeData": cellRangeData}
        return toReturn

    except errors.HttpError as e:
        # The API encountered a problem before the script started executing.
        print e.content
    except client.AccessTokenCredentialsError as e:
      ipdb.set_trace()
      print('An exception occurred: {}'.format(e))
  except BaseException as exception:
    print('An exception occurred: {}'.format(exception))


@view_config(route_name="scottishParliament/votingModel", renderer="templates/scottishParliament_votingModel.pt")
def scottishParliament_votingModel(context, request):
  return {};

@view_config(route_name="scottishParliament/data", renderer="json")
def scottishParliament_data(context, request):
  


  

  # ipdb.set_trace()

  return {}
  

@view_config(route_name="scottishParliament/updateSwings", renderer="json")
def scottishParliament_updateSwings(context, request):
  # ipdb.set_trace()

  import csv
  import os

  voteTypes = ["constituency", "list"]
  parliamentaryDataFilesDir = os.path.join(os.path.dirname(__file__), "static", "scottishParliamentaryElections", "2011")
  voteData = \
      { "constituency":   { "fileName":  os.path.join(parliamentaryDataFilesDir, "Scottish Parliament Elections 2011 - Constituency Vote.csv"),
                            "votesByConstituency": {},
                          },
        "list":           { "fileName":  os.path.join(parliamentaryDataFilesDir, "Scottish Parliament Elections 2011 - List Vote.csv"),
                            "votesByConstituency": {},
                          },
        "regions":        {},
        "constituencies": [],
      }


  voteTree = ScottishParliamentaryElection()
  for voteType in voteTypes:
    with open(voteData[voteType]['fileName'], "rb") as csvFile:
      csvReader   = csv.reader(csvFile, csv.excel)
      rows        = []
      headerRow   = None
      rowCounter  = 0
      for row in csvReader:
        if rowCounter == 0:
          headerRow   = row
          traverse(voteTree, {}, "parties")[voteType] = headerRow[10:]
        else:
          columnCounter = 0
          rowDict = {}
          for columnName in headerRow:
            rowDict[columnName] = row[columnCounter]
            columnCounter += 1
          rows.append(rowDict)
          
          region        = rowDict["Region"]
          constituency  = rowDict["Constituency"]
          if region not in voteData['regions']:
            voteData['regions'][region] = {"constituencies":[]}
          if constituency not in voteData['regions'][region]['constituencies']:
            voteData['regions'][region]['constituencies'].append(constituency)
          if constituency not in voteData['constituencies']:
            voteData['constituencies'].append(constituency)

          #voteData['constituency']['votesByConstituency'][constituency] = {"dataRow": rowDict}
          

          for columnNumber in range(10, len(headerRow)):
            fromParty = headerRow[columnNumber]

            traverse( voteTree, 
                       PM(), "2016",
                          PM(), region,
                            PM(), constituency,
                              PM(), fromParty,
                                PM(), voteType,
                    )["baseVote"] = int(camelCase(row[columnNumber]) or 0)

            # for toParty in headerRow[10:]:
            #   nationalNode.getNode(fromParty).getNode(toParty).getDict(voteType)["swing"] = 0
            #   regionalNode.getNode(fromParty).getNode(toParty).getDict(voteType)['swing'] = 0
            #   constituencyNode.getNode(fromParty).getNode(toParty).getDict(voteType)['swing'] = 0


        rowCounter += 1
    voteData[voteType]["columnNames"] = headerRow
    voteData[voteType]["data"] = rows
  
  voteData['constituency']['parties'] = voteData['constituency']['columnNames'][10:]

  traverse(voteTree, {}, 'swings', {}, 'constituency')
  traverse(voteTree, {}, 'swings', {}, 'list')

  # traverse(voteTree, {}, "swings", {}, "constituency")["national.Labour.SNP"] = 100
  # traverse(voteTree, {}, "swings", {}, "list")        ["national.SNP.Green"]  = 50
  
  # import pprint
  # pp = pprint.PrettyPrinter(indent=4)
  # with open("voteTree.py", "wb") as writeDict:
  #   pprint.pprint(voteTree, writeDict)

  # voteTree.runConstituencyVote()

  # import pprint
  # pp = pprint.PrettyPrinter(indent=4)
  # with open("voteTree.constituencyProcessed.py", "wb") as writeDict:
  #   pprint.pprint(voteTree, writeDict)

  # voteTree.runListVote()

  # import pprint
  # pp = pprint.PrettyPrinter(indent=4)
  # with open("voteTree.listProcessed.py", "wb") as writeDict:
  #   pprint.pprint(voteTree, writeDict)

  # ipdb.set_trace()

  #calculate seats from 2011
  #129 total members of parliament
  #73 constituencies, FPTP
  #56 List Vote Seats
  #  8 regions
  #  7 seats in each region
  #  De Hondt by region

  #Constituency Vote
  voteData['constituency']['results']       = {}
  voteData['constituency']['votingNumbers'] = {}
  for rowData in voteData['constituency']['data']:
    # voteData['constituency']['votingNumbers'][rowData]['Constituency'] = {}
    partyVote = -1
    

  regions = {
      'Central Scotland': {'constituencies': ['Airdrie and Shotts',
         'Coatbridge and Chryston',
         'Cumbernauld and Kilsyth',
         'East Kilbride',
         'Falkirk East',
         'Falkirk West',
         'Hamilton, Larkhall and Stonehouse',
         'Motherwell and Wishaw',
         'Uddingston and Bellshill']},
       'Glasgow': {'constituencies': ['Glasgow Anniesland',
         'Glasgow Cathcart',
         'Glasgow Kelvin',
         'Glasgow Maryhill and Springburn',
         'Glasgow Pollok',
         'Glasgow Provan',
         'Glasgow Shettleston',
         'Glasgow Southside',
         'Rutherglen']},
       'Highlands and Islands': {'constituencies': ['Argyll and Bute',
         'Caithness, Sutherland and Ross',
         'Na h-Eileanan an Iar',
         'Inverness and Nairn',
         'Moray',
         'Orkney Islands',
         'Shetland Islands',
         'Skye, Lochaber and Badenoch']},
       'Lothian': {'constituencies': ['Almond Valley',
         'Edinburgh Central',
         'Edinburgh Eastern',
         'Edinburgh Northern and Leith',
         'Edinburgh Pentlands',
         'Edinburgh Southern',
         'Edinburgh Western',
         'Linlithgow',
         'Midlothian North and Musselburgh']},
       'Mid Scotland and Fife': {'constituencies': ['Clackmannanshire and Dunblane',
         'Cowdenbeath',
         'Dunfermline',
         'Kirkcaldy',
         'Mid Fife and Glenrothes',
         'North East Fife',
         'Perthshire North',
         'Perthshire South and Kinrossshire',
         'Stirling']},
       'North East Scotland': {'constituencies': ['Aberdeen Central',
         'Aberdeen Donside',
         'Aberdeen South and North Kincardine',
         'Aberdeenshire East',
         'Aberdeenshire West',
         'Angus North and Mearns',
         'Angus South',
         'Banffshire and Buchan Coast',
         'Dundee City East',
         'Dundee City West']},
       'South Scotland': {'constituencies': ['Ayr',
         'Carrick, Cumnock and Doon Valley',
         'Clydesdale',
         'Dumfriesshire',
         'East Lothian',
         'Ettrick, Roxburgh and Berwickshire',
         'Galloway and West Dumfries',
         'Kilmarnock and Irvine Valley',
         'Midlothian South, Tweeddale and Lauderdale']},
       'West Scotland': {'constituencies': ['Clydebank and Milngavie',
         'Cunninghame North',
         'Cunninghame South',
         'Dumbarton',
         'Eastwood',
         'Greenock and Inverclyde',
         'Paisley',
         'Renfrewshire North and West',
         'Renfrewshire South',
         'Strathkelvin and Bearsden']}
  }

  

  idMap = {"regions":{}, "constituencies":{}}
  for (region, value) in regions.items():
    regionID = camelCase(region)
    idMap['regions'][regionID] = {"title": region}
    for constituency in value['constituencies']:
      idMap['constituencies'][camelCase(constituency)] =  \
      { "title":  constituency, 
        "region": regionID,
        "parties": {},
      }



  newSwings = {}
  newSwings['constituency'] = request.params['swingsConstituency']
  newSwings['list']         = request.params['swingsList']

  swings = {"constituency": {}, "list": {}}
  for (swingType, swingSet) in newSwings.items():
    swings[swingType] = {}
    swingList = swingSet.split("\n")
    for swingDef in swingList:
      if swingDef == "":
        continue
      swingDef = swingDef.split("=")
      swings[swingType][swingDef[0]] = float(swingDef[1])

  # import copy
  
  # voteTree = ScottishParliamentaryElection()
  # voteTree['2016']    = copy.deepcopy(request.root["2011"]['2016'])
  # voteTree['parties'] = copy.deepcopy(request.root["2011"]["parties"])


  voteTree['swings'] = swings
  voteTree.runConstituencyVote()
  voteTree.runListVote()

  # ipdb.set_trace()

  return voteTree['seats']




#yogesh
@view_config(route_name="mapppm", renderer="templates/mapppm.pt")
def mapppm(context, request):
  toReturn = {}

  return toReturn