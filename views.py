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
import os, subprocess
import urllib
import time

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors


@view_config(route_name = "debug", renderer="json")
def debug(request):
  ipdb.set_trace()

  request.root['modelClasses']['Wood']['svgDisplayDefs']['svgDefinitions'][('volume',)]['svgDisplayDefByValue']['toReturn = True']['svgQuantiseEquation'] = \
      """toReturn = svgFieldValue / 2.5"""
  request.root['modelClasses']['Wood']['svgDisplayDefs']['svgDefinitions'][('volume',)]['svgDisplayDefByValue']['toReturn = True']['height'] = \
      '\nif svgQuantiseValue < 1.0:\n  toReturn = 8 * svgQuantiseValue\nelse:\n  toReturn = 8\n'

  toInsert="#fieldInfo_<a href=\"https://www.forestry.gov.uk/pdf/TimberVolumeCalculator.pdf/$FILE/TimberVolumeCalculator.pdf\">source for 2.5m3 per tree</a>"
  if toInsert not in request.root['modelClasses']['Wood']['inputFieldHUD']['FieldOrder.preClone']['orderList']:
    request.root['modelClasses']['Wood']['inputFieldHUD']['FieldOrder.preClone']['orderList']\
        .insert(4, toInsert)

  # if "Voting" not in request.root['iframeModelClasses']:
  request.root['iframeModelClasses']['Voting'] = \
      { "icon": "earth.svg",
        "src" : "votingModel/scotland/national",
      }
  request.root['iframeModelClasses']['Ideation'] = \
      { "icon": "earth.svg",
        "src" : "https://ideationboard.visual.tools/",
      }
  request.root['iframeModelClasses']['RegionalData'] = \
        { "icon": "gas-mask.svg",
          "src" : "/static/threeJS/map/map.html",
          "displayName" : "Regional Data",
        }
  request.root['iframeModelClasses']['CurriculumRadialMap'] = \
        { "icon": "gas-mask.svg",
          "src" : "/static/legacy/curriculumRadialMap/d3TableHack-2.html",
          "displayName" : "Curriculum Radial Map",
        }


  transaction.commit()

  return {}

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

@view_config(route_name='blueprintByName',             renderer='templates/thisEqualsThat.pt')
def blueprintByName(request):
    print ""
    print "Blueprint Name:"
    print request.matchdict["blueprintName"]
    return {'project': 'thisEqualsThat'}

@view_config(route_name='infogramByID',             renderer='templates/thisEqualsThat.pt')
def infogramByID(request):
    print ""
    print "InfogramID:"
    print request.matchdict["infogramID"]
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
  standard = []
  for key in modelClasses.keys():
    standard.append({"name":key, "displayName": modelClasses[key]['displayName'] if "displayName" in modelClasses[key] else modelClasses[key]['name']})

  jsonOutput    = \
      { "standard": standard,
        "iframe":   request.root['iframeModelClasses']
      }

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

@view_config(route_name="saveInfogram", renderer="json")
def saveInfogram(request):
  # ipdb.set_trace()

  #this functionality should be added at some point
  #titleInput        = request.params['titleInput']
  #toggleFeatures    = json.loads(request.params['toggleFeatures'])
  #svg 			 	      = request.params["svg"]

  modelInstanceUUID = request.params["modelInstanceUUID"]

  newModelInstance  = copyClassInstance(modelInstanceUUID, request, request.root['modelInstances'], request.root['savedModelInstances'])


  # maybe, maybe not
  #newModelInstance['svg'] = svg

  transaction.commit()

  # with open(os.path.join(os.path.dirname(__file__), "visualisations", "svg", "%s.svg" % (uuid, ) ) , "w") as svgFile:
  #   svgFile.write(svg)

  #### Write a file to the filesystem and then nginx can serve it directly. Give that URL, including the UUID
  ####  various possiblities

  toReturn = {}
  toReturn["infogramID"]    = newModelInstance['uuid']
  toReturn["infogramURL"]   = "https://visual.tools/infogram/%s" % (newModelInstance['uuid'] , )
  toReturn["infogramPath"]  = "/infogram/%s" % (newModelInstance['uuid'] , )

  print
  print "saveInfogram: %s" % ( toReturn, )
  print "saved: "
  print newModelInstance
  print
  print
  print "loaded: "
  print request.root['savedModelInstances'][newModelInstance['uuid']]
  print
  return toReturn

  # toReturn['uuid'] = newModelInstance['uuid']

  # # add query string arguments for title and axes etc
  # toReturn['embedURL'] = request.relative_url("/embedSVG/%s" % (newModelInstance['uuid'], ) )
  #return request.relative_url("visualisations/svg/%s.svg" % (uuid, ) )
@view_config(route_name="saveSVG", renderer="json")
def saveSVG(request):
  # ipdb.set_trace()

  #svgToSave           = request.params['svgToSave']
  readableFileName    = request.headers['X-VisualTools-SvgFilename']
  nginxTempFileName   = request.headers['X-File']

  thisFileDir         = os.path.dirname(os.path.realpath(__file__))
  # find a free uuid filename
  svgFileName         = "%s.%s.svg" % (readableFileName, uuid.uuid4().hex)
  svgFilePath         = os.path.join(thisFileDir, "static", "print", "svg")
  while (os.path.isfile(os.path.join(svgFilePath, svgFileName) ) ):
    svgFileName = "%s.%s.svg" % (readableFileName, uuid.uuid4().hex)
    svgFilepath = os.path.join(thisFileDir, "static", "print", "svg")

  svgFilePathAndName = os.path.join(svgFilePath, svgFileName)

  setNginxTemporaryFilePermissionsFilePathAndName = os.path.join(thisFileDir, "serverConfigurationFiles", "setNginxTemporaryFilePermissions")
  subprocess.call("sudo %s %s %s" % (setNginxTemporaryFilePermissionsFilePathAndName, nginxTempFileName, svgFilePathAndName), shell=True )
  # os.rename(nginxTempFileName, svgFilePathAndName )

  svgURL = "https://visual.tools/print/svg/%s" % ( svgFileName, )

  print "svgSave: \n  %s\n  %s\n  %s" % (nginxTempFileName, svgFilePathAndName, svgURL)

  return { "svgURL": svgURL }



