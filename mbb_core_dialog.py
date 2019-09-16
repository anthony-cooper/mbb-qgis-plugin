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
from .mbb_core_dialog_addmap import mbb_dialog_addmap



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

        self.addCriteria.clicked.connect(lambda: self.addCriteriaTab())
        self.addProperty.clicked.connect(lambda: self.addPropertyItem())
        self.removeCriteria.clicked.connect(lambda: self.removeCriteriaTab())
        self.removeProperty.clicked.connect(lambda: self.removePropertyItem())
        self.upCriteria.clicked.connect(lambda: self.moveUpCriteriaTab())
        self.upProperty.clicked.connect(lambda: self.moveUpPropertyItem())

        self.addMap.clicked.connect(lambda: self.addMapItem())
        self.removeMap.clicked.connect(lambda: self.removeMapItem())
        self.upMap.clicked.connect(lambda: self.moveUpMapItem())


        self.existingTemplateBrowser.clicked.connect(lambda: self.loadExistingFile(self.existingTemplate, 'QGIS Print Composer Template (*.qpt)'))


        self.otherItem = 'All (Other) Items'

        #defaults for setup file


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
        name = (self.stackedWidget.currentWidget()).objectName()
        i = self.stackedWidget.currentIndex()
        validEntry = False

        #Check valid entry for sheet #, and prep next sheet
        if name == 'Setup':                                    #Setup
            validEntry = self.setup()
        if name == 'Template':                                 #Template
            validEntry = self.setupTemplate()
            if self.criteriaTabs.count() == 0:
                self.addCriteriaTab()
        if name == 'Dynamic':                                  #Lead Dynamic Layer
            validEntry = self.dynamicLayersList()
        if name == 'DynamicDetails':                           #Dynamic details
            validEntry = self.confirmDynamicDetails()
            validEntry = self.selectMapItems()
        if name == 'Maps':                                     #Maps
            validEntry = self.confirmMapItems()



        if validEntry:      #If valid entry (if not valid entry, do nothing else)
            if i < self.stackedWidget.count()-1:    #if before final sheet
                self.stackedWidget.setCurrentIndex(i + 1)   #move to next
                self.update_buttons()   #update the buttons
            else:
                self.writeSetupFile()
                if self.newLayout: #Check if new layout and load if neccessary
                    manager = QgsProject.instance().layoutManager()
                    manager.addLayout(self.template)

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
        #self.layers = self.load_all_layers(QgsProject.instance().layerTreeRoot().children(), self.layers)
        lyrs = QgsProject.instance().mapLayers()
        for layer_id, layer in lyrs.items():
            self.layers.append([layer,[]])



        # Fetch the current project layouts
        manager = QgsProject.instance().layoutManager()
        self.allLayoutNames = []

        if len(manager.printLayouts()) == 0:
            self.existingLayout.setCheckable(False)
            self.existingLayout.setChecked(False)
        else:
            self.existingLayouts.clear()
            self.existingLayout.setCheckable(True)
            for layout in manager.printLayouts():
                self.allLayoutNames.append(layout.name())
            self.existingLayouts.addItems(self.allLayoutNames)
        return True

    def writeSetupFile(self):
        #Prep header
        headerQMS = []
        headerQMS.append(['<<HEADER>>', 3])
        headerQMS.extend(self.mapsDetailsQMS)
        headerQMS.append(['<<END OF HEADER>>'])
        self.headerLength = len(headerQMS)
        headerQMS[0][1] = self.headerLength

        layersHeaderQMS = []
        layersHeaderQMS.extend(self.itemsHeaderQMS)
        layersHeaderQMS.extend(self.mapsHeaderQMS)

        self.generateSheetsList()

        if os.path.exists(os.path.join(self.setupPath, self.setupName + ".QMapSetup")):
            os.remove(os.path.join(self.setupPath, self.setupName + ".QMapSetup"))

        with open(os.path.join(self.setupPath, self.setupName + ".QMapSetup"), 'w+', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(headerQMS)
            writer.writerow(layersHeaderQMS)
            writer.writerows(self.mapSheetsQMS)

    def generateSheetsList(self):
        self.mapSheetsQMS = []
        #for location in locations:
        for layer in self.dynamicLayers:
            details = [123,456,layer.name(), 'Dynamic Layer']
            for map in self.templateMaps:
                details.extend([25000, 15, 'layer'+'|'+'dylayer'])
            self.mapSheetsQMS.append(details)

    def addCriteriaTab(self):
        self.additem_dlg = mbb_dialog_additem()
        self.additem_dlg.show()
        result = self.additem_dlg.exec_()
        if result:
            criteria = self.additem_dlg.coreText.text()
            tab = QWidget()
            tabTree = QTreeWidget()
            #print(tabTree)
            tabLayout = QVBoxLayout()

            tabLayout.addWidget(tabTree)
            tabLayout.setSizeConstraint(QLayout.SetFixedSize)
            tabTree.setFixedWidth(810)
            tabTree.setFixedHeight(300)
            tabTree.setColumnCount(2)
            tabTree.setHeaderLabels(['Search Text', 'Written Text'])
            tab.setLayout(tabLayout)
            self.criteriaTabs.insertTab(self.criteriaTabs.count(), tab, criteria)
            #print(tab.children())
            self.dynamicLayersList()

    def removeCriteriaTab(self):
        if self.criteriaTabs.count() > 1:
            self.criteriaTabs.removeTab(self.criteriaTabs.currentIndex())
            self.dynamicLayersList()

    def moveUpCriteriaTab(self):
        loc = self.criteriaTabs.currentIndex()
        if loc > 0:
            name = self.criteriaTabs.tabText(loc)
            widget = self.criteriaTabs.currentWidget()
            self.criteriaTabs.removeTab(loc)
            self.criteriaTabs.insertTab(loc - 1, widget,name)
            self.dynamicLayersList()

    def addPropertyItem(self):
        self.additem_dlg = mbb_dialog_additem()
        self.additem_dlg.show()
        result = self.additem_dlg.exec_()
        if result:
            item = self.additem_dlg.coreText.text()
            alt = self.additem_dlg.altText.text()
            tab = self.criteriaTabs.currentWidget()
            # print(tab)
            # tabLayout = tab.layout()
            # print(tabLayout)
            treeWidget = tab.children()[1]
            #print(treeWidget)
            if len(treeWidget.selectedItems()) == 0:#item not selected:
                twi = QTreeWidgetItem(treeWidget,[item, alt],0)
                twi.addChild(QTreeWidgetItem([self.otherItem, alt],0))
                treeWidget.expandItem(twi)
            else: #item selected:
                twi = treeWidget.currentItem()
                twi = QTreeWidgetItem(twi,[item, alt],0)
                twi.addChild(QTreeWidgetItem([self.otherItem, alt],0))
                treeWidget.expandItem(twi)


            self.dynamicLayersList()

    def removePropertyItem(self):
        tab = self.criteriaTabs.currentWidget()
        tw = tab.children()[1]

        for item in tw.selectedItems():
            idx = tw.indexOfTopLevelItem(item)
            if idx != -1:
                tw.takeTopLevelItem(idx)
            else:
                twi = item.parent()
                idx = twi.indexOfChild(item)
                twi.takeChild(idx)


        self.dynamicLayersList()

    def moveUpPropertyItem(self):
        tab = self.criteriaTabs.currentWidget()
        tw = tab.children()[1]

        for item in tw.selectedItems():
            idx = tw.indexOfTopLevelItem(item)
            if idx != -1:
                if idx > 0:
                    item = tw.takeTopLevelItem(idx)
                    tw.insertTopLevelItem(idx - 1, item)
            else:
                twi = item.parent()
                idx = twi.indexOfChild(item)
                if idx > 0:
                    item = twi.takeChild(idx)
                    twi.insertChild(idx - 1, item)


        self.dynamicLayersList()


    def returnValues(self):

        return self.headerLength, os.path.join(self.setupPath, self.setupName + ".QMapSetup"), self.template, self.templateMaps

    def setupTemplate(self):
        self.newLayout = self.layoutTemplate.isChecked()
        if self.newLayout:
            if (self.newLayoutName.text() == '') or (self.newLayoutName.text() in self.allLayoutNames):
                print('Invalid Layout Name')
                return False


            if os.path.exists(self.existingTemplate.text()):
                self.template = QgsPrintLayout(QgsProject.instance())
                with open(self.existingTemplate.text()) as f:
                    template_content = f.read()
                doc = QDomDocument()
                doc.setContent(template_content)

                # adding to existing items
                self.template.loadFromTemplate(doc, QgsReadWriteContext())

                self.template.setName(self.newLayoutName.text())

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
            #print(self.templateMaps)


            return True

    def loadExistingFile(self, item, fileType):
        file = QFileDialog.getOpenFileName(self,'Select File', '/home',fileType)
        if file[0] is not '':
            item.setText(file[0])

    def dynamicLayersList(self):
        self.dynamicLayers = []
        layers = self.layers.copy()
        searchLists = []
        for i in range(0, self.criteriaTabs.count()):
            self.mapItems.removeTab(i)
            tab = self.criteriaTabs.widget(i)
            treeWidget = tab.children()[1]
            searchList = self.createSearchList(treeWidget)
            #searchLists.append(searchList)

        #print(searchLists)
        #searchLists[0] = self.createSearchList(self.tTree)
        #searchLists[1] = self.createSearchList(self.eTree)
        #searchLists[2] = self.createSearchList(self.sTree)

        #for searchList in searchLists:
            layers = self.deepSearch(layers,searchList)


        self.previewTree.clear()
        for layer in layers:
            #print(layer)
            twi = QTreeWidgetItem(self.previewTree,[layer[0].name()],0)
            print(layer[1])
        self.dynamicLayers = layers
        if len(self.dynamicLayers) > 0:
            return True
        else:
            print('No Layers')

    def confirmDynamicDetails(self):
        self.itemsHeaderQMS = []
        self.itemsHeaderQMS.extend(['easting', 'northing', 'dynamicLayer', 'pageName'])

    def loadQMS(self):
        #Read QMS file
        with open(QMSFile, newline='') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=','))
            headerLength = reader[0][1]

    def selectMapItems(self):
        for i in range(0, self.mapItems.count()  - 1):
            self.mapItems.removeTab(i)

        for mapItem in self.templateMaps:
            tab = QWidget()
            tabTree = QTreeWidget()
            tabLayout = QVBoxLayout()
            tabLayout.addWidget(tabTree)
            tabLayout.setSizeConstraint(QLayout.SetFixedSize)
            tabTree.setFixedWidth(810)
            tabTree.setFixedHeight(550)
            tabTree.setColumnCount(2)
            tabTree.setHeaderLabels(['Layer Name', 'Included in Legend'])
            tab.setLayout(tabLayout)
            self.mapItems.insertTab(self.mapItems.count(), tab, mapItem.displayName())


        return True

    def addMapItem(self):
        self.addmap_dlg = mbb_dialog_addmap()
        layerList = self.addmap_dlg.layerList
        layers = QgsProject.instance().mapLayers()
        layerList.clear()
        layerList.addItem('<><> LEAD DYNAMIC LAYER <><>')
        for layer_id, layer in layers.items():
            layerList.addItem(layer.name())



        self.addmap_dlg.show()
        result = self.addmap_dlg.exec_()
        if result:
            tab = self.mapItems.currentWidget()
            treeWidget = tab.children()[1]
            for layer in layerList.selectedItems():
                item = layer.text()
                twi = QTreeWidgetItem(treeWidget,[item],0)


    def removeMapItem(self):
        tab = self.mapItems.currentWidget()
        tw = tab.children()[1]

        for item in tw.selectedItems():
            idx = tw.indexOfTopLevelItem(item)
            if idx != -1:
                tw.takeTopLevelItem(idx)
            else:
                twi = item.parent()
                idx = twi.indexOfChild(item)
                twi.takeChild(idx)

    def moveUpMapItem(self):
        tab = self.mapItems.currentWidget()
        tw = tab.children()[1]

        for item in tw.selectedItems():
            idx = tw.indexOfTopLevelItem(item)
            if idx != -1:
                if idx > 0:
                    item = tw.takeTopLevelItem(idx)
                    tw.insertTopLevelItem(idx - 1, item)
            else:
                twi = item.parent()
                idx = twi.indexOfChild(item)
                if idx > 0:
                    item = twi.takeChild(idx)
                    twi.insertChild(idx - 1, item)


    def confirmMapItems(self):
        self.mapsHeaderQMS = []
        self.mapsDetailsQMS = []

        for map in self.templateMaps:
            self.mapsHeaderQMS.extend([map.displayName() + '_Scale',  map.displayName() + '_Rotation', map.displayName() + '_Layers'])
            self.mapsDetailsQMS.append([map.displayName])
        return True


    def deepSearch(self, layers, searchList):
        #print(layers)
        #print(searchList)
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
                        if any(x[0] not in layer[0].name() for x in negSearch):
                            output.append([layer[0],[search]])
                            found.append(layer)
                    else:
                        if search[0] in layer[0].name():
                            research.append(layer)
                            found.append(layer)
                for layer in found:
                    layers.remove(layer)
                for item in self.deepSearch(research, search[1]):
                    output.append([item[0], [search[1]]])
            else:

                for layer in layers:
                    if search == self.otherItem:
                        search = ''
                    if (search == '') and (len(searchList) > 1):
                        negSearch = searchList.copy()
                        negSearch.remove(search)
                        if any(x not in layer[0].name() for x in negSearch):
                            output.append([layer[0], [search]])
                            found.append(layer)
                    else:
                        if search in layer[0].name():
                            output.append([layer[0], [search]])
                            found.append(layer)
                for layer in found:
                    layers.remove(layer)


        #print(output)
        return output

    def createSearchList(self, treeWidget):
        items = []
        searchList = []
        for idx in range(treeWidget.topLevelItemCount()):
            items.append(treeWidget.topLevelItem(idx))
        #print(items)
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
                layers.append(child,[])
            elif isinstance(child, QgsLayerTreeGroup):
                layers = self.load_all_layers(child.children(), layers)
        return layers
