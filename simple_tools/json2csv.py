import time, os.path
import sys, codecs, csv, json
from encodings.aliases import aliases
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.Qsci import QsciScintilla
from qgis.utils import iface
from qgis.gui import QgsFileWidget, QgsMessageBar
from qgis.core import Qgis
from collections import OrderedDict

encodingList= ['utf-8','windows-1252','latin1','utf-16']


class json2csv(QDialog):
  def __init__(self, parent=None):
    self.path = os.path.abspath(os.path.dirname(__file__))
    flags= Qt.WindowTitleHint | Qt.WindowCloseButtonHint #| Qt.WindowStaysOnTopHint
    #| Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint
    QDialog.__init__(self, parent, flags) # parent=None permet de retrouver la fenetre dans la barre des taches
    win= iface.mainWindow()
    self.nbRows= 20
    self.delimiter= ';'
    self.concatFields= '_'
    
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
    
    # Appliquer la même police que dans tout QGIS :
    fontFamily= QSettings().value('qgis/stylesheet/fontFamily', 'Arial')
    fontPointSize= QSettings().value('qgis/stylesheet/fontPointSize', '9')
    styleSheet= 'font-family:"{}"; font-size:{}pt;'.format(fontFamily,fontPointSize)
    self.setStyleSheet(styleSheet)
    
    
    self.setWindowTitle( self.tr("Convert a JSON file to CSV") )
    # Il faut positionner le dialog MANUELLEMENT, sinon Qt va le repositionner automatiquement à chaque hide -> show :
    ###self.setGeometry(win.geometry().x()+150, win.geometry().y()+50, 800, 600)
    self.setGeometry(win.geometry().x()+10, win.geometry().y()-10, 600, 500)
    
    grille= QGridLayout(self)
    grille.setContentsMargins(6, 2, 6, 2)
    
    li= 0
    etiPres1= QLabel('<center><b>'+ self.tr("Convert JSON to CSV by flattening the json tree") +'</b></center>')
    grille.addWidget(etiPres1, li, 0, 1, 2)
    li += 1
    etiPres2= QLabel(self.tr("Sub level branches are converted to simple fields and their fieldnames are concatenated (separated by '_')"))
    grille.addWidget(etiPres2, li, 0, 1, 2)
    
    li += 1
    hLayout0= QHBoxLayout()
    grille.addLayout(hLayout0, li, 0, 1, 2)
    etiEx1= QLabel('<b>{"id":123, "contact": {"tel":555, "mail":"a@b.c"}}</b>')
    hLayout0.addWidget(etiEx1)    #grille.addWidget(etiPres2, li, 0, 1, 2)
    hLayout0.addStretch()
    etiEx2= QLabel('==>')
    hLayout0.addWidget(etiEx2) 
    hLayout0.addStretch()
    etiEx3= QLabel('<b>id;contact_tel;contact_mail<br>123;555;a@b.c</b>')
    hLayout0.addWidget(etiEx3) 
    
    li += 1
    eti1= QLabel(self.tr("Choose the file"))
    grille.addWidget(eti1, li, 0, 1, 1)
    self.choixFic= QgsFileWidget()
    #self.choixFic.setFilePath("Choisir le fichier à afficher")
    self.choixFic.setFilter('*.json;;*.*')
    self.choixFic.setStorageMode(QgsFileWidget.GetFile)
    self.choixFic.fileChanged.connect( self.lireFic )
    grille.addWidget(self.choixFic, li, 1, 1, 1)
    
    li += 1   ## The content of de JSON file
    self.edit= QsciScintilla(self)
    self.edit.setUtf8(True) # permet saisie des accents (requis meme pour cp1252)
    self.edit.setMarginWidth(0, '9999') # Margin 0 is used for line numbers
    self.edit.setMarginLineNumbers(0, True)
    self.edit.setMarginWidth(1,1) # la marge entre num lignes et blocs
    self.edit.setTabWidth(3)
    self.edit.setReadOnly(True)
    grille.addWidget(self.edit, li, 0, 1, 2)
    
    li += 1
    hLayout1= QHBoxLayout()
    grille.addLayout(hLayout1, li, 0, 1, 2)
    #
    etiOption= QLabel('<b>'+ self.tr("Options:") +' </b>')
    hLayout1.addWidget(etiOption)
    #
    hLayout1.addStretch()
    #
    etiDelim= QLabel(self.tr("CSV delimiter"))
    hLayout1.addWidget(etiDelim)
    self.lDelim= QLineEdit(';',self)
    self.lDelim.setToolTip(self.tr("Define the CSV delimiter"))
    self.lDelim.setMaximumWidth(15)
    hLayout1.addWidget(self.lDelim)
    hLayout1.addStretch()
    #
    etiNbLi= QLabel(self.tr("Preview"))
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
    #
    hLayout1.addStretch()
    #
    bReload= QPushButton(self.tr("Reload"))
    bReload.clicked.connect(self.reloadFile)
    hLayout1.addWidget(bReload)
    #bPreview= QPushButton(self.tr("Update the preview below"))
    #bPreview.clicked.connect(self.remplirTable)
    #hLayout1.addWidget(bPreview) #  grille.addWidget(bPreview, li, 0, 1, 1)
    
    li += 1
    self.encod= 'utf-8'
    self.choixEncod= QComboBox()
    self.choixEncod.addItems( encodingList )
    self.choixEncod.setCurrentText(self.encod)
    self.choixEncod.addItems( sorted(list( set(aliases.values()) ) ) )
    self.choixEncod.currentTextChanged.connect( self.comboEncodageChanged )
    grille.addWidget(self.choixEncod, li, 0, 1, 1)
    eti2= QLabel('<- '+ self.tr("If the JSON content has strange characters, try a different encoding"))
    grille.addWidget(eti2, li, 1, 1, 1)
    
    li += 1
    self.messageBar = QgsMessageBar(self)
    grille.addWidget(self.messageBar, li, 0, 1, 2)
    
    li += 1
    self.csvView= QsciScintilla(self)
    self.csvView.setUtf8(True) # permet saisie des accents (requis meme pour cp1252)
    self.csvView.setMarginWidth(0, '9999') # Margin 0 is used for line numbers
    self.csvView.setMarginLineNumbers(0, True)
    self.csvView.setMarginWidth(1,1) # la marge entre num lignes et blocs
    self.csvView.setReadOnly(True)
    grille.addWidget(self.csvView, li, 0, 1, 2)

    """li += 1
    self.newView= QTableView() # Necessaire de le rendre global pour que l'objet ne soit pas supprimé quand la fonction action se termine !
    self.newView.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.newView.installEventFilter(self) # Voir self.eventFilter : pour traiter les Ctrl+C
    grille.addWidget(self.newView, li, 0, 1, 2) #"""
    
    li += 1
    bSave= QPushButton(self.tr("Save to a CSV file"))
    bSave.clicked.connect(self.saveCSV)
    bSave.setToolTip(self.tr("Convert the JSON file to a CSV file"))
    #hLayout1.addWidget(bSave) #grille.addWidget(bSave, li, 1, 1, 1)
    grille.addWidget(bSave, li, 1, 1, 1)
    
    self.sep= ',' # Séparateur de champs par défaut
    self.data= None

  def tr(self, txt, disambiguation=None):
    return QCoreApplication.translate('json2csv', txt, disambiguation)


  def lireFic(self, fic):
    if not QFile.exists(fic): return False
    debut=time.time()
    
    file= codecs.open(fic, 'rb')
    if not file: return False
    
    self.data= bytearray()
    for row in range(1, self.nbRows+1):
      li= file.readline( 102400 ) # bytes (pas affichable : il faudra le 'decoder')
      if li==b'':
        row -= 1 # row sert à compter les lignes lues
        break
      self.data += li
    
    file.close()
    self.nbLignesLues= row
    
    QApplication.instance().processEvents()
    print( "Duree readline :"+ str(time.time() - debut) ) #print( self.data )
    
    if self.data[:2]==bytearray(b'\xff\xfe') or self.data[:2]==bytearray(b'\xfe\xff'):
      self.encod= 'utf-16'
      blocker= QSignalBlocker( self.choixEncod ) ## Prevent firing any signal from the object "choixEncod"
      self.choixEncod.setCurrentText(self.encod)
      blocker.unblock()
      self.afficherTexte('utf-16')
    else:
      self.afficherTexte()
    
    #self.remplirTable()
    self.convert()


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
    #  self.edit.setReadOnly(True) # Empeche la modif du texte
    #else:
    #  self.edit.setReadOnly(False) # Autorise la modif du texte



  def convert(self): ## Convert the JSON file to CSV an show in preview
    fic= os.path.normpath( self.choixFic.filePath() )
    if not QFile.exists(fic): return False
    debut=time.time()
    
    file= codecs.open(fic, 'r', self.encod, 'ignore')
    if not file: return False
    js= json.load(file)
    
    QApplication.instance().processEvents()
    print( "Duree json.load :"+ str(time.time() - debut) ) #print( self.data )
    debut=time.time()
    
    """txt= ''
    nbLi= self.edit.lines()
    for row in range(nbLi):
      li= self.edit.text(row)
      if len(li)>1: li= li[:-1] # On enleve le retour à la ligne final
      txt += li
    js = json.loads(txt) """
    """
    input = map(lambda x: self.flattenjson(x,"_"), js)
    self.lignes= []
    self.columns= []
    for row in input:
      self.lignes.append(row)
      for x in row.keys():
        if not x in self.columns: self.columns.append(x)
    #"""
    #columns = [x for row in input for x in row.keys()]
    #columns = list(set(columns))
    self.lignes= []
    self.columns= []
    
    obj= js
    field= '_noname_'
    while True: # Inspect the "root" of the json
      nb= len(obj)
      if isinstance(obj,list): # If it's a list :
        for elem in obj:
          self.lignes.append( self.flattenjson(elem,field) )
        break

      if not isinstance(obj,dict): # Not a list nor a dict
        self.lignes.append( {field:obj} )
        break
      
      for field,val in obj.items(): break # Get the "first" item
      
      if nb==1: # If it's a root elem without siblings :
        self.columns.append(field) # Store its fieldname for CSV
        obj= val # And continue with its child
        continue
      # Else :
      self.lignes.append( self.flattenjson(obj) )
      break
    
    """
    if isinstance(js, list): # If it's a list :
      print('list=',js)
      for elem in js:
        if isinstance(elem,dict):
          self.lignes.append( self.flattenjson(elem) )
        else:
          self.columns.append(elem)
    
    elif isinstance(js, dict): # Either a single elem  or  "tree" object
      obj= js
      while True: # If js is a tree : will flatten its root
        nb= len(obj)
        for key,val in obj.items(): break # Get the "first" item
        if nb=1 and isinstance(val,dict): # If it's a root elem without siblings :
          self.columns.append(key) # Store its fieldname for CSV
          obj= val # And continue with its child
          continue
        elif nb=1 and isinstance(val,list): # If it's a root elem with a list of children :
          self.columns.append(key) # Store its fieldname for CSV
          for elem in val:
            self.lignes.append( self.flattenjson(elem) )
          break
        self.lignes.append( self.flattenjson(obj) )
        break
      
      
    else:
      msg= self.tr("Bad JSON file; can't convert it.")
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Warning, 30 )
      return False
    #"""
    #print( self.lignes )
    for row in self.lignes:
      for x in row.keys():
        if not x in self.columns: self.columns.append(x)
    #print("columns =", self.columns )
    
    delim= self.lDelim.text()
    if delim=='':  delim= self.delimiter
    
    csv= delim.join(self.columns)  +"\n"
    nl= 0
    for row in self.lignes:
      li= map(lambda x: row.get(x,""), self.columns)
      for col in li:
        csv += str(col) +delim
      csv= csv[:-1] +"\n"
      nl += 1
      if nl==self.nbRows: break
    
    self.csvView.setText(csv)
    
    print( "Duree convert to CSV :"+ str(time.time() - debut) ) #print( self.data )


  def flattenjson(self, dico, field='_noname_'):
    if not isinstance(dico, dict):
      #print(dico.__class__.__name__, dico)
      return {field:dico}
    
    #print('dict=',dico)
    #"""
    val= OrderedDict() # {}
    for i in dico.keys():
      #if isinstance(dico[i], list):
      #  val[i]= self.flattenjson(dico[i], self.concatFields)
      if isinstance(dico[i], dict):
        get = self.flattenjson(dico[i], self.concatFields)
        for j in get.keys():
          val[i + self.concatFields + j] = get[j]
      else:
        val[i] = dico[i]
    
    return val



  def reloadFile(self):
    self.lireFic( self.choixFic.filePath() )


  def comboEncodageChanged(self, txt): # encoding defini par le choix du user dans le combobox "choixEncod"
    self.encod= txt
    if self.data:
      self.afficherTexte( self.encod )
      self.convert()



  def saveCSV(self, checked=False):
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

    
    self.messageBar.pushMessage( self.tr("Saving in progress"), self.tr("it may take a long time if the file is big..."), Qgis.Info, 90 )
    QApplication.instance().processEvents()
    
    #try: newFile= open(new, 'wb')
    try: newFile= codecs.open(new, 'w', self.encod, 'ignore')
    except Exception as e:
      errno, strerror = e.args
      msg= strerror
      self.messageBar.clearWidgets()
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Critical, 30 )
      return False
    
    delim= self.lDelim.text()
    if delim=='':  delim= self.delimiter
    #with open(new, 'wb') as newFile:
    csv_w = csv.writer(newFile, delimiter=delim, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_w.writerow(self.columns)
    for row in self.lignes:
      csv_w.writerow(map(lambda x: row.get(x,""), self.columns))
    
    """
    try: file= codecs.open(fic, 'rb')
    except Exception as e:
      errno, strerror = e.args
      msg= strerror
      self.messageBar.pushMessage( self.tr("Failed")+" ", msg, Qgis.Critical, 30 )
      return False
    
    try: newFile= codecs.open(new, 'w', self.encod, 'ignore')
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
    
    newFile.write( self.dernierCaractere.encode(self.encod) )
    
    for row in range(self.nbRows): # Passer les premieres lignes du CSV d'origine car deja lues dans lireFic
      li= file.readline()
      if li==b'':  break
    
    while True:
      li= file.readline()
      if li==b'':  break
      newFile.write( li )
    
    file.close()
    #"""
    newFile.close()
    
    self.messageBar.clearWidgets()
    msg= self.tr("The file was successfully saved")
    self.messageBar.pushMessage( self.tr("Success")+" ", msg, Qgis.Success, 30 )



  def eventFilter(self, source, event): ## Add event filter : pour traiter les Ctrl+C
    if (event.type() == QEvent.KeyPress and event.matches(QKeySequence.Copy)):
      self.copySelection()
      return True
    return super(json2csv,self).eventFilter(source, event)

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
