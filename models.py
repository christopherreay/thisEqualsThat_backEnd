from persistent.mapping import PersistentMapping
PM = PersistentMapping

from persistent.list    import PersistentList
PL = PersistentList


from collections import OrderedDict as OD

import models as models

import re, logging, uuid, copy, json
import transaction

import ipdb
import math

#dynamic data sets
from datetime import datetime
import time
import requests

def isalambda(v):
  LAMBDA = lambda:0
  return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__

def getAddressOrDefault(dict, fieldAddress):
  if fieldAddress in dict:
    return dict[fieldAddress]
  elif "__default" in dict:
    return dict['__default']
  else:
    return None

import re

def camelCase(toConvert):
  # try:
    # ipdb.set_trace()
    toReturn = ""
    step1 = re.sub("[^\w]", "", toConvert.title())
    #step1 = toConvert.title().replace(" ", "")
    if len(step1) > 0:
      toReturn  = step1[0].lower()
    if len(step1) > 1:
      toReturn += step1[1:]#
    return toReturn
  # except:
  #   ipdb.set_trace()

def traverse(obj, *params):
  # ipdb.set_trace()
  
  paramIndex = 0
  while paramIndex < len(params):
      defaultValue  = params[paramIndex]
      name          = params[paramIndex+1]
      paramIndex += 2

      if name not in obj:
        obj[name] = defaultValue
      
      if paramIndex == len(params) and params[paramIndex -1] == True:
        return obj
      else:
        obj = obj[name]

  return obj

def traverseNames(obj, defaultClass, names):
  for name in names:
    if name not in obj:
      obj[name] = defaultClass()
    obj = obj[name]
  return obj


#Base Class for all collections includes UUID and getList and getDict functions
#  which create a dict or list if none such exists already
class Node(PersistentMapping):
  def __init__(self, **kwargs):
    super(Node, self).__init__()
    #self['context'] = PersistentMapping()
    self['uuid']    = uuid.uuid4().hex
    self.update(kwargs)
  def getList(self, name):
    if not name in self:
      self[name] = PersistentList()
    return self[name]
  def getDict(self, name):
    if not name in self:
      self[name] = PersistentMapping()
    return self[name]
  def getNode(self, name):
    if not name in self:
      self[name] = Node()
    return self[name]
  def getByDefault(self, defaultValue, name):
    if not name in self:
      self[name] = defaultValue
    return self['name']
  def getValue(self, name, defaultValue):
    if name not in self:
      self[name] = defaultValue
    return self[name]

  def __str__(self):
    #print type(self)
    if "name" in self:
      return self['name']
    else: 
      return str(self.__dict__)
  def __repr__(self):
    return self.__str__()



#just a container for ModelClass objects
#  PersistentMapping is from the Object Persistence mechanism. Makes a python
#    dictionary which is directly persistable inside Data.fs
class ModelClasses(PersistentMapping):
  pass
#no idea
class ModelFields(Node):
  pass
   
#placeToRecordExternalDatasetUpdateTimings
class DynamicDataSets(Node):
  pass

class Users(Node):
  pass
class User(Node):
  pass

class VoteCount(Node):
  pass

class Title(Node):
  def getIdentifier():
    if "identifier" not in self:
      step1       = self.title.title().replace(" ", "")
      identifier  = step1[0].lower() + step1[1:]
      self['identifier'] = identifier
    return self['identifier']

class Vote(Node):
  def __init__(self, **kwargs):
    super(Vote, self).__init__(kwargs)

  def addTo(election, data):
    election['votes'].append(self);

class Party(Title):
  def __init__(self, **kwargs):
    super(Title, self).__init__(kwargs)

  def addTo(election, data):
    election['parties'].append(self);

class Constituency(Title):
  pass
class Region(Title):
  pass
class ScottishParliamentaryElection(Node):
  def __init__(self, **kwargs):
    super(ScottishParliamentaryElection, self).__init__()
    self.update(kwargs)

  def getSwingTarget(self, swingString):
    target = self
    for swingStep in swingString.split("."):
      target = self.getNode(swingStep)
    return target

  def getSwing(self, swingAddress):
    target = self.getSwingTarget(constituencyAddress)
    return target['value']
  def addSwing(self, swingAddress, percent):
    target = self.getSwingTarget(swingAddress)
    target.value = percent
  def runConstituencyVote(self):
    # ipdb.set_trace()

    self['seats'] = {"constituency":{}}

    parties = self['parties']['constituency']
    swings  = self['swings']['constituency']

    national = self['2016']
    for (regionName, region) in national.items():
      for (constituencyName, constituency) in region.items():
        # for fromParty in parties:
        #   for toParty in parties:
        #     targetList = ["national", region, constituency]

        #     swing = 0
        #     for target in targetList:
        #       try:
        #         swing += target[fromParty][toParty]['constituency']
        #       except:
        #         pass
        #     if not swing == 0:
        #     traverse(swings, {},fromParty, [], toParty).append(swing)
                        
        for fromParty in parties:
          try:
            baseVote = constituency[fromParty]['constituency']['baseVote']
            constituency[fromParty]['constituency']['calculatedVotes'] = 0
          except:
            pass

        for fromParty in parties:
          try:
            baseVote = constituency[fromParty]['constituency']['baseVote']
            # traverse(constituency[fromParty]['constituency'], 0, "calculatedVotes")
            constituency[fromParty]['constituency']['calculatedVotes'] += baseVote
            for toParty in parties:
              targetList = [constituencyName, regionName, "national"]
              for target in targetList:
                swingAddress = target+"."+fromParty+"."+toParty
                try:
                  swing       = swings[swingAddress]
                  swingVotes  = int(baseVote * (min(swing, 100) / 100.0))
                  constituency[fromParty] ['constituency'] ['calculatedVotes'] -=  swingVotes
                  traverse(constituency, {}, toParty, {}, 'constituency', 0, 'calculatedVotes')
                  constituency[toParty]['constituency']['calculatedVotes'] +=  swingVotes
                except:
                  continue
          except:
            pass
        
        winningVotes = -1
        for party in parties:
          if constituency[party]['constituency']['calculatedVotes'] > winningVotes:
            winningVotes = constituency[party]['constituency']['calculatedVotes']
            winningParty = party
          constituency['winningParty'] = winningParty
        traverse(self['seats']['constituency'], {}, winningParty, [], 'constituencies').append(constituencyName)
        traverse(self['seats'], {}, 'constituency', {}, winningParty, {}, 'regions', 0, regionName)
        self['seats']['constituency'][winningParty]['regions'][regionName] += 1


  def runListVote(self):
    # ipdb.set_trace()

    self['seats']['list'] = {}

    parties = self['parties']['list']
    swings  = self['swings']['list']

    national = self['2016']
    for (regionName, region) in national.items():
      for (constituencyName, constituency) in region.items():
        # for fromParty in parties:
        #   for toParty in parties:
        #     targetList = ["national", region, constituency]

        #     swing = 0
        #     for target in targetList:
        #       try:
        #         swing += target[fromParty][toParty]['constituency']
        #       except:
        #         pass
        #     if not swing == 0:
        #     traverse(swings, {},fromParty, [], toParty).append(swing)

        for fromParty in parties:
          try:
            baseVote = constituency[fromParty]['constituency']['calculatedVotes']
            constituency[fromParty]['list']['calculatedVotes'] = 0
          except:
            pass

        for fromParty in parties:
          try:
            baseVote = constituency[fromParty]['constituency']['calculatedVotes']
            
            # traverse(constituency[fromParty]['list'], 0, "calculatedVotes")
            constituency[fromParty]['list']['calculatedVotes'] += baseVote
            for toParty in parties:
              targetList = [constituencyName, regionName, "national"]
              for target in targetList:
                swingAddress = target+"."+fromParty+"."+toParty
                try:
                  swing       = swings[swingAddress]
                  swingVotes  = int(baseVote * (min(swing, 100) / 100.0))
                  constituency[fromParty] ['list'] ['calculatedVotes'] -=  swingVotes
                  traverse(constituency, {}, toParty, {}, 'list', 0, 'calculatedVotes')
                  constituency[toParty]['list']['calculatedVotes'] +=  swingVotes
                  print toParty, swingVotes, constituency[toParty]['list']['calculatedVotes']
                except:
                  continue
          except:
            pass
      
      #implement dehondt voting thing
      
      #transaction.commit()
            
      #add up votes from constituencies
      
      for (constituencyName, constituency) in region.items():
        for party in parties:
          try:
            votesFromConstituency = constituency[party]['list']['calculatedVotes']
            traverse(self['seats']['list'], {}, party, {}, regionName, 0, "calculatedVotes")
            self['seats']['list'][party][regionName]["calculatedVotes"] += votesFromConstituency
          except:
            pass

      for party in parties:
        try:
          traverse(self['seats']['list'], {}, party, {}, regionName, 0, 'calculatedSeats')
          # self['seats']['list'][regionName][party]['calculatedSeats'] = self['seats']['constituency'][party]['regions'][regionName]
        except:
          pass

      print "Region: ", regionName
      for dehondtRound in range(7):
        winningVotes = -1
        for party in parties:
          try:
            constituencySeats = self['seats']['constituency'][party]['regions'][regionName]
          except:
            constituencySeats = 0
          try:
            listSeats         = self['seats']['list'][party][regionName]['calculatedSeats']
          except:
            listSeats = 0
          try:
            dehondtDevisor    = constituencySeats + listSeats + 1
            effectiveVotes = int(self['seats']['list'][party][regionName]['calculatedVotes'] /  dehondtDevisor)
            print party, dehondtDevisor, effectiveVotes
            if effectiveVotes > winningVotes:
              winningParty = party
              winningVotes = effectiveVotes
          except Exception, e:
            #print e
            pass
        print winningParty+ ": wins"
        self['seats']['list'][winningParty][regionName]['calculatedSeats'] += 1

      #   if constituency[party]['list']['calculatedVotes'] > winningVotes:
      #     winningVotes = constituency[party]['constituency']['calculatedVotes']
      #     winningParty = party
      #   constituency[party]['constituency']['winningParty'] = winningParty
      # traverse(self['seats']['constituency'], [], winningParty).append(constituencyName)



#    ipdb.set_trace()

  def calculateConstituencyVotes(self):
    pass

  


class SwingVote(Node):
  def __init__(self, **kwargs):
    super(SwingVote, self).__init__(kwargs)
  

class DynamicDataSet(Node):
  def __init__(self, **kwargs):
    super(DynamicDataSet, self).__init__()
    self['fieldDefinitions']          = PersistentMapping()
    self['processorDefinitions']      = PersistentMapping()
    self['subModelDefinitions']       = PersistentMapping()
    self['svgDisplayDefDefinitions']  = PersistentMapping()
  def nextTimeForUpdate(self):
    for (key, item) in self.items():
      #stuff about datetime
      #cant be bothered
      pass
  def getRawData(self):
    dataContainer = self
    if not "getRawData" in dataContainer:
      return False
    toReturn = None
    exec(dataContainer['getRawData'])
    dataContainer['rawData'] = toReturn
  def getFieldDefinitions(self):
    dataContainer = self
    toReturn = {}
    exec(dataContainer["buildFieldDefinitions"])
    dataContainer['fieldDefinitions'] = toReturn
  def getSelectInputFieldColumnValues(self):
    dataContainer = self
    fieldColumnValues = dataContainer['selectInputFieldValues'] = Node()
    for dataPoint in dataContainer['rawData']:
      for columnName in dataContainer['selectInputFieldNames']:
        columnValues = fieldColumnValues.getList(columnName)
        columnValue = dataPoint[columnValue]
        if columnValue not in columnValues:
          columnValues.append(columnValue)
  def buildSelectInputFields(self):
    dataContainer = self
    newFieldDefinitions = {}
    for fieldName in self['selectInputFieldNames']:
      fieldValues = list(self['selectInputFieldValues'][fieldName])
      selectFieldValuesDict = {}
      for fieldValue in fieldValues:
        selectFieldValuesDict[fieldValue] = fieldValue
      defaultValue = ""
      if "__all__" in fieldValues:
        defaultValue = "__all__"
      newFieldDefinitions[fieldName] = \
          ClassField( {"name": fieldName,
                      "fieldType": "select",
                      "defaultValue": defaultValue,
                      "rangeBottom": 1,
                      "rangeTop": 1000000,
                      "rangeType": "log",
                      "selectableValues": selectFieldValuesDict,
                      "unit":               "arbitraryText",
                      "unitPrefix":          "",
                      "unitSuffix":          "",
                      "inputField":          True, 
                      "outputField":         True, 
                      "defaultInputField":   False, 
                      "defaultOutputField":  False,
                      "svgComponent":         None
                      })
    self['fieldDefinitions'].update(newFieldDefinitions)
  def getProcessorDefinitions(self):
    dataContainer = self
    toReturn = {}
    exec(dataContainer["buildProcessorDefinitions"])
    dataContainer['processorDefinitions'] = toReturn
  def getSubModelDefinitions(self):
    dataContainer = self
    toReturn = {}
    exec(dataContainer["buildSubModelDefinitions"])
    dataContainer['subModelDefinitions'] = toReturn
  def getSVGDisplayDefDefinitions(self):
    dataContainer = self
    toReturn = {}
    exec(dataContainer['buildSVGDisplayDefDefinitions'])
    dataContainer['svgDisplayDefDefinitions'] = toReturn
  def updateStatic(self):
    dataContainer = self
    toReturn = "blankStaticLogEntry"
    if not "updateStatic" in dataContainer:
      self.getFieldDefinitions()
      self.getProcessorDefinitions()
      self.getSubModelDefinitions()
      self.getSVGDisplayDefDefinitions()
      toReturn = "DefaultStaticUpdate: CurrentDateTime/lazy"
    else:
      toReturn = None
      exec(dataContainer['updateStatic'])
    if "updateStaticLog" not in dataContainer:
      dataContainer['updateStaticLog'] = PersistentList()
    dataContainer['updateStaticLog'].append(toReturn)
  def updateData(self):
    dataContainer = self
    toReturn = "blankDataLogEntry"
    exec(dataContainer['updateData'])
    if "updateDataLog" not in dataContainer:
      dataContainer['updateDataLog'] = PersistentList()
    dataContainer['updateDataLog'].append(toReturn)

