from persistent.mapping import PersistentMapping
from persistent.list    import PersistentList

import re, logging
import transaction

log = logging.getLogger(__name__)

class MyModel(PersistentMapping):
  __parent__ = __name__ = None

class OtherModel(MyModel):
  pass

class ModelClass(MyModel):
  fieldContext      = PersistentMapping()
  initialiseSource  = ""
  
  def __init__(self, name):
    name = ""
    self.initialiseModelClass()
    transaction.commit()
  def initialiseModelClass():
    pass

  def createInstance(self):
    newInstance = ModelInstance()
    newInstance.setParentModelClass(self)
    newInstance.fieldContext = self.fieldContext.copy()
    transaction.commit()
    return newInstance
  def initialiseInstanceContext(self):
    pass
    """newInstanceContext = self.fieldContext
    eval(self.initialiseSource)
    transaction.commit()
    return toReturn
    """
  
  
  def addSimpleField(self, name, defaultValue):
    self.fieldContext[name] = defaultValue
    transaction.commit()
  def addModelLink(self, localName, localFieldName, remoteName, subModelModule, subModelClassName, subModel, localLinkEquation, remoteLinkEquation):
    if not subModelModule:
      newSubModel = subModel
    elif not subModelClassName:
      newSubModel = subModelModule()
    else:
      newSubModel = getattr(subModelModule, subModelClassName)
    
    subModelLink = SubModelLink()
    subModelLink.setParentModel(self, localName)
    subModelLink.setChildModel(newSubModel, remoteName)
    
    subModelLink.setParentToChildEquation(localLinkEquation)
    subModelLink.setChildToParentEquation(remoteLinkEquation)
    
    self.fieldContext[localName] = subModelLink
    transaction.commit()
  def addFieldProcessor(fieldToProcess, evalString):
    self.fieldContext["%s.process" % fieldToProcess] = evalString
    transaction.commit()

class SimpleField(MyModel):
  def __init__(self, name, parent, fieldType, defaultValue, rangeBottom, rangeTop, rangeStep, selectableValues):
    self.name                         = name
    self.parent                       = parent
    self.parent.fieldContext['name']  = self
    self.fieldType                    = fieldType
    self.defaultValue                 = defaultValue
    
    self.rangeBottom                  = rangeBottom
    self.rangeTop                     = rangeTop
    self.rangeStep                    = rangeStep
    
    self.selectableValues             = selectableValues
    
    self.currentValue                 = defaultValue
    
    transaction.commit()

class CircularFieldDependencyException(Exception):
  def __init__(self, message):
    self.message = message
class FieldValueProcessor(MyModel):
  dependentFieldRegex       = re.compile("\!\!field\_(?P<fieldName>.*?)\!\!")

  dependsOnInput            = False
  inputProcessors           = PersistentMapping()
  
  def __init__(self, targetField, evalString, parentModel):
    self.targetField          = targetField
    self.evalString           = evalString
    self.currentlyProcessing  = False
    self.parentModel          = parentModel
    
    transaction.commit()
  def getCurrentInputField():
    return self.inputProcessors[self.parentModel.currentInputField]
  def chooseEvalString():
    inputField = self.parentModel.currentInputField
    if inputField in self.inputProcessors:
      evalString = self.inputProcessors[inputField]
    else:
      evalString = self.inputProcessors["default"]
    return evalString
  def process(self):
    if self.currentlyProcessing == True:
      log.info("Cannot process field %s, alreading being processed" % self.targetField.name)
      raise CircularFieldDependencyException("already processed %s" % self.targetField.name)
    
    evalString = self.chooseEvalString()
    
    dependentFields = FieldValueProcessor.dependentFieldRegex.findAll(self.evalString)
    
    for dependentField in dependentFields:
      processingField = self.parentModel[dependentField]
      fieldProcessor  = processingField['processor']
      if fieldProcessor:
        fieldValue = fieldProcessor.process()
        evalString.replace("!!field_%s!!" % dependentField, fieldValue)
    
    currentFieldValue = self.targetField.currentValue
    
    toReturn = None
    eval(evalString)
    return toReturn
    
class SubModelLink(MyModel):
  def __init__(self):
    parentModel            = ""
    childModel             = ""
    parentToChildEquation  = ""
    childToParentEquation  = ""
    transaction.commit()
  def setParentModel(self, parentModel, localName):
    self.parentModel      = parentModel
    self.parentFieldName  = localName
    transaction.commit()
  def setChildModel(self, childModel, remoteName):
    self.childModel       = childModel
    self.childFieldName   = remoteName
    transaction.commit()
  def setChildToParentEquation(self, equation):
    self.childToParentEquation = equation
    transaction.commit()
  def setParentToChildEquation(self, equation):
    self.parentToChildEquation = equation
    transaction.commit()  

