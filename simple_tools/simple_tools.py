# -*- coding: utf-8 -*-
"""***************************************************************************
    copyright            : Philippe Desboeufs
    begin                : 2020-09-12
   ***************************************************************************
   *   This program is free software; you can redistribute it and/or modify  *
   *   it under the terms of the GNU General Public License as published by  *
   *   the Free Software Foundation; either version 2 of the License, or     *
   *   (at your option) any later version.                                   *
   ************************************************************************"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.core import *
from qgis.gui import *
import os
from qgis.utils import iface, pluginMetadata
#from qgis import processing
#from .provider import Provider
#from qgis.core import QgsProcessingProvider
#from .example_processing_algorithm import ExampleProcessingAlgorithm
from .categorized_from_csv import csvToCategorized
#from .test_algorithm import pluginAlgorithm

cePlugin= os.path.basename( os.path.dirname(__file__) )
version= pluginMetadata(cePlugin,'version') ## Pour les changements, voir le fichier metadata.txt


def showHelp( parent=None ):  ### Help window
  if not parent:  parent= iface.mainWindow()
  form= QDialog(parent)
  
  overrideLocale= QSettings().value("locale/overrideFlag", False, type=bool)
  if not overrideLocale:  locale= QLocale.system().name()
  else:
    locale= QSettings().value("locale/userLocale", "")
    if locale.__class__.__name__=='QVariant': locale= 'en_EN'
  
  title= pluginMetadata( cePlugin, 'name[%s]'% locale.split("_")[0] )
  if title=='' or title=='__error__':
    title= pluginMetadata( cePlugin, 'name')
  form.setWindowTitle( title )
  
  form.move( parent.pos().x()+50, parent.pos().y()+50 )
  #form.resize(800,600)
  web= QWebView(form)
  Layout_1= QGridLayout(form)
  Layout_1.setContentsMargins( 0, 0, 0, 0 )
  Layout_1.addWidget(web, 0, 0, 1, 1)
  path = os.path.abspath(os.path.dirname(__file__))
  ficAide= path + os.sep +"help_"+ locale.split("_")[0] +'.html' #help_fr.html
  if not QFileInfo(ficAide).exists(): # si pas de help_fr.qm, on cherche help_fr_FR.qm
    ficAide= path + os.sep +"help_"+ locale +'.html'
  if not QFileInfo(ficAide).exists():
    ficAide= path + os.sep +'help.html'
  web.setUrl( QUrl.fromLocalFile(ficAide) )
  #if modal : form.exec_() # pour le bouton Aide dans la fenetreParam
  #else : 
  form.show()



class plugin:
  def __init__(self, iface):
    self.provider= None # Processing
    self.csvEditor= None # Dialog
    self.params= "PluginStylingHelper/" # User Param in QSettings

  def tr(self, txt, disambiguation=None):
    return QCoreApplication.translate('plugin', txt, disambiguation)

  def initGui(self):
    pluginPath= os.path.abspath(os.path.dirname(__file__))
    # Translator :
    overrideLocale= QSettings().value("locale/overrideFlag", False, type=bool)
    if not overrideLocale:  localeFullName= QLocale.system().name()
    else:
      localeFullName= QSettings().value("locale/userLocale", "")
      if localeFullName.__class__.__name__=='QVariant': localeFullName= 'en_EN'
    localePath= pluginPath + os.sep +"i18n"+ os.sep +"translation_" + localeFullName[0:2] + ".qm"
    if not QFileInfo(localePath).exists(): # If no corrector_ll.qm, looking for corrector_ll_CC.qm
      localePath = pluginPath + os.sep +"i18n"+ os.sep +"translation_" + localeFullName + ".qm"
    if QFileInfo(localePath).exists():
      self.translator = QTranslator()
      self.translator.load(localePath)
      QCoreApplication.installTranslator(self.translator)
    
    icons= pluginPath + os.sep + "icons" + os.sep
    self.pluginMenu= iface.pluginMenu().addMenu( QIcon(icons+'tools.png'), self.tr("Simple tools") )
    
    self.aEditor= QAction( QIcon( icons +'edit.png'),
      self.tr("Inspect the first rows of a big CSV or text file"), iface.mainWindow() )
    self.aEditor.triggered.connect( self.showCsvEditor )
    self.pluginMenu.addAction( self.aEditor )
    iface.addToolBarIcon( self.aEditor )
    
    self.actionAide= QAction( self.tr('Help (plugin version %s)')% version, iface.mainWindow() )
    self.actionAide.triggered.connect( showHelp )
    self.pluginMenu.addAction( self.actionAide )
    
    self.initProcessing()


  def unload(self):
    self.pluginMenu.parentWidget().removeAction(self.pluginMenu.menuAction()) # Remove from Extension menu
    iface.removeToolBarIcon(self.aEditor)
    """if hasattr(self, 'action'):
      iface.addLayerMenu().removeAction(self.action)
      iface.layerToolBar().removeAction(self.action)
      #iface.removeVectorToolBarIcon(self.action)
      #self.iface.removeToolBarIcon(self.action)  #self.iface.layerToolBar().removeAction(self.action)  """
    try: QgsApplication.processingRegistry().removeProvider(self.provider)
    except: pass

  def initProcessing(self):
    self.provider= Provider( 'styling_helper', self.tr('Styling helper') )
    QgsApplication.processingRegistry().addProvider(self.provider)

  def showCsvEditor(self):
    if not self.csvEditor:
      from .open_BIG_CSV import bigFileEditor
      self.csvEditor= bigFileEditor()
    self.csvEditor.show()



class Provider(QgsProcessingProvider):
  def __init__(self, procId, name):
    QgsProcessingProvider.__init__(self)
    self.procId= procId
    self.procName= name
  
  def loadAlgorithms(self, *args, **kwargs):
    self.addAlgorithm( csvToCategorized() )
    #self.addAlgorithm( pluginAlgorithm() )

  def id(self, *args, **kwargs): ## The ID of the provider, used for identifying it
    """This string should be a unique, short, character only string,
    eg "qgis" or "gdal". This string should not be localised."""
    return self.procId

  def name(self, *args, **kwargs):
    """The human friendly name of your plugin in Processing.
    This string should be as short as possible (e.g. "Lastools", not
    "Lastools version 1.0.1 64-bit") and localised."""
    return self.procName

  def icon(self):
    """Should return a QIcon which is used for your provider inside the Processing toolbox."""
    return QgsProcessingProvider.icon(self)