#Stores data by UUID. This class is used to store data by ModelClass or by ModelInstance. The Node base class has a uuid created in its init method.
class ValueByInstance(Node):
  def __init__(self):
    super(ValueByInstance, self).__init__()
  def hasData(self, key, instance):
    if not key in self:
      return False
    if not instance['uuid'] in self[key]:
      return False
    return True
  def getValue(self, instance, key):
    return self.getDict(key)[instance['uuid']]
  def setValue(self, instance, key, value):
    self.getDict(key)[instance['uuid']] = value
  def hasInstance(self, instance, key):
    return instance['uuid'] in self.getDict(key)
  def addToList(self, instance, key, value):
    uuid = instance['uuid']
    keyDict = self.getDict(key)
    if uuid not in keyDict:
      keyDict[uuid] = PersistentList()
    keyDict[uuid].append(value)
    return keyDict[uuid]
  def clearList(self, instance, key):
    uuid = instance['uuid']
    keyDict = self.getDict(key)
    if uuid not in keyDict:
      keyDict[uuid] = PersistentList()
    keyDict[uuid].clear()
    return keyDict[uuid]

#BranchPath is the base class for InputSetter and OutputSetter
class BranchPath(Node):
  def __init__(self, modelClass, fieldAddress, pathName):
    super(BranchPath, self).__init__()
    self['modelClass']    = modelClass
    self['fieldAddress']  = fieldAddress
    currentClass = modelClass
    path = self.getList("path")
    #travel along the fieldAddress, collecting the Branch objects
    #  you pass along the way, and record them all in self['path']
    #  which is a list.
    for fieldName in fieldAddress:
      currentBranch = currentClass['fields'][fieldName]
      path.append(currentBranch)
      if "subModelClass" in currentBranch:
        currentClass = currentBranch['subModelClass']
        
  def setValue(self, instance, value):
    self['path'][-1]['instanceData'].setValue(instance, "fieldValue", value)
  def getValue(self, instance):
    return self['path'][-1]['instanceData'].getValue(instance, "fieldValue")
  
  def __str__(self):  
    toReturn = "\n\nBranchPath:"
    for branch in self['path']:
      toReturn += "\n  %s" % branch
    return toReturn
  def __repr__(self):
    return self.__str__()
    
#inputSetter is used to set the currentValue of a field
#  when a user changes its value
class InputSetter(BranchPath):
  def __init__(self, modelClass, fieldAddress):
    super(InputSetter, self).__init__(modelClass, fieldAddress, "inputSetter")

#used to read the final value from when a ProcessPath is process() ed
class OutputSetter(BranchPath):
  def __init__(self, modelClass, fieldAddress):
    super(OutputSetter, self).__init__(modelClass, fieldAddress, "outputSetter")

#Constructed from one InputSetter and one OutputSetter. An annonymous
#  Branch is made to join the InputSetter and OutputSetter at the
#  ModelClass where they meat up together.
#  .process(instance) performs all calculations to make the
#    currentOutput the correct value given the currentInput    
class ProcessPath(Node):
  def __init__(self, modelClass, inputFieldAddress, outputFieldAddress):
    super(ProcessPath, self).__init__()

    print "ProcessPath(init):\n  inputField: %s\n  outputField: %s" % (inputFieldAddress, outputFieldAddress)

    inputSetter   = self['inputSetter']  = \
        modelClass.getInputSetter(inputFieldAddress)
    outputSetter  = self['outputSetter'] = \
        modelClass.getOutputSetter(outputFieldAddress)
    #inputPath and outputPath contain a list of Branch objects
    inputPath     = inputSetter['path']
    outputPath    = outputSetter['path']

    outputPathMaxIndex = len(outputPath) -1

    #this loops finds the common root of inputSetter and outputSetter
    for i in range(len(inputPath)):
      #ipdb.set_trace()
      if inputPath[i]['uuid'] == outputPath[i]['uuid']:
        continue
      if i == outputPathMaxIndex:
        break
    
    #rootBranch contains the common root of inputSetter and outputStter
    rootBranch  =   inputPath[i]
    #linkBranch is an anonymous Branch which connects the inputSetter to the outputSetter
    linkBranch  =   Branch(rootBranch['modelClass'], rootBranch['fieldName'], rootBranch['field'])
    linkBranch['outputFieldName'] = outputPath[i]['fieldName']
    
    self['inputSetter']   = inputSetter
    self['outputSetter']  = outputSetter
    self['rootI']         = i
    self['linkBranch']    = linkBranch
  

    
  #Travel from the end of the inputSetter to the beginiing of the inputSetter (the commonRoot) and then from the start of the outputSetter
  #  to the end of the outpuSetter, updating all the relevant values
  #  in all the fields along the way. In the end, outputSetter.getValue(instance) will contain the correct value.
  def process(self, instance):
    ##ipdb.set_trace()
    instance['currentlyProcessing'] = []
    processPath = self
    print "Processing Path:\n  input: %s\n  output: %s" % (self['inputSetter'], self['outputSetter'])
  
    #rootI is the [index] of the common root Branch
    rootI = processPath['rootI']
    inputPath = processPath['inputSetter']['path'][rootI:-1]
    inputField = processPath['inputSetter']['path'][-1]
    #iterate from end of inputSetter (backwards) to commonRoot. Updating fieldValues along the way
    for branch in reversed(inputPath):
      #assume that the ModelClass we are currently Processing has
      #  all the modelInstance values set already. Call "process"
      #  to calculate the value of the currentOutputField given that
      #  the currentInputField and its value have already been set.
      remoteFieldValue = branch['subModelClass']['fields'][branch['remoteFieldName']]['processor'].process(instance, inputField['field']['name'])
      #look up the Branch connecting this ModelClass to its parent.
      #  the top of this Branch is the currentInputField for the parent
      #  ModelClass. Set the value of that field value of currentOutputFIeld
      #  for this (the child) ModelClass
      branch.setFieldValue(instance, remoteFieldValue)
      inputField = branch
      #currentlyProcessing is used to find circular dependencies during
      #  processing
      del instance['currentlyProcessing'][:]
    
    ##ipdb.set_trace()
    # iterate from commonRoot to end of outputSetter (forwards). Updating fieldValues along the way
    for branch in processPath['outputSetter']['path'][rootI:]:
      #process this ModelClass, assuming that all values have been set
      fieldValue = branch['processor'].process(instance, inputField['field']['name'])
      #set the value of currentInputField for the child ModelClass
      #  using the calculated currentOutputField from this, the parent,
      #  ModelClass
      branch.setFieldValue(instance, fieldValue)
      #traverse along the path, down the ModelClass tree
      if 'subModelClass' in branch:
        branch['subModelClass']['fields'][branch['remoteFieldName']].setFieldValue(instance, branch.getFieldValue(instance))
        inputField = branch['subModelClass']['fields'][branch['remoteFieldName']]
      del instance['currentlyProcessing'][:]
    return fieldValue


#contains all the data for an instance of a ModelClass.
#  each time a user creates a new instance of ModelClass
#  on the web interface. One of these objects is created to contain the
#  relevant data.
#  Much of the time, the ModelInstance does not directly contain
#    data, but its UUID is used as the lookup key for data stored
#    directly in ModelClass objects
class ModelInstance(Node):
  def __init__(self, modelInstances, modelClass):
    super(ModelInstance, self).__init__()
    #modelInstances is a global store of all ModelInstance objects
    #  the UUID of a modelInstance is sent to the browser for identification
    modelInstances[self['uuid']] = self
    
    self['modelClass']          = modelClass
    #contains a list of the fields whos values are part of the calculation
    #  for this ModelClass for this step in the iteration along the ProcessPath
    self['currentlyProcessing'] = PersistentList()
    
    print "Setting Defaults for ModelClass: %s" % self['modelClass']['name']
    #set the currentInputField to either the last field updated by the user, or
    #  the default, if the user has not yet interacted with this instanceData
    inputField  = self["lastAlteredInput"]  = modelClass['defaultInputField']
    #set the currentOutputField to ...
    outputField = self["lastAlteredOutput"] = modelClass['defaultOutputField']
    #set the currentVisualisation to ...
    visualisationField = self["lastAlteredVisualisation"] = modelClass['defaultVisualisationField']

    #record the inputFieldAltered sequence for embed URL and other things... cant remember whwat
    modelFieldAlteredSequence = self['modelFieldAlteredSequence'] = PersistentList()

    #store BottomModel data and memoise bottomModel instances
    self['bottomModel']         = None
    self['isBottomModel']       = False
    self['bottomModelHistory']  = PersistentMapping()

    #setup the process path for this modelInstance
    self.getInputSetter(inputField)
    self.getOutputSetter(outputField)
    #  and process :)
    self.process()

 
  #utility method to get InputSetter from the parent ModelClass.
  #  make this the official InputSetter for this modelInstance
  def getInputSetter(self, inputFieldAddress):
    self['inputFieldAddress'] = inputFieldAddress
    toReturn = self['inputSetter']  = self['modelClass'].getInputSetter(inputFieldAddress)
    return toReturn
  #utility method to get OutputSetter from the parent ModelClass
  #  make this the official OutputSetter for this modelInstane
  def getOutputSetter(self, outputFieldAddress):
    self['outputFieldAddress']        = outputFieldAddress
    toReturn = self['outputSetter'] = self['modelClass'].getOutputSetter(outputFieldAddress)
    return toReturn
  
  #utility method to get ProcessPath from the parent ModelClass
  #  make this the official OutputSetter for this modelInstane
  def getProcessPath(self):
    toReturn = self['processPath'] = self['modelClass'].getProcessPath(self['inputFieldAddress'], self['outputFieldAddress'])
    return toReturn
  #utility method to get ProcessPath for this Instance. Used by the svgOutputCalculter, e.g.
  #  DO NOT STORE THIS PROCESS PATH AS THE OFFICIAL PROCESS PATH FOR THIS INSTANCE
  def getProcessPathTemp(self, inputFieldAddress, outputFieldAddress):
    toReturn = self['modelClass'].getProcessPath(inputFieldAddress, outputFieldAddress)
    return toReturn

  #process this instance.
  def process(self):
    ##ipdb.set_trace()
    processPath = self.getProcessPath()
    return processPath.process(self)
  
  #get the JSON definition for this instance.
  #  Sent to the browser to constuct sliders and stuff
  def getJSInterface(self, boundInputField=None):
    boundInputFullAddress = json.dumps(boundInputField)
    (fieldDefinitions,  fieldBranches)  = self['modelClass'].getFieldDefinitions()
    ##ipdb.set_trace()    
    #if not 'jsInterface' in self:
    jsInterface = self['jsInterface'] = \
    { "id":         self['uuid'],
      "modelClass": self['modelClass']['name'],
      "fields": dict(fieldDefinitions),
    }
    #more bottomModel stuff
    if boundInputField is not None:
      jsInterface['fields'][boundInputFullAddress]['inputField'] = False
    fieldValues = jsInterface['fieldValues'] = {}
    for (fieldName, fieldBranch) in fieldBranches.items():
      fieldValues[fieldName] = fieldBranch.getFieldValue(self)   

    if "inputFieldHUD" in self['modelClass']:
      jsInterface['inputFieldHUDJSON'] = self['modelClass']['inputFieldHUD'] 
    print    ("MODELINSTANCE", self.keys())
    return jsInterface

  def getCanonicalURLJSON(self):
    #modelClass, fieldValues, lastAlteredInput, lastAlteredOutput, lastAlteredVisualisation
    
    (fieldDefinitions,  fieldBranches)  = self['modelClass'].getFieldDefinitions()
    ##ipdb.set_trace()    
    #if not 'jsInterface' in self:
    urlData = \
    { "id":     self['uuid'],
      "fields": dict(fieldDefinitions).keys()
    }
    #more bottomModel stuff
    #if self['boundInputField'] is not None:
    #  urlData['fields'][boundInputFullAddress]['inputField'] = False
    fieldValues = urlData['fieldValues'] = {}
    for (fieldName, fieldBranch) in fieldBranches.items():
      fieldValues[fieldName] = fieldBranch.getFieldValue(self)    
    return urlData

  def setFieldValues(self, fieldValues):
    # ipdb.set_trace()

    (fieldDefinitions, fieldBranches) = self['modelClass'].getFieldDefinitions()
    for (fieldName, fieldBranch) in fieldBranches.items():
      fieldBranch.setFieldValue(self, fieldValues[fieldName])


