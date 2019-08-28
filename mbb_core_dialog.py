# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mbb_qgis_pluginDialog
                                 A QGIS plugin
  A tool to automatically set up QGIS Atlas layouts

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-07-17
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Anthony Cooper
        email                : anthony.cooper@outlook.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import csv
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import *
from .mbb_core_dialog_additem import mbb_dialog_additem



# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mbb_core_dialog_base.ui'))


class mbb_qgis_pluginDialog(QtWidgets.QDialog, FORM_CLASS):


    def __init__(self, parent=None):
        """Constructor."""
        super(mbb_qgis_pluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.stackedWidget.setCurrentIndex(0)
        self.update_buttons()
        self.stackedWidget.currentChanged.connect(self.update_buttons)
        self.nextButton.clicked.connect(self.__next__)
        self.prevButton.clicked.connect(self.prev)
        self.tAdd.clicked.connect(lambda: self.addDynamicItem(0))
        self.eAdd.clicked.connect(lambda: self.addDynamicItem(1))
        self.sAdd.clicked.connect(lambda: self.addDynamicItem(2))
        self.sAdd_2.clicked.connect(lambda: self.addDynamicItem(3))
        self.tRemove.clicked.connect(lambda: self.removeDynamicItem(0))
        self.eRemove.clicked.connect(lambda: self.removeDynamicItem(1))
        self.sRemove.clicked.connect(lambda: self.removeDynamicItem(2))

        self.existingTemplateBrowser.clicked.connect(lambda: self.loadExistingFile(self.existingTemplate, 'QGIS Print Composer Template (*.qpt)'))

        self.sMoveUp.clicked.connect(lambda: self.createSearchList(self.tTree))
        self.sTree.clear()
        self.eTree.clear()
        self.tTree.clear()

        self.otherItem = 'All (Other) Items'

        #defaults for setup file
        self.templateQMS = ['TEMPLATE NAME', ]
        self.mapsdetailsQMS = [['MAIN MAP'], ['SUPER MAP']]
        self.consistentQMS = ['CONSISTENT ITEMS']
        self.dynamicQMS = ['DYNAMIC ITEMS']
        self.legendQMS = ['LEGEND DETAILS']

        self.mapsQMS = []
        self.mainMapQMS = ["MainMap_X", "MainMap_Y", "MainMap_Scale", "MainMap_Orientation", "MainMap_Layers"]
        self.mapsQMS.extend(self.mainMapQMS)
        self.otherItemsQMS = []

        self.mapSheetsQMS = [[1,2,3,4,'TEST',6,7]]

        self.mapName = 'TEST'






    def  update_buttons(self):
        i = self.stackedWidget.currentIndex()
        self.prevButton.setEnabled(i > 0)
        if i == (self.stackedWidget.count()-1):
            self.nextButton.setText('Generate Atlas')
        else:
            self.nextButton.setText('Next >')

    def prev(self):
        i = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(i - 1)
        self.update_buttons()

    def __next__(self):
        i = self.stackedWidget.currentIndex()

        validEntry = True

        #Check valid entry for sheet #, and prep next sheet
        if i == 0:                          #Setup
            validEntry = self.setup()
        if i == 1:                          #Template
            validEntry = self.setupTemplate()
        if i == 2:                          #Consistent
            validEntry = self.setup()
        if i == 3:                          #Dynamic
            validEntry = self.setup()
        if i == 4:                          #Review
            validEntry = self.setup()



        if validEntry:      #If valid entry (if not valid entry, do nothing else)
            if i < self.stackedWidget.count()-1:    #if before final sheet
                self.stackedWidget.setCurrentIndex(i + 1)   #move to next
                self.update_buttons()   #update the buttons
            else:
                self.writeSetupFile()
                self.accept()   #return to main run, do the generation

    def setup(self):
        #If using existing template is it valid file
            #return False

        #If saving new copy is it valid location
            #return False

        self.setupPath = os.path.abspath(QgsProject.instance().homePath())
        self.setupName = 'test'

        #Take template (default or existing) and load in data

        self.layers = []

        # Fetch the currently loaded layers
        self.layers = self.load_all_layers(QgsProject.instance().layerTreeRoot().children(), self.layers)

        # Fetch the current project layouts
        manager = QgsProject.instance().layoutManager()
        if len(manager.printLayouts()) == 0:
            self.existingLayout.setCheckable(False)
            self.existingLayout.setChecked(False)
        else:
            self.existingLayouts.clear()
            self.existingLayout.setCheckable(True)
            for layout in manager.printLayouts():
                self.existingLayouts.addItem(layout.name())



        return True

    def writeSetupFile(self):
        #Prep header
        headerQMS = []
        headerQMS.append(['<<HEADER>>', 7, self.mapName])
        headerQMS.append(self.templateQMS)
        headerQMS.extend(self.mapsdetailsQMS)
        headerQMS.append(self.consistentQMS)
        headerQMS.append(self.dynamicQMS)
        headerQMS.append(self.legendQMS)
        headerQMS.append(['<<END OF HEADER>>'])
        self.headerLength = len(headerQMS)
        headerQMS[0][1] = self.headerLength

        layersHeaderQMS = []
        layersHeaderQMS.extend(self.mapsQMS)
        layersHeaderQMS.extend(self.otherItemsQMS)


        if os.path.exists(os.path.join(self.setupPath, self.setupName + ".QMapSetup")):
            os.remove(os.path.join(self.setupPath, self.setupName + ".QMapSetup"))

        with open(os.path.join(self.setupPath, self.setupName + ".QMapSetup"), 'w+', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(headerQMS)
            writer.writerow(layersHeaderQMS)
            writer.writerows(self.mapSheetsQMS)

    def returnValues(self):
        returnQMS = []
        returnQMS.append([self.headerLength, self.mapName])
        returnQMS.append(self.templateQMS)
        returnQMS.append(self.mapsdetailsQMS)
        returnQMS.append(self.consistentQMS)
        returnQMS.append(self.dynamicQMS)
        returnQMS.append(self.legendQMS)
        returnQMS.append(os.path.join(self.setupPath, self.setupName + ".QMapSetup"))
        return returnQMS

    def setupTemplate(self):
        self.newLayout = self.layoutTemplate.isChecked()
        if self.newLayout:
            if os.path.exists(self.existingTemplate.text()):
                self.template = QgsPrintLayout(QgsProject.instance())
                with open(self.existingTemplate.text()) as f:
                    template_content = f.read()
                doc = QDomDocument()
                doc.setContent(template_content)

                # adding to existing items
                self.template.loadFromTemplate(doc, QgsReadWriteContext())

                #self.template.setName("TEST")
                #manager = QgsProject.instance().layoutManager()
                #manager.addLayout(self.template)

            else:
                #Give warning not able to load
                print('No File')
                return False
        else:
            manager = QgsProject.instance().layoutManager()
            for layout in manager.printLayouts():
                if layout.name() == self.existingLayouts.currentText():
                    self.template = layout

        #find maps in template
        self.templateMaps = []
        for i in self.template.items():
            if isinstance(i, QgsLayoutItemMap):
                self.templateMaps.append(i)

        if len(self.templateMaps) == 0:
            #Give warning no maps in template
            print('No Maps')
            return False
        else:
            print(self.templateMaps)
            return True

    def loadExistingFile(self, item, fileType):
        file = QFileDialog.getOpenFileName(self,'Select File', '/home',fileType)
        if file[0] is not '':
            item.setText(file[0])

    def dynamicLayersList(self):
        layers = self.layers.copy()
        searchLists = [[],[],[]]
        searchLists[0] = self.createSearchList(self.tTree)
        searchLists[1] = self.createSearchList(self.eTree)
        searchLists[2] = self.createSearchList(self.sTree)

        for searchList in searchLists:
            layers = self.deepSearch(layers,searchList)


        self.previewList.clear()
        for layer in layers:
            self.previewList.addItem(layer.name())

    def loadQMS(self):
        #Read QMS file
        with open(QMSFile, newline='') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=','))
            headerLength = reader[0][1]


    def deepSearch(self, layers, searchList):
        output = []
        for search in searchList:
            research = []
            found = []
            if type(search) == list:
                for layer in layers:

                    if search[0] == self.otherItem:
                        search[0] = ''
                    if (search[0] == '') and (len(searchList) > 1):
                        negSearch = searchList.copy()
                        negSearch.remove(search)
                        if any(x[0] not in layer.name() for x in negSearch):
                            output.append(layer)
                            found.append(layer)
                    else:
                        if search[0] in layer.name():
                            research.append(layer)
                            found.append(layer)
                for layer in found:
                    layers.remove(layer)
                for item in self.deepSearch(research, search[1]):
                    output.append(item)
            else:

                for layer in layers:
                    if search == self.otherItem:
                        search = ''
                    if (search == '') and (len(searchList) > 1):
                        negSearch = searchList.copy()
                        negSearch.remove(search)
                        if any(x not in layer.name() for x in negSearch):
                            output.append(layer)
                            found.append(layer)
                    else:
                        if search in layer.name():
                            output.append(layer)
                            found.append(layer)
                for layer in found:
                    layers.remove(layer)



        return output

    def addDynamicItem(self,ty):
        self.additem_dlg = mbb_dialog_additem()
        self.additem_dlg.show()
        result = self.additem_dlg.exec_()
        if result:
            item = self.additem_dlg.coreText.text()
            if ty == 0:
                twi = QTreeWidgetItem(self.tTree,[item],0)
                #twi.addChild(QTreeWidgetItem([self.otherItem],0))
                #self.tTree.expandItem(twi)
            elif ty == 1:
                twi = QTreeWidgetItem(self.eTree,[item],0)
                #twi.addChild(QTreeWidgetItem([self.otherItem],0))
                #self.eTree.expandItem(twi)
            elif ty == 2:
                twi = QTreeWidgetItem(self.sTree,[item],0)
                twi.addChild(QTreeWidgetItem([self.otherItem],0))
                self.sTree.expandItem(twi)
            elif ty == 3:
                twi = self.sTree.currentItem()
                twi = QTreeWidgetItem(twi,[item],0)
                twi.addChild(QTreeWidgetItem([self.otherItem],0))
                self.sTree.expandItem(twi)
                self.sTree.expandItem(twi)

            self.dynamicLayersList()

    def removeDynamicItem(self,ty):
        if ty == 0:
            tw = self.tTree
        elif ty == 1:
            tw = self.eTree
        elif ty == 2:
            tw = self.sTree

        for item in tw.selectedItems():
            idx = tw.indexOfTopLevelItem(item)
            if idx != -1:
                tw.takeTopLevelItem(idx)
            else:
                twi = item.parent()
                idx = twi.indexOfChild(item)
                twi.takeChild(idx)


        self.dynamicLayersList()

    def createSearchList(self, treeWidget):
        items = []
        searchList = []
        for idx in range(treeWidget.topLevelItemCount()):
            items.append(treeWidget.topLevelItem(idx))
        searchList = self.createSearchLists(items)
        return searchList

    def createSearchLists(self, levelItems):
        searchList = []
        if any(item.childCount() != 0 for item in levelItems):
            for item in levelItems:
                if item.childCount() != 0 :
                    items = []
                    for idx in range(item.childCount()):
                        items.append(item.child(idx))
                    rList = self.createSearchLists(items)
                else:
                    rList = ['']

                searchList.append([item.text(0), rList])
        else:
            for item in levelItems:
                searchList.append(item.text(0))

        return searchList

    def load_all_layers(self, group, layers):
        for child in group:
            if isinstance(child, QgsLayerTreeLayer):
                layers.append(child)
            elif isinstance(child, QgsLayerTreeGroup):
                layers = self.load_all_layers(child.children(), layers)
        return layers
