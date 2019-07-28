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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

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
            validEntry = self.setupFiles()
        if i == 1:                          #Template
            validEntry = self.setupFiles()
        if i == 2:                          #Consistent
            validEntry = self.setupFiles()
        if i == 3:                          #Dynamic
            validEntry = self.dynamicLayersList()
        if i == 4:                          #Review
            validEntry = self.setupFiles()



        if validEntry:      #If valid entry (if not valid entry, do nothing else)
            if i < self.stackedWidget.count()-1:    #if before final sheet
                self.stackedWidget.setCurrentIndex(i + 1)   #move to next
                self.update_buttons()   #update the buttons
            else:
                self.accept()   #return to main run, do the generation

    def setupFiles(self):
        #If using existing template is it valid file
            #return False

        #If saving new copy is it valid location
            #return False

        #Take template (default or existing) and load in data



        return True

    def dynamicLayersList(self):
        layers = ['FloodModel_BASE_0020_d_Max', 'FloodModel_BASE_0020_h_Max', 'FloodModel_BASE_0020_TMax_h', 'FloodModel_BASE_0020_TMax_V', 'FloodModel_BASE_0020_V_Max', 'FloodModel_BASE_0020_ZUK0_Max', 'FloodModel_BASE_0020_ZUK1_Max', 'FloodModel_BASE_0100_d_Max', 'FloodModel_BASE_0100_h_Max', 'FloodModel_BASE_0100_TMax_h', 'FloodModel_BASE_0100_TMax_V', 'FloodModel_BASE_0100_V_Max', 'FloodModel_BASE_0100_ZUK0_Max', 'FloodModel_BASE_0100_ZUK1_Max', 'FloodModel_BASE_C100_d_025_46', 'FloodModel_BASE_C100_d_Max', 'FloodModel_BASE_C100_h_025_46', 'FloodModel_BASE_C100_h_Max', 'FloodModel_BASE_C100_MB1_025_46', 'FloodModel_BASE_C100_q_025_46', 'FloodModel_BASE_C100_TMax_h', 'FloodModel_BASE_C100_TMax_V', 'FloodModel_BASE_C100_V_025_46', 'FloodModel_BASE_C100_V_Max', 'FloodModel_BASE_C100_ZUK0_025_46', 'FloodModel_BASE_C100_ZUK0_Max', 'FloodModel_BASE_C100_ZUK1_025_46', 'FloodModel_BASE_C100_ZUK1_Max', 'FloodModel_DEVELOPED_0100_d_Max', 'FloodModel_DEVELOPED_0100_h_Max', 'FloodModel_DEVELOPED_0100_TMax_h', 'FloodModel_DEVELOPED_0100_TMax_V', 'FloodModel_DEVELOPED_0100_V_Max', 'FloodModel_DEVELOPED_0100_ZUK0_Max', 'FloodModel_DEVELOPED_0100_ZUK1_Max', 'FloodModel_DEVELOPED-DEFENDED_0100_d_Max', 'FloodModel_DEVELOPED-DEFENDED_0100_h_Max', 'FloodModel_DEVELOPED-DEFENDED_0100_TMax_h', 'FloodModel_DEVELOPED-DEFENDED_0100_TMax_V', 'FloodModel_DEVELOPED-DEFENDED_0100_V_Max', 'FloodModel_DEVELOPED-DEFENDED_0100_ZUK0_Max', 'FloodModel_DEVELOPED-DEFENDED_0100_ZUK1_Max', 'FloodModel_DEVELOPED-DEFENDED_C100_d_Max', 'FloodModel_DEVELOPED-DEFENDED_C100_h_Max', 'FloodModel_DEVELOPED-DEFENDED_C100_TMax_h', 'FloodModel_DEVELOPED-DEFENDED_C100_TMax_V', 'FloodModel_DEVELOPED-DEFENDED_C100_V_Max', 'FloodModel_DEVELOPED-DEFENDED_C100_ZUK0_Max', 'FloodModel_DEVELOPED-DEFENDED_C100_ZUK1_Max']
        searchLists = []
        searchLists.append(['h_Max', 'd_Max'])
        searchLists.append(['0020', '0100', 'C100'])
        searchLists.append([['BASE',['']],['DEVELOPED',['','DEFENDED']]])

        for searchList in searchLists:
            layers = self.deepSearch(layers,searchList)
            #print(layers)
        print('Final')
        print(layers)
        return true

    def deepSearch(self, layers, searchList):
        output = []
        for search in searchList:
            research = []
            found = []
            if type(search) == list:
                for layer in layers:
                    if (search[0] == '') and (len(searchList) > 1):
                        negSearch = searchList.copy()
                        negSearch.remove(search)
                        if any(x[0] not in layer for x in negSearch):
                            output.append(layer)
                            found.append(layer)
                    else:
                        if search[0] in layer:
                            research.append(layer)
                            found.append(layer)
                for layer in found:
                    layers.remove(layer)
                for item in self.deepSearch(research, search[1]):
                    output.append(item)
            else:

                for layer in layers:
                    if (search == '') and (len(searchList) > 1):
                        negSearch = searchList.copy()
                        negSearch.remove(search)
                        if any(x not in layer for x in negSearch):
                            output.append(layer)
                            found.append(layer)
                    else:
                        if search in layer:
                            output.append(layer)
                            found.append(layer)
                for layer in found:
                    layers.remove(layer)



        return output


    def load_all_layers(self, group, layers):
        for child in group:
            if isinstance(child, QgsLayerTreeLayer):
                layers.append(child)
            elif isinstance(child, QgsLayerTreeGroup):
                layers = self.load_all_layers(child.children(), layers)
        return layers