#Big complicated object that administrates loads of stuff
#  FieldNames by RootClass
#  
class Branch(Node):
  dependentFieldRegex       = re.compile("\!\!(?P<fieldName>.*?)\!\!")
  def __init__(self, modelClass, fieldName, field):
    super(Branch, self).__init__()
    #my parent ModelClass
    self['modelClass']    = modelClass
    #the name of this FieldBranch in the parent ModelClass
    self['fieldName']     = fieldName
    #the fieldDefinition (more or less the same as the JSON object sent to 
    #  the browser to define the Field
    self['field']         = field
    #Data stored by RootModelClass (e.g. the path to this FieldBranch from the RootModelClass, e.g. ["inputWatts", "mass"] for CPS: Coal: mass)
    self['classData']     = ValueByInstance()
    #data stored by ModelInstance (e.g the currentValue of this field)
    self['instanceData']  = ValueByInstance()
    
  def initialise(self, root, fieldAddress):
    #store Field name by RootClass
    self['classData'].setValue(root, "fieldAddress", fieldAddress)
    #create a DisplayName and store by RootClass
    self['classData'].setValue(root, "displayFieldAddress", "%s: %s %s %s" % (self['modelClass']['name'], self['field']['unitPrefix'], self['fieldName'], self['field']['unitSuffix']))
    
    #create a flat dictionary for ALL branches attached to a ModelClass and
    #  all its SubModelClasses
    root['fieldBranches'][fieldAddress] = self
    #if a Branch has a SubModel hanging off the end of it, then we
    #  initialise the SubModel's fields recursively, making them
    #  available in the flat field list in the RootModelClass
    if "subModelClassDef" in self:
      subModelDef   = self['subModelClassDef']
      subModelClass = self['subModelClass'] = self['modelClass']['modelClassContainer'][subModelDef['className']]
      self['remoteFieldName']       = subModelDef['remoteFieldName']
      subModelClass.initialise(root, fieldAddress)
    #extract some specific data from the actual Fields, that affects
    #  the parent RootModelClass of that Field (e.g. defaultInputField)
    if self['modelClass'] == root:
      if self['field']['defaultInputField'] == True:
        root['defaultInputField'] = fieldAddress
      if self['field']['defaultOutputField'] == True:
        root['defaultOutputField'] = fieldAddress
      if self['field']['defaultVisualisationField'] == True:
        root['defaultVisualisationField'] = fieldAddress
    return self
  
  def getFieldValue(self, instance):
    if not self['instanceData'].hasInstance(instance,"fieldValue"):
      toReturn = self['field']['defaultValue']
      self['instanceData'].setValue(instance, "fieldValue", toReturn)
    else:
      toReturn = self['instanceData'].getValue(instance, "fieldValue")
    return toReturn
    
  def setFieldValue(self, instance, value):
    self['instanceData'].setValue(instance, "fieldValue", value)
  
  def process(self, instance, inputField):
    print "BranchProcess:\n  instance: %s\n  inputField: %s" % (instance, inputField)
    
  def __str__(self):
    subModelClass = {"name": "noSubModel"}
    if "subModelClass" in self:
      subModelClass = self['subModelClass']
    remoteFieldName = "__noRemoteFieldName"
    if "remoteFieldName" in self:
      remoteFieldName = self['remoteFieldName']
    outputField = "__noOutputField"
    if "outputFieldName" in self:
      outputField = self['outputFieldName']
    
      
    return  "Branch: %s, Field: %s, SubModel: %s\n  outputField: %s" \
        % ( self['modelClass']['name'], 
            self['field']['name'], 
            subModelClass['name'],
            outputField
          )
          
          
class ModelClassAlreadyDefinedException(Exception):
  def __init__(self, message):
    self.message = message
class ModelClass(Node):
  def __init__(self, root, modelClassName, fields, processors, subModels, svgDisplayDefs, **kwargs):
    super(ModelClass, self).__init__()
    modelClasses    = root['modelClasses']
    fieldUnitIndex  = root['fieldUnitIndex']
    if modelClassName in modelClasses:
      raise ModelClassAlreadyDefinedException("There is already a ModelClass called %s" % modelClassName)
    modelClasses[modelClassName] = self
    
    self["modelClassContainer"] = modelClasses
    self['fieldUnitIndex']      = fieldUnitIndex
    self["name"]                = modelClassName
    self["hasInstance"]         = False

    self['fieldBranches']       = PersistentMapping()
    
    self["inputSetters"]        = PersistentMapping()
    self["outputSetters"]       = PersistentMapping()
    self["processPaths"]        = PersistentMapping()

    self['fieldsByUnit']        = Node()

    self["classInstanceData"]   = ValueByInstance()

    fieldDict = self.getDict("fields")
    for (fieldName, field) in fields.items():
      field["modelClass"]    = self['name']
      branch                = Branch(self, fieldName, field)
      fieldDict[fieldName]  = branch
      fieldUnitIndex.getList(field['unit']).append(branch)
      self['fieldsByUnit'].getList(field['unit']).append(branch)
    
    processorDict = self.getDict('fieldProcessors')
    for (fieldName, processorDict) in processors.items():
        field = fieldDict[fieldName]
        field['processor'] = FieldProcessor(field, processorDict)
           
    for (fieldName, subModelDef) in subModels.items():
      fieldDict[fieldName]['subModelClassDef']  = subModelDef
    
    self['svgDisplayDefs']      = SVGDisplayDefs(self, svgDisplayDefs)

    self.update(kwargs)
    

  def initialise(self, root=None, address=tuple()):
    if root==None:
      root = self
    if not "initialised" in root:
      for (fieldName, fieldBranch) in self['fields'].items():
        fieldBranch.initialise(root, address + (fieldName,))
    if root==self:
      root['initialised'] = True
      
  def getInputSetter(self, inputFieldAddress):
    if not inputFieldAddress in self['inputSetters']:
      self['inputSetters'][inputFieldAddress]   = InputSetter(self, inputFieldAddress)
    return self['inputSetters'][inputFieldAddress]
  
  def getOutputSetter(self, outputFieldAddress):
    if not outputFieldAddress in self['outputSetters']:
      self['outputSetters'][outputFieldAddress] = OutputSetter(self, outputFieldAddress)
    return self['outputSetters'][outputFieldAddress]
  
  def getProcessPath(self, inputFieldAddress, outputFieldAddress):
    #ipdb.set_trace()
    if inputFieldAddress not in self['processPaths']:
      inputFieldMem = self['processPaths'][inputFieldAddress] = PersistentMapping()      
    inputFieldMem = self['processPaths'][inputFieldAddress]
    if outputFieldAddress not in inputFieldMem:
      inputFieldMem[outputFieldAddress] = ProcessPath(self, inputFieldAddress, outputFieldAddress)
    
    return self['processPaths'][inputFieldAddress][outputFieldAddress]
  
    
  def getFieldDefinitions(self, root=None):
    if root == None:
      root = self
    
    if root == self and "fieldDefinitions" in self:
      fieldDefinitions  = self['fieldDefinitions']
      fieldBranches     = self['fieldBranches']
    else:
      fieldDefinitions = {}
      fieldBranches    = {}
      
      for (fieldName, field) in self['fields'].items():
        fieldDefinition = field['field']
        fieldAddress    = field['classData'].getValue(root, "fieldAddress")
        fullAddress     = json.dumps(fieldAddress)
        ##ipdb.set_trace()
        while "__dict__" not in fieldDefinition:
          time.sleep(0.1)

        fieldDefinitions[fullAddress] = fieldDefinition.__dict__['data']
        fieldDefinitions[fullAddress]['displayFieldAddress'] = \
            field['classData'].getValue(root, "displayFieldAddress")
        fieldDefinitions[fullAddress]['fullAddress'] = fullAddress

        fieldBranches[fullAddress] = field
        if 'subModelClass' in field:
          (subFieldDefinitions, subFieldBranches) = field['subModelClass'].getFieldDefinitions(root=root)
          fieldDefinitions.update(subFieldDefinitions)
          fieldBranches.update(subFieldBranches)
        
      if self == root:
        self['fieldDefinitions']  = PersistentMapping(fieldDefinitions)
        self['fieldBranches']     = PersistentMapping(fieldBranches)
        transaction.commit()

    return (fieldDefinitions, fieldBranches)
    
  def getModelInstance(self, modelInstances):
    instance          = ModelInstance(modelInstances, self)

    #jsInterface       = instance.getJSInterface()

    return instance    
  
  def __str__(self):
    return "Class: %s\n  fields: %s\n  inputSetters: %s\n  outputSetters: %s\n  processPaths: %s\n  svgDisplayDefs: %s\n\n" \
        % (self['name'], self['fields'], self['inputSetters'], self['outputSetters'], self['processPaths'], self['svgDisplayDefs'])
        
class ClassField(Node):
    
  """def __init__( self, 
                name, fieldType, 
                defaultValue, rangeBottom, rangeTop, rangeType,
                selectableValues, 
                unit=None, unitPrefix="", unitSuffix="",
                inputField=False, outputField=False, 
                defaultInputField=False, defaultOutputField=False,
                svgComponent=None                
              ):
  """
  def __init__( self, data):
    super(ClassField, self).__init__()
    
    self['visualisationField']        = False
    self['defaultVisualisationField'] = False

    self.update(data)
    """ 
    self['name']                        = name
    
    self['fieldType']                   = fieldType
    self['defaultValue']                = defaultValue
    
    self['rangeBottom']                 = rangeBottom
    self['rangeTop']                    = rangeTop
    self['rangeType']                   = rangeType
    
    self['unit']                        = unit
    self['unitPrefix']                  = unitPrefix
    self['unitSuffix']                  = unitSuffix
    
    self['selectableValues']            = selectableValues
    
    self['inputField']                  = inputField
    self['outputField']                 = outputField
    self['defaultInputField']           = defaultInputField
    self['defaultOutputField']          = defaultOutputField
    """
  def __str__(self):
    return self['name']
  def __repr__(self):
    return self.__str__()

class FieldProcessor(Node):
  dependentFieldRegex       = re.compile("\!\!(?P<fieldName>.*?)\!\!")
  def __init__(self, classField, inputFieldEquations):
    super(Node, self).__init__()
    self["classField"]          = classField
    for inputFieldName in inputFieldEquations:
      self.addExecString(inputFieldName, inputFieldEquations[inputFieldName])
  
  def addDefaultProcessor(self, execString):
    self.addExecString("__default", execString)
  def addExecString(self, inputFieldName, execString):
    self[inputFieldName] = \
        PersistentMapping({ "execString": execString,
            "dependentFields": FieldProcessor.dependentFieldRegex.findall(execString)})
  
  def process(self, instance, inputFieldName):
    ##ipdb.set_trace()
    print "Processing field: %s" % inputFieldName
    classField        = self['classField']
    classFieldName    = classField['field']['name']
    modelClass        = classField['modelClass']
    modelClassFields  = modelClass['fields']
    
    currentlyProcessing = instance['currentlyProcessing']
    currentlyProcessing.append(classFieldName)
    
    if inputFieldName == classFieldName:
      return classField.getFieldValue(instance)
    elif inputFieldName in self:
      fieldProcessor = self[inputFieldName]
    elif "__default" in self:
      fieldProcessor = self['__default']
    else:
      return classField.getFieldValue(instance)
    
    dependentFields = fieldProcessor['dependentFields']
    for dependentField in dependentFields:
      print "searching for sub-dependency: %s" % dependentField
      if dependentField in currentlyProcessing:
        return classField.getFieldValue(instance)
      
    print "DEPENDENT FIELDS"
    print dependentFields
    
    execString = fieldProcessor['execString']
    for dependentField in dependentFields:
      print "Processing %s" % dependentField
      if not "processor" in modelClassFields[dependentField]:
        fieldValue = modelClassFields[dependentField].getFieldValue(instance)
      else:
        fieldValue = modelClassFields[dependentField]['processor'].process(instance, inputFieldName)
      
      execString = \
          execString.replace("!!%s!!" % dependentField, "%s" % fieldValue)

      print "replacing !!%s!! with %s" % (dependentField, fieldValue)

    toReturn = None
    print "Processing: \n%s" % execString
    exec(execString)

    print "processedValue %s: %s" % (classFieldName, toReturn)
    return toReturn
      
