# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.gui import QgsFileWidget, QgsMessageBar, QgsFilterLineEdit
from qgis.core import *
from qgis.utils import iface



class resultats(QDialog): ## Fenêtre pour les résultats des contrôles
	def __init__(self, parent):
		if not parent:  parent = iface.mainWindow()
		QDialog.__init__(self, parent)
		self.setWindowTitle( "Résultats des contrôles" )
		self.move( parent.pos().x()+50, parent.pos().y()+50 )  #form.resize(800,600)
		self.web = QWebView(self)
		Layout_1 = QGridLayout(self)
		Layout_1.setContentsMargins( 0, 0, 0, 0 )
		Layout_1.addWidget(self.web, 0, 0, 1, 1)

	def voir(self, html): ## Afficher la liste des problèmes et des couches OK
		self.web.setHtml( html )
		self.show()




class panneau(QWidget):
	def __init__(self, parent, pluginSettings, verifGaspar=True):
		QWidget.__init__(self, parent)
		self.pluginSettings = pluginSettings
		self.verifGaspar = verifGaspar
		if verifGaspar:  self.repModeles = 'modeles_PPR' # Si c'est un controle de couches de PPR :
		else:  self.repModeles = 'verif_standard'
		self.run = False
		self.fenResult = resultats(self) # Dialog
		self.resultats = '' # Résultats des contrôles (texte HTML)
		self.erreurs = ''
		self.modeles = []
		self.couchesParModeles = {}
		
		## Appliquer la même police que dans tout QGIS :
		fontFamily = QSettings().value('qgis/stylesheet/fontFamily', 'Arial')
		fontPointSize = QSettings().value('qgis/stylesheet/fontPointSize', '9')
		styleSheet = 'font-family:"{}"; font-size:{}pt;'.format(fontFamily,fontPointSize)
		self.setStyleSheet(styleSheet)
		try:  self.fontPS = int(fontPointSize)
		except: self.fontPS = 9
		
		self.createDialog()
		self.restaurerParam()
		self.afficherAide()


	def createDialog(self):
		win = iface.mainWindow()
		self.messageBar = iface.messageBar()
		
		grille = QGridLayout(self)
		grille.setContentsMargins(6, 6, 6, 6)
		
		li= 0 ## Présentation :
		etiTitre = QLabel("<b>{}</b>".format(self.parent().windowTitle()) )
		etiTitre.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		grille.addWidget(etiTitre, li, 0, 1, 2)
		li += 1
		if self.verifGaspar : etiPres2 = QLabel("vérifier si elles respectent le standard")
		else:  etiPres2 = QLabel("vérifier si elles sont conformes aux couches modèles")
		etiPres2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		#etiPres2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
		grille.addWidget(etiPres2, li, 0, 1, 2)
		#
		if self.verifGaspar:
			li += 1 ## Préfixe GASPAR du service :
			hLayoutGasp = QHBoxLayout()
			grille.addLayout(hLayoutGasp, li, 0, 1, 2)
			etiPreGasp= QLabel("Préfixe GASPAR du service : ")
			hLayoutGasp.addWidget(etiPreGasp)
			self.qlPrefixe = QLineEdit( self )
			self.qlPrefixe.setPlaceholderText("par exemple : 31DDT")
			self.qlPrefixe.setToolTip("Les premiers caractères du code GASPAR, SANS les 8 derniers chiffres")
			hLayoutGasp.addWidget(self.qlPrefixe)
			#
			li += 1 ## Département :
			hLayoutDep = QHBoxLayout()
			grille.addLayout(hLayoutDep, li, 0, 1, 2)
			etiDep = QLabel("<b>Code département ou région sur 3 caractères</b>")
			etiDep.setToolTip("Ce code se retrouve dans le nom des couches des PPR")
			etiDep.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
			hLayoutDep.addWidget(etiDep)
			self.depreg = QLineEdit( self )
			self.depreg.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
			self.depreg.setPlaceholderText("ex.: 031")
			self.depreg.setToolTip("Ce code se retrouve dans le nom des couches des PPR")
			hLayoutDep.addWidget(self.depreg)
		#
		li += 1 ## Dossier où se trouvent les modèles du standard :
		etiModeles = QLabel("<b>Dossier où se trouvent les couches modèles :</b>")
		etiModeles.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
		grille.addWidget(etiModeles, li, 0, 1, 2)
		li += 1
		hLayoutMod = QHBoxLayout()
		grille.addLayout(hLayoutMod, li, 0, 1, 2)
		#etiRep1= QLabel("<b>Option</b>");		hLayoutMod.addWidget(etiRep1)
		bMod = QPushButton(QgsApplication.getThemeIcon('/mIconFolderOpen.svg'),'')
		#bMod.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
		#bMod.adjustSize()	#bMod.setMaximumWidth(40)	#bMod.setWidth(20) #
		bMod.clicked.connect(self.choixRepModeles)
		bMod.setToolTip("Choisir le dossier où se trouvent les couches modèles du standard")
		hLayoutMod.addWidget(bMod)
		self.editMod = QgsFilterLineEdit(self)
		self.editMod.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
		self.editMod.setPlaceholderText("Dossier des couches modèles du standard")
		self.editMod.setToolTip("Choisir le dossier où se trouvent les couches modèles du standard")
		self.editMod.valueChanged.connect( self.analyserModeles )
		hLayoutMod.addWidget(self.editMod)
		#
		li += 1 ## Liste des couches modèles :
		hLayoutCouches = QHBoxLayout()
		grille.addLayout(hLayoutCouches, li, 0, 1, 2)
		etiChoix = QLabel("Couches modèles trouvées dans le dossier :\n\nLes couches à contrôler doivent avoir des noms\nqui commencent comme leur modèle")
		etiChoix.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		hLayoutCouches.addWidget(etiChoix)
		#
		self.listCouches = QListWidget(self)
		self.listCouches.setSelectionMode( QAbstractItemView.ExtendedSelection )
		self.listCouches.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
		self.listCouches.setMaximumHeight(100)
		self.listCouches.setToolTip("Ctrl+clic pour en sélectionner plusieurs")
		hLayoutCouches.addWidget(self.listCouches)
		#
		li += 1 ## Dossier où se trouvent les couches à contrôler :
		etiDossier = QLabel("<b>Dossier où se trouvent les couches à contrôler :</b>")
		etiDossier.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
		grille.addWidget(etiDossier, li, 0, 1, 2)
		li += 1
		hLayoutRep = QHBoxLayout()
		grille.addLayout(hLayoutRep, li, 0, 1, 2)
		bRep = QPushButton(QgsApplication.getThemeIcon('/mIconFolderOpen.svg'),'')
		bRep.clicked.connect(self.choixRep)
		bRep.setToolTip("Choisir le dossier où se trouvent les couches à contrôler (source bureau d'étude ou autre)")
		hLayoutRep.addWidget(bRep)
		self.infoRep = QgsFilterLineEdit(self) # QLineEdit( self )
		self.infoRep.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
		self.infoRep.setPlaceholderText("Dossier des couches à contrôler")
		self.infoRep.setToolTip("Choisir le dossier se trouvent les couches à contrôler (source bureau d'étude ou autre)")
		hLayoutRep.addWidget(self.infoRep)
		#
		li += 1 ## Options + Bouton pour lancer les vérifications
		hLayoutGo = QHBoxLayout()
		grille.addLayout(hLayoutGo, li, 0, 1, 2)
		self.corrigerAuto = QCheckBox("Corriger les attributs")
		if self.verifGaspar:
			self.corrigerAuto.setToolTip("Correction automatique de certains attributs invalides (code GASPAR, erreurs de majuscules)")
		else:
			self.corrigerAuto.setToolTip("Correction automatique des erreurs de majuscules/minuscules dans les attributs")
		hLayoutGo.addWidget(self.corrigerAuto)
		hLayoutGo.addStretch()
		bGo = QPushButton('  Vérifier les couches  ')
		bGo.setMinimumHeight(30)
		bGo.setStyleSheet("""QPushButton { font-weight:bold; background-color:#D0FFF0;
			border:2px outset #33f; border-radius:4px;}
			QPushButton:pressed{ border:2px inset #33f; background-color:#C8F4E8; }""")
		bGo.setToolTip("Contrôler que les couches respectent les modèles")
		bGo.setDefault(True)
		bGo.clicked.connect(self.lancerControles)
		hLayoutGo.addWidget(bGo)
		hLayoutGo.addStretch()
		#
		li += 1 ## Bouton pour assembler les couches partageant le même modèle
		hLayoutFus = QHBoxLayout()
		grille.addLayout(hLayoutFus, li, 0, 1, 2)
		hLayoutFus.addStretch()
		self.bFusion = QPushButton('  Assembler les couches valides partageant le même modèle  ')
		#self.bFusion.setMinimumHeight(30)
		'''self.bFusion.setStyleSheet("""QPushButton { font-weight:bold; background-color:#D0FFF0;
			border:2px outset #33f; border-radius:4px;}
			QPushButton:pressed{ border:2px inset #33f; background-color:#C8F4E8; }""") #'''
		self.bFusion.setToolTip("S'il y a plusieurs dossiers avec des couches similaires, regrouper les objets par modèle")
		self.bFusion.clicked.connect(self.assemblerCouches)
		hLayoutFus.addWidget(self.bFusion)
		self.bFusion.setVisible(False)
		hLayoutFus.addStretch()
		#
		li += 1 ## Infos sur la progression du téléchargement
		self.progress= QLabel()
		self.progress.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.progress.setStyleSheet("QLabel {background-color:#a3eeeb; color:#000;}") #  font:bold 17px;
		self.progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
		grille.addWidget(self.progress, li, 0, 1, 2)
		#
		li += 1 ## Suivi et résultats des vérifications :
		self.journal = QListWidget(self)
		self.journal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
		#etiDep.setMinimumWidth(200)
		grille.addWidget(self.journal, li, 0, 1, 2)
		#
		self.setTabOrder(self.editMod, self.infoRep)
		self.setTabOrder(self.infoRep, self.corrigerAuto)
		self.setTabOrder(self.corrigerAuto, bGo)
		if self.verifGaspar:
			self.setTabOrder(bGo, self.qlPrefixe)
			self.setTabOrder(self.qlPrefixe, self.depreg)



	def sauverParam(self): ## Enregistrer les choix de l'utilisateur
		S = QgsSettings()
		S.beginGroup(self.pluginSettings)
		if self.verifGaspar:
			S.setValue('prefixe', self.qlPrefixe.text() )
			S.setValue('departement', self.depreg.text() )
		S.setValue('dossierModeles', self.editMod.text() )
		S.setValue('dossierControle', self.infoRep.text() )
		S.setValue('corrigerAuto', self.corrigerAuto.isChecked() )

	def restaurerParam(self): ## Retrouver les précédents choix de l'utilisateur
		S = QgsSettings()
		S.beginGroup(self.pluginSettings)
		if self.verifGaspar:
			self.qlPrefixe.setText( S.value('prefixe','') )
			self.depreg.setText( S.value('departement','') )
		self.infoRep.setText( S.value('dossierControle','') )
		self.corrigerAuto.setChecked( S.value('corrigerAuto',True,type=bool) )
		repMod = S.value('dossierModeles', '')
		if repMod and QFile.exists(repMod):
			self.editMod.setText( repMod )
			return
		# Si dossier des modèles par encore défini, copier les modèles par défaut du plugin dans un nouveau dossier :
		desti = self.repModeles # Dossier par défaut où copier les modeles ( sera créé dans QGISprofil\QGIS )
		repMod = os.path.dirname(__file__) +os.sep +'MODELES'
		iniFic = S.fileName()
		if QFile.exists(iniFic): # Si la config QGIS est stockee dans QGIS3.ini, copier les modeles dans un sou-rep (desti)
			iniDir = os.path.dirname(iniFic)
			if QDir(iniDir +os.sep +desti).exists() or QDir(iniDir).mkdir(desti):
				userMod = os.path.abspath( os.path.join(iniDir,desti) ) # dossier des modeles du user
				# Copier tous les fichiers des modèles du plugin vers le dossier du user :
				for f in sorted( os.listdir(repMod) ):
					fic = os.path.abspath( os.path.join(repMod,f) )
					if os.path.isdir(fic):  continue
					QFile.copy( fic, os.path.join(userMod,f) )
				repMod = userMod # Le dossier dans le profil devient le dossier des modèles
		self.editMod.setText( repMod )



	def analyserModeles(self): ## Créer la liste des modèles et champs depuis le dossier
		self.listCouches.clear()
		self.modeles = []
		self.chpsModeles = {}
		self.resultats = ''
		
		rep = self.editMod.text()
		if rep=='': return False #QMessageBox.critical(self, "Attention !", "Il faut choisir le dossier des couches modèles.")
		if not QFile.exists(rep): return False
		pluginRep = os.path.abspath( os.path.dirname(__file__) ) # Le dossier du plugin
		rep = os.path.abspath( rep )
		if os.path.commonprefix([pluginRep,rep])==pluginRep: # Si rep est dans le dossier du plugin :
			self.editMod.setText('')
			QMessageBox.critical(self, "Attention !",
				"Les couches modèles ne doivent pas être placées dans le dossier de l'extension." \
				"\nVeuillez les copier ailleurs.")
			return False
		
		self.log('######  Les couches modèles et leurs champs  ######', 'gras')
		nbCouches = 0
		for f in sorted( os.listdir(rep) ): ## Chercher les couches dans le dossier
			fic = os.path.abspath( os.path.join(rep,f) )
			if os.path.isdir(fic): continue
			nom, ext = os.path.splitext(f)
			if ext.lower() in ['.shp','.tab','.gpkg']:
				self.listCouches.addItem(nom)
				self.modeles.append(nom)
				self.chpsModeles[nom] = {'fic':fic}
				nbCouches += 1
		
		## Analyser les champs des modèles :
		for mo in self.modeles:
			self.log( mo, 'gras')
			lay = QgsVectorLayer( self.chpsModeles[mo]['fic'], mo, 'ogr')
			if not lay or not lay.isValid():
				self.log("! QGIS n'a pas réussi à ouvrir cette couche ! Vérifiez son format...", 'erreur')
			chps = lay.fields()
			noms = chps.names()
			self.chpsModeles[mo]['champs'] = noms
			types = {} ; log = ''
			for ch in chps.toList():
				types[ch.name()] = ch.typeName()
				log += ch.name() +'('+ch.typeName()+') '
			self.chpsModeles[mo]['types'] = types
			self.couchesParModeles[mo] = [] # Préparer la liste des couches de ce modèle
			self.log( log )
		
		self.modelesHTML = '<div style="font-size:90%">'+ self.resultats +'</div>'
		
		if nbCouches==0:  self.log('AUCUNE couche modèle dans "{}"'.format(rep), 'erreur')
		
		## Préparer la liste des attributs autorisés (par mod. et par champ) depuis ATTRIBUTS.ini :
		self.STD_VALEURS = {}
		ficIni = os.path.abspath( os.path.join(rep,'ATTRIBUTS.ini') )
		if not QFile.exists(ficIni): return
		s = QSettings( ficIni, QSettings.IniFormat )
		for g in s.childGroups():
			if not g in self.modeles:
				print(g, ": modèle inconnu")
				continue
			self.STD_VALEURS[g] = {}
			s.beginGroup(g)
			for ch in s.childKeys():
				v = s.value(ch)
				if v.__class__.__name__=='list': self.STD_VALEURS[g][ch] = v
				else:  self.STD_VALEURS[g][ch] = v.split(',')
			s.endGroup()
		
		if len(self.STD_VALEURS)>0:
			self.log('Les valeurs autorisées par le standard ont été chargées depuis "ATTRIBUTS.ini"', 'succes')



	def verifParam(self): ## Vérifier les parametres et si OK, les enregistrer
		if self.verifGaspar:
			if len(self.depreg.text())<3:
				self.messageBar.pushMessage("Il faut indiquer le n° de département ou région sur 3 caractères", Qgis.Warning, 5)
				return False
			# Préfixe GAPSPAR : retirer les caractères interdits dans les fichiers :
			prefixe = self.qlPrefixe.text()
			prefixe = prefixe.replace('/','').replace('\\','').replace(':','').replace('*','').replace('?','')
			prefixe = prefixe.replace('"','').replace('<','').replace('>','').replace('|','')
			self.qlPrefixe.setText(prefixe)
			self.prefixe = prefixe
			if len(prefixe)<4:
				QMessageBox.critical(self, "Attention !",
					"Il faut indiquer le préfixe GASPAR de votre service.\n  Par exemple : 31DDT")
				return False
		
		if self.modeles==[]:
			self.messageBar.pushMessage("Vous n'avez aucun modèle de couches !",Qgis.Warning,5)
			return False
		
		CHEMIN = self.infoRep.text()
		if CHEMIN=='':
			QMessageBox.critical(self, "Attention !", "Il faut choisir le dossier des couches à contrôler.")
			return False
		if not QFile.exists( CHEMIN ):
			QMessageBox.critical(self, "Attention !",
				"Le dossier des couches à contrôler <u>{}</u> n'existe pas.".format(CHEMIN) )
			return False
		self.repCtrl = CHEMIN
		
		rep = self.editMod.text()
		if rep=='':
			QMessageBox.critical(self, "Attention !", "Il faut choisir le dossier des couches modèles.")
			return False
		if not QFile.exists( rep ):
			QMessageBox.critical(self, "Attention !",
				"Le dossier des couches modèles <u>{}</u> n'existe pas.".format(rep) )
			return False
		
		self.sauverParam() # Enregistrer les choix de l'utilisateur
		return True



	def lancerControles(self): ## Fonction principale associée au bouton "Vérifier les couches"
		button = self.sender() # The widget that called this function
		if self.run: # Re-cliquer sur le bouton permet de stopper le traitement
			self.run = False
			button.setText( self.buttonText )
			return
		
		self.analyserModeles() # Ré-analyser les couches modeles et attributs (au cas où ils auraient été modifiés)
		if not self.verifParam(): return # Vérifier les parametres (msg d'erreurs dans self.verifParam)
		self.run = True
		self.buttonText= button.text() # Sauve le texte "normal" du bouton
		button.setText("  Stopper le traitement  ")
		
		self.progress.setText('')
		self.journal.clear()
		self.erreurs = ''
		self.resultats = '<style>* {font-family:sans-serif}</style>'+ self.modelesHTML
		self.couchesModifiees = [] # Les couches corrigées automatiquement (certains attributs)
		self.sousRep = False
		
		nbOK = 0
		couchesOK = []
		if self.verifGaspar: prefixe = self.prefixe
		else:  prefixe = False
		self.progress.setText("<b>Les contrôles démarrent...</b>")
		
		def parcourir(rep, racine=True): ## Fonction récursive pour parcourir des dossiers
			if not self.run: return 0 # Traitement interrompu par le user
			dossier = os.path.basename(rep)
			self.log('Dossier : '+ dossier, 'dossier' )
			nbCouches = 0 # Nombre de couches trouvées qui correspondent à un des modèles
			# Vérifier si dossier est un num GASPAR :
			gaspar = False
			if prefixe and dossier[:len(prefixe)]==prefixe: # Si verifGaspar, tester si dossier est un code GASPAR:
				num = dossier[len(prefixe):]
				if len(num)==8 and num.isdigit(): gaspar = num
			#
			if prefixe and not gaspar and not racine:
				self.log('! Le nom du dossier DOIT être un code GASPAR : votre préfixe suivi de 8 chiffres', 'erreur')
				return 0
			#
			for f in sorted( os.listdir(rep) ):
				if not self.run:  break # Traitement interrompu par le user
				fic = os.path.abspath( os.path.join(rep,f) )
				if os.path.isdir(fic):
					if racine: # Parcourir les sous-rep seulement au niveau racine
						nbc = parcourir(fic, False)
						if nbc>0:  self.sousRep = True
						nbCouches += nbc
					continue
				nom, ext = os.path.splitext(f)
				if ext.lower() in ['.shp','.tab','.gpkg']:  #if f[-3:].lower() in ['shp','tab']:
					nbCouches += self.verifierCouche(fic, gaspar)
			#
			return nbCouches
		
		nbFic = parcourir(self.repCtrl)
		
		self.log(' ') # Ligne vide
		if nbFic > 0: self.log("####### FIN - {} couches trouvées #######".format(nbFic), 'succes')
		else: self.log("####### FIN - AUCUNE couche n'a été trouvée #######", 'erreur')
		
		if self.run:
			titre = "<b>---- FIN ----</b>"
			self.run= False
		else: # Si traitement interrompu
			titre= "----  Traitement interrompu  ----"
		self.progress.setText(titre)
		button.setText(self.buttonText)
		
		if self.erreurs=='':
			QMessageBox.information(self, "Fin des contrôles", "Aucune erreur n'a été relevée dans les couches.")
		else:
			self.fenResult.voir( self.resultats )



	def verifierCouche(self, chemin, gaspar): ## Vérifier elle correspond à un modèle et ses champs
		""" gaspar = n° sur 8 chiffres  ou  False """
		fic = os.path.basename(chemin)
		self.log('## Couche : '+ fic , 'couche')
		ppr = False
		modele = False
		for mo in self.modeles: ## Parcourir les modèles :
			if fic[:len(mo)] != mo:  continue
			# Si le nom de fic correspond à ce modèle
			modele = mo
			break
		if not modele:
			self.log(' Ce nom ne correspond à aucun modèle')
			return 0
		if gaspar:
			ficMod = modele +'_'+ gaspar
			if fic[:len(ficMod)] != ficMod:
				self.log('Le numéro gaspar du nom de fichier NE CORRESPOND PAS à celui du dossier', 'erreur')
				self.log('Le nom du fichier devrait commencer par : '+ficMod, 'gras')
				return 0
		
		layer = QgsVectorLayer(chemin, fic, 'ogr')
		if not layer or not layer.isValid():
			self.log("! QGIS n'a pas réussi à ouvrir cette couche ! Vérifiez son format...", 'erreur')
			return 0
		
		## Comparer les noms et types des champs de la couche avec ceux de son modèle :
		chps = layer.fields()
		nomsCh = chps.names()
		chpsOK = False
		if self.chpsModeles[modele]['champs'] == nomsCh: # Exactement les mêmes noms et dans le même ordre
			chpsOK = True
		
		errType = ''
		for Ch in chps.toList(): # Comparer les types de champs
			if not Ch.name() in self.chpsModeles[modele]['types']: continue
			if Ch.typeName() != self.chpsModeles[modele]['types'][Ch.name()]:
				errType += "{}({}) ".format( Ch.name(), Ch.typeName() )
		
		if chpsOK: # Si la couche a exactement les mêmes noms de champs et dans le même ordre
			if errType=='':  self.log('  Les champs respectent le modèle '+modele, 'succes')
			else:  self.log('Noms des champs OK, mais types incorrects : '+ errType, 'erreur')
		
		else: # Sinon, est-ce que tous les champs du modèle sont présents dans la couche, même dans le désordre :
			absents = ''
			for nom in self.chpsModeles[modele]['champs']:
				if not nom in nomsCh: absents = absents +nom +' '
			if absents == '': self.log('  Les champs sont présents mais dans le DÉSORDRE', 'erreur')
			else: self.log('Des champs sont absents : '+ absents, 'erreur')
			
			if errType!='':  self.log('  Certains champs ont un type incorrect : '+ errType, 'erreur')
		
		valOK = self.verifierValeurs(layer, modele, gaspar)
		
		if valOK and chpsOK and errType=='': # Si les noms et type des champs sont valides et les valeurs aussi :
			self.couchesParModeles[modele].append(layer)
			if self.sousRep:  self.bFusion.setVisible(True)
		
		return 1


	def verifierValeurs(self, layer, modele, gaspar): ## Vérifier que les attributs respectent le standard
		if not modele in self.STD_VALEURS:  return True
		valOK = True
		erreurs = {} # Listes de valeurs invalides par nom de champ
		corriger = self.corrigerAuto.isChecked()
		featModifs = {} # Modifications à enregistrer
		chpsModifs = {} # Noms des champs avec la valeurs corrigées auto 
		listeMAJ = {} # Valeurs en majuscules par nom de champ avec la val originale
		vals = self.STD_VALEURS[modele]
		if gaspar: # Ajouter la vérif du code GASPAR
			gaspar = self.prefixe + gaspar
			vals['ID_GASPAR'] = []
		
		for ch,liste in vals.items():
			erreurs[ch] = {}
			chpsModifs[ch] = {}
			listeMAJ[ch] = {}
			for v in liste: listeMAJ[ch][v.upper()] = v
		
		for feat in layer.getFeatures():
			fid = feat.id()
			attribModif = {} # Liste des n° de champ modifier, avec leur nouvelle valeur
			for ch,liste in vals.items(): # Trouver les listes de valeurs pour chaque champ du standard
				v = feat.attribute(ch)
				if not v: continue # Le champ ch est absent
				if gaspar and ch=='ID_GASPAR':
					if v != gaspar: 
						if corriger:
							idCh = feat.fieldNameIndex(ch)
							attribModif[idCh] = gaspar
							chpsModifs[ch][v] = True
						else:
							erreurs['ID_GASPAR'][v] = False # Devrait être égale au nom du dossier
							valOK = False
					continue
				if not v in liste:
					if corriger and v.upper() in listeMAJ[ch]:
						idCh = feat.fieldNameIndex(ch)
						attribModif[idCh] = listeMAJ[ch][v.upper()] # La valeur originale
						chpsModifs[ch][v] = True
					else:
						erreurs[ch][v] = False
						valOK = False
			
			if attribModif!={}:  featModifs[fid] = attribModif
		
		if featModifs!={}: ## S'il y a des corrections d'attributs à appliquer
			changeOK = True # Suivre si tous les changements ont bien été appliqués sans erreur
			if layer.startEditing():
				for fid, modifs in featModifs.items(): # Appliquer toutes les corrections
					if not layer.changeAttributeValues(fid,modifs): #not layer.isEditCommandActive() or  and layer.isModified()
						changeOK = False
						break
				if changeOK: # Si tous les changeAttributeValues ont bien marché :
					lay = QgsProject.instance().addMapLayer(layer)
					if lay.isEditable(): # Vérifier si le mode édition n'a pas "sauté"
						self.couchesModifiees.append(layer)
						listeMod = []
						for ch, v in chpsModifs.items(): #del erreurs[ch] # Retirer de la liste des erreurs
							if v!={}:  listeMod.append(ch)
						self.log("Des valeurs erronées ont été corrigées dans : "+' '.join(listeMod), 'succes')
						self.log("! Vérifier la couche, corriger éventuellement les autres valeurs erronées puis l'ENREGISTRER !")
					else: # Certains facteurs peuvent désactiver le mode édition et faire perdre toutes les corrections !
						QgsProject.instance().removeMapLayer(lay)
						changeOK = False
				else: # Echec de la modif de certains attributs => abandon des modifs
					layer.rollBack()
			else: # Pas réussi à passer en mode édition
				changeOK = False
			#
			if not changeOK: # Si échec des modifications : regrouper les valeurs invalides dans "erreurs"
				valOK = False
				for ch, v in chpsModifs.items(): # Fusionner avec "erreurs"
					erreurs[ch] = {**erreurs[ch], **v} # Fusionner les 2 dict de valeurs
				self.log("La correction automatique des valeurs a échoué : échec de la mise à jour de la couche")
		
		if valOK:  return True
		else:
			for ch,liste in erreurs.items():
				if liste!={}: self.log('-- '+ ch +' valeurs erronées non corrigées: '+ ' '.join(liste), 'erreur')
			return False



	def assemblerCouches(self): ## Fonction associée au bouton "Assembler les couches"
		pass



	def choixRepModeles(self): ## Choix du répertoire des couches modèles
		rep = QFileDialog.getExistingDirectory(self, self.editMod.toolTip() )
		if not rep or rep=='':  return
		self.editMod.setText( os.path.normpath(rep) )


	def choixRep(self): ## Choix du répertoire où enregistrer les couches téléchargées
		rep = QFileDialog.getExistingDirectory(self, self.infoRep.toolTip() )
		if not rep or rep=='':  return
		self.infoRep.setText( os.path.normpath(rep) )



	def log(self, msg, niveau='info'): ## Afficher journal des traitements dans self.journal
		#item = QListWidgetItem(msg, self.journal, 0)
		item = QListWidgetItem(msg, None, 0)
		if niveau=='erreur':
			item.setBackground( QBrush(QColor(255,155,155)) )
			self.erreurs += msg +'\n'
			msg = '<span style="background-color:#faa">'+ msg +'</span>'
		elif niveau=='succes':
			item.setBackground( QBrush(Qt.green) )
			msg = '<span style="background-color:#afa">'+ msg +'</span>'
		elif niveau=='dossier':
			self.journal.addItem(' ')
			font = item.font(); font.setBold(True); font.setPointSize(self.fontPS+2); item.setFont(font)
			item.setBackground( QBrush(QColor(200,200,200)) )
			msg = '<br><span style="font:bold 120% Arial;background-color:#bbb">'+ msg +'</span>'
		elif niveau=='couche':
			self.journal.addItem(' ')
			font = item.font();  font.setBold(True);  item.setFont(font)
			msg = '<span style="display:inline-block; font:bold 100% Arial; margin-top:8px">'+ msg +'</span>'
		elif niveau=='gras':
			font = item.font();  font.setBold(True);  item.setFont(font)
			msg = '<span style="font:bold 100% Arial">'+ msg +'</span>'
		self.journal.addItem(item)
		self.journal.scrollToItem(item)
		QApplication.instance().processEvents()
		self.resultats += msg +'<br>'



	def afficherAide(self): ## Afficher l'aide du plugin dans self.journal
		self.progress.setText('Informations importantes')
		self.journal.addItem(' ')
		item = QListWidgetItem('Remarques sur les couches à contrôler :', self.journal, 0)
		font = item.font(); font.setBold(True); font.setPointSize(self.fontPS+2); item.setFont(font)
		item.setBackground( QBrush(QColor(200,200,200)) )
		self.journal.addItem(item)
		self.journal.addItem('## Nom des couches')
		self.journal.addItem(' -- Le nom du fichier doit commencer exactement comme son modèle')
		self.journal.addItem("## Doivent respecter les mêmes noms de champs, mêmes types et même ordre")
		if self.verifGaspar:
			self.journal.addItem('## Nom de dossier : doit être le code GASPAR du PPR')
			self.journal.addItem(" -- Les codes GASPAR : préfixe du service suivi d'un nombre à 8 chiffres")
		self.journal.addItem('## Les couches peuvent être dans des sous-dossiers du dossier choisi')
		if self.verifGaspar:
			self.journal.addItem(' -- Un dossier par PPR nommé avec son code GASPAR')
		else:
			self.journal.addItem(' -- Le traitement vérifiera tous les modèles dans chaque sous-dossier')
		
		self.journal.addItem(' ')
		item = QListWidgetItem('Remarques sur les couches modèles :', self.journal, 0)
		font = item.font(); font.setBold(True); font.setPointSize(self.fontPS+2); item.setFont(font)
		item.setBackground( QBrush(QColor(200,200,200)) )
		self.journal.addItem(item)
		self.journal.addItem('-- Les couches modèles doivent être des vecteurs .shp, .gpkg ou .tab')
		self.journal.addItem('-- ATTRIBUTS.ini : listes des attributs autorisés par modèle et par champ')
		
		self.journal.addItem(' ')
		QApplication.instance().processEvents()