class ModelInstance(MyModel):
  def __init__(self, modelClass):
    self.fieldContext       = modelClass.fieldContext.copy()
    self.currentOutputField = False
    self.currentInputField  = False
    transaction.commit()
  
    
  def process():
    #PU_debug_tools::PU_DEBUG_METHOD($this, __METHOD__, func_get_args());
  
    writableField = self.fieldContext[self.currentOutputField]
    
  
    """
    
    $node = &$this->node;
    if (!$faf_field_name)
    { $faf_field_name = $node->field_output_field['und'][0]['value']."_faf";
    }
    
    $this->debug[] = "process faf: $faf_field_name";
    $this->debug[] = $node;
    $faf_field = field_info_instance("node", $faf_field_name, $node->type);
    $faf_field_writeable = &$node->$faf_field_name;
    $this->debug[] = $faf_field;
    $this->debug[] = $faf_field_writeable;

    if (array_key_exists("processing_faf", $faf_field_writeable))
    { dpm("FIELD: $faf_field_name is currently processing. Circular reference detected");
      return False;
    }
    $faf_field_writeable['processing_faf'] = True;
    
    $toEval = $faf_field['settings']['calculation_php'];
    
    //INPUT DEPENDENT CALCULATION//
    { $current_input_field_name     = $node->field_input_field['und'][0]['value'];
      $current_input_field_name_faf = $current_input_field_name."_faf";
      
      $toEval_depInput  = $faf_field['settings']['calculation_php_'.$current_input_field_name_faf];
      
      $input_data_field = &$node->$current_input_field_name;
      $input_value      = $input_data_field['und'][0]['value'];
      
      $this->debug[] = "input_value: $input_value";
    }
    $toEval = str_replace("!!depends_on_input!!", "\n\n".$toEval_depInput."\n\n", $toEval);

    if ($toEval)
    { $dependent_fields = find_double_bang_fields($toEval);
      $debug[] = $dependent_fields;
      
      $dep_field_dict = array();
      foreach ($dependent_fields as $_ => $code_part)
      { if (substr($code_part, 0, 2) == "!!")
        { $dep_field_name = substr($code_part, 2, strlen($code_part) -4);
          $dep_field_dict[$dep_field_name] = $code_part;
        }
      }
      foreach($dep_field_dict as $dep_field_name => $code_part)
      { $debug[] = "Check Dependency: $dep_field_name";
        
        $dep_field_name_faf = $dep_field_name."_faf";
        if (property_exists($node, $dep_field_name_faf))
        { $debug[] = "Processing Dependency: $dep_field_name_faf";
          if (! $this->process_faf($dep_field_name_faf))
          { return True;
          }
        }
        $this->debug[] = array($code_part, $dep_field_name, $toEval);
        $toEval = 
            str_replace($code_part, 
                        "((double) \$node->".$dep_field_name."['und'][0]['value'])", 
                        $toEval
                       );
      }

      $this->debug[] = $toEval;
      eval($toEval);

      $target_field_name = $faf_field['settings']['annotated_field'];
      $target_field = &$node->$target_field_name;
      $target_field['und'][0]['value'] = $output_value;
      
      $this->debug[] = "output_value";
      $this->debug[] = $output_value;
    }
    $faf_field_writeable['processed_faf'] = True;
    return True;"""

class coal(ModelClass):
    def initialiseModel(self):
      self.fieldContext['mass']               = 100
  

class CoalPowerStation(ModelClass):
  def initialiseModelClass(self):
    priceField = SimpleField("price", self, "slider", 50000000, 1, 100000000000, 1, None)
    
    self.fieldContext['price']                = 1000000
    self.fieldContext['energy']               = 500000000
    self.fieldContext['effeciency%']          = 70
    self.fieldContext['inputWatts']           = 71428571.4286
   
    self.addModelLink("inputWatts_subModel", "inputWatts", "energy", "", "coal", "", "localLinkEquation", "remoteLinkEquation")

class coal(ModelClass):
  def initialiseModelClass(self):
    self.fieldContext['mass']                 = 100
    self.fieldContext['volume']               = 100
    self.fieldContext['energy']               = 100

class windMill(ModelClass):
  pass

class lightbulb(ModelClass):
  pass


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = MyModel()
        zodb_root['app_root'] = app_root
        app_root['otherModel'] = OtherModel()

        transaction.commit()
        
    coalPowerStation = CoalPowerStation("coalPowerStation")
    zodb_root['app_root']['coalPowerStation'] = coalPowerStation
    
    print coalPowerStation.fieldContext['price']      
    
    appRoot = zodb_root['app_root']
    appRoot['coalPowerStation'] = ModelClass()
    
    return zodb_root['app_root']
    
    
    