class SVGDisplayDefs(Node):
  def __init__(self, modelClass, svgFieldDefinitions):
    super(Node, self).__init__()
    #self['modelClass']          = modelClass
    self['svgDefinitions']      = svgFieldDefinitions
  
  def process(self, modelInstance):

    print "\n\nProcessing visualisation path"
    print "  from: %s to %s" % (modelInstance['lastAlteredOutput'], modelInstance['lastAlteredVisualisation'])

    context = {}
    modelClass = modelInstance['modelClass']
        
    output_to_valueQuantise_Dict = getAddressOrDefault(self['svgDefinitions'], modelInstance['lastAlteredVisualisation'])
    print "\nUsing algorithm: %s" % (output_to_valueQuantise_Dict, )

    svgProcessPath  = modelInstance.getProcessPathTemp(modelInstance['lastAlteredOutput'], output_to_valueQuantise_Dict['modelOutputField_forSVGConversion'])
    svgFieldValue   = svgProcessPath.process(modelInstance)
    print "processed Value: %s" % (svgFieldValue, )

    if 'closure' in output_to_valueQuantise_Dict:
      data = output_to_valueQuantise_Dict['closure']

    svgDisplayDefByValue = output_to_valueQuantise_Dict['svgDisplayDefByValue']
    if isinstance(svgDisplayDefByValue, basestring):
      toReturn = None
      exec(svgDisplayDefByValue)
      svgDisplayDefByValue = toReturn

    toReturn = False
    for (checkValueExec, svgDisplayDef) in svgDisplayDefByValue.items():
      exec(checkValueExec)
      if toReturn == True:
        break
    foundValueMatch = toReturn
    
    if foundValueMatch == True:
      toReturn = 0 #will be quantised value for SVG scalethingy
      exec(svgDisplayDef['svgQuantiseEquation'])
      svgQuantiseValue = toReturn
      
      print "process SVGDef"
      print "  svgDisplayDef['svgQuantiseEquation']"
      print "  %s" % (svgQuantiseValue, )
      
      exec(svgDisplayDef['height'])
      svgRelativeHighness = toReturn
      print "process svgHeight\n  svgDisplayDef['height']\n  %s" % (svgRelativeHighness, )

      svg3dConfiguration = dict(svgDisplayDef['defaultSVG3dDict'])
      toReturn = svg3dConfiguration
      
      #ipdb.set_trace();

      exec(svgDisplayDef['svg3dParameterExec'])
      svg3dConfiguration.update(toReturn)
      
            
      if "postProcessing" in svgDisplayDef:
        postProcessing = dict(svgDisplayDef['postProcessing'])
      else:
        postProcessing = {}

      svgHUD = {}
      if "svgHUD" in svgDisplayDef:
        svgHUD = svgDisplayDef['svgHUD']

      # inputFieldHUD = {}
      # if "inputFieldHUD" in svgDisplayDef:
      #   inputFieldHUD = svgDisplayDef['inputFieldHUD']

      svgDisplayJSONDict = \
          { "representationName"    : svgDisplayDefByValue['name'],
            "svgFile"               : svgDisplayDef['svgFile'],
            "rootGroupNodeSelector" : svgDisplayDef['rootGroupNodeSelector'],
            "svg3dConfiguration"    : svg3dConfiguration,
            "svgField"              : modelInstance['lastAlteredVisualisation'],
            "svgFieldValue"         : svgFieldValue,
            "svgRelativeHighness"   : svgRelativeHighness,
            "postProcessing"        : postProcessing,
            "svgHUD"                : svgHUD,
            #"inputFieldHUD"         : inputFieldHUD,
          } 
      
      return svgDisplayJSONDict

  """def getSVGDisplay(self, outputFieldAddress):
    output_to_valueQuantise_Dict = getAddressOrDefault(self['byOutputField'], outputFieldAddress)
    outputSetter = self['modelClass'].getOutputSetter(outputFieldAddress)
    outputFieldValue = outputSetter.getValue(self['modelInstance'])

    inputValueEquations_to_svgDisplayDef  \
        = output_to_valueQuantise_Dict['value_toQuantiseIndex']

    svgDisplayDef           = False
    for (inputValueEquation, __svgDisplayDef) in inputValueEquations_to_svgDisplayDef.items():
      fieldValue = outputFieldValue
      toReturn = False
      
      exec(inputValueEquation)
      
      if toReturn == True or inputValueEquation == "__default":
        svgDisplayDef = __svgDisplayDef
        break

    svgDisplayJSDict = {}
    if not svgDisplayDef == False:
      svgDisplayJSDict = svgDisplayDef.process(self['modelClass'], self['modelInstance'], outputFieldAddress, outputFieldValue)
    
    return svgDisplayJSDict

  def process(self, svgDisplayDef, outputFieldAddress, outputFieldValue):
    
    toReturn = \
        { "svgComponentName": "rg1024_metal_barrel",
              "svg3d": \
                  { "translate3d" : {"x": 100, "y": 300, "z": 0},
                "clone3d"     : \
                    { "row":      1,
                      "x":        600,
                      "layer":  4000,
                      "y":        -600,
                      "z":        300,
                      "nb:":      4,
                    },
              },
              "animateOptions":
                  { "duration":       1000, 
                      "easing":         "easeInCubic"
                  }
            
        }
    modelClass      = self['modelClass']
    modelInstance   = self['modelInstance']
    exec(svgDisplayDef)
    
    return toReturn
  """

class svgDisplayDef(Node):
  def __init__(self, jsDict, svgOutFieldAddress, execString):
    super(Node, self).__init__()
    self['jsDict']              = jsDict
    self['svgOutFieldAddress']  = svgOutFieldAddress
    self['execString']          = execString
  
  def process(modelClass, modelInstance, outputFieldAddress, outputFieldValue):
    #self['modelClass']          = modelClass
    #self['modelInstance']       = modelInstance
    #self['outputFieldAddress']  = outputFieldAddress
    #self['outputFieldValue']    = outputFieldValue

    processPath                 = modelInstance.getProcessPathTemp(outputFieldAddress, self['svgOutFieldAddress'])
    self['svgOutFieldValue']    = processPath.process()
    
    toReturn                    = False
    exec(self['execString'])
    return toReturn

class cuboidRep(Node):
  def __init__(self, w, h, d, volumeOrCount):
    super(Node, self).__init__()
    self['w'] = w
    self['h'] = h
    self['d'] = d
    heightRatio = 1.0 / h
    normalisedWidth = heightRatio * w
    normalisedDepth = heightRatio * d
    volumeToHeightEquation = """toReturn = math.pow(svgFieldValue / (normalisedWidth * normalisedDepth), 1.0/3)"""

  
