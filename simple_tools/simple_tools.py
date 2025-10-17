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
		self.pluginSettings = "PluginSimpleTools/" # Section dans QGIS.ini pour les paramètres de ce plugin
		self.paramAjust = 'ajusterAttribTables' # Nom du paramètre dans QGIS.ini
		self.params = "PluginStylingHelper/" # User Param in QSettings
		self.modifAttribTables = None

	def tr(self, txt, disambiguation=None):
		return QCoreApplication.translate('plugin', txt, disambiguation)

	def initGui(self):
		pluginPath = os.path.abspath(os.path.dirname(__file__))
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
		
		icons = pluginPath + os.sep + "icons" + os.sep
		win = iface.mainWindow()
		self.pluginMenu = iface.pluginMenu().addMenu( QIcon(icons+'tools.png'), self.tr("Simple tools") )
		self.pluginBar = []
		self.attribBar = []
		
		self.jConv = QAction( QIcon( icons +'json.png'), self.tr("Open JSON or convert it to CSV"), win )
		self.jConv.triggered.connect(self.showJsonConv)
		self.pluginMenu.addAction( self.jConv )    #iface.addToolBarIcon(self.jConv)
		self.pluginBar.append(self.jConv)
		
		self.actionEditor = QAction( QIcon( icons +'edit.png'),
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
		
		self.CategorizedStyle = QAction( QIcon(icons+'csv2style.png'),
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
		
		self.aRedim = QAction( QIcon( icons +'redim.png'),
			"Options pour ajuster lignes et colonnes dans les tables attributaires", win )
		self.aRedim.triggered.connect( self.Redim )
		self.pluginMenu.addAction( self.aRedim )
		
		self.actionAide = QAction( QIcon( icons +'help.png'),
			self.tr('Help (plugin version %s)')% PluginVersion, win )
		self.actionAide.triggered.connect( showHelp )
		self.pluginMenu.addAction( self.actionAide )
	 
		self.initProcessing()
		
		self.toolBar = iface.addToolBar( self.tr("Simple tools") )
		for action in self.pluginBar:  self.toolBar.addAction(action) #iface.addToolBarIcon(action)
		for action in self.attribBar:  iface.attributesToolBar().addAction(action)
		# Ajouter 3 boutons dans chaque table attributaire : Largeur auto, Hauteur auto et Réduire colonnes :
		S = QgsSettings()
		S.beginGroup(self.pluginSettings)
		if S.value(self.paramAjust,'')!='no':  self.modifAttribTables = AddAttributeTableAction()



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
		if self.modifAttribTables:
			iface.mainWindow().removeEventFilter(self.modifAttribTables)
			del self.modifAttribTables


	def initProcessing(self):
		self.provider = processProvider('styling_helper', self.tr('Styling helper') )
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


	def Redim(self): ## Activer/désactiver les outils de largeur de colonnes et hauteur de lignes
		if self.modifAttribTables:  actuel = 0
		else:  actuel = 1
		rep, ok = QInputDialog.getItem( iface.mainWindow(), "Options pour les tables attributaires",
			"Ajouter dans chaque vue attributaire 3 boutons pour :\n"
			+"  -- ajuster la hauteur des lignes à leur contenu\n"
			+"  -- ajuster la largeur des colonnes à leur contenu\n"
			+"  -- choisir et appliquer une largeur unique à toutes les colonnes",
			['OUI','NON'], actuel, False )
		if not ok:  return
		S = QgsSettings()
		S.beginGroup(self.pluginSettings) 
		if rep=='NON' and self.modifAttribTables:
			iface.mainWindow().removeEventFilter(self.modifAttribTables)
			del self.modifAttribTables
			self.modifAttribTables = None
			S.setValue(self.paramAjust, 'no')
		elif rep=='OUI' and not self.modifAttribTables:
			self.modifAttribTables = AddAttributeTableAction()
			S.setValue(self.paramAjust, 'yes')



### Ajoute 3 boutons dans chaque table attributaire : Largeur auto, Hauteur auto et Réduire colonnes
class AddAttributeTableAction(QObject):
	def __init__(self):
		super().__init__()
		self.mainWin = iface.mainWindow()
		self.mainWin.installEventFilter(self)
		self.largeur = 60 # largeur par defaut des colonnes

	def eventFilter(self, obj, event):
		if event.type() == QEvent.ChildAdded and obj == self.mainWin:
				self.attribute_dialog_opened()
		return super(AddAttributeTableAction, self).eventFilter(obj, event)

	def attribute_dialog_opened(self):
		tbl_dlgs = [w for w in self.mainWin.children() if 'QgsAttributeTableDialog' in w.objectName()]
		if not tbl_dlgs:  return
		table_dialog = tbl_dlgs[0]
		toolbar = [c for c in table_dialog.children() if c.objectName() == 'mToolbar'][0]
		# check if action has already been added to toolbar
		already_exists = [a for a in toolbar.actions() if a.objectName() == 'hauteurAuto']
		if already_exists:  return
		icons = os.path.abspath(os.path.dirname(__file__)) + os.sep + "icons" + os.sep
		
		largeurAuto = QAction( QIcon( icons +'redim_col.png'),
			"Ajuster la largeur des colonnes pour s'adapter automatiquement à leur contenu", table_dialog )
		largeurAuto.setObjectName('largeurAuto')
		toolbar.addAction(largeurAuto)
		largeurAuto.triggered.connect(self.largeurAuto)
		
		reduireCol = QAction( QIcon( icons +'redim_largeur.png'),
			"choisir et appliquer une largeur unique à toutes les colonnes", table_dialog )
		reduireCol.setObjectName('reduireCol')
		toolbar.addAction(reduireCol)
		reduireCol.triggered.connect(self.reduireCol)
		
		hauteurAuto = QAction( QIcon( icons +'redim.png'),
			"Ajuster la hauteur des lignes pour s'adapter automatiquement à leur contenu", table_dialog )
		hauteurAuto.setObjectName('hauteurAuto')
		#hauteurAuto.setToolTip("redimensionner la hauteur des lignes pour s'adapter automatiquement au contenu de leurs cellules")
		toolbar.addAction(hauteurAuto)
		hauteurAuto.triggered.connect(self.hauteurAuto)

	def hauteurAuto(self):
		'''pour redimensionner la hauteur des lignes pour s'adapter automatiquement au contenu de leurs cellules'''
		atb = QgsApplication.activeWindow()
		tv = atb.findChild(QTableView,'mTableView')
		tv.resizeRowsToContents()

	def largeurAuto(self):
		atb = QgsApplication.activeWindow()
		tv = atb.findChild(QTableView,'mTableView')
		tv.resizeColumnsToContents()

	def reduireCol(self):
		atb = QgsApplication.activeWindow()
		tv = atb.findChild(QTableView,'mTableView')
		largeur, ok = QInputDialog.getInt( atb, "Entrer la largeur des colonnes",
				"Largeur en pixels :", self.largeur, 5, 2000 )
		if not ok:  return
		self.largeur = largeur
		for i in range( tv.model().columnCount() ):
			tv.setColumnWidth( i, largeur )



## Pour la définition d'un new traitement dans Processing
class processProvider(QgsProcessingProvider):
	def __init__(self, procId, name):
		QgsProcessingProvider.__init__(self)
		self.procId = procId
		self.procName = name

	def loadAlgorithms(self, *args, **kwargs):
		#self.addAlgorithm( pluginAlgorithm() )
		self.addAlgorithm( csvToCategorized() )

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


