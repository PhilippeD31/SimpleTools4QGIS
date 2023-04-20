import time, os, os.path, sys
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.Qsci import QsciScintilla
from qgis.utils import iface
from qgis.gui import * #QgsFileWidget, QgsMessageBar
from qgis.core import * #Qgis, QgsApplication


chDoublon = 'doublon' # Champ : 1 indique une dalle avec des doublons (même emprise)
chBordure = 'bordure' # Champ : 1 indique une dalle en bordure de zone
chQualite = 'qualite' # Champ : 1 indique une bonne dalle (claire) à 5 qui indique une dalle très sombre
chNuages  = 'nuages' 	# Champ : 1 indique une dalle avec des nuages
chInutile = 'inutile'	# Champ : 1 indique une dalle inutile car en doublon et mal classées en : bordure, nuages et qualite


class analyseDalles(QDialog):
	def __init__(self, parent=None):
		self.path = os.path.abspath(os.path.dirname(__file__))
		flags = Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint # | Qt.WindowStaysOnTopHint | Qt.WindowSystemMenuHint
		QDialog.__init__(self, parent, flags) # parent=None permet de retrouver la fenetre dans la barre des taches
		win = iface.mainWindow()
		
		self.sep = '_' # Séparateur de champs par défaut
		self.encod = 'utf-8'
		self.coucheGrille = None ; self.SansDoublons = None
		
		self.setWindowTitle("Analyser les dalles raster d'un dossier (et sous-dossiers) et créer une grille")
		# Il faut positionner le dialog MANUELLEMENT, sinon Qt va le repositionner automatiquement à chaque hide -> show :
		###self.setGeometry(win.geometry().x()+150, win.geometry().y()+50, 800, 600)
		self.setGeometry(win.geometry().x()-200, win.geometry().y()+300, 600, 600)
		# Appliquer la même police que dans tout QGIS :
		fontFamily = QSettings().value('qgis/stylesheet/fontFamily','Arial')
		fontPointSize = QSettings().value('qgis/stylesheet/fontPointSize','9')
		styleSheet = 'font-family:"{}"; font-size:{}pt;'.format(fontFamily,fontPointSize)
		self.setStyleSheet(styleSheet)
		
		grille= QGridLayout(self)
		grille.setContentsMargins(5, 2, 5, 2)  #hLayout1= QHBoxLayout()    grille.addLayout(hLayout1, 0, 0)
		
		li= 0
		eti0= QLabel("  Parcourir des dossiers entiers de photos satellite. Faire la grille avec leurs emprises.\n     Des Actions de couche sont ajoutées pour afficher les photos depuis la grille.\n  Chercher les doublons, les dalles en bordure de zone.\n  Possibilité d'indiquer la présence de nuages sur une photo. Noter la qualité.")
		grille.addWidget(eti0, li, 0, 1, 2)
		
		li += 1
		eti1= QLabel("<b>Choisir le dossier à parcourir </b>")
		eti1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		grille.addWidget(eti1, li, 0, 1, 1)
		self.choixFic = QgsFileWidget() 
		self.choixFic.setMinimumSize(400,20)
		self.choixFic.setStorageMode(QgsFileWidget.GetDirectory)
		self.choixFic.setFilePath("D:\\RGB\\PARTIEL-1")
		grille.addWidget(self.choixFic, li, 1, 1, 1)
		
		li += 1
		hLayout1 = QHBoxLayout()
		eti2 = QLabel("<b>Chercher les fichiers :</b>")
		hLayout1.addWidget(eti2)
		self.typeFic = QLineEdit("jp2")
		self.typeFic.setFixedWidth(40)
		hLayout1.addWidget(self.typeFic)
		hLayout1.addStretch()
		self.cbDoublons = QCheckBox("Chercher les doublons")
		self.cbDoublons.setToolTip('Cherche les doublons (même emprise) et met le champ "'+chDoublon+'" à 1')
		self.cbDoublons.setChecked(True)
		hLayout1.addWidget(self.cbDoublons)
		self.cbBordure = QCheckBox("Chercher les dalles en bordure")
		self.cbBordure.setToolTip('Marquer les dalles en bordure de zone (1 zone par dossier): met le champ "'+chBordure+'" à 1')
		self.cbBordure.setChecked(True)
		hLayout1.addWidget(self.cbBordure)
		grille.addLayout(hLayout1, li, 0, 1, 2)
		
		li += 1
		hLayout2 = QHBoxLayout()
		etiLargeur = QLabel("<b>Largeur des dalles</b> en mètres :")
		etiLargeur.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
		hLayout2.addWidget(etiLargeur)
		self.boxLargeur = QDoubleSpinBox(self)
		self.boxLargeur.setDecimals(0)
		self.boxLargeur.setMinimum(10)
		self.boxLargeur.setMaximum(1000000)
		self.boxLargeur.setValue(1000)
		self.boxLargeur.setSuffix(" m")
		self.boxLargeur.setFixedWidth(100)		#self.typeFic.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		hLayout2.addWidget(self.boxLargeur)
		hLayout2.addStretch()
		bParcourir = QPushButton(" Commencer le traitement ")
		bParcourir.clicked.connect(self.trouverDalles)
		hLayout2.addWidget(bParcourir)
		grille.addLayout(hLayout2, li, 0, 1, 2)
		
		li += 1
		etiInfos1 = QLabel("Les fichiers doivent avoir un nom au format *_xmin_ymax_* avec en option _dateheure")
		grille.addWidget(etiInfos1, li, 0, 1, 2)
		li += 1
		etiInfos2 = QLabel("&nbsp;&nbsp;et xmin et ymax doivent être <b>en km en L93</b>. Par exemple: S2E_20211124<b>_0546_6275_</b>L93.jp2")
		grille.addWidget(etiInfos2, li, 0, 1, 2)
		
		li += 1
		self.edit= QsciScintilla(self)
		self.edit.setUtf8(True) # permet saisie des accents (requis meme pour cp1252)
		self.edit.setMarginWidth(0, '99999') # Margin 0 is used for line numbers
		self.edit.setMarginLineNumbers(0, True)
		self.edit.setMarginWidth(1,1) # la marge entre num lignes et blocs
		#self.edit.ensureCursorVisible()
		grille.addWidget(self.edit, li, 0, 1, 2)
		
		li += 1
		self.messageBar = QgsMessageBar(self)
		grille.addWidget(self.messageBar, li, 0, 1, 2)
		"""
		li += 1
		bDoublons = QPushButton("Marquer les cases en double dans la grille (même emprise)")
		bDoublons.clicked.connect(self.chercherDoublons)
		bDoublons.setToolTip("Cherche les doublons et mettre le champ ''doublons'' à 1 sinon 0")
		grille.addWidget(bDoublons, li, 0, 1, 2)
		
		li += 1
		bBordures = QPushButton("Marquer les dalles en bordure de zone (1 zone par dossier)")
		bBordures.clicked.connect(self.chercherBordures)
		grille.addWidget(bBordures, li, 0, 1, 2)
		#"""
		li += 1
		bAGarder = QPushButton('Marquer les dalles "inutiles" car en doublon: valeurs max de bordure, nuages et qualité')
		bAGarder.setToolTip("Les utiles (inutile=0) sont celles dont la valeur de bordure est la plus basse puis la valeur de nuages, puis celle de qualite")
		bAGarder.clicked.connect(self.marquerDallesInutiles)
		grille.addWidget(bAGarder, li, 0, 1, 2)
		
		li += 1
		bCopier = QPushButton('Copier les dalles "utiles" (inutile=0) dans un nouveau dossier')
		bCopier.clicked.connect(self.copierDalles)
		grille.addWidget(bCopier, li, 0, 1, 2)
		
		li += 1
		self.newView= QTableView() # Necessaire de le rendre global pour que l'objet ne soit pas supprimé quand la fonction action se termine !
		self.newView.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.newView.installEventFilter(self) # Voir self.eventFilter : pour traiter les Ctrl+C
		grille.addWidget(self.newView, li, 0, 1, 2)
		
		self.data= None


	def log(self, txt):
		self.edit.append(txt)
		self.edit.setCursorPosition(self.edit.lines(),0)
		QgsApplication.processEvents() # Apres le append , il faut demander à l'Appli de le traiter MAINTENANT



	def trouverDalles(self):
		cible = self.choixFic.filePath()
		typeFichier = self.typeFic.text().strip()
		if typeFichier=='':
			QMessageBox.critical(self, "Attention !", "Il faut indiquer le type de fichiers cherchés")
			return
		typeFichier = typeFichier.lower()
		
		self.largeur = self.boxLargeur.value()
		self.edit.clear()
		
		self.champs = QgsFields()
		self.champs.append( QgsField('fichier',QVariant.String,'varchar',100) )
		self.champs.append( QgsField('xmin',QVariant.Int,'Integer',8) )
		self.champs.append( QgsField('ymax',QVariant.Int,'Integer',8) )
		self.champs.append( QgsField('date',QVariant.String,'varchar',30) )
		self.champs.append( QgsField('dossier',QVariant.String,'varchar',100) )
		self.champs.append( QgsField('chemin',QVariant.String,'varchar',254) )
		self.champs.append( QgsField(chDoublon,QVariant.Int,'Integer',1) )
		self.champs.append( QgsField(chBordure,QVariant.Int,'Integer',1) )
		self.champs.append( QgsField(chQualite,QVariant.Int,'Integer',1) )
		self.champs.append( QgsField(chNuages, QVariant.Int,'Integer',1) )
		self.champs.append( QgsField(chInutile,QVariant.Int,'Integer',1) )
		
		nomFinale = 'grille'
		finale= QgsVectorLayer("Polygon?crs=EPSG:2154", nomFinale, "memory")
		#finale.setCrs(layer.crs()) #change memorylayer crs to layer crs
		#finale.setProviderEncoding( layer.dataProvider().encoding() )
		finalePr= finale.dataProvider()
		finale.startEditing()
		finalePr.addAttributes( self.champs.toList() )
		finale.commitChanges()
		
		self.nbDalles = 0 ; self.nbDossiers = 0
		self.listDalles = []
		def parcourir(dossier, racine=''):
			self.nbDossiers += 1
			if racine=='': racine=dossier
			self.log(dossier + "\n")
			for fic in sorted( os.listdir(dossier) ):
				chemin = os.path.abspath( os.path.join(dossier,fic) )
				if os.path.isdir(chemin):
					parcourir(chemin, racine)
					continue
				if fic[-3:].lower()!=typeFichier:  continue
				feat = self.creerFeatGeom(chemin, fic)
				finalePr.addFeatures( [feat] )
				self.nbDalles += 1
				self.listDalles.append(fic)
			
		parcourir( cible )
		
		self.remplirTable()
		
		path = os.path.abspath(os.path.dirname(__file__))
		path = os.path.join(path, 'styles', 'grille_dalles_raster.qml')
		finale.loadNamedStyle(path)
		
		self.coucheGrille = QgsProject.instance().addMapLayer(finale)
		iface.mapCanvas().clearCache()
		iface.mapCanvas().refresh()
		
		if self.cbDoublons.isChecked():  self.chercherDoublons()
		
		if self.cbBordure.isChecked():  self.chercherBordures()
		
		self.log("\n\n##########  FIN : voir la couche {} ##########\n".format(nomFinale) )
		self.log('\n#### INFOS PRATIQUES :\n- Pour Afficher une des dalles, vous pouvez utiliser l\'action de couche "Afficher une dalle" présente dans "{}"'.format(nomFinale) )
		self.log('\n- Vous pouvez indiquer la qualité des photos en mettant une valeur de 1 (très bonne, claire) à 5 (très mauvaise, sombre) dans le champ "{}" dans "{}"'.format(chQualite,nomFinale) )
		self.log('\n- Si une dalle a des nuages, vous pouvez mettre le champ "{}" à 1 dans "{}"\n'.format(chNuages,nomFinale) )
		self.log('\n- "{}" est une couche mémoire. Pour la conserver, il faudra la sauvegarder (menu Couche > Sauvegarder sous).\n'.format(nomFinale) )
		#QMessageBox.about(self, "FIN", "Le résultat est dans la couche <u>"+ nomFinale +"</u><br>C'est une couche 'mémoire'. Pour la conserver, il faudra la sauvegarder (menu Couche > Sauvegarder sous)." )
		self.messageBar.pushMessage("{} dalles trouvées. Voir les infos pratiques ci-dessus".format(self.nbDalles),Qgis.Success,20)


	def creerFeatGeom(self, chemin, fic):
		feat = QgsFeature()
		feat.setFields(self.champs)
		feat['fichier'] = fic
		feat['chemin'] = chemin
		feat['dossier'] = os.path.basename( os.path.dirname(chemin) )
		feat[chDoublon] = 0
		feat[chBordure] = 0
		feat[chQualite] = 0
		feat[chNuages] = 0
		feat[chInutile] = 0
		columns = fic.split(self.sep)
		nb = len(columns)
		coordX = 0
		coordY = 0
		dateTime = ''
		#for col in range(nb):  columns[col]
		for col in columns:
			if not col.isnumeric(): continue
			val = float(col)
			if val>9999:
				dateTime = col
				feat['date'] = dateTime
				continue
			if coordX == 0:
				coordX = val * 1000
				feat['xmin'] = int(coordX)
			else:
				coordY = val * 1000
				feat['ymax'] = int(coordY)
		
		if coordX!=0 and coordY!=0:
			geom = QgsGeometry.fromRect( QgsRectangle(coordX,coordY-self.largeur,coordX+self.largeur,coordY) )
			if geom and geom.isGeosValid(): feat.setGeometry(geom)
		
		return feat


	def remplirTable(self):
		nbLi = len( self.listDalles ) #self.edit.lines()
		model= QStandardItemModel()
		model.setRowCount(nbLi)
		
		li = self.listDalles[0] #self.edit.text(0)
		columns = li.split(self.sep)
		nbCol = len(columns)
		model.setColumnCount(nbCol)
		
		### Remplir la table :
		for row in range(nbLi):
			li = self.listDalles[row] #self.edit.text(row)
			if len(li)>1: li= li[:-1] # On enleve le retour à la ligne final
			columns= li.split(self.sep)
			nb= len(columns)
			if nbCol < nb:
				nbCol= nb
				model.setColumnCount(nbCol)
			
			for col in range(nb):
				item = QStandardItem( columns[col] )
				item.setTextAlignment( Qt.AlignCenter | Qt.AlignVCenter)
				model.setItem(row, col, item)
		
		if li=='': # Si la derniere ligne est vide, ne pas en tenir compte
			model.setRowCount(nbLi-1)
		
		#self.newView.verticalHeader().setDefaultSectionSize(17)
		##self.newView.resizeColumnsToContents();
		##self.newView.resizeRowsToContents();
		#self.newView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);
		self.newView.setModel(model)



	def chercherDoublons(self):
		self.log("\n\n#### Chercher les dalles qui ont les mêmes xmin et ymax...\n")
		if self.coucheGrille:  grille = self.coucheGrille
		else:  grille = iface.activeLayer()
		nom = grille.id() #grille.name()
		#req = "?query=SELECT xmin, ymax, count(*) nbDalles, max(chemin) chemin, min(geometry) geometry FROM "+ nom +" group by xmin, ymax"
		req = "?query=SELECT xmin, ymax, count(*) nb FROM "+ nom +" group by xmin, ymax"
		lDoublons = QgsVectorLayer( req, "SansDoublons", "virtual")
		if not lDoublons:
			QMessageBox.warning(self, "Echec", "La recherche de doublons a échoué !")
			return
		#lDoublons.setCrs( grille.crs() )
		#self.lDoublons = QgsProject.instance().addMapLayer(lDoublons)
		#QMessageBox.information(self, "FIN", "Le résultat est dans la couche <u>SansDoublons</u><br>C'est une couche 'virtuelle'. Pour la conserver, il faudra la sauvegarder (menu Couche > Sauvegarder sous)." )
		doublons = dict()
		for feat in lDoublons.getFeatures():
			if feat['nb']==1:  continue
			index = str(feat['xmin']) +'#'+ str(feat['ymax'])
			doublons[index] = feat['nb']
		
		champs = grille.fields().names()
		if not chDoublon in champs:
			self.log('Ajouter le champ "'+chDoublon+'" à la grille\n')
			newCh = QgsField(chDoublon,QVariant.Int,'Integer',1)
			grillePr = grille.dataProvider()
			grille.startEditing()
			grillePr.addAttributes( [newCh] )
			grille.commitChanges()
		fieldIndex = grille.fields().indexOf(chDoublon)
		print('fieldIndex =', fieldIndex)
		
		self.log('Parcourir les cases pour positionner le champ "'+chDoublon+'"\n')
		grille.startEditing()
		grille.beginEditCommand("Chercher doublons")
		for feat in grille.getFeatures():
			fid = feat.id()
			index = str(feat['xmin']) +'#'+ str(feat['ymax'])
			if index in doublons: doubl = 1
			else:  doubl = 0
			grille.changeAttributeValue(fid, fieldIndex, doubl)
		
		grille.endEditCommand()
		###grille.commitChanges()
		self.log("####  FIN de la recherche des doublons\n")



	def chercherBordures(self):
		#self.edit.clear()
		if self.coucheGrille:  grille = self.coucheGrille
		else:  grille = iface.activeLayer()
		nom = grille.id() #grille.name()
		
		self.log("\n\n#### Chercher les dalles qui sont en bordure de zone (1 zone par dossier) :\n")
		self.log("Chercher les minY et maxY par colonne de chaque dossier\n")
		req = "?query=SELECT dossier, xmin, min(ymax) miny, max(ymax) maxy FROM "+ nom +" group by dossier, xmin"
		print(req)
		min_max_y = QgsVectorLayer( req, "min_max_y", "virtual")
		if not min_max_y:
			QMessageBox.warning(self, "Echec", "La recherche de min_max_y a échoué !")
			return
		cols = dict()
		for feat in min_max_y.getFeatures():
			index = feat['dossier'] +'#'+ str(feat['xmin'])
			cols[index] = [feat['miny'], feat['maxy']]
		#QgsProject.instance().addMapLayer(min_max_y)
		
		self.log("Chercher les minX et maxX par ligne de chaque dossier\n")
		req = "?query=SELECT dossier, ymax, min(xmin) minx, max(xmin) maxx FROM "+ nom +" group by dossier, ymax"
		min_max_x = QgsVectorLayer( req, "min_max_x", "virtual")
		if not min_max_x:
			QMessageBox.warning(self, "Echec", "La recherche de min_max_x a échoué !")
			return
		lines = dict()
		for feat in min_max_x.getFeatures():
			index = feat['dossier'] +'#'+ str(feat['ymax'])
			lines[index] = [feat['minx'], feat['maxx']]
		#QgsProject.instance().addMapLayer(min_max_x)
		
		champs = grille.fields().names()
		if not chBordure in champs:
			self.log("Ajoute le champ '"+chBordure+"' à la grille\n")
			newCh = QgsField(chBordure,QVariant.Int,'Integer',1)
			grillePr = grille.dataProvider()
			grille.startEditing()
			grillePr.addAttributes( [newCh] )
			grille.commitChanges()
		
		self.log("Parcourir les cases pour mettre le champ '"+chBordure+"' à 1 aux extrémités\n")
		fieldIndex = grille.fields().indexOf(chBordure)
		print('fieldIndex =', fieldIndex)
		
		grille.startEditing()
		grille.beginEditCommand("Chercher bordures par colonne")
		nb = 0
		for feat in grille.getFeatures():
			#nb += 1
			#if nb > 10: break
			fid = feat.id()
			idX = feat['dossier'] +'#'+ str(feat['xmin'])
			idY = feat['dossier'] +'#'+ str(feat['ymax'])
			
			if cols[idX][0]==feat['ymax'] or cols[idX][1]==feat['ymax']:  bordure = 1
			elif lines[idY][0]==feat['xmin'] or lines[idY][1]==feat['xmin']: bordure = 1
			else:  bordure = 0
			grille.changeAttributeValue(fid, fieldIndex, bordure)
			#attrs = { 0 : "hello", 1 : 123 }
			#layer.dataProvider().changeAttributeValues({ fid : attrs })
		
		grille.endEditCommand()
		###grille.commitChanges()
		self.log("####  FIN de la recherche de bordures\n")



	def marquerDallesInutiles(self):
		self.edit.clear()
		if self.coucheGrille:  grille = self.coucheGrille
		else:  grille = iface.activeLayer()
		nom = grille.name()
		champs = grille.fields().names()
		erreur = ''
		if not chBordure in champs: erreur = ' -- {}\n'.format(chBordure)
		if not chNuages  in champs: erreur += ' -- {}\n'.format(chNuages)
		if not chQualite in champs: erreur += ' -- {}\n'.format(chQualite)
		if erreur!='':
			QMessageBox.warning(self,'Impossible','La couche {} n\'a pas le(s) champs :\n{}'.format(nom,erreur) )
			return
		
		self.log("#### Marquer les dalles inutiles car en doublon\n")
		self.log("  avec des dalles dont les valeurs bordure, nuages et qualite sont meilleures...\n\n")
		self.log("Vérification ou ajout du champs '{}'\n".format(chInutile) )
		if not chInutile in champs:
			self.log("Ajouter le champ '"+chInutile+"' à la grille\n")
			newCh = QgsField(chInutile,QVariant.Int,'Integer',1)
			grillePr = grille.dataProvider()
			grille.startEditing()
			grillePr.addAttributes( [newCh] )
			grille.commitChanges()
		
		fieldIndex = grille.fields().indexOf(chInutile)
		precXmin = 99999 ; precYmax = 99999
		
		grille.startEditing()
		grille.beginEditCommand("Chercher les dalles inutiles")
		"""Requete:  SELECT xmin, ymax FROM grille ORDER BY xmin, ymax, bordure, nuages, qualite """
		req = QgsFeatureRequest()
		tri = [ req.OrderByClause('xmin',True), req.OrderByClause('ymax',True) ]
		tri.append( req.OrderByClause(chBordure,True) )
		tri.append( req.OrderByClause(chNuages,True) )
		tri.append( req.OrderByClause(chQualite,True) )
		tri.append( req.OrderByClause('dossier',True) ) # Pour regrouper par zone, si bordure, nuages et qualite sont égaux
		req.setOrderBy( req.OrderBy(tri) )
		for feat in grille.getFeatures(req):
			fid = feat.id()
			# On ne marque "inutile" que les dalles en doublon à chaque emplacement (mêmes x et y que la dalle précédente) :
			if feat['xmin']==precXmin and feat['ymax']==precYmax:  inutile = 1 # Doublon
			else:  inutile = 0 # 1ere dalle à cet emplacement
			grille.changeAttributeValue(fid, fieldIndex, inutile)
			precXmin = feat['xmin'] ; precYmax = feat['ymax']

		grille.endEditCommand()
		###grille.commitChanges()
		self.log("\n####################  FIN  ####################\n")
		self.log('\nColonne "'+chInutile+'"=1 pour les dalles "inutiles".\n')
		self.log('\nPour Ouvrir les dalles UTILES du dossier (inutile=0),\n  vous pouvez utiliser l\'action de couche disponible dans "' +nom +'"\n')



	def copierDalles(self):
		self.edit.clear()
		if self.coucheGrille:  grille = self.coucheGrille
		else:  grille = iface.activeLayer()
		nomCouche = grille.name()
		champs = grille.fields().names()
		if not chInutile in champs:
			QMessageBox.warning(self,'Impossible','La couche {} n\'a pas le champ : "{}"'.format(nom,chInutile) )
			return
		
		ret = QMessageBox.question(self, 'Copie', 'Voulez-vous copier toutes les dalles utiles de la couche "{}" dans un autre dossier ?'.format(nomCouche), QMessageBox.Yes | QMessageBox.No )
		if ret != QMessageBox.Yes:  return
		dir = QFileDialog.getExistingDirectory(self,"Choisir le dossier où copier les dalles","C:\\",QFileDialog.ShowDirsOnly )
		if not dir:  return
		dir = os.path.normpath(dir)
		if not QFile.exists(dir): return
		
		msgBar = self.messageBar()
		msgBar.pushMessage("Patientez pendant la copie des dalles...",Qgis.Info,0)
		self.log("#### La copie des dalles :\n")
		
		self.continuer = True
		thisMethod = getattr(self, sys._getframe().f_code.co_name) # Reference to the current method
		button = self.sender() ; buttonText = button.text()
		button.clicked.disconnect()
		def stopperTraitement(): # peut être déclenché par le même bouton ; voir ci-dessous
			print("stopperTraitement")
			self.continuer = False
			button.setText( buttonText )
			button.clicked.disconnect()
			button.clicked.connect(thisMethod)
		button.clicked.connect( stopperTraitement )
		button.setText( "Stopper la copie" )
	
		req = QgsFeatureRequest()
		req.setFilterExpression(chInutile +"=0")
		nb = 0 ; nbOK = 0
		for feat in grille.getFeatures(req): ## Parcourir les dalles utiles
			nom = os.path.basename(feat['chemin'])
			desti = os.path.join(dir,nom)
			res = QFile.copy( feat['chemin'], desti )
			if res:
				res = "- copié : "
				nbOK += 1
			else  : res = "! ECHEC copie : "
			nb += 1
			self.log(res +desti +'\n')		
			if not self.continuer: # self.continuer peut etre modifié par le bouton 
				self.log("\n#####  La copie a été interrompue  #####\n")		
				return
		
		# Retablir la fonction initiale du bouton :
		button.setText( buttonText )
		button.clicked.disconnect()
		button.clicked.connect(thisMethod)
		
		msgBar.clearWidgets()
		msgBar.pushMessage("{} dalles ont été copiées".format(nbOK),Qgis.Success,0)
		self.log("\n####################  FIN  ####################\n")
		self.log('\n{} dalles ont été copiées dans "{}"\n'.format(nbOK,dir) )




	def creerShape(self, fichier, champsQgs):
		win= self #iface.mainWindow()
		if QFile.exists(fichier):
			ret= QMessageBox.question(win, u"Attention",
			u"Le fichier %s existe déjà.<br>Voulez-vous le supprimer ou annuler le processus ?"% fichier, QMessageBox.Ok | QMessageBox.Cancel )
			if not ret==QMessageBox.Ok:
				return False
			ret= QgsVectorFileWriter.deleteShapeFile( fichier )
			if not ret:
				QMessageBox.warning(win, u"Echec", u"Le fichier %s n'a pu être supprimé." % fichier, QMessageBox.Cancel )
				return False
		fields= QgsFields()
		for f in champsQgs: fields.append(f)
		zonages= QgsVectorFileWriter( fichier, u'88591', fields, QGis.WKBMultiPolygon, QgsCoordinateReferenceSystem('EPSG:2154'), "ESRI Shapefile")
		if zonages.hasError() != QgsVectorFileWriter.NoError:
			QMessageBox.warning(win, u"Echec", u"Erreur creation de: %s <br>%s"% (fichier,zonages.errorMessage()), QMessageBox.Cancel )
			del zonages
			self.annuler()
			return False
		del zonages
		
		champs=[] ### Liste des noms de chaque champs
		for ch in champsQgs:
			champs.append( ch.name() )
		return champs



	 # add event filter : pour traiter les Ctrl+C
	def eventFilter(self, source, event):
		if (event.type() == QEvent.KeyPress and event.matches(QKeySequence.Copy)):
			self.copySelection()
			return True
		return super(analyseDalles,self).eventFilter(source, event)

	def copySelection(self): # Pour copier dans le press papier TOUTES les cases sélectionnées
		selection= self.newView.selectedIndexes()
		if selection:
			rows = sorted(index.row() for index in selection)
			columns = sorted(index.column() for index in selection)
			rowcount = rows[-1] - rows[0] + 1
			colcount = columns[-1] - columns[0] + 1
			table = [[''] * colcount for _ in range(rowcount)]
			for index in selection:
				row = index.row() - rows[0]
				column = index.column() - columns[0]
				table[row][column]= index.data() if index.data() else ''
			#print(table)
			#t= '\n'.join( [ self.sep.join( l ) for l in table if l!=[None] ] ) # self.sep.join( table[0] )
			t= '\n'.join( [self.sep.join( l ) for l in table] ) # self.sep.join( table[0] )
			QApplication.clipboard().setText(t)