def appmaker(zodb_root):
    #print "Starting App"
    if not 'app_root' in zodb_root:
        print "...building new database"
        app_root = Node()
        zodb_root['app_root'] = app_root

        modelClasses                = app_root['modelClasses']        = ModelClasses()
        modelInstances              = app_root['modelInstances']      = Node()
        savedModelInstances         = app_root['savedModelInstances'] = Node()
        modelFields                 = app_root['fieldUnitIndex']      = ModelFields()

        users                       = app_root['users']               = Users()
        
        representations = {}

        representations["Barrels of Oil"] = \
            OD(       { "class": "cloneable",
                        "toReturn = True":
                          { "svgFile"                 : "2barrel.svg",
                            "rootGroupNodeSelector"   : "#barrel",
                            "svgQuantiseEquation"     : 
"""toReturn = svgFieldValue / 0.158987295
""",
                            "height"                  : 
#"""context['heightOfCubes'] = math.pow(svgFieldValue/4.235, 1.0/3)
#toReturn = context['heightOfCubes']
#""",
                            """
if svgQuantiseValue < 1.0:
  toReturn = (0.159 * svgQuantiseValue) / 0.05903910399 / math.pi
else:
  toReturn = 0.85725
""",
                            "defaultSVG3dDict"        : 
                            { "translate3d" : {"x": 100, "y": 100, "z": 0},
                              "clone3d": 
                              {   "row":        1,
                                  "x":          50,
                                  "layer":      100,
                                  "y":          -50,
                                  "z":          50,
                                  "nb":         40
                              },
                            },
                            "svg3dParameterExec"        :
                                  """
cubeRoot = math.ceil(svgQuantiseValue ** (1 / 3.0))
total = math.ceil(svgQuantiseValue)
layer = total / cubeRoot
row   = layer / cubeRoot
sqrt = math.ceil(math.sqrt(svgQuantiseValue))
if sqrt <= 10:
  row   = sqrt
  layer = 100
toReturn['clone3d'].update(
  { "nb"    : total,
    "row"   : row,
    "layer" : layer
  }
)
if svgQuantiseValue > 1.0:
  svgRelativeHighness = math.ceil(total / layer) * 0.85725

#toReturn['clone3d']['x'] = context['heightOfCubes'] * 400
#toReturn['clone3d']['y'] = context['heightOfCubes'] * -400
#toReturn['clone3d']['z'] = context['heightOfCubes'] * 400
#print toReturn
#print svgQuantiseValue
#numberOfCubes = svgQuantiseValue
#numberOfCubes = math.ceil(math.sqrt(svgQuantiseValue)) / context['heightOfCubes']
#sqrt = math.ceil(math.sqrt(numberOfCubes))
#if sqrt > 10:
#  row = math.ceil(numberOfCubes)
#else:
#  row = sqrt
#toReturn['clone3d'].update(
#  { "nb"  : 1,
#        #math.ceil(svgQuantiseValue), # / context['heightOfCubes'],
#    "row" : row
#  }
#)
                                  """,
                            "svgHUD":
                            { "RandomiseClones.postColor":
                              { "randomisePosition":
                                { "degreeOfRandom": 2,
                                },
                                "randomiseColors":
                                { "degreeOfRandom": 0,
                                },         
                                "randomiseColorsByGroup":
                                { "degreeOfRandom": 2,
                                },
                              },         
                            },

                          }
                      }
            )
        representations["Trees"] = \
            OD(       { "class": "cloneable", 
                        "toReturn = True":
                          { "svgFile"                 : "barrel.svg",
                            "rootGroupNodeSelector"   : "#barrel",
                            "svgQuantiseEquation"     : 
"""toReturn = svgFieldValue / 0.7853
""",
                            "height"                  : 
#"""context['heightOfCubes'] = math.pow(svgFieldValue/4.235, 1.0/3)
#toReturn = context['heightOfCubes']
#""",
                            """
if svgQuantiseValue < 1.0:
  toReturn = (0.7853 * svgQuantiseValue) / 0.0624921884 / math.pi
else:
  toReturn = 4
""",
                            "defaultSVG3dDict"        : 
                              { "translate3d" : {"x": 210, "y": 100, "z": 0},
                                    "clone3d": {
                                        "row":        1,
                                        "x":          35,
                                        "layer":      1000,
                                        "y":          -50,
                                        "z":          50,
                                        "nb":         40
                                    },
                                  },
                              "svg3dParameterExec"        :
                                  """
sqrt = math.ceil(math.sqrt(svgQuantiseValue))
if sqrt > 10:
  row = 10
else:
  row = sqrt
nb = math.ceil(svgQuantiseValue)
toReturn['clone3d'].update(
  { "nb"  :   nb,
    "row" :   row,
    "layer":  nb+10,
  }
)
                                  """,

                            "svgHUD":
                            { "RandomiseClones.postColor":
                              { "randomisePosition":
                                { "degreeOfRandom": 12,
                                },
                                "randomiseColors":
                                { "degreeOfRandom": 10,
                                },         
                                "randomiseColorsByGroup":
                                { "degreeOfRandom": 25,
                                },
                              },         
                            },
                          }
                      }
            )
        representations["People"] = \
            OD({ "class": "cloneable",
                  "toReturn = True":
                          { "svgFile"                 : "person.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : """toReturn = svgFieldValue""",
                            "height"                  : """toReturn = 1.72""",
                            "defaultSVG3dDict"        : 
            { "translate3d" : {"x": 100, "y": 100, "z": 0},
                                    "clone3d": {
                                        "row":        6,
                                        "x":         30,
                                        "layer":    200,
                                        "y":          -80,
                                        "z":          50,
                                        "nb":         40
                                    },
                                  },
                              "svg3dParameterExec"        : \
                                  """
nb = math.ceil(svgQuantiseValue)
toReturn['clone3d'].update(
      { "nb"  :     nb,
        "row" :     math.ceil(math.sqrt(svgQuantiseValue)),
        "layer":    nb+10,
      }
)
                                  """,

                            "svgHUD":
                            { "RandomiseClones.postColor":
                              { "randomiseColors":
                                { "degreeOfRandom": 5,
                                },         
                                "randomiseColorsByGroup":
                                { "degreeOfRandom": 0,

                                },
                                "randomisePosition":
                                { "degreeOfRandom": 20,
                                },
                              },         
                            },
                          }
                      })
        representations["Ratios of People"] = \
            OD({  "class": "weird",
                  "toReturn = True":
                          { "svgFile"                 : "person.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : """toReturn = svgFieldValue""",
                            "height"                  : """toReturn = 1.72""",
                            "defaultSVG3dDict"        : 
                                { "translate3d" : {"x": 100, "y": 300, "z": 0},
                                  "clone3d": 
                                  { "row":        10,
                                    "x":          30,
                                    "layer":      1000,
                                    "y":          -80,
                                    "z":          50,
                                    "nb":         100
                                  },
                                },
                            "svg3dParameterExec"        :
                                  """
toReturn['recolorClones'] = svgFieldValue
cloneCount = float(svgFieldValue[0]['cloneCount1'])
toReturn['clone3d'].update(
  { "row" : math.sqrt(cloneCount),
    "nb"  : cloneCount,
    "layer": cloneCount + 10,
  }
)
                                  """,

                            "svgHUD":
                            { "RandomiseClones.postColor":
                              { "randomiseColors":
                                { "degreeOfRandom": 1,
                                },         
                                "randomiseColorsByGroup":
                                { "degreeOfRandom": 5,
                                },
                                "randomisePosition":
                                { "degreeOfRandom": 10,
                                  "randomMultiplier": 64, #default was 32
                                },
                              },         
                            },
                          }
                      })

        representations["Lightbulbs"] = \
            OD({ "class": "cloneable",
                  "toReturn = True":
                          { "svgFile"                 : "lightbulb_simple.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : """toReturn = svgFieldValue""",
                            "height"                  : """toReturn = 0.15""",
                            "defaultSVG3dDict"        : 
                                { "translate3d" : {"x": 200, "y": 200, "z": 0},
                                    "clone3d": {
                                        "row":        6,
                                        "x":          50,
                                        "layer":      400,
                                        "y":          -60,
                                        "z":          50,
                                        "nb":         40
                                    },
                                },
                              "svg3dParameterExec"        :
                                  """
nb = math.ceil(svgQuantiseValue)
toReturn['clone3d'].update(
    { "nb"      : nb,
      "row"     : math.ceil(math.sqrt(svgQuantiseValue)),
      "layer"   : nb + 10,
    }
)
                                  """,
                            "svgHUD":
                            { "RandomiseClones.postColor":
                              { "randomiseColors":
                                { "degreeOfRandom": 0,
                                },         
                                "randomiseColorsByGroup":
                                { "degreeOfRandom": 5,
                                },
                                "randomisePosition":
                                { "degreeOfRandom": 5,
                                },
                              },         
                            },
                          }
                      })

        representations["Grey Cube"] = \
            OD({ "class": "howMuch",
                  "toReturn = True":
                          { "svgFile"                 : "declarative_cube_grey.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : """toReturn = svgFieldValue""",
                            "height"                  : """toReturn = math.pow(svgFieldValue / 4.23508127518, 1.0/3)""",
                            "defaultSVG3dDict"        : 
                            { "translate3d" : {"x": 200, "y": 200, "z": 0},
                                   "clone3d": {
                                           "row":        6,
                                             "x":          150,
                                         "layer":      100,
                                             "y":          -90,
                                             "z":          220,
                                            "nb":         1
                                              },
                            },
                            "svg3dParameterExec"        :
                                """
                                """,
                            "svgHUD":
                            { "fillManager.postClone":
                              { "cubeShader":
                                { "initialColorString": "rgba(128,128,128,0.7)",
                                  "fillSmasher":
                                  { ".faceBack, .faceFront"  : "pickedColor            .toString('rgb')",
                                    ".faceTop,  .faceBottom" : "pickedColor.darken(10) .toString('rgb')",
                                    ".faceLeft, .faceRight"  : "pickedColor.darken(20) .toString('rgb')",
                                  },
                                }
                              }
                            }
                          }
             })
        representations["Grey Cube 100"]    = copy.deepcopy(representations["Grey Cube"])
        representations["Grey Cube 100"]    ['toReturn = True']['svgHUD']["fillManager.postClone"]["cubeShader"]["initialColorString"] = "rgba(120, 120, 120, 0.7)"
        
        representations["Grey Cube in Air"] = copy.deepcopy(representations["Grey Cube"])
        representations["Grey Cube in Air"] ['toReturn = True']['svgHUD']["fillManager.postClone"]["cubeShader"]["initialColorString"] = "rgba(109,192,196,0.31)"

        representations["Yellow Cube"]      = copy.deepcopy(representations["Grey Cube"])
        representations["Yellow Cube"]      ['toReturn = True']['svgHUD']["fillManager.postClone"]["cubeShader"]["initialColorString"] = "rgba(200,200,53,0.9)"
        #123.6,76.4,200
        #1.61780104712, 1, 2.61780104712
        """ width = height * 2.61780104712
            depth = height * 1.61780104712
            volume = height * height * 2.61780104712 * height * 1.61780104712
            volume = height ^ 3 * 4.23508127518
            height = (volume / 4.23508127518) ^ 1/3
        """
######
        """"svgHUD":
                            { "colorPickers.postClone":
                              { ".face":
                                { "initialColorString": "rgba(53, 53, 53, 0.9)",
                                  "onColorChange":
                                      "#"" var topColor  = pickedColor.transition("black", 0.10);
                                          var sideColor = pickedColor.transition("black", 0.175);

                                          toReturn  = 
                                              `.face                            { fill: ${ pickedColor .toRgbaString() };  } 
                                               .face.faceTop,  .face.faceBottom { fill: ${ topColor    .toRgbaString() };  } 
                                               .face.faceLeft, .face.faceRight  { fill: ${ sideColor   .toRgbaString() };  }
                                              `;
                                      "#"",
                                }
                              }
                            }

        """
        representations["Kier Bales"] = \
            OD({ "class": "cloneable",
                "toReturn = True":
                          { "svgFile"                 : "declarative_cube_yellow.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : 
"""toReturn = svgFieldValue / 1.88606
""",
                            "height"                  : 
#"""context['heightOfCubes'] = math.pow(svgFieldValue/4.235, 1.0/3)
#toReturn = context['heightOfCubes']
#""",
                            """
if svgQuantiseValue < 1.0:
  toReturn = svgFieldValue / 1.236 / 2
else:
  toReturn = 0.764
""",
                            "defaultSVG3dDict"        : 
                              { "translate3d" : {"x": 100, "y": 100, "z": 0},
                                    "clone3d": {
                                        "row":        "na",
                                        "x":          180,
                                        "layer":      "na",
                                        "y":          -130,
                                        "z":          220,
                                        "nb":         "na"
                                    },
                                  },
                              "svg3dParameterExec"        :
                                  """
#cubeRoot = math.ceil(svgQuantiseValue ** (1 / 3.0))
total = math.ceil(svgQuantiseValue)
#layer = total / cubeRoot
#row   = layer / cubeRoot
#numberOfLayers = math.ceil(total / layer)

#1.61803398874989
#1
#0.618033988749897
#1.61803398874989 + 0.618033988749897 = 2.2360679775

##Golden Rectangle
#x * 1.6x = 64
#1.6x**2 = 64
#x**2 = 64 / 1.6
#x = (64 / 1.6) ** (1/2)

#Golden Cuboid
#x * 1.6x * 0.6x = 64
#2.2x**3 = 64
#x = (64 / 2.2) ** (1.0/3)

if total <= 64:
  #row   = sqrt   = math.ceil(math.sqrt(svgQuantiseValue))
  row             = math.ceil((total / 1.61803398874989) ** 0.5)
  layer           = 64
  numberOfLayers  = 1
else:
  gdRatioY        = (svgQuantiseValue / 2.2360679775) ** (1.0/3)
  row             = gdRatioY
  layer           = (1 + 1.61803398874989) * gdRatioY**2
  numberOfLayers  = math.ceil(total / layer)
toReturn['clone3d'].update(
  { "nb"    : total,
    "row"   : row,
    "layer" : layer
  }
)



if svgQuantiseValue > 1.0:
  svgRelativeHighness = (math.ceil(numberOfLayers) * .75) + ((numberOfLayers-1) * (1.3-.75))

heightInCM = svgRelativeHighness * 100
toReturn['translate3d'].update(
    {"y" : max(heightInCM * 1.5, 100) + (row * 20),
     "x" : max(row * 40, 100)
    }
)


#toReturn['clone3d']['x'] = context['heightOfCubes'] * 400
#toReturn['clone3d']['y'] = context['heightOfCubes'] * -400
#toReturn['clone3d']['z'] = context['heightOfCubes'] * 400
#print toReturn
#print svgQuantiseValue
#numberOfCubes = svgQuantiseValue
#numberOfCubes = math.ceil(math.sqrt(svgQuantiseValue)) / context['heightOfCubes']
#sqrt = math.ceil(math.sqrt(numberOfCubes))
#if sqrt > 10:
#  row = math.ceil(numberOfCubes)
#else:
#  row = sqrt
#toReturn['clone3d'].update(
#  { "nb"  : 1,
#        #math.ceil(svgQuantiseValue), # / context['heightOfCubes'],
#    "row" : row
#  }
#)
                                  """
                          }
                      }
            )

        representations["Kier Bales Logo"] = \
            OD({ "class": "cloneable",
                "toReturn = True":
                          { "svgFile"                 : "declarative_cube_kierGroup.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : 
"""toReturn = svgFieldValue / 1.27875
""",
                            "height"                  : 
#"""context['heightOfCubes'] = math.pow(svgFieldValue/4.235, 1.0/3)
#toReturn = context['heightOfCubes']
#""",
                            """
if svgQuantiseValue < 1.0:
  toReturn = (1.27875 * svgQuantiseValue) / 1.55 / 1.1
else:
  toReturn = 0.75
""",
                            "defaultSVG3dDict"        : 
                              { "translate3d" : {"x": 100, "y": 100, "z": 0},
                                    "clone3d": {
                                        "row":        "na",
                                        "x":          180,
                                        "layer":      "na",
                                        "y":          -130,
                                        "z":          220,
                                        "nb":         "na"
                                    },
                                  },
                              "svg3dParameterExec"        :
                                  """
#cubeRoot = math.ceil(svgQuantiseValue ** (1 / 3.0))
total = math.ceil(svgQuantiseValue)
#layer = total / cubeRoot
#row   = layer / cubeRoot
#numberOfLayers = math.ceil(total / layer)

#1.61803398874989
#1
#0.618033988749897
#1.61803398874989 + 0.618033988749897 = 2.2360679775

##Golden Rectangle
#x * 1.6x = 64
#1.6x**2 = 64
#x**2 = 64 / 1.6
#x = (64 / 1.6) ** (1/2)

#Golden Cuboid
#x * 1.6x * 0.6x = 64
#2.2x**3 = 64
#x = (64 / 2.2) ** (1.0/3)

if total <= 64:
  #row   = sqrt   = math.ceil(math.sqrt(svgQuantiseValue))
  row             = math.ceil((total / 1.61803398874989) ** 0.5)
  layer           = 64
  numberOfLayers  = 1
else:
  gdRatioY        = (svgQuantiseValue / 2.2360679775) ** (1.0/3)
  row             = gdRatioY
  layer           = (1 + 1.61803398874989) * gdRatioY**2
  numberOfLayers  = math.ceil(total / layer)
toReturn['clone3d'].update(
  { "nb"    : total,
    "row"   : row,
    "layer" : layer
  }
)



if svgQuantiseValue > 1.0:
  svgRelativeHighness = (math.ceil(numberOfLayers) * .75) + ((numberOfLayers-1) * (1.3-.75))

heightInCM = svgRelativeHighness * 100
toReturn['translate3d'].update(
    {"y" : max(heightInCM * 1.5, 100) + (row * 20),
     "x" : max(row * 40, 100)
    }
)


#toReturn['clone3d']['x'] = context['heightOfCubes'] * 400
#toReturn['clone3d']['y'] = context['heightOfCubes'] * -400
#toReturn['clone3d']['z'] = context['heightOfCubes'] * 400
#print toReturn
#print svgQuantiseValue
#numberOfCubes = svgQuantiseValue
#numberOfCubes = math.ceil(math.sqrt(svgQuantiseValue)) / context['heightOfCubes']
#sqrt = math.ceil(math.sqrt(numberOfCubes))
#if sqrt > 10:
#  row = math.ceil(numberOfCubes)
#else:
#  row = sqrt
#toReturn['clone3d'].update(
#  { "nb"  : 1,
#        #math.ceil(svgQuantiseValue), # / context['heightOfCubes'],
#    "row" : row
#  }
#)
                                  """
                          }
                      }
            )
        
        
        for (key, item) in representations.items():
          item["name"] = key
        

        priceField = ClassField({ "name":           "price", 
                                "fieldType":        "slider", 
                                "defaultValue":     50000000, 
                                "rangeBottom":             1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "GBP", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "GBP",
                                "inputField":          False, 
                                "outputField":         False, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                })
        energyField = ClassField({ "name":           "energy", 
                                "fieldType":        "slider", 
                                "defaultValue":     50000000, 
                                "rangeBottom":             1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Joules", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "J",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "svgComponent":         None
                                })
        



        ScottishParliamentaryElection = None




             
        # ofWhatSelectDict = {k: v for k, v in representations.iteritems() if "cloneable" in v["class"]}
        ofWhatRepDict = {}
        for (key, rep) in representations.items():
          if ("cloneable" in rep['class'] ):
            normalisedRep         = copy.deepcopy(rep)
            normalisedRep["toReturn = True"]["svgQuantiseEquation"] = "toReturn = svgFieldValue"
            normalisedRep["toReturn = True"]["svgHUD"]              = { "RandomiseClones.postColor":
                                                                        { "randomiseColors":
                                                                          { "degreeOfRandom": 10,
                                                                          },         
                                                                          "randomiseColorsByGroup":
                                                                          { "degreeOfRandom": 10,
                                                                          },
                                                                          "randomisePosition":
                                                                          { "degreeOfRandom": 10,
                                                                          },
                                                                        },         
                                                                      }
            ofWhatRepDict[key] = normalisedRep
        ofWhatSelectDict = {}
        for key in ofWhatRepDict.keys():
          ofWhatSelectDict[key] = key



        print ofWhatSelectDict
        HowMany = ModelClass(app_root, "HowMany",
            { "howMany": ClassField({ 
                                "name":                 "howMany",
                                "displayName":          "How Many",
                                "displayIcon":          "howMany.svg",
                                "description":          "Choose how many of what to show in the diagram",
                                "fieldType":            "slider", 
                                "defaultValue":         10, 
                                "rangeBottom":          1, 
                                "rangeTop":             1000, 
                                "rangeType":           "log",
                                "fieldPrecisionFunction": "toReturn = Math.ceil(currentValue);",
                                "selectableValues":     None, 
                                "unit":                "number", 
                                "unitPrefix":          "count of", 
                                "unitSuffix":          "",
                                "inputField":          True, 
                                "outputField":         True,
                                "visualisationField":  True,
                                "defaultInputField":   True, 
                                "defaultOutputField":  True,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              "ofWhat": ClassField({ 
                                "name":               "ofWhat",
                                "displayName":          "Of What",
                                "displayIcon":          "howMany.svg",
                                "description":          "Choose how many of what to show in the diagram",
                                "fieldType":          "select", 
                                "defaultValue":       "Trees", 
                                "rangeBottom":             0, 
                                "rangeTop":             100, 
                                "rangeType":           "linear",
                                "selectableValues":     ofWhatSelectDict, 
                                "unit":                "choice List",
                                "unitPrefix":           "", 
                                "unitSuffix":          "item",
                                "inputField":           True, 
                                "outputField":          False,
                                "visualisationField":   False,
                                "defaultInputField":    False, 
                                "defaultOutputField":   False,
                                "defaultVisualisationField": False,
                                "svgComponent":         None
                                }),

            },
            { "howMany" :  { "__default" : 
                                  """toReturn = !!howMany!!
                                  """
                            },
              
            },
            {#LIST OF SUBMODEL FIELD MAPPINGS
            #  { local(parent)FieldName: { "className": subModelClass, "remoteFieldName": targetFieldInSubModelClass} , ... }
            },
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("howMany", ),
                    "closure": {"ofWhatRepDict": ofWhatRepDict },
                    "svgDisplayDefByValue": """toReturn = data['ofWhatRepDict'][modelClass['fields']['ofWhat'].getFieldValue(modelInstance)]""",
                  },
            },
            inputFieldHUD = 
            { "FieldOrder.preClone":
              { "orderList":
                [ "howMany"               ,
                  "ofWhat"                ,
                ],
              },
            }
          ,
          displayName = "How Many",
        ) 

        PeopleRatioPlay = ModelClass(app_root, "PeopleRatioPlay",
            { "ratios": ClassField({ 
                                "name":                 "ratios", 
                                "displayName":          "Ratios",
                                "displayIcon":          "howMany.svg",
                                "description":          "Bleh",
                                "fieldType":            "text", 
                                "defaultValue":         0.1, 
                                "rangeBottom":             0, 
                                "rangeTop":             100, 
                                "rangeType":           "linear",
                                "selectableValues":     None, 
                                "unit":                "percent", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "%",
                                "inputField":          True, 
                                "outputField":         True,
                                "visualisationField":  False,
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "colors": ClassField({ 
                                "name":               "colors", 
                                "fieldType":          "text", 
                                "defaultValue":       "rgba(0,255,0, 0.77)", 
                                "rangeBottom":             0, 
                                "rangeTop":             100, 
                                "rangeType":           "linear",
                                "selectableValues":     None, 
                                "unit":                "rgb", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "",
                                "inputField":           True,
                                "outputField":          False,
                                "visualisationField":   False, 
                                "defaultInputField":    False, 
                                "defaultOutputField":   False,
                                "svgComponent":         None
                                }),
              "numberOfClones": ClassField({ 
                                "name":               "numberOfClones",
                                "displayName":          "Size of Gathering",
                                "displayIcon":          "howMany.svg",
                                "description":          "Choose how many people in total in the diagram",
                                "fieldType":          "text", 
                                "defaultValue":       "100", 
                                "rangeBottom":             0, 
                                "rangeTop":             100, 
                                "rangeType":           "linear",
                                "selectableValues":     None, 
                                "unit":                "number", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "people",
                                "inputField":           True, 
                                "outputField":          False,
                                "visualisationField":   False, 
                                "defaultInputField":    False, 
                                "defaultOutputField":   False,
                                "svgComponent":         None
                                }),
              
              "outputTable": ClassField({ 
                                "name":               "outputTable", 
                                "displayName":          "Table of Values",
                                "displayIcon":          "grid.svg",
                                "description":          "Contains a table of data used to generate the diagram",
                                "fieldType":          "text", 
                                "defaultValue":       {}, 
                                "rangeBottom":             0, 
                                "rangeTop":             100, 
                                "rangeType":           "linear",
                                "selectableValues":     None, 
                                "unit":                "percent", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "%",
                                "inputField":           False, 
                                "outputField":          True,
                                "visualisationField":   True,
                                "defaultInputField":    False, 
                                "defaultOutputField":   True,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              "randomLayout": ClassField({ 
                                "name":               "randomLayout", 
                                "displayName":          "Randomise Positions",
                                "displayIcon":          "randomize.svg",
                                "description":          "Put specials in random positions",
                                "fieldType":          "select", 
                                "defaultValue":       "Yes", 
                                "rangeBottom":             0, 
                                "rangeTop":             100, 
                                "rangeType":           "linear",
                                "selectableValues":     {"Yes": "Yes", "No": "No"}, 
                                "unit":                "choice",
                                "unitPrefix":           "", 
                                "unitSuffix":          "Yn",
                                "inputField":           True, 
                                "outputField":          False,
                                "visualisationField":   False,
                                "defaultInputField":    False, 
                                "defaultOutputField":   False,
                                "defaultVisualisationField": False,
                                "svgComponent":         None
                                }),

            },
            { "outputTable" :  { "__default" : 
                                  """toReturn = [ { 'ratios':         '!!ratios!!'.split("|"), 
                                                    'colors':        '!!colors!!'.split("|"), 
                                                    'cloneCount1' :   !!numberOfClones!!, 
                                                    'randomLayout' :  '!!randomLayout!!'
                                                  },
                                                ]
                                  """
                            },
              
            },
            {#LIST OF SUBMODEL FIELD MAPPINGS
            #  { local(parent)FieldName: { "className": subModelClass, "remoteFieldName": targetFieldInSubModelClass} , ... }
            },
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("outputTable", ),
                    "svgDisplayDefByValue": representations["Ratios of People"]
                  },
            },
            inputFieldHUD =
            { "Remove.preClone":
              { "hideFields":
                { "fieldsToHide": ["[\"colors\"]", "[\"ratios\"]"],
                },
              },
              "RatioColor.postColor":
              { "config":{},
              },
            },
            displayName = "Percentage",
        )

        Wood = ModelClass(app_root, "Wood", 
            { "energy": ClassField({ 
                                "name":        "energy",
                                "displayName":          "Energy Burned",
                                "displayIcon":          "burn.svg",
                                "description":          "Energy thru combustion in air",

                                "fieldType":        "slider", 
                                "defaultValue":     5000000, 
                                "rangeBottom":             1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Joules", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "J",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "svgComponent":         None
                                }),
              "mass":  ClassField({ 
                                "name":        "mass",
                                "displayName":          "Mass",
                                "displayIcon":          "scales.svg",
                                "description":          "Mass of wood",

                                "fieldType":        "slider", 
                                "defaultValue":     100, 
                                "rangeBottom":             0.1, 
                                "rangeTop":             1000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Kilograms", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "kg",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),

              "volume": ClassField({ "name":        "volume",
                                "displayName":          "Volume of Wood",
                                "displayIcon":          "size.svg",
                                "description":          "How much wood?",
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          True, 
                                "outputField":         True, 
                                "visualisationField":  True,
                                "defaultInputField":   False,
                                "defaultOutputField":  False,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              "massCO2": ClassField({ "name":        "massCO2", 
                                "displayName":          "CO2 thru Combustion",
                                "displayIcon":          "randomize.svg",
                                "description":          "Mass of CO2 in KG produced by burning this amount of wood",
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.001, 
                                "rangeTop":           10000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "kg", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "kg",
                                "inputField":          False, 
                                "outputField":         False, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
            },
            { "energy": { "mass"    : "toReturn = !!mass!!    * 19000000.0",
                          "volume"  : "toReturn = !!volume!!  * 500.0 * 19000000.0",
                          "massCO2" : "toReturn = !!massCO2!! / 1.835 * 19000000.0"
                         },
              "mass":   { "energy"  : "toReturn = !!energy!!  / 19000000.0",
                          "volume"  : "toReturn = !!volume!!  * 500.0",
                          "massCO2" : "toReturn = !!massCO2!! / 1.835"
                        },
              "volume": { "energy"  : "toReturn = !!energy!!  / 19000000.0 / 500.0",
                          "mass"    : "toReturn = !!mass!!    / 500.0",
                          "massCO2" : "toReturn = !!massCO2!! / 1.835 / 500.0"
                        },
              "massCO2":{ "energy"  : "toReturn = !!energy!!  * 1.835 / 19000000.0",
                          "mass"    : "toReturn = !!mass!!    * 1.835",
                          "volume"  : "toReturn = !!volume!!  * 500.0 * 1.835",
                        }
            },
            {#LIST OF SUBMODEL FIELD MAPPINGS
            #  { local(parent)FieldName: { "className": subModelClass, "remoteFieldName": targetFieldInSubModelClass} , ... }
              "massCO2": {"className": "CO2", "remoteFieldName": "mass"}
            },
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Trees"]
                  },
                ("energy", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Trees"]
                  },
                ("mass", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Trees"]
                  },
                ("volume", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Trees"]
                  },
                ("massCO2", ):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_frozen"),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("massCO2", "volume_frozen"):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_frozen"),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("massCO2", "volume_100"):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_100"),
                    "svgDisplayDefByValue": representations["Grey Cube 100"]
                  },
                ("massCO2", "volume_inAir"):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_inAir"),
                    "svgDisplayDefByValue": representations["Grey Cube in Air"]
                  },
            },
            inputFieldHUD = 
            { "FieldOrder.preClone":
              { "orderList":
                [ "groupHeader_Wood"          ,
                  "#fieldInfo_Here be fascinating things about trees and stuff like that CO2 and Burnings and hangings too"               ,
                  "mass"                      ,
                  "volume"                    ,
                  "energy"                    ,
                  "groupHeader_CO2"           ,
                  "massCO2, mass"             ,
                  "massCO2, volume_100"       ,
                  "massCO2, volume_inAir"     ,
                ],
                "fieldDetails":
                { "mass":       
                  { "displayName":          "Mass",
                    "displayIcon":          "scales.svg",
                    "description":          "Mass of wood (some tree)",
                  },
                  "volume":     
                  { "displayName":          "Volume",
                    "displayIcon":          "size.svg",
                    "description":          "Size of wood",
                  },
                  "energy":     
                  { "displayName":          "Energy",
                    "displayIcon":          "energy.svg",
                    "description":          "Energy thru Combustion",
                  },
                },
              },
            }
        )


        CO2 = ModelClass(app_root, "CO2",
          {   "mass":  ClassField({ "name":        "mass",
                                "displayName":          "Mass",
                                "displayIcon":          "scales.svg",
                                "description":          "Mass of CO2 in KG", 
                                "fieldType":        "slider", 
                                "defaultValue":     100, 
                                "rangeBottom":             0.1, 
                                "rangeTop":             1000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Kilograms", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "kg",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "volume_frozen": ClassField({ "name":        "volume_frozen", 
                                "displayName":          "Volume Frozen",
                                "displayIcon":          "size.svg",
                                "description":          "If the CO2 is frozen solid, how big would it be?",
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          False, 
                                "outputField":         True,
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "volume_100": ClassField({ "name":        "volume_100",
                                "displayName":          "CO2 Pure Gas",
                                "displayIcon":          "size.svg",
                                "description":          "If the CO2 is pure gas, 100% CO2, how big would it be?",
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          True, 
                                "outputField":         True, 
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "volume_inAir": ClassField({ "name":        "volume_inAir", 
                                "displayName":          "CO2 in Air",
                                "displayIcon":          "size.svg",
                                "description":          "How much Air do you need to count up this amount of CO2?",
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          True, 
                                "outputField":         True, 
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              # "timeToBreathOut": ClassField({ "name":        "timeToBreathOut", 
              #                   "displayName":          "Time to Breath",
              #                   "displayIcon":          "breath.svg",
              #                   "description":          "How long would it take a person to breath this amount of CO2 into the atmosphere?",
              #                   "fieldType":        "slider", 
              #                   "defaultValue":     10, 
              #                   "rangeBottom":        0.00000001, 
              #                   "rangeTop":           1000000000,
              #                   "rangeType":           "log",
              #                   "selectableValues":     None, 
              #                   "unit":                "s", 
              #                   "unitPrefix":           "", 
              #                   "unitSuffix":          "seconds",
              #                   "inputField":          True, 
              #                   "outputField":         True, 
              #                   "defaultInputField":   False, 
              #                   "defaultOutputField":  False,
              #                   "svgComponent":         None
              #                   }),
              
            },

            { "mass":             { "volume_100"      : "toReturn = !!volume_100!! / .5562",
                                    "volume_inAir"    : "toReturn = !!volume_inAir!! / .5562 / 2500",
                                    # "timeToBreathOut" : "toReturn = !!volume_inAir!! / 0.00120048019"
                                  },
              "volume_frozen":    { "mass"            : "toReturn = !!mass!! / 1562.0"        },
              "volume_100":       { "mass":             "toReturn = !!mass!! * (.5562)",
                                    "volume_inAir"    : "toReturn = !!volume_inAir!! / 2500",
                                    # "timeToBreathOut" : "toReturn = !!singleCube!!"
                                  },
              "volume_inAir":     { "mass"            : "toReturn = !!mass!! * .5562 * 2500",
                                    "volume_100"      : "toReturn = !!volume_100!! * 2500",
                                    # "timeToBreathOut" : "toReturn = !!volume_inAir!!"
                                  },
              # "timeToBreathOut":  { "mass"            : "toReturn = (!!energy!! / 27000000) * 0.00120048019",
              #                       "volume_100"      : "toReturn = !!mass!! * 0.00120048019",
              #                       "volume_inAir"    : "toReturn = !!volume_inAir!!"
              #                     }

            },
            {},
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("volume_frozen", ),
                    "svgDisplayDefByValue": representations["Kier Bales Logo"],
                  },
                ("mass", ):
                  { "modelOutputField_forSVGConversion" : ("volume_frozen", ),
                    "svgDisplayDefByValue": representations["Grey Cube"],
                  },
                ("volume_frozen", ):
                  { "modelOutputField_forSVGConversion" : ("volume_frozen", ),
                    "svgDisplayDefByValue": representations["Grey Cube"],
                  },
                ("volume_100", ):
                  { "modelOutputField_forSVGConversion" : ("volume_100", ),
                    "svgDisplayDefByValue": representations["Grey Cube 100"],
                  },
                ("volume_inAir", ):
                  { "modelOutputField_forSVGConversion" : ("volume_inAir", ),
                    "svgDisplayDefByValue": representations["Grey Cube in Air"],
                  },
            },
            inputFieldHUD = 
            { "FieldOrder.preClone":
              { "orderList":
                [ "groupHeader_Carbon Dioxide"  ,
                  "mass"                        ,
                  "groupHeader_Volume as Gases" ,
                  "volume_100"                  ,
                  "volume_inAir"                ,
                ],
              },
            }
        )

        LightBulb = ModelClass(app_root, "LightBulb",
        {     "energy": ClassField({ "name":        "energy",
                                "displayName":          "Energy",
                                "displayIcon":          "energy.svg",
                                "description":          "Total energy to power lightbulbs", 
                                "fieldType":        "slider", 
                                "defaultValue":         60, 
                                "rangeBottom":             1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Joules", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "J",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "svgComponent":         None
                                }),
              "count":  ClassField({ "name":        "count", 
                                "displayName":          "Number of Bulbs",
                                "displayIcon":          "count.svg",
                                "description":          "Number of lightbulbs", 
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":             1, 
                                "rangeTop":             1000, 
                                "rangeType":           "log",
                                "fieldPrecisionFunction": "toReturn = Math.ceil(currentValue);",
                                "selectableValues":     None, 
                                "unit":                "unit", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "light bulbs",
                                "inputField":          True, 
                                "outputField":         True,
                                "visualisationField":  True,
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),

              "time": ClassField({ "name":              "time", 
                                "displayName":          "Time",
                                "displayIcon":          "time.svg",
                                "description":          "Time lightbulbs are on", 
                                "fieldType":            "slider", 
                                "defaultValue":       3600, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "s", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "seconds",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "watts": ClassField({ "name":        "watts", 
                                "displayName":          "Watts",
                                "displayIcon":          "energy.svg",
                                "description":          "Watts per lightbulb", 
                                "fieldType":        "slider", 
                                "defaultValue":       60, 
                                "rangeBottom":        0.001, 
                                "rangeTop":           10000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "w", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "Watts",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
            },
            { "energy": { "__default"  : "toReturn = !!count!!  * !!time!!  * !!watts!!",
                        },
              "count":  { "__default"  : "toReturn = !!energy!! / !!time!!  / !!watts!!",
                        },
              "time":   { "__default"  : "toReturn = !!energy!! / !!count!! / !!watts!!",
                        },
              "watts":  { "__default"  : "toReturn = !!energy!! / !!count!! / !!time!!",
                        }
            },
            {#LIST OF SUBMODEL FIELD MAPPINGS
            #  { local(parent)FieldName: { "className": subModelClass, "remoteFieldName": targetFieldInSubModelClass} , ... }
              #"massCO2": {"className": "CO2", "remoteFieldName": "mass"}
            },
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("count", ),
                    "svgDisplayDefByValue": representations["Lightbulbs"]
                  },
            },
            inputFieldHUD = 
            { "FieldOrder.preClone":
              { "orderList":
                [ "groupHeader_Lightbulbs"  ,
                  "count"                        ,
                  "groupHeader_Energy Calculation" ,
                  "watts"                  ,
                  "time"                ,
                  "groupHeader_Total Energy" ,
                  "energy"                  ,
                ],
              },
            }
        )

        CPS = ModelClass(app_root, "CPS", 
            #LIST OF FIELDS
            { "price":  priceField,
              "energy": energyField,
              "inputWatts": ClassField({ "name":   "inputWatts", 
                                "fieldType":        "slider", 
                                "defaultValue":     50000000, 
                                "rangeBottom":             1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Joules", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "J",
                                "inputField":          False, 
                                "outputField":         False, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              
              "efficiency": ClassField({ "name":   "efficiency", 
                                "fieldType":        "slider", 
                                "defaultValue":     70, 
                                "rangeBottom":             1, 
                                "rangeTop":     100, 
                                "rangeType":           "linear",
                                "selectableValues":     None, 
                                "unit":                "percent", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "%",
                                "inputField":          True, 
                                "outputField":         False, 
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),

            },
            #LIST OF EQUATIONS
            #  { fieldName: { currentInputField: Equation, ...}, ... }
            { "energy": { "__default": "toReturn = !!inputWatts!! * (!!efficiency!! / 100.0)"},
              "inputWatts": { "__default": "toReturn = !!energy!! / (!!efficiency!! / 100.0)"}
            },
            #LIST OF SUBMODEL FIELD MAPPINGS
            #  { local(parent)FieldName: { "className": subModelClass, "remoteFieldName": targetFieldInSubModelClass} , ... }
            {"inputWatts": {"className": "Coal", "remoteFieldName": "energy"}
            },
            #SVG DISPLAY DEFINITIONS
            #  { currentOutputField: { stuff } , ... }
            {   "__default" :
                { "modelOutputField_forSVGConversion" : ("inputWatts", "volume"),
                  "svgDisplayDefByValue":               representations["Barrels of Oil"]
                },
                (u"inputWatts", u"volume"):
                { "modelOutputField_forSVGConversion" : ("inputWatts", "mass"),
                  "svgDisplayDefByValue":               representations["People"]
                }
            }
        )
        
        Coal = ModelClass(app_root, "Coal", 
            { "price": priceField,
              "energy": ClassField({ "name":        "energy", 
                                
                                "displayName":          "Energy Burned",
                                "displayIcon":          "size.svg",
                                "description":          "How much energy on combustion", 

                                "fieldType":        "slider", 
                                "defaultValue":     5000000, 
                                "rangeBottom":             1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Joules", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "J",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "svgComponent":         None
                                }),
              "mass":  ClassField({ "name":        "mass", 

                                "displayName":          "Mass",
                                "displayIcon":          "size.svg",
                                "description":          "Mass of Coal (How Much)", 
                                
                                "fieldType":        "slider", 
                                "defaultValue":     100, 
                                "rangeBottom":             0.1, 
                                "rangeTop":             1000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Kilograms", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "kg",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),

              "volume": ClassField({ "name":        "volume", 
                                
                                "displayName":          "Volume",
                                "displayIcon":          "size.svg",
                                "description":          "How big is the Coal", 

                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          True, 
                                "outputField":         True, 
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              "massCO2": ClassField({ "name":        "massCO2", 
                                "displayName":          "CO2",
                                "displayIcon":          "size.svg",
                                "description":          "How much CO2 produced on combustion", 

                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.001, 
                                "rangeTop":           10000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "kg", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "kg",
                                "inputField":          False, 
                                "outputField":         False, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "singleCube": ClassField({ "name":        "singleCube", 

                                "displayName":          "Single Cube Graphic",
                                "displayIcon":          "size.svg",
                                "description":          "this is an outputField that shows a cube",

                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.001, 
                                "rangeTop":           10000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          False, 
                                "outputField":         False,
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "aluminiumCube": ClassField({ "name":        "aluminiumCube", 

                                "displayName":          "Aluminum Cube",
                                "displayIcon":          "size.svg",
                                "description":          "This is an output field which renders as alu cubes",

                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.001, 
                                "rangeTop":           10000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          False, 
                                "outputField":         False,
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
            },
            { "energy": { "mass"   : "toReturn = !!mass!! * 27000000",
                          "volume" : "toReturn = (!!volume!! / 0.00120048019) * 27000000",
                          "massCO2" : "toReturn = !!mass!! * 27000000"
                        },
              "mass":   { "energy":  "toReturn = !!energy!! / 27000000",
                          "volume":  "toReturn = !!volume!! / 0.00120048019",
                          "massCO2" : "toReturn = !!massCO2!! / 2.93"
                        },
              "volume": { "energy":  "toReturn = (!!energy!! / 27000000) * 0.00120048019",
                          "mass"  :  "toReturn = !!mass!! * 0.00120048019",
                          "singleCube": "toReturn = !!singleCube!!",
                          "massCO2": "toReturn = !!mass!! * 0.00120048019"
                        },
              "massCO2":{ "mass"      : "toReturn = !!mass!!    * 2.93",
                          "volume"    : "toReturn = (!!volume!! / 0.00120048019) * 2.93",
                          "energy"    : "toReturn = ((!!energy!! / 27000000) * 0.00120048019) * 2.93",
                        }, 
              "singleCube": { "energy":  "toReturn = (!!energy!! / 27000000) * 0.00120048019",
                              "mass"  :  "toReturn = !!mass!! * 0.00120048019",
                              "volume":  "toReturn = !!volume!!",
                              "massCO2": "toReturn = !!volume!!"
                        },
              "aluminiumCube": { "energy":  "toReturn = (!!energy!! / 27000000) * 0.00120048019",
                              "mass"  :  "toReturn = !!mass!! * 0.00120048019",
                              "volume":  "toReturn = !!volume!!",
                              "massCO2": "toReturn = !!volume!!"
                        },
            },
            {
              "massCO2": {"className": "CO2", "remoteFieldName": "mass"}
            },
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("energy", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("mass", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("singleCube", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("aluminiumCube", ):
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Kier Bales Logo"]
                  },
                ("massCO2", ):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_frozen"),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("massCO2", "volume_frozen"):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_frozen"),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("massCO2", "volume_100"):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_100"),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
                ("massCO2", "volume_inAir"):
                  { "modelOutputField_forSVGConversion" : ("massCO2", "volume_inAir"),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
            }
        )
        
        person = ModelClass(app_root, "Person", 
            { "energy": ClassField({ "name":        "energy", 
                                "fieldType":        "slider", 
                                "defaultValue":     5000000, 
                                "rangeBottom":            1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Joules", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "J",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "svgComponent":         None
                                }),
              "number of people": ClassField({ "name":  "number of people", 
                                "fieldType":        "slider", 
                                "defaultValue":     1, 
                                "rangeBottom":            1, 
                                "rangeTop":     10000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "person unit", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "people",
                                "inputField":          True, 
                                "outputField":         True, 
                                "visualisationField":  True,
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              "type of analysis" : ClassField({ "name":  "type of analysis", 
                                "fieldType":        "select", 
                                "defaultValue":     9418000.05, 
                                "rangeBottom":            0, 
                                "rangeTop":     0, 
                                "rangeType":           "log",
                                "selectableValues": { "energy in food consumed":                    9418000.05, 
                                                      "total aggregated energy usage (lifestyle)":  349052942.466              
                                                    },
                                "unit":                "", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "",
                                "inputField":          True, 
                                "outputField":         False, 
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }), 
              #""" "energy in food daily":  ClassField("Energy Eaten daily", "slider",
              #          9418.05, 2000, 20000, "linear",
              #          None,
              #          inputField=True,
              #          unit="Joules", unitSuffix="J",                                         {
              #          outputField=True,
              #          defaultOutputField=True
              #          ),
              #"total daily energy usage (lifestyle)": ClassField("total daily energy usage (lifestyle)", "slider",
              #          349052942.466, 0, 10000000000, "log", #3043*41868000/365
              #          None,
              #          inputField=True,
              #          unit="Joules", unitSuffix="J",
              #          outputField=True
              #),
              #"""
              "mass": ClassField({ "name":        "mass", 
                                "fieldType":        "slider", 
                                "defaultValue":     70.80, 
                                "rangeBottom":            1, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Kilograms", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "kg",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "svgComponent":         None
                                }),
              "mass per person": ClassField({ "name":   "mass per person", 
                                "fieldType":            "slider", 
                                "defaultValue":         70.8, 
                                "rangeBottom":          30, 
                                "rangeTop":             200, 
                                "rangeType":            "linear",
                                "selectableValues":     None,
                                "unit":                 "Kilograms", 
                                "unitPrefix":           "", 
                                "unitSuffix":           "kg",
                                "inputField":           True, 
                                "outputField":          False, 
                                "defaultInputField":    False, 
                                "defaultOutputField":   False,
                                "svgComponent":         None
                                }), 
            },
            { "number of people": { "energy"   : "toReturn = !!energy!! / !!type of analysis!!",
                                    "type of analysis"   : "toReturn = !!energy!! / !!type of analysis!!",
                                    "mass"     : "toReturn = !!mass!!   / !!mass per person!!"
                                  },
              "energy"          : { "__default":                     
                                            "toReturn = !!type of analysis!! * !!number of people!!",
                                  },
              "mass"            : { "__default":
                                            "toReturn = !!mass per person!!  * !!number of people!!",
                                  },
            },
            {},
            {   "__default" :
                { 
                  "modelOutputField_forSVGConversion" : ("number of people", ),
                  "svgDisplayDefByValue": representations["People"]
                }
            }
        )
        
        comparisonVisual = SVGDisplayDefs(None,
            { "__default":
              { "modelOutputField_forSVGConversion" : ("volume", ),
                  "svgDisplayDefByValue": 
                      OD({ "toReturn = True":
                          { "svgFile"                 : "declarative_cube_yellow.svg",
                            "rootGroupNodeSelector"   : "#person",
                            "svgQuantiseEquation"     : """toReturn = svgFieldValue""",
                            "svgHeightComparisonClass": "__default",
                            "defaultSVG3dDict"        : 
            { "translate3d" : {"x": 200, "y": 200, "z": 0},
                                    "clone3d": {
                                        "row":        6,
                                        "x":          150,
                                  "layer":          100,
                                        "y":          -90,
                                        "z":          220,
                                        "nb":         40
                                    },
                                  },
                              "svg3dParameterExec"        :
                                  """toReturn['clone3d'].update(
                                        { "nb"  : math.ceil(svgQuantiseValue),
                                          "row" : math.ceil(math.sqrt(svgQuantiseValue))
                                        }
                                    )
                                  """
                          }
                      })
              }
            }
        )

        #######################static  data sets##########################

        VolMassDen = ModelClass(app_root, "VolMassDen", 
            { "volume": ClassField({ "name":        "volume",
                                "displayName":          "Volume",
                                "displayIcon":          "size.svg",
                                "description":          "How big is the thing", 
                                "fieldType":        "slider", 
                                "defaultValue":     10, 
                                "rangeBottom":        0.00000001, 
                                "rangeTop":           10000000,
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3",
                                "inputField":          True, 
                                "outputField":         True, 
                                "visualisationField":   True,
                                "defaultInputField":   False, 
                                "defaultOutputField":  True,
                                "defaultVisualisationField": True,
                                "svgComponent":         None
                                }),
              "mass": ClassField({ "name":        "mass", 
                                "displayName":          "Mass",
                                "displayIcon":          "howMany.svg",
                                "description":          "How heavy is the thing",
                                "fieldType":        "slider", 
                                "defaultValue":     10.0, 
                                "rangeBottom":            0.00000001, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "Kilograms", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "Kg",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   False, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
              "density": ClassField({ "name":        "density", 
                                "displayName":          "Density",
                                "displayIcon":          "howMany.svg",
                                "description":          "How dense is the thing",
                                "fieldType":        "slider", 
                                "defaultValue":     1.0, 
                                "rangeBottom":  0.000000001, 
                                "rangeTop":     100000000000, 
                                "rangeType":           "log",
                                "selectableValues":     None, 
                                "unit":                "m3/kg", 
                                "unitPrefix":           "", 
                                "unitSuffix":          "m3/kg",
                                "inputField":          True, 
                                "outputField":         True, 
                                "defaultInputField":   True, 
                                "defaultOutputField":  False,
                                "svgComponent":         None
                                }),
            },
              {           "mass": { "__default": 
                                            "toReturn = !!volume!!  / !!density!!",
                                  },
                        "volume": { "__default":                     
                                            "toReturn = !!mass!!    * !!density!!",
                                  },
                       "density": { "__default":
                                            "toReturn = !!volume!!  / !!mass!!",
                                  },
            },
            {
            },
            {   "__default" :
                  { "modelOutputField_forSVGConversion" : ("volume", ),
                    "svgDisplayDefByValue": representations["Grey Cube"]
                  },
            },
            inputFieldHUD = 
            { "FieldOrder.preClone":
              { "orderList":
                [ "groupHeader_Volume Mass & Density"  ,
                  "volume"                        ,
                  "mass" ,
                  "density"                  ,
                  "groupHeader_Note:<br />You can change the Calculated Output Field below",
                ],
              },
            },
            displayName = "How Much",
        )


        #######################dynamic data sets##########################
        #ipdb.set_trace()
        dynamicDataSets = app_root['dynamicDataSets'] = DynamicDataSets()
### Google Script API or some shit access Google Sheets


#         bristolHealth_2012HealthData = dynamicDataSets['bristolHealth_2012HealthData'] = DynamicDataSet()
#         bristolHealth_2012HealthData['selectInputFieldNames'] = ["question", "ward", "year"]
#         bristolHealth_2012HealthData['getRawData'] = \
# """toReturn = requests.get("https://opendata.bristol.gov.uk/resource/8pfz-pbsq.json").json()
# fieldColumnValues = dataContainer['selectInputFieldValues'] = Node()
# for columnName in dataContainer['selectInputFieldNames']:
#   columnValues = fieldColumnValues.getList(columnName)
#   columnValues.append("__all__")
# for dataPoint in toReturn:
#   for columnName in dataContainer['selectInputFieldNames']:
#     columnValues = fieldColumnValues.getList(columnName)
#     columnValue = dataPoint[columnName]
#     if columnValue not in columnValues:
#       columnValues.append(columnValue)
# """
#         bristolHealth_2012HealthData.getRawData()
#         bristolHealth_2012HealthData.buildSelectInputFields()
#         bristolHealth_2012HealthData['fieldDefinitions'].update(
#             { "percentage" : ClassField({ "name":        "percentage", 
#                                 "fieldType":        "slider", 
#                                 "defaultValue":     10, 
#                                 "rangeBottom":            1, 
#                                 "rangeTop":     100000000000, 
#                                 "rangeType":           "log",
#                                 "selectableValues":     None, 
#                                 "unit":                "ratio", 
#                                 "unitPrefix":           "", 
#                                 "unitSuffix":          "%",
#                                 "inputField":          False, 
#                                 "outputField":         True, 
#                                 "defaultInputField":   False, 
#                                 "defaultOutputField":  True,
#                                 "svgComponent":         None
#                                 }),
#              "color1": ClassField({ 
#                                 "name":               "color1", 
#                                 "fieldType":          "text", 
#                                 "defaultValue":       "rgb(255,-255,-255)", 
#                                 "rangeBottom":             0, 
#                                 "rangeTop":             100, 
#                                 "rangeType":           "linear",
#                                 "selectableValues":     None, 
#                                 "unit":                "percent", 
#                                 "unitPrefix":           "", 
#                                 "unitSuffix":          "%",
#                                 "inputField":           True,
#                                 "outputField":          False,
#                                 "visualisationField":   False, 
#                                 "defaultInputField":    False, 
#                                 "defaultOutputField":   False,
#                                 "svgComponent":         None
#                                 }),
#               "numberOfClones": ClassField({ 
#                                 "name":               "color1", 
#                                 "fieldType":          "text", 
#                                 "defaultValue":       "100", 
#                                 "rangeBottom":             0, 
#                                 "rangeTop":             100, 
#                                 "rangeType":           "linear",
#                                 "selectableValues":     None, 
#                                 "unit":                "unit", 
#                                 "unitPrefix":           "", 
#                                 "unitSuffix":          "unit",
#                                 "inputField":           True, 
#                                 "outputField":          False,
#                                 "visualisationField":   False, 
#                                 "defaultInputField":    True, 
#                                 "defaultOutputField":   False,
#                                 "svgComponent":         None
#                                 }),
#               "outputTable": ClassField({ 
#                                 "name":               "outputTable", 
#                                 "fieldType":          "text", 
#                                 "defaultValue":       {}, 
#                                 "rangeBottom":             0, 
#                                 "rangeTop":             100, 
#                                 "rangeType":           "linear",
#                                 "selectableValues":     None, 
#                                 "unit":                "percent", 
#                                 "unitPrefix":           "", 
#                                 "unitSuffix":          "%",
#                                 "inputField":           False, 
#                                 "outputField":          True,
#                                 "visualisationField":   True,
#                                 "defaultInputField":    False, 
#                                 "defaultOutputField":   False,
#                                 "defaultVisualisationField": True,
#                                 "svgComponent":         None
#                                 }),
#             })
#         buildQueryString = "whereClauseList = []\n"
#         for inputFieldName in bristolHealth_2012HealthData['selectInputFieldNames']:
#           buildQueryString+=("""\nif "!!%s!!" != "__all__":  whereClauseList.append("%s='!!%s!!'") """ % (inputFieldName, inputFieldName, inputFieldName))
#         buildQueryString+=("""\n\nwhereClauseString = " AND ".join(whereClauseList)""")

#         wqs = buildQueryString.replace("!!question!!", "__all__").replace("!!ward!!", "__all__").replace("!!year!!", "2012")
#         print wqs
#         #ipdb.set_trace()

#         getSodaAVGValue = \
# wqs + \
# """
# payload = {"$select": "value"}
# if whereClauseString:
#   payload.update({"$where": whereClauseString})
# queryResult = requests.get("https://opendata.bristol.gov.uk/resource/8pfz-pbsq.json", params=payload).json()
# print(queryResult)
# total = 0.0
# count = 0
# for dataPoint in queryResult:
#   total += float(dataPoint['value'])
#   count += 1
# avg = total/count
# """

#         bristolHealth_2012HealthData['processorDefinitions'].update(
#             { "outputTable" :  { "__default" : 
#                                   """toReturn = [ { 'ratio1': !!percentage!!, 'color1': '!!color1!!', 'cloneCount1' : '!!numberOfClones!!'},
#                                                 ]
#                                   """},
#               "percentage": 
#                   { "__default": 
# buildQueryString + \
# """
# uri = "https://opendata.bristol.gov.uk/resource/8pfz-pbsq.json"
# payload = {"$select": "value"}
# if whereClauseString:
#   payload.update({"$where": whereClauseString})
# print("  uri: %s\\n   payload: %s" % (uri,payload))
# queryResult = requests.get(uri, params=payload)
# queryResultJSON = queryResult.json()
# print(queryResult.request.url)
# print(queryResultJSON)
# total = 0.0
# count = 0
# for dataPoint in queryResultJSON:
#   total += float(dataPoint['value'])
#   count += 1
# avg = total/count

# toReturn = avg
# """
#                   }
#             }
#         )
#         bristolHealth_2012HealthData['svgDisplayDefDefinitions'].update(
#         { "__default" :
#                   { "modelOutputField_forSVGConversion" : ("outputTable", ),
#                     "svgDisplayDefByValue": rep_ratioPeople
#                   },
#         }
#         )
          
#         BristolHealthData = ModelClass(app_root, "BristolHealthData", 
#             bristolHealth_2012HealthData['fieldDefinitions'],
#             bristolHealth_2012HealthData['processorDefinitions'],
#             bristolHealth_2012HealthData['subModelDefinitions'],
#             bristolHealth_2012HealthData['svgDisplayDefDefinitions']
#           )

        for (modelClassName, modelClass) in modelClasses.items():
          modelClass.initialise()  
        
        

        transaction.commit()
        
    #coalPowerStation = CoalPowerStation("coalPowerStation")
    #zodb_root['app_root']['coalPowerStation'] = coalPowerStation
    
    #print coalPowerStation.fieldContext['price']      
    
    appRoot = zodb_root['app_root']

    iframeModelClasses = appRoot['iframeModelClasses'] = OD()
    iframeModelClasses["Money"] = \
        { "icon": "money.svg",
          "src" : "/static/threeJS/money/money.html",
        }
    iframeModelClasses["Seesaw"] = \
        { "icon": "seesaw.svg",
          "src" : "/static/threeJS/seesaw/seesaw.html",
        }
    iframeModelClasses["Particle"] = \
        { "icon": "gas-mask.svg",
          "src" : "/static/threeJS/particle/particle.html",
          "displayName" : "Particulate",
        }
    iframeModelClasses["Earth"] = \
        { "icon": "earth.svg",
          "src" : "/static/threeJS/globe/index.html",
        }
    iframeModelClasses["Box"] = \
        { "icon": "earth.svg",
          "src" : "/static/threeJS/box/box.html",
        }

    transaction.commit()

    #appRoot['coalPowerStation'] = ModelClass()
    #coal = Coal("coal", appRoot)
    #appRoot['coal'] = coal
    
    return zodb_root['app_root']
    

