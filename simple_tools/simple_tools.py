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
PluginVersion= pluginMetadata(cePlugin,'version') ## Pour les changements, voir le fichier metadata.txt


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
		self.provider = None # Processing
		self.csvEditor = None # Dialog
		self.jsonConv = None # Dialog
		self.dallesRaster = None # Dialog
		self.extractionGPKG = None # Dialog
		self.verifStandard = None # Panneau
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
		win = iface.mainWindow()
		self.pluginMenu= iface.pluginMenu().addMenu( QIcon(icons+'tools.png'), self.tr("Simple tools") )
		self.pluginBar = []
		self.attribBar = []
		
		self.jConv= QAction( QIcon( icons +'json.png'), self.tr("Open JSON or convert it to CSV"), win )
		self.jConv.triggered.connect(self.showJsonConv)
		self.pluginMenu.addAction( self.jConv )    #iface.addToolBarIcon(self.jConv)
		self.pluginBar.append(self.jConv)
		
		self.actionEditor= QAction( QIcon( icons +'edit.png'),
			self.tr("Inspect the first rows of a big CSV or text file"), win )
		self.actionEditor.triggered.connect( self.showCsvEditor )
		self.pluginMenu.addAction( self.actionEditor ) #iface.addToolBarIcon( self.actionEditor )
		self.pluginBar.append(self.actionEditor)
		
		aExtraireGPKG = QAction( QIcon( icons +'gpkg_extraction.png'),
			self.tr("Multi-layer GPKG to multiple GPKG files"), win )
		aExtraireGPKG.triggered.connect(self.showExtractionGPKG)
		self.pluginMenu.addAction( aExtraireGPKG )
		self.pluginBar.append(aExtraireGPKG)
		
		aVerifStandard = QAction( QIcon( icons +'verif_standard.png'),
			self.tr("Check if some layers abide by a standard (template layers)"), win )
		aVerifStandard.triggered.connect(self.showVerifStandard)
		self.pluginMenu.addAction( aVerifStandard )
		self.pluginBar.append(aVerifStandard)
		
		self.CategorizedStyle= QAction( QIcon(icons+'csv2style.png'),
			self.tr('Categorized style from CSV'), win )
		self.CategorizedStyle.triggered.connect( showHelp )
		self.pluginMenu.addAction( self.CategorizedStyle )
		 
		self.tabSelAction = QAction( QIcon( icons +'table_selec.png'),
			self.tr("Open Attributes Table FILTERED on SELECTED features"), win )
		self.tabSelAction.triggered.connect(self.showTabSel)
		self.pluginMenu.addAction( self.tabSelAction )
		self.attribBar.append(self.tabSelAction)
		
		self.aDalles = QAction( QIcon( icons +'dalles.png'),
			self.tr("Analyze raster tiles in a folder and create a grid"), win )
		self.aDalles.triggered.connect(self.showDallesRaster)
		self.pluginMenu.addAction( self.aDalles )
		#self.pluginBar.append(self.aDalles)
		
		self.actionAide= QAction( QIcon( icons +'help.png'),
			self.tr('Help (plugin version %s)')% PluginVersion, win )
		self.actionAide.triggered.connect( showHelp )
		self.pluginMenu.addAction( self.actionAide )
	 
		self.initProcessing()
		
		self.toolBar = iface.addToolBar( self.tr("Simple tools") )
		for action in self.pluginBar:  self.toolBar.addAction(action) #iface.addToolBarIcon(action)
		for action in self.attribBar:  iface.attributesToolBar().addAction(action)


	def unload(self):
		self.pluginMenu.parentWidget().removeAction(self.pluginMenu.menuAction()) # Remove from Extension menu
		parent = self.toolBar.parentWidget().removeToolBar(self.toolBar)
		#for action in self.pluginBar:  iface.removeToolBarIcon(action)
		for action in self.attribBar:  iface.attributesToolBar().removeAction(action)
		#try:
		#  if hasattr(self,'jConv'):  iface.removeToolBarIcon(self.jConv)
		#except: pass
		try: QgsApplication.processingRegistry().removeProvider(self.provider)
		except: pass
		try: # Cacher le panneau verifStandard
			self.verifStandard.hide()
			iface.removeDockWidget(self.verifStandard)
			self.verifStandard.deleteLater()
		except: pass
		if self.jsonConv:  self.jsonConv.hide()


	def initProcessing(self):
		self.provider= Provider( 'styling_helper', self.tr('Styling helper') )
		QgsApplication.processingRegistry().addProvider(self.provider)


	def showCsvEditor(self):
		if not self.csvEditor:
			from .open_BIG_CSV import bigFileEditor
			self.csvEditor= bigFileEditor()
		self.csvEditor.show()


	def showJsonConv(self):
		if not self.jsonConv:
			from .json2csv import json2csv
			self.jsonConv = json2csv()
		self.jsonConv.show()


	def showDallesRaster(self):
		if not self.dallesRaster:
			from .grille_dalles_raster import analyseDalles
			self.dallesRaster = analyseDalles()
		self.dallesRaster.show()


	def showTabSel(self):
		layer = iface.activeLayer()
		if layer.type()!=0:  return # If NOT vector layer
		if layer.selectedFeatureCount() == 0:
			iface.showAttributeTable(layer)
			return
		
		selected_fid = layer.selectedFeatureIds() #[]
		#selection = layer.selectedFeatures()
		#for feature in selection:
		#  selected_fid.append(feature.id())
		expression = '$id in ({})'.format(','.join(map(str,selected_fid)))
		print('selection expression =', expression)
		iface.showAttributeTable( layer, expression )


	def showExtractionGPKG(self):
		if not self.extractionGPKG:
			from .GPKGmulti_vers_plusieursGPKG import extractionGPKG
			self.extractionGPKG = extractionGPKG()
		self.extractionGPKG.show()


	def showVerifStandard(self):
		if self.verifStandard:
			self.verifStandard.show()
			return
		from .verif_standard import panneau
		self.verifStandard = QDockWidget("Contrôler que des couches respectent un standard", iface.mainWindow() )
		self.verifStandard.setWidget( panneau( self.verifStandard, "verif_standard", False ) )
		self.verifStandard.setObjectName("verif_standard")
		self.verifStandard.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
		iface.addDockWidget( Qt.RightDockWidgetArea, self.verifStandard )
		self.verifStandard.show()




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
		This string should be as short as possible (e.g. "Lastools" and localised."""
		return self.procName

	def icon(self):
		"""Should return a QIcon which is used for your provider inside the Processing toolbox."""
		return QgsProcessingProvider.icon(self)

