# =============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================


# noinspection PyPackageRequirements
import wx

from gui.bitmap_loader import BitmapLoader
from service.fit import Fit
from .lists import FitList, TargetList
from .vector import VectorPicker, DirectionPicker


class GraphControlPanel(wx.Panel):

    def __init__(self, graphFrame, parent):
        super().__init__(parent)
        self.graphFrame = graphFrame
        self.inputs = {}

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        optsSizer = wx.BoxSizer(wx.HORIZONTAL)

        commonOptsSizer = wx.BoxSizer(wx.VERTICAL)
        ySubSelectionSizer = wx.BoxSizer(wx.HORIZONTAL)
        yText = wx.StaticText(self, wx.ID_ANY, 'Axis Y:')
        ySubSelectionSizer.Add(yText, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.ySubSelection = wx.Choice(self, wx.ID_ANY)
        self.ySubSelection.Bind(wx.EVT_CHOICE, self.OnYTypeUpdate)
        ySubSelectionSizer.Add(self.ySubSelection, 1, wx.EXPAND | wx.ALL, 0)
        commonOptsSizer.Add(ySubSelectionSizer, 0, wx.EXPAND | wx.ALL, 0)

        xSubSelectionSizer = wx.BoxSizer(wx.HORIZONTAL)
        xText = wx.StaticText(self, wx.ID_ANY, 'Axis X:')
        xSubSelectionSizer.Add(xText, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.xSubSelection = wx.Choice(self, wx.ID_ANY)
        self.xSubSelection.Bind(wx.EVT_CHOICE, self.OnXTypeUpdate)
        xSubSelectionSizer.Add(self.xSubSelection, 1, wx.EXPAND | wx.ALL, 0)
        commonOptsSizer.Add(xSubSelectionSizer, 0, wx.EXPAND | wx.TOP, 5)

        self.showY0Cb = wx.CheckBox(self, wx.ID_ANY, 'Always show Y = 0', wx.DefaultPosition, wx.DefaultSize, 0)
        self.showY0Cb.SetValue(True)
        self.showY0Cb.Bind(wx.EVT_CHECKBOX, self.OnShowY0Change)
        commonOptsSizer.Add(self.showY0Cb, 0, wx.EXPAND | wx.TOP, 5)
        optsSizer.Add(commonOptsSizer, 0, wx.EXPAND | wx.RIGHT, 10)

        graphOptsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inputsSizer = wx.BoxSizer(wx.VERTICAL)
        graphOptsSizer.Add(self.inputsSizer, 0, wx.EXPAND | wx.ALL, 0)

        self.srcVectorSizer = wx.BoxSizer(wx.VERTICAL)
        self.srcVectorLabel = wx.StaticText(self, wx.ID_ANY, '')
        self.srcVectorSizer.Add(self.srcVectorLabel, 0, wx.ALIGN_CENTER_HORIZONTAL| wx.BOTTOM, 5)
        self.srcVector = VectorPicker(self, style=wx.NO_BORDER, size=75, offset=90)
        self.srcVectorSizer.Add(self.srcVector, 0, wx.SHAPED | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        graphOptsSizer.Add(self.srcVectorSizer, 0, wx.EXPAND | wx.LEFT, 30)

        self.tgtVectorSizer = wx.BoxSizer(wx.VERTICAL)
        self.tgtVectorLabel = wx.StaticText(self, wx.ID_ANY, '')
        self.tgtVectorSizer.Add(self.tgtVectorLabel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 5)
        self.tgtVector = DirectionPicker(self, style=wx.NO_BORDER, size=75, offset=-90)
        self.tgtVectorSizer.Add(self.tgtVector, 0, wx.SHAPED | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        graphOptsSizer.Add(self.tgtVectorSizer, 0, wx.EXPAND | wx.LEFT, 10)

        optsSizer.Add(graphOptsSizer, 0, wx.EXPAND | wx.ALL, 0)
        mainSizer.Add(optsSizer, 0, wx.EXPAND | wx.ALL, 10)

        srcTgtSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fitList = FitList(graphFrame, self)
        self.fitList.SetMinSize((270, -1))
        srcTgtSizer.Add(self.fitList, 1, wx.EXPAND | wx.ALL, 0)
        self.targets = []
        self.targetList = TargetList(graphFrame, self)
        self.targetList.SetMinSize((270, -1))
        self.targetList.update(self.targets)
        srcTgtSizer.Add(self.targetList, 1, wx.EXPAND | wx.LEFT, 10)
        mainSizer.Add(srcTgtSizer, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)

        self.SetSizer(mainSizer)

        self.drawTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnDrawTimer, self.drawTimer)

    def updateControls(self):
        view = self.graphFrame.getView()
        self.ySubSelection.Clear()
        self.xSubSelection.Clear()
        for yDef in view.yDefs:
            self.ySubSelection.Append(self._formatLabel(yDef), (yDef.handle, yDef.unit))
        self.ySubSelection.SetSelection(0)
        for xDef in view.xDefs:
            self.xSubSelection.Append(self._formatLabel(xDef), (xDef.handle, xDef.unit))
        self.xSubSelection.SetSelection(0)

        # Vectors
        if view.srcVectorDef is not None:
            self.srcVectorLabel.SetLabel(view.srcVectorDef.label)
            self.srcVector.Show(True)
            self.srcVectorLabel.Show(True)
        else:
            self.srcVector.Show(False)
            self.srcVectorLabel.Show(False)
        if view.tgtVectorDef is not None:
            self.tgtVectorLabel.SetLabel(view.tgtVectorDef.label)
            self.tgtVector.Show(True)
            self.tgtVectorLabel.Show(True)
        else:
            self.tgtVector.Show(False)
            self.tgtVectorLabel.Show(False)

        # Target list
        self.targetList.Show(view.hasTargets)

        self.updateInputs()
        self.Layout()

    def updateInputs(self):
        # Clean up old inputs
        for children in self.inputs.values():
            for child in children:
                if child is not None:
                    child.Destroy()
        self.inputsSizer.Clear()
        self.inputs.clear()

        # Set up inputs from scratch
        view = self.graphFrame.getView()
        shownHandles = set()
        srcVectorDef = view.srcVectorDef
        if srcVectorDef is not None:
            shownHandles.add(srcVectorDef.lengthHandle)
            shownHandles.add(srcVectorDef.angleHandle)
        tgtVectorDef = view.tgtVectorDef
        if tgtVectorDef is not None:
            shownHandles.add(tgtVectorDef.lengthHandle)
            shownHandles.add(tgtVectorDef.angleHandle)
        selectedX = view.xDefMap[self.xType]
        for inputDef in (view.inputMap[selectedX.mainInput], *(i for i in view.inputs)):
            if (inputDef.handle, inputDef.unit) != selectedX.mainInput and inputDef.mainOnly:
                continue
            if inputDef.handle in shownHandles:
                continue
            shownHandles.add(inputDef.handle)
            # Handle UI input fields
            fieldSizer = wx.BoxSizer(wx.HORIZONTAL)
            fieldTextBox = wx.TextCtrl(self, wx.ID_ANY, style=0)
            fieldTextBox.Bind(wx.EVT_TEXT, self.OnFieldChanged)
            if inputDef.defaultValue is not None:
                inputDefault = inputDef.defaultValue
                if not isinstance(inputDefault, str):
                    inputDefault = ('%f' % inputDefault).rstrip('0')
                    if inputDefault[-1:] == '.':
                        inputDefault += '0'
                fieldTextBox.ChangeValue(inputDefault)
            fieldSizer.Add(fieldTextBox, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            fieldIcon = None
            if inputDef.iconID is not None:
                icon = BitmapLoader.getBitmap(inputDef.iconID, 'icons')
                if icon is not None:
                    fieldIcon = wx.StaticBitmap(self)
                    fieldIcon.SetBitmap(icon)
                    fieldSizer.Add(fieldIcon, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
            fieldLabel = wx.StaticText(self, wx.ID_ANY, self._formatLabel(inputDef))
            fieldSizer.Add(fieldLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
            self.inputs[(inputDef.handle, inputDef.unit)] = (fieldTextBox, fieldIcon, fieldLabel)
            self.inputsSizer.Add(fieldSizer, 0, wx.EXPAND | wx.BOTTOM, 5)

    def OnShowY0Change(self, event):
        event.Skip()
        self.graphFrame.draw()

    def OnYTypeUpdate(self, event):
        event.Skip()
        self.graphFrame.draw()

    def OnXTypeUpdate(self, event):
        event.Skip()
        self.updateInputs()
        self.Layout()
        self.graphFrame.draw()

    def OnFieldChanged(self, event):
        event.Skip()
        self.drawTimer.Stop()
        self.drawTimer.Start(Fit.getInstance().serviceFittingOptions['marketSearchDelay'], True)

    def OnDrawTimer(self, event):
        event.Skip()
        self.graphFrame.clearCache()
        self.graphFrame.draw()

    def getValues(self):
        values = {}
        return values

    @property
    def showY0(self):
        return self.showY0Cb.GetValue()

    @property
    def yType(self):
        return self.ySubSelection.GetClientData(self.ySubSelection.GetSelection())

    @property
    def xType(self):
        return self.xSubSelection.GetClientData(self.xSubSelection.GetSelection())

    def unbindExternalEvents(self):
        self.fitList.unbindExternalEvents()

    def _formatLabel(self, axisDef):
        if axisDef.unit is None:
            return axisDef.label
        return '{}, {}'.format(axisDef.label, axisDef.unit)
