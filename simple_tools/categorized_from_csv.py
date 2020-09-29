# -*- coding: utf-8 -*-
"""**************************************************************************
  copyright : Philippe Desboeufs
  begin     : 2020-09-12
  Based on the code from igeofr :
    https://github.com/igeofr/qgis2/blob/master/scripts/CSV_RGB_or_HEX_to_categorized_style.py
  ***************************************************************************
  *   This program is free software; you can redistribute it and/or modify  *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  ************************************************************************"""
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import csv, codecs, os

class csvToCategorized(QgsProcessingAlgorithm):
  INPUT = 'INPUT'
  Value_field= 'Value_field'
  CSV_file= 'CSV_file'
  CSV_Delim= 'CSV_Delim'
  CSV_Encoding= 'CSV_Encoding'
  Column_value= 'Column_value'
  Column_label= 'Column_label'
  Column_color= 'Column_color'
  Opacity= 'Opacity'
  Outline= 'Outline'
  Outline_width= 'Outline_width'
  Save_layer_style_as_default= 'Save_layer_style_as_default'

  def tr(self, string):
    return QCoreApplication.translate('csvToCategorized', string)

  def createInstance(self):
    return csvToCategorized()

  def name(self):
    return 'Categorized style from CSV'

  def displayName(self):
    return self.tr('Categorized style from CSV [code,label,color]')

  def shortHelpString(self):
    return self.tr("Apply a categorized style to a vector layer from a CSV file with values, labels and colors.<br><br>Color values:<br>a name: green<br>or RGB: 0,255,34<br>or hexa: #00FF22")

  def group(self): ## Returns the name of the group this algorithm belongs to
    return self.tr(self.groupId())

  def groupId(self): ## Returns the unique ID of the group this algorithm belongs to
    return '' # 'Vector'


  def initAlgorithm(self, config):
    """ Here we define the inputs and output of the algorithm, along with some other properties."""
    # We add the input vector features source. It can have any kind of geometry.QgsProcessingParameterFeatureSource
    self.addParameter(
     QgsProcessingParameterVectorLayer(self.INPUT,self.tr('Target layer'),[QgsProcessing.TypeVectorAnyGeometry]) )
    
    self.addParameter(
      QgsProcessingParameterField(self.Value_field, self.tr('Value field for the categories'), '', self.INPUT) )
    
    self.addParameter(
     QgsProcessingParameterFile( self.CSV_file,
      self.tr('CSV file with columns: field values, labels, colors'), extension='csv' ) )
    self.addParameter(
      QgsProcessingParameterString(self.CSV_Delim, self.tr('CSV Delimiter'), ';') )
    self.addParameter(
      QgsProcessingParameterString(self.CSV_Encoding, self.tr('CSV Encoding'), 'utf-8') )
    
    self.addParameter(
      QgsProcessingParameterNumber(self.Column_value, self.tr('Column number with the values (categories)'), defaultValue='0', minValue=0) )
    self.addParameter(
      QgsProcessingParameterNumber(self.Column_label, self.tr('Column number with the labels'), defaultValue='1', minValue=0) )
    self.addParameter(
     QgsProcessingParameterNumber(self.Column_color,
      self.tr('Column number with the colors'),
       defaultValue='2', minValue=0) )
    
    self.addParameter(
     QgsProcessingParameterNumber(self.Opacity, self.tr('Opacity: 0 (fully transparent) to 1 (fully opaque)'),
      QgsProcessingParameterNumber.Double, defaultValue='0.7', minValue=0, maxValue=1) )
    
    self.addParameter(
      QgsProcessingParameterBoolean(self.Outline, self.tr('Outline'), defaultValue=True) )
    self.addParameter(
     QgsProcessingParameterNumber(self.Outline_width, self.tr('Outline width'),
      QgsProcessingParameterNumber.Double, defaultValue='0.26', minValue=0) )
    
    self.addParameter(
      QgsProcessingParameterBoolean(self.Save_layer_style_as_default, self.tr('Save layer style as default') ) )



  def processAlgorithm(self, parameters, context, feedback):
    #layer= self.parameterAsSource(parameters, self.INPUT, context)
    layer= self.parameterAsLayer(parameters, self.INPUT, context)
    Value_field= self.parameterAsString( parameters, self.Value_field, context )
    CSV_file= self.parameterAsString( parameters, self.CSV_file, context )
    CSV_Delim= self.parameterAsString( parameters, self.CSV_Delim, context )
    CSV_Encoding= self.parameterAsString( parameters, self.CSV_Encoding, context )
    Column_value= self.parameterAsInt( parameters, self.Column_value, context )
    Column_label= self.parameterAsInt( parameters, self.Column_label, context )
    Column_color= self.parameterAsInt( parameters, self.Column_color, context )
    Opacity= self.parameterAsDouble( parameters, self.Opacity, context )
    Outline= self.parameterAsBoolean( parameters, self.Outline, context )
    Outline_width= self.parameterAsDouble( parameters, self.Outline_width, context )
    Save_layer_style_as_default= self.parameterAsBoolean( parameters, self.Save_layer_style_as_default, context )
    
    """ Verif inutiles :
    fileName, fileExtension = os.path.splitext(CSV_file)
    if fileExtension.lower() != '.csv':
      raise QgsProcessingException( self.tr("Warning: CSV is required!") ) #self.invalidSourceError(parameters, self.INPUT))
      #feedback.reportError( self.tr("Warning: CSV is required!"), True )
      #return {}
    if Column_value<0 or Column_label<0 or Column_color<0 or Opacity<=0 or Opacity>=1 or Outline_width<0:
      raise QgsProcessingException( self.tr("Warning: invalid parameter") ) #"""
    
    if layer.geometryType()==QgsWkbTypes.PolygonGeometry: layerType= 'Polygon'
    elif layer.geometryType()==QgsWkbTypes.LineGeometry   : layerType= 'LineString'
    elif layer.geometryType()==QgsWkbTypes.PointGeometry  : layerType= 'Point'
    else: raise QgsProcessingException( self.tr("Layer type not supported for styling.") )
    
    if Outline == False :  b_outline = 'no' # For polygons
    else :  b_outline = 'yes'
    v_width = str(Outline_width) # Border width
    feedback.setProgress(10) # Update the progress bar

    feedback.setProgressText( self.tr("Reading the CSV file:") )
    # Opening the csv
    tab = [] # un tableau qui va stocker les lignes et colonnes choisies du CSV  
    with open(CSV_file, encoding=CSV_Encoding, errors='ignore') as f:
      read_csv= csv.reader(f, delimiter=CSV_Delim)
      fieldNames= read_csv.__next__()  # Permet de passer l'entete du CSV
      nbCol= len(fieldNames)
      if nbCol<3 or nbCol<Column_value+1 or nbCol<Column_label+1 or nbCol<Column_color+1:
        feedback.reportError( self.tr("Header of the CSV file: ") +str(fieldNames), True )
        raise QgsProcessingException( self.tr("Error: the number of columns of the CSV file is lower than expected.\n Please check these parameters: the csv delimiter and the number of each column.") )
        
      for row in read_csv: # Permet de definir les colonnes value, label, color
        try: col_select= row[Column_value], row[Column_label], row[Column_color]
        except Exception as e:
          raise QgsProcessingException( self.tr("Error on a column number") +"\n"+ str(e.args) )
        # Insere chaque ligne du CSV dans le tableau
        tab.append(col_select)
    
    #Permet la suppression des doublons
    Lt= list(set(tab))
    Lt.sort()
    feedback.setProgress(50) # Update the progress bar
    
    categories = []
    for value, label, color in Lt :
      tab_list = value +' - '+label+' - '+color
      feedback.setProgressText(u'Category : %s' % tab_list)
      
      if layerType == 'Polygon':
        # Source : http://gis.stackexchange.com/questions/53121/how-change-border-line-to-no-pen-with-python-console
        symbol= QgsFillSymbol.createSimple( {'style':'solid','outline_style':b_outline,'outline_width':v_width,'color':color} )
        symbol.setOpacity(Opacity)
        category= QgsRendererCategory(value, symbol, label)
        categories.append(category)
      
      elif layerType == 'LineString':
        symbol = QgsLineSymbol.createSimple( {'style':'solid','line_width':v_width,'color': color} )
        symbol.setOpacity(Opacity)
        category = QgsRendererCategory(value, symbol, label)
        categories.append(category)
      
      else: # Point
        symbol = QgsMarkerSymbol.createSimple( {'style':'solid','outline_style':'no','outline_width':v_width,'color': color} )
        symbol.setOpacity(Opacity)
        category = QgsRendererCategory(value, symbol, label)
        categories.append(category)
    
    # Permet de creer le rendu et de l'affecter a la couche sur un champ defini
    expression= Value_field # Nom du champ sur lequel doit s'appliquer la symbologie
    renderer= QgsCategorizedSymbolRenderer(expression, categories)
    layer.setRenderer(renderer)
    
    # Creation des fichiers de style
    if Save_layer_style_as_default :
      layer.saveDefaultStyle() 
      feedback.setProgressText( self.tr("Saving as the default style (creates a QML)") )
    
    layer.triggerRepaint()
    
    feedback.setProgress(100)
    return {}
    
    ### TEST :
    total = 100.0 / layer.featureCount() if layer.featureCount() else 0
    features= layer.getFeatures()
    for current, feature in enumerate(features):
      if feedback.isCanceled():  break  # Stop the algorithm if cancel button has been clicked
      # Add a feature in the sink
      #sink.addFeature(feature, QgsFeatureSink.FastInsert)
      feedback.setProgress(int(current * total)) # Update the progress bar