@view_config(route_name="getInfogramByID", renderer="json")
def getInfogramByID(request):
  # bb3233ea051545fd80fa3b88a83d8136
  infogramID = request.params["infogramID"]

  # ipdb.set_trace()

  newModelInstance  = copyClassInstance(infogramID, request, request.root['savedModelInstances'], request.root['modelInstances'])

  modelInstanceInterface = newModelInstance.getJSInterface()

  jsOutput = [ modelInstanceInterface ]

  transaction.commit()

  print
  print "getInfogramByID: %s" % (modelInstanceInterface['id'], )
  print
  print jsOutput
  print

  return jsOutput


def copyClassInstance(modelInstanceUUID, request, fromDict, toDict):
  modelInstance       = fromDict[modelInstanceUUID]
  modelClass          = modelInstance['modelClass']

  urlData                       = modelInstance.getCanonicalURLJSON()
  #urlData['outputField']        = modelInstance['lastAlteredOutput']
  #urlData['visualisationField'] = modelInstance['lastAlteredVisualisation']

  newModelInstance          = modelClass.getModelInstance(toDict)
  newModelInstance.setFieldValues(urlData['fieldValues'])

  newModelInstance['lastAlteredInput']          = modelInstance['lastAlteredInput']
  newModelInstance['lastAlteredOutput']         = modelInstance['lastAlteredOutput']
  newModelInstance['lastAlteredVisualisation']  = modelInstance['lastAlteredVisualisation']

  return newModelInstance

@view_config(route_name="getVisualisation")
def getVisualisation(request):

  uuid = request.matchdict['uuid']

  res = request.response
  res.content_type  = "image/svg"
  res.text = "<image src=\"%s\"/>" % (request.relative_url("getSVGData/%s" % (uuid, ) ))
  return res

@view_config(route_name="getSVGData")
def getSVGData(request):
  modelInstance = request.root['savedModelInstances'][request.matchdict['uuid']]

  res = request.response
  res.content_type  = "image/svg+xml"
  res.text = modelInstance['svg']
  return res




@view_config(route_name="inputFieldAltered", renderer="json")
def inputFieldAltered(request):
  # try:
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
      modelInstance['modelFieldAlteredSequence'].append(("input", inputField, inputFieldValue, time.time()))
      modelInstance.getInputSetter(inputField).setValue(modelInstance, inputFieldValue)
    except KeyError as e:
      print "Exception in setting input value: %s" % e
      valueFromInstance.append("inputField")
      valueFromInstance.append("newValue")

      inputField = modelInstance['lastAlteredInput']
      modelInstance.getInputSetter(inputField)

    except ValueError as e:
      print e
    try:
      outputField     = tuple(json.loads(request.params['outputField']))
      modelInstance['modelFieldAlteredSequence'].append(("output", outputField, None, time.time()))
      modelInstance.getOutputSetter(outputField)
    except Exception as e:
      print repr(e)
      valueFromInstance.append("outputField")
      outputField = modelInstance['lastAlteredOutput']
    try:
      visualisationField = tuple(json.loads(request.params['visualisationField']))
      modelInstance['modelFieldAlteredSequence'].append(("visualisation", visualisationField, None, time.time()))
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

    return {    "modelClass": modelInstance['modelClass']['name'],

                "fieldName": modelInstance['outputFieldAddress'],
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
  # except:
  #   return {}

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


@view_config(route_name="votingModel/scotland/national", renderer="templates/scottishParliament_votingModel.pt")
def scottishParliament_votingModel(context, request):
  # ipdb.set_trace()
  return {}

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

@view_config(route_name="commonSpace/comments", renderer="templates/commonSpace_comments.pt")
def commonSpace_comments(context, request):
  # ipdb.set_trace()
  return {}


#yogesh
@view_config(route_name="mapppm", renderer="templates/mapppm.pt")
def mapppm(context, request):
  toReturn = {}


#holochain
#@view_config(route_name="holochain", renderer="templates/holochain.pt")
#def mapppm(context, request):
#  toReturn = {}


#@view_config(route_name="holochain/projects", renderer="json")
#def holochain_projects(request):
#  projects = request['root']['holoProjects']
#  toReturn = {}

#@view_config(route_name="holochain/addProject", renderer="json")
#def holochain_addProject(request):
#  toReturn = {}

#@view_config(route_name="holochain/loadProject", renderer="json")
#def holochain_loadProject(request):
#  toReturn = {}

#@view_config(route_name="holochain/createServer", renderer="json")
#def holochain_createServer(request):
#  toReturn = {}

#@view_config(route_name="holochain/destroyServer", renderer="json")
#def holochain_loadProject(request):
#  toReturn = {}

#@view_config(route_name="holochain/refreshServers", renderer="json")
#def holochain_loadProject(request):
#  toReturn = {}

  return toReturn
