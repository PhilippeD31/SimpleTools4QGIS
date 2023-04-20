import time, os.path
import  codecs # csv, io, 
from encodings.aliases import aliases
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtSql import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.Qsci import QsciScintilla
from qgis.utils import iface
from qgis.gui import QgsFileWidget, QgsMessageBar
from qgis.core import Qgis
from osgeo import gdal


class extractionGPKG(QDialog):
	def __init__(self, parent=None):
		self.path = os.path.abspath(os.path.dirname(__file__))
		flags= Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint # | Qt.WindowStaysOnTopHint | Qt.WindowSystemMenuHint
		QDialog.__init__(self, parent, flags) # parent=None permet de retrouver la fenetre dans la barre des taches
		win = iface.mainWindow()
		
		self.setWindowTitle("Extraire les couches d'un Geopackage multi-couches")
		# Il faut positionner le dialog MANUELLEMENT, sinon Qt va le repositionner automatiquement à chaque hide -> show :
		###self.setGeometry(win.geometry().x()+150, win.geometry().y()+50, 800, 600)
		self.setGeometry(win.geometry().x()-50, win.geometry().y()+20, 700, 500)
		
		grille = QGridLayout(self)
		grille.setContentsMargins(10, 10, 10, 10)  #hLayout1= QHBoxLayout()    grille.addLayout(hLayout1, 0, 0)
		
		li = 0
		eti1 = QLabel("<b>Choisir le GPKG multi-couches :</b>")
		eti1.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
		grille.addWidget(eti1, li, 1, 1, 1)
		li += 1
		self.choixFic= QgsFileWidget()
		#self.choixFic.setFilePath("Choisir le fichier à afficher")
		self.choixFic.setFilter('*.gpkg')
		self.choixFic.setStorageMode(QgsFileWidget.GetFile)
		self.choixFic.fileChanged.connect( self.lireFic )
		self.choixFic.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		grille.addWidget(self.choixFic, li, 0, 1, 3)
		
		li += 1
		self.messageBar = QgsMessageBar(self)
		self.messageBar.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		grille.addWidget(self.messageBar, li, 0, 1, 3)
		
		li += 1
		liTableView = li
		eti = QLabel("""<center><b>Extraire les couches d'un Geopackage multi-couches</b>
			<br>dans autant de fichiers GPKG</center>""")
		grille.addWidget(eti, li, 1, 1, 2)
		
		li += 1
		etiDir = QLabel("<b>Dossiers où enregistrer les couches GPKG :</b>")
		etiDir.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		grille.addWidget(etiDir, li, 1, 1, 2)
		
		li += 1
		self.choixDir = QgsFileWidget()
		self.choixDir.setStorageMode(QgsFileWidget.GetDirectory)
		self.choixDir.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		grille.addWidget(self.choixDir, li, 1, 1, 2)
		
		li += 1
		etiVide1 = QLabel("")
		grille.addWidget(etiVide1, li, 1, 1, 2)
		
		li += 1
		etiOp = QLabel("<b>Options</b>")
		grille.addWidget(etiOp, li, 2, 1, 1)
		
		li += 1
		self.majuscules = QCheckBox("Passer les noms de couche en majuscules")
		grille.addWidget(self.majuscules, li, 1, 1, 2)
		
		li += 1
		etiPre = QLabel("<b>Ajouter le prefix</b>")
		grille.addWidget(etiPre, li, 1, 1, 1)
		self.prefix = QLineEdit()		#self.typeFic.setMinimumSize(50,28)
		#self.typeFic.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		grille.addWidget(self.prefix, li, 2, 1, 1)
		li += 1
		etiSuf = QLabel("<b>Ajouter le suffix</b>")
		grille.addWidget(etiSuf, li, 1, 1, 1)
		self.suffix = QLineEdit()		#self.typeFic.setMinimumSize(50,28)
		#self.typeFic.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
		grille.addWidget(self.suffix, li, 2, 1, 1)
		
		li += 1
		self.garderStyles = QCheckBox("Garder les styles du gpkg d'origine")
		grille.addWidget(self.garderStyles, li, 1, 1, 2)
		
		li += 1
		bExt = QPushButton("Extraire les couches")
		bExt.clicked.connect(self.extraireCouches)
		bExt.setToolTip("Sauvegarde chaque couche dans un fichier GPKG séparé")
		grille.addWidget(bExt, li, 1, 1, 2)
		
		li += 1
		etiVide2 = QLabel("")
		grille.addWidget(etiVide2, li, 1, 1, 2)
		
		li += 1
		self.etat = QLabel("")
		self.etat.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grille.addWidget(self.etat, li, 1, 1, 2)

		
		self.newView = QTableView() # Necessaire de le rendre global pour que l'objet ne soit pas supprimé quand la fonction action se termine !
		self.newView.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.newView.installEventFilter(self) # Voir self.eventFilter : pour traiter les Ctrl+C
		self.newView.setMaximumSize(300,2000)
		grille.addWidget(self.newView, liTableView, 0, li-liTableView+1, 1)
		
		li += 1
		self.progBarre= QProgressBar(self)
		self.progBarre.setMinimum(0)
		self.progBarre.setTextVisible(False)
		grille.addWidget(self.progBarre, li, 0, 1, 3)
		
		self.data = None
		self.db = QSqlDatabase.addDatabase("QSQLITE")



	def lireFic(self, fic):
		if not QFile.exists(fic): return False
		debut=time.time()
		
		self.db.setDatabaseName(fic)
		if not self.db.open():
			QMessageBox.critical( self, "Echec", "Le fichier '{}' n'a pas pu être lu comme une base GPKG".format(fic) )
			self.db = None
			return
		
		self.data = []
		query = QSqlQuery(self.db)
		query.exec("SELECT table_name FROM gpkg_contents")
		while query.next():
			self.data.append( query.value(0) )
		
		self.remplirTable()

		# Enregistrer les styles :
		self.styles = {}
		query.exec("SELECT f_table_name,f_geometry_column,stylename,styleqml,stylesld FROM layer_styles")
		while query.next():
			self.styles[query.value(0)] = [ query.value(1), query.value(2), query.value(3), query.value(4) ]
		
		self.db.close()



	def remplirTable(self):
		nbLi = len(self.data)
		model = QStandardItemModel()
		model.setRowCount(nbLi)
		model.setColumnCount(1)
		model.setHeaderData(0, Qt.Horizontal, "Couches")

		### Remplir la table :
		row = 0
		for table in self.data:
			item = QStandardItem( table )
			item.setEditable(False)
			item.setTextAlignment( Qt.AlignCenter | Qt.AlignVCenter)
			model.setItem(row, 0, item)
			row = row+1
		
		self.newView.setModel(model)
		#self.newView.verticalHeader().setDefaultSectionSize(17)
		#self.newView.resizeRowsToContents()
		self.newView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		#self.newView.resizeColumnsToContents()
		self.newView.selectColumn(0)



	def extraireCouches(self):
		self.messageBar.clearWidgets()
		debut = time.time()
		self.etat.setText('')
		
		if not self.data:
			msg = "Il faut d'abord ouvrir un fichier GPKG !"
			self.messageBar.pushMessage("Attention", msg, Qgis.Warning, 10 )
			return False
		
		selection = self.newView.selectedIndexes()
		liste = []
		for M in selection:  liste.append(M.data())
		
		if liste==[]:
			msg = "Il faut sélectionner les couches à extraire"
			self.messageBar.pushMessage("Attention", msg, Qgis.Warning, 10 )
			return False
		
		self.messageBar.pushMessage("Enregistrement en cours", "si le fichier est gros cela peut être long...", Qgis.Info, 90 )
		QApplication.instance().processEvents()
		self.progBarre.setValue(0)
		self.progBarre.setMaximum( len(liste) )

		#gdal.UseExceptions()
		#gdal.SetConfigOption('CPL_DEBUG', 'ON')
		majuscules = self.majuscules.isChecked()
		prefix = self.prefix.text().strip()
		suffix = self.suffix.text().strip()
		
		fic = self.choixFic.filePath()
		ds = gdal.OpenEx(fic, gdal.OF_VECTOR)
		dir = self.choixDir.filePath()
		if dir=='': dir = os.path.dirname(fic)
		
		erreurs = ''
		N = 0
		for table in liste:
			if majuscules:  layer = prefix +table.upper() +suffix
			else:  layer = prefix +table +suffix
			desti = dir +os.sep +layer +'.gpkg'
			self.etat.setText(layer)
			QApplication.instance().processEvents()
			if QFile.exists(desti):
				if not QFile.remove(desti):
					erreurs += table +": ECHEC: le fichier existant dans "+dir+" n'a pu être supprimé.\n\n"
					continue
			try:
				res = gdal.VectorTranslate( desti, ds, format='GPKG', layerName=layer,
					SQLStatement='SELECT * FROM '+ table )
				if not res:
					erreurs += "Echec de l'enregistrement de "+desti +"\n\n"
					continue
			except Exception as e: # Type d'exception: e.__class__.__name__
				if hasattr(e, 'msg'): erreur= e.msg
				elif hasattr(e, 'message'): erreur= e.message
				else: erreur= repr(e)
				erreurs += "Echec de l'enregistrement de "+desti +".\n"+ erreur +"\n\n"
				continue
			N += 1
			self.progBarre.setValue(N)
		
		if self.garderStyles.isChecked(): ## Récupérer les styles depuis le GPKG source :
			self.etat.setText("Application des styles aux nouveaux GPKG")
			QApplication.instance().processEvents()
			newdb = QSqlDatabase.addDatabase("QSQLITE")
			query = QSqlQuery(newdb)
			for table in liste:
				if majuscules:  layer = prefix +table.upper() +suffix
				else:  layer = prefix +table +suffix
				desti = dir +os.sep +layer +'.gpkg'
				if not QFile.exists(desti): continue
				newdb.setDatabaseName(desti)
				if not newdb.open(): continue
				query.exec("""CREATE TABLE layer_styles(id INTEGER PRIMARY KEY AUTOINCREMENT, f_table_catalog character varying(256), f_table_schema character varying(256), f_table_name character varying(256), f_geometry_column character varying(256), stylename character varying(30), styleqml character varying, stylesld character varying, useasdefault boolean, description character varying, owner character varying(30), ui character varying(30), update_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP)""")
				query.prepare("""INSERT INTO layer_styles
					(f_table_catalog, f_table_schema, f_table_name, f_geometry_column,
						stylename, styleqml, stylesld, useasdefault, description, owner)
					VALUES ('', '', ?, ?, ?, ?, ?, 1, '', '')""")
				query.addBindValue( layer )
				query.addBindValue( self.styles[table][0] )
				query.addBindValue( layer )
				query.addBindValue( self.styles[table][2] )
				query.addBindValue( self.styles[table][3] )
				if not query.exec():
					erreurs += "Soucis à la sauvegarde du style de "+table +".\n"+ query.lastError().text() +"\n\n"
				newdb.close()
		
		ds = None		
		self.etat.setText("<center><b>---- FIN ----</b><br>durée : %.1f sec</center>"% (time.time() - debut) )
		self.messageBar.clearWidgets()
		if N==0: self.messageBar.pushMessage("ECHEC ", "Aucune couche extraite", Qgis.Critical, 20)
		elif N<len(liste):
			self.messageBar.pushMessage("Soucis ", "Certaines couches n'ont pas pu être extraites", Qgis.Warning, 20)
		else:
			self.messageBar.pushMessage("OK ", "les couches ont bien été enregistrées", Qgis.Success, 10)
		
		if erreurs!='': QMessageBox.warning(self, "Problèmes pendant l'extraction", erreurs )



	# add event filter : pour traiter les Ctrl+C
	def eventFilter(self, source, event):
		if (event.type() == QEvent.KeyPress and event.matches(QKeySequence.Copy)):
			self.copySelection()
			return True
		return super(extractionGPKG,self).eventFilter(source, event)

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


