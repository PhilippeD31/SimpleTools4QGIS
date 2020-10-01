import time, os.path
import sys, codecs # csv, io, 
from encodings.aliases import aliases
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.Qsci import QsciScintilla
from qgis.utils import iface
from qgis.gui import QgsFileWidget, QgsMessageBar
from qgis.core import Qgis

encodingList= ['utf-8','windows-1252','latin1','utf-16']


class bigFileEditor(QDialog):
  def __init__(self, parent=None):
    self.path = os.path.abspath(os.path.dirname(__file__))
    flags= Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint # | Qt.WindowStaysOnTopHint | Qt.WindowSystemMenuHint
    QDialog.__init__(self, parent, flags) # parent=None permet de retrouver la fenetre dans la barre des taches
    win= iface.mainWindow()
    self.nbRows= 20
    
    # Translator :
    pluginPath= os.path.abspath(os.path.dirname(__file__))
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
    
    
    self.setWindowTitle( self.tr("Display the first rows of a big text file") )
    # Il faut positionner le dialog MANUELLEMENT, sinon Qt va le repositionner automatiquement à chaque hide -> show :
    ###self.setGeometry(win.geometry().x()+150, win.geometry().y()+50, 800, 600)
    self.setGeometry(win.geometry().x()+10, win.geometry().y()+20, 800, 600)
    
    grille= QGridLayout(self)
    grille.setContentsMargins(2, 2, 2, 2)
    
    li= 0
    eti1= QLabel(self.tr("Choose the file"))
    grille.addWidget(eti1, li, 0, 1, 1)
    self.choixFic= QgsFileWidget()
    #self.choixFic.setFilePath("Choisir le fichier à afficher")
    self.choixFic.setFilter('*.csv;;*.txt;;*.*')
    self.choixFic.setStorageMode(QgsFileWidget.GetFile)
    self.choixFic.fileChanged.connect( self.lireFic )
    grille.addWidget(self.choixFic, li, 1, 1, 1)
    
    li += 1
    self.edit= QsciScintilla(self)
    self.edit.setUtf8(True) # permet saisie des accents (requis meme pour cp1252)
    self.edit.setMarginWidth(0, '9999') # Margin 0 is used for line numbers
    self.edit.setMarginLineNumbers(0, True)
    self.edit.setMarginWidth(1,1) # la marge entre num lignes et blocs
    grille.addWidget(self.edit, li, 0, 1, 2)
    
    li += 1
    self.encod= 'utf-8'
    self.choixEncod= QComboBox()
    self.choixEncod.addItems( encodingList )
    self.choixEncod.setCurrentText(self.encod)
    self.choixEncod.addItems( sorted(list( set(aliases.values()) ) ) )
    self.choixEncod.currentTextChanged.connect( self.comboEncodageChanged )
    grille.addWidget(self.choixEncod, li, 0, 1, 1)
    eti2= QLabel('<- '+ self.tr("If the CSV content has strange characters, try a different encoding"))
    grille.addWidget(eti2, li, 1, 1, 1)
    
    li += 1
    self.messageBar = QgsMessageBar(self)
    grille.addWidget(self.messageBar, li, 0, 1, 2)
    
    li += 1
    hLayout1= QHBoxLayout()
    grille.addLayout(hLayout1, li, 0, 1, 2)
    #
    etiNbLi= QLabel(self.tr("Display"))
    etiNbLi.setToolTip(self.tr("To Define the number of lines to display"))
    hLayout1.addWidget(etiNbLi)
    self.sbNbRows= QSpinBox(self)
    hLayout1.addWidget(self.sbNbRows)
    self.sbNbRows.setMinimum(1)
    self.sbNbRows.setMaximum(10000)
    self.sbNbRows.setValue(self.nbRows)
    self.sbNbRows.setSuffix(' '+ self.tr("lines")) #self.sbNbRows.setPrefix(self.tr("Display") +' ')
    self.sbNbRows.setToolTip(self.tr("Number of lines to display (Maximum: 10000)"))
    def nbRowsChanged(val):
      self.nbRows= self.sbNbRows.value()
    self.sbNbRows.valueChanged[int].connect(nbRowsChanged)
    
    bReload= QPushButton(self.tr("Reload"))
    bReload.clicked.connect(self.reloadFile)
    hLayout1.addWidget(bReload)
    #
    hLayout1.addStretch()
    bPreview= QPushButton(self.tr("Update the preview below"))
    bPreview.clicked.connect(self.remplirTable)
    hLayout1.addWidget(bPreview) #  grille.addWidget(bPreview, li, 0, 1, 1)
    bSave= QPushButton(self.tr("Save the modified file"))
    bSave.clicked.connect(self.saveChanges)
    bSave.setToolTip(self.tr("Save your modifications in a new file"))
    hLayout1.addWidget(bSave) #grille.addWidget(bSave, li, 1, 1, 1)

    li += 1
    self.newView= QTableView() # Necessaire de le rendre global pour que l'objet ne soit pas supprimé quand la fonction action se termine !
    self.newView.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.newView.installEventFilter(self) # Voir self.eventFilter : pour traiter les Ctrl+C
    grille.addWidget(self.newView, li, 0, 1, 2)
    
    self.sep= ',' # Séparateur de champs par défaut
    self.data= None

  def tr(self, txt, disambiguation=None):
    return QCoreApplication.translate('bigFileEditor', txt, disambiguation)


  def reloadFile(self):
    self.lireFic( self.choixFic.filePath() )


  def comboEncodageChanged(self, txt): # encoding defini par le choix du user dans le combobox "choixEncod"
    self.encod= txt
    if self.data:
      self.afficherTexte( self.encod )
      self.remplirTable()


  def lireFic(self, fic):
    if not QFile.exists(fic): return False
    debut=time.time()
    
    file= codecs.open(fic, 'rb')
    if not file: return False
    #file= QFile( fic )
    #if not file.open( QIODevice.ReadOnly | QIODevice.Text ): return False
    
    self.data= bytearray()
    for row in range(1, self.nbRows+1):
      li= file.readline() # bytes (pas affichable : il faudra le 'decoder')
      if li==b'':
        row -= 1 # row sert à compter les linges lues
        break
      self.data += li
    
    file.close()
    self.nbLignesLues= row
    
    print( "Duree :"+ str(time.time() - debut) ) #print( self.data )
    
    if self.data[:2]==bytearray(b'\xff\xfe') or self.data[:2]==bytearray(b'\xfe\xff'):
      self.encod= 'utf-16'
      blocker= QSignalBlocker( self.choixEncod ) ## Prevent firing any signal from the object "choixEncod"
      self.choixEncod.setCurrentText(self.encod)
      blocker.unblock()
      self.afficherTexte('utf-16')
    else:
      self.afficherTexte()
    
    self.remplirTable()


  def afficherTexte(self, encodage=False): ## Décoder les lignes du fichier et les afficher dans l'éditeur
    """ pour la fonction bytearray.decode(enco,'replace'), le caractere de remplacement est: '\ufffd' 
     @encodage : paramètre envoyé par comboEncodageChanged (choix dans le combobox) """
    self.errEncodage= False # Traquer les erreurs d'encodage à la lecture
    self.messageBar.clearWidgets()
    
    if encodage: ## On veut savoir si l'encodage choisi par User provoque des erreurs avec "decode" :
      try:
        txt= self.data.decode(encodage) # bytearray -> unicode
      except UnicodeError:
        txt= self.data.decode(encodage, 'replace')
        self.errEncodage= True
      except LookupError:
        txt= self.data.decode('ascii', 'replace')
        self.errEncodage= True
    
    else: ## Recherche automatique de l'encodage du texte
      for enco in encodingList:
        try: # on veut savoir si la lecture avec self.encod a rencontré des erreurs d'encodage :
          txt= self.data.decode(enco) # bytearray -> unicode
          self.errEncodage= False
          self.encod= enco
          break
        except UnicodeError:
          txt= self.data.decode(enco, 'replace')
          self.errEncodage= True
        except LookupError:
          txt= self.data.decode('ascii', 'replace')
          self.errEncodage= True
      
      blocker= QSignalBlocker( self.choixEncod ) ## Empecher  tout signal  depuis l'objet combobox
      self.choixEncod.setCurrentText(self.encod)
      blocker.unblock()
    
    self.edit.setText(txt)
    
    print( "nb li", self.edit.lines(), self.nbLignesLues )
    self.dernierCaractere= ''
    
    if self.edit.lines() > self.nbLignesLues: # Si le nb de lignes affichées est supérieur au nb de lignes lues
      if txt[-2:] == '\r\n':
        self.dernierCaractere= txt[-2:] # Garder les derniers caractères en mémoire pour la fonction saveChanges
        self.edit.setText( txt[:-2] ) # On enleve le retour à la ligne final
      elif txt[-1] == '\n':
        self.dernierCaractere= txt[-1] # Garder le dernier caractère en mémoire pour la fonction saveChanges
        self.edit.setText( txt[:-1] ) # On enleve le retour à la ligne final
    
    if self.errEncodage:
      msg= self.tr("You may change the encoding above in order to correct the \ufffd")
      showMore= self.tr("When reading the file with encoding %s \n some characters were not reconized \n and they are printed as \ufffd \nWhich means that the file was saved with a different encoding.") % self.encod +"\n"
      self.messageBar.pushMessage( self.tr("Attention "), msg, showMore, Qgis.Warning, 30 )
      self.edit.setReadOnly(True) # Empeche la modif du texte
    else:
      self.edit.setReadOnly(False) # Autorise la modif du texte


  def remplirTable(self):
    nbLi= self.edit.lines()
    model= QStandardItemModel()
    model.setRowCount(nbLi)
    
    ### Chercher le séparateur et compter le nombre de colonnes :
    self.sep= ','
    li= self.edit.text(0)
    if li.count(';') > li.count(self.sep): # s'il y a plus de ; que de virgules
      self.sep= ';'
    if li.count('\t') > li.count(self.sep): # s'il y a plus de tabu que de virgules ou de ;
      self.sep= '\t'
    columns= li.split(self.sep)
    nbCol= len(columns)
    model.setColumnCount(nbCol)
    
    ### Remplir la table :
    for row in range(nbLi):
      li= self.edit.text(row)
      if len(li)>1: li= li[:-1] # On enleve le retour à la ligne final
      columns= li.split(self.sep)
      nb= len(columns)
      if nbCol < nb:
        nbCol= nb
        model.setColumnCount(nbCol)
      
      for col in range(nb):
        item= QStandardItem( columns[col] )
        item.setTextAlignment( Qt.AlignCenter | Qt.AlignVCenter)
        model.setItem(row, col, item)
    
    if li=='': # Si la derniere ligne est vide, ne pas en tenir compte
      model.setRowCount(nbLi-1)
    
    self.newView.setModel(model)
    #self.newView.verticalHeader().setDefaultSectionSize(17)
    self.newView.resizeColumnsToContents();
    self.newView.resizeRowsToContents();
    #self.newView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);


  def saveChanges(self, checked=False):
    self.messageBar.clearWidgets()
    if self.errEncodage: # Si les erreurs d'encodage n'ont pas été corrigées, refuser le save
      msg= self.tr("You can't save the file with this encoding: %s. Please choose another one!") % self.encod
      showMore= self.tr("The original file was saved with another encoding.\n\nYou may find it by trying other encodings in the list above.")
      self.messageBar.pushMessage( self.tr("Stop"), msg, showMore, Qgis.Critical, 10 )
      return False
    
    fic= os.path.normpath( self.choixFic.filePath() )
    
    new, filter= QFileDialog.getSaveFileName(self, self.tr("Enter the name of the new file"), os.path.dirname(fic), '*.csv')
    if not new or new=='':  return
    new= os.path.normpath(new)
    
    if os.path.normcase(fic) == os.path.normcase(new):
      msg= self.tr("Sorry, you can't save with the same path et file name!")
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Critical, 30 )
      return False
    
    try: file= codecs.open(fic, 'rb')
    except Exception as e:
      errno, strerror = e.args
      msg= strerror
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Critical, 30 )
      return False
    
    try: newFile= codecs.open(new, 'wb')
    except Exception as e:
      file.close()
      errno, strerror = e.args
      msg= strerror
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Critical, 30 )
      return False
    
    res= newFile.write( self.edit.text().encode(self.encod) )
    if res==None:
      newFile.close()
      file.close()
      msg= self.tr("Couldn't write %s") % new
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Critical, 30 )
      return False
    
    self.messageBar.pushMessage( self.tr("Saving in progress"), self.tr("it may take a long time if the file is big..."), Qgis.Info, 90 )
    QApplication.instance().processEvents()
    
    newFile.write( self.dernierCaractere.encode(self.encod) )
    
    for row in range(self.nbRows): # Passer les premieres lignes du CSV d'origine car deja lues dans lireFic
      li= file.readline()
      if li==b'':  break
    
    while True:
      li= file.readline()
      if li==b'':  break
      newFile.write( li )
    
    newFile.close()
    file.close()
    
    self.messageBar.clearWidgets()
    msg= self.tr("The file was successfully saved")
    self.messageBar.pushMessage( self.tr("Success")+" ", msg, Qgis.Success, 30 )



  def eventFilter(self, source, event): ## Add event filter : pour traiter les Ctrl+C
    if (event.type() == QEvent.KeyPress and event.matches(QKeySequence.Copy)):
      self.copySelection()
      return True
    return super(bigFileEditor,self).eventFilter(source, event)

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

