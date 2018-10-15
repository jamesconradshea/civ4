#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2010-2018 by James Conrad Shea (Duckstab)
# This software is made available under the terms of the Creative Commons 
# Attribution-NonCommercial-ShareAlike 2.0 License
# See
#   http://creativecommons.org/licenses/by-nc-sa/2.0/legalcode
# for full terms. 

from btsColorEditorConfig import *

from Tkinter import *
from xml.dom.minidom import *
from os import path, makedirs, utime

import random
import math
import shutil
import string

S = [
    0.0, 1.0 / 6, 2.0 / 6, 3.0 / 6, 4.0 / 6, 5.0 / 6, 6.0 / 6
    ]
VERY_DARK = 0.1
VERY_DESATURATED = 0.1
DARK = 0.3
DESATURATED = 0.3
VERY_LIGHT = 0.9
LIGHT = 0.7
ONE_LEVEL = 1.0 / 256
MIN_DELTA = 8

class Color:

    def __init__(self, r, g, b):
        self.iRed = r
        self.iGreen = g
        self.iBlue = b
        self.fRed = r / 255.0
        self.fGreen = g / 255.0
        self.fBlue = b / 255.0
        self.asString = "#" + ("%02x%02x%02x" % (self.iRed, self.iGreen, self.iBlue))
        temp = [r, g, b]
        tempSorted = sorted(temp)
        profile = [None, None, None]
        for i in range(3):
            for j in range(3):
                if (tempSorted[i] == temp[j]):
                    profile[i] = j
        min = profile[0]
        mid = profile[1]
        max = profile[2]
        frgb = (self.fRed, self.fGreen, self.fBlue)
        l = frgb[min]
        sMaxComponent = frgb[max] - l
        s = sMaxComponent
        sMidComponent = frgb[mid] - l
        if (sMaxComponent != 0.0):
            delta = S[1] * sMidComponent / sMaxComponent
        else:
            delta = 0
        if (max == 0):
            if (mid == 1):
                h = S[0] + delta
            else:
                h = S[6] - delta
        elif (max == 1):
            if (mid == 0):
                h = S[2] - delta
            else:
                h = S[2] + delta
        else:
            if (mid == 0):
                h = S[4] + delta
            else:
                h = S[4] - delta
        self.hue = h
        self.lightness = l
        self.saturation = s

    def __repr__(self):
        return self.asString

    def __eq__(self, other):
        return self.asString == other.asString

    def __ne__(self, other):
        return self.asString != other.asString

    @classmethod
    def fromFloats(cls, fr, fg, fb):
        return Color(int(fr * 255), int(fg * 255), int(fb * 255))

    @classmethod
    def fromInt(cls, i):
        return Color((i >> 16) & 0xff, (i >> 8) & 0xff, i & 0xff)

    @classmethod
    def parse(cls, s):
        return Color.fromInt(int(s[1:], 16))

    @classmethod
    def randomColor(cls):
        return Color.fromInt(random.randint(0, (256*256*256)-1))

    def rgb(self):
        return (self.iRed, self.iGreen, self.iBlue)

    def frgb(self):
        return (self.fRed, self.fGreen, self.fBlue)

    def yuv(self):
        y = 0.299*self.fRed + 0.587*self.fGreen + 0.114*self.fBlue
        u = -0.14713*self.fRed + (-0.28886)*self.fGreen + 0.436*self.fBlue
        v = 0.615*self.fRed + (-0.51499)*self.fGreen + (-0.10001)*self.fBlue
        return (y, u, v)        

    def distance(self, other):
        (sy, su, sv) = self.yuv()
        (oy, ou, ov) = other.yuv();
        dy = sy - oy
        du = su - ou
        dv = sv - ov
        # The color metric used in previous versions went from 0 to
        # 765, so this scale factor just makes it compatible with the
        # heuristics used elsewhere 
        return 255 * math.sqrt(dy*dy + du*du + dv*dv)

    def isLight(self):
        return self.lightness >= LIGHT

    def isVeryLight(self):
        return self.lightness >= VERY_LIGHT

    def isDark(self):
        return self.lightness <= DARK

    def isVeryDark(self):
        return self.lightness <= VERY_DARK

    def darkenedTo(self, l):
        result = self
        oldL = result.lightness
        if (l < oldL):
            diff = oldL - l
            frgb = [self.fRed, self.fGreen, self.fBlue]
            for i in range(3):
                frgb[i] -= diff
            result = Color.fromFloats(frgb[0], frgb[1], frgb[2])
            while (result.lightness > l):
                for i in range(3):
                    frgb[i] = max(0.0, rgb[i] - ONE_LEVEL)
                result = Color.fromFloats(frgb[0], frgb[1], frgb[2])
        return result

    def lightenedTo(self, l):
        result = self
        oldL = result.lightness
        if (l > oldL):
            sRemainder = 1.0 - l
            frgb = (self.fRed, self.fGreen, self.fBlue)
            frgbNew = [0.0, 0.0, 0.0]
            d = 1.0 - oldL
            for i in range(3):
                if (d == 0.0):
                    frgbNew[i] = l
                else:
                    frgbNew[i] = (l + sRemainder * ((frgb[i] - oldL) / d))
            result = Color.fromFloats(frgb[0], frgb[1], frgb[2])
            while (result.lightness < l):
                for i in range(3):
                    frgbNew[i] = min(1.0, frgbNew[i] + ONE_LEVEL)
                result = Color.fromFloats(frgbNew[0], frgbNew[1], frgbNew[2])
        return result

    def desaturatedTo(self, s):
        result = self
        oldS = result.saturation
        if (s < oldS):
            frgb = self.frgb()
            frgbNew = [0.0, 0.0, 0.0]
            l = self.lightness
            factor = (s / oldS)
            for i in range(3):
                frgbNew[i] = l + factor * (frgb[i] - l)
            result = Color.fromFloats(frgbNew[0], frgbNew[1], frgbNew[2])
            while (result.saturation > s):
                for i in range(3):
                    frgbNew[i] = max(0.0, frgbNew[i] - ONE_LEVEL)
                result = Color.fromFloats(frgbNew[0], frgbNew[1], frgbNew[2])
        return result

    def movedFrom(self, other, d):
        if (self.distance(other) >= d):
            return self
        if (other.isLight()):
            for level in [LIGHT, DARK, VERY_DARK]:
                temp = self.darkenedTo(level)
                if (temp.distance(other) >= d):
                    return temp
        elif (other.isDark()):
            for level in [DARK, LIGHT, VERY_LIGHT]:
                temp = self.lightenedTo(level)
                if (temp.distance(other) >= d):
                    return temp
        if (self.distance(BLACK) >= self.distance(WHITE)):
            return BLACK
        else:
            return WHITE

    def nudgedFrom(self, other):
        rgb = list(self.rgb())
        otherRgb = list(other.rgb())
        iOffset = random.randint(0, 2)
        for i in range(3):
            ii = (i + iOffset) % 3
            delta = max(MIN_DELTA, abs(rgb[ii] - otherRgb[ii]) / 10)
            if (rgb[ii] < otherRgb[ii]):
                rgb[ii] = max(0, rgb[ii] - delta)
            elif (rgb[ii] > otherRgb[ii]):
                rgb[ii] = min(255, rgb[ii] + delta)
            elif (rgb[ii] < 128):
                rgb[ii] += MIN_DELTA
            else:
                rgb[ii] -= MIN_DELTA
        return Color(rgb[0], rgb[1], rgb[2])        

BLACK = Color.fromInt(0)
WHITE = Color.fromInt(0xffffff)

class XmlMap:

    def __init__(self, document, elementName, keyNodeName):
        self.data = dict()
        self.element = elementName
        self.keyNode = keyNodeName
        for elem in document.getElementsByTagName(elementName):
            key = elem.getElementsByTagName(keyNodeName)[0].childNodes[0].nodeValue
            self.put(key, elem)

    def get(self, key):
        if (key in self.data):
            return self.data[key]
        else:
            return None

    def put(self, key, elem):
        if (key not in self.data):
            self.data[key] = elem

    def merge(self, document):
        for elem in document.getElementsByTagName(self.element):
            key = elem.getElementsByTagName(self.keyNode)[0].childNodes[0].nodeValue
            self.data[key] = elem

    def keys(self):
        return self.data.keys()

    def __str__(self):
        return self.data.__str__()
    
def findPath(relativePath):
    result = path.join(COLOR_EDITOR_CUSTOM_ASSETS, relativePath)
    if (path.exists(result)):
        return result
    for directory in COLOR_EDITOR_ASSET_PATH.split(';'):
        result = path.join(directory, relativePath)
        if (path.exists(result)):
            return result
    return None

# Wrapper around minidom's parser that helps handle Unicode
def parseXmlFile(filename):
    f = open(filename, 'r')
    s = f.read()
    ss = s.encode('us-ascii', 'xmlcharrefreplace')
    doc = parseString(ss)
    return doc

def writeXmlFile(doc, filename):
    o = open(filename, 'w')
    s = doc.toxml().encode('us-ascii', 'xmlcharrefreplace')
    o.write(s)
    o.close()
    utime(filename, None)

class ColorInfo:

    def __init__(self, civInfo):
        # Maps new color names to their old-school equivalents
        self.aliases = dict()
        self.civInfo = civInfo
        self.relpath = "xml/interface/CIV4PlayerColorInfos.xml"
        filename = findPath(self.relpath)
        if (filename):
            self.document = parseXmlFile(filename)
            self.documentMap = XmlMap(self.document, "PlayerColorInfo", "Type")
            # Back up original color info
            if (self.isOldSchoolColorInfo()):
                shutil.copy(filename, path.join(COLOR_EDITOR_CUSTOM_ASSETS, self.relpath + "-orig"))
        for civ in self.civInfo.getCivs():
            prefix = "COLOR_EDITOR_" + civ[13:] + "_"
            civColorName = civInfo.getPlayerColorName(civ)
            primary = prefix + "PRIMARY"
            secondary = prefix + "SECONDARY"
            text = prefix + "TEXT"
            pcn = self.getPrimaryColorName(civColorName)
            if pcn is None:
                doc = self.document
                colorInfosElem = doc.getElementsByTagName("PlayerColorInfos")[0]
                colorInfoElem = doc.createElement("PlayerColorInfo")
                colorInfosElem.appendChild(colorInfoElem)
                typeElem = doc.createElement("Type")
                colorInfoElem.appendChild(typeElem)
                typeText = doc.createTextNode(civColorName)
                typeElem.appendChild(typeText)
                primaryElem = doc.createElement("ColorTypePrimary")
                colorInfoElem.appendChild(primaryElem)
                primaryText = doc.createTextNode(primary)
                primaryElem.appendChild(primaryText)
                secondaryElem = doc.createElement("ColorTypeSecondary")
                colorInfoElem.appendChild(secondaryElem)
                secondaryText = doc.createTextNode(secondary)
                secondaryElem.appendChild(secondaryText)
                textElem = doc.createElement("TextColorType")
                colorInfoElem.appendChild(textElem)
                textText = doc.createTextNode(text)
                textElem.appendChild(textText)
                self.documentMap = XmlMap(self.document, "PlayerColorInfo", "Type")
            self.setAlias(primary, self.getPrimaryColorName(civColorName))
            self.setPrimaryColorName(civColorName, primary)
            self.setAlias(secondary, self.getSecondaryColorName(civColorName))
            self.setSecondaryColorName(civColorName, secondary)
            self.setAlias(text, self.getTextColorName(civColorName))
            self.setTextColorName(civColorName, text)

    def getColorName(self, playerColorSymbol, colorType):
        elem = self.documentMap.get(playerColorSymbol)
        if elem:
            return elem.getElementsByTagName(colorType)[0].childNodes[0].nodeValue
        else:
            return None

    def setColorName(self, playerColorSymbol, colorType, value):
        elem = self.documentMap.get(playerColorSymbol)
        elem.getElementsByTagName(colorType)[0].childNodes[0].nodeValue = value

    def getPrimaryColorName(self, playerColorSymbol):
        return self.getColorName(playerColorSymbol, "ColorTypePrimary")

    def setPrimaryColorName(self, playerColorSymbol, value):
        self.setColorName(playerColorSymbol, "ColorTypePrimary", value)

    def getSecondaryColorName(self, playerColorSymbol):
        return self.getColorName(playerColorSymbol, "ColorTypeSecondary")

    def setSecondaryColorName(self, playerColorSymbol, value):
        self.setColorName(playerColorSymbol, "ColorTypeSecondary", value)

    def getTextColorName(self, playerColorSymbol):
        return self.getColorName(playerColorSymbol, "TextColorType")

    def setTextColorName(self, playerColorSymbol, value):
        self.setColorName(playerColorSymbol, "TextColorType", value)

    def isOldSchoolColorInfo(self):
        return ("COLOR_PLAYER_BLACK" == self.getPrimaryColorName("PLAYERCOLOR_BLACK"))

    def setAlias(self, newName, oldName):
        if (newName != oldName):
            self.aliases[newName] = oldName

    def getAlias(self, newName):
        name = newName
        while (name in self.aliases):
            name = self.aliases[name]
        return name

    def save(self):
        filename = path.join(COLOR_EDITOR_CUSTOM_ASSETS, self.relpath)
        writeXmlFile(self.document, filename)

class ColorVals:

    def __init__(self, colorInfo):
        self.colorInfo = colorInfo
        self.civInfo = colorInfo.civInfo
        self.colors = dict()
        self.relpath = "xml/interface/CIV4ColorVals.xml"
        filename = findPath(self.relpath)
        if (filename):
            self.document = parseXmlFile(filename)
            self.documentMap = XmlMap(self.document, "ColorVal", "Type")
            # Back up original color vals
            if (self.isOldSchoolColorVals()):
                shutil.copy(filename, path.join(COLOR_EDITOR_CUSTOM_ASSETS, self.relpath + "-orig"))
            for civ in self.civInfo.getCivs():
                playerColorName = self.civInfo.getPlayerColorName(civ)
                sourcePlayerColorName = self.civInfo.getRenamedColor(playerColorName)
                for colorType in ["ColorTypePrimary", "ColorTypeSecondary", "TextColorType"]:
                    colorName = self.colorInfo.getColorName(playerColorName, colorType)
                    if sourcePlayerColorName is None:
                        colorElem = self.getOrCreateColorElem(colorName)
                    else:
                        # This means two or more civs originally shared the same player color; split them
                        sourceColorName = self.colorInfo.getColorName(sourcePlayerColorName, colorType)
                        sourceColorElem = self.getOrCreateColorElem(sourceColorName)
                        colorElem = self.copyColorElem(colorName, sourceColorElem)
                        self.documentMap.put(colorName, colorElem)
                    color = self.colorFromElem(colorElem)
                    self.colors[colorName] = color
                        

    def getOrCreateColorElem(self, colorName):
        colorElem = self.documentMap.get(colorName)
        if (not colorElem):
            oldName = self.colorInfo.getAlias(colorName)
            colorElem = self.documentMap.get(oldName)
            if (colorElem):
                colorElem = self.copyColorElem(colorName, colorElem)
            else:
                return None
            self.documentMap.put(colorName, colorElem)
        return colorElem
                
    def isOldSchoolColorVals(self):
        return (not self.documentMap.get("COLOR_EDITOR_BARBARIAN_PRIMARY"))

    def copyColorElem(self, colorName, colorElem):
        doc = self.document
        colorValsElem = doc.getElementsByTagName("ColorVals")[0]
        colorValElem = doc.createElement("ColorVal")
        colorValsElem.appendChild(colorValElem)
        typeElem = doc.createElement("Type")
        colorValElem.appendChild(typeElem)
        typeText = doc.createTextNode(colorName)
        typeElem.appendChild(typeText)
        fRedElem = doc.createElement("fRed")
        colorValElem.appendChild(fRedElem)
        fRedText = doc.createTextNode(colorElem.getElementsByTagName("fRed")[0].childNodes[0].nodeValue)
        fRedElem.appendChild(fRedText)
        fGreenElem = doc.createElement("fGreen")
        colorValElem.appendChild(fGreenElem)
        fGreenText = doc.createTextNode(colorElem.getElementsByTagName("fGreen")[0].childNodes[0].nodeValue)
        fGreenElem.appendChild(fGreenText)
        fBlueElem = doc.createElement("fBlue")
        colorValElem.appendChild(fBlueElem)
        fBlueText = doc.createTextNode(colorElem.getElementsByTagName("fBlue")[0].childNodes[0].nodeValue)
        fBlueElem.appendChild(fBlueText)
        fAlphaElem = doc.createElement("fAlpha")
        colorValElem.appendChild(fAlphaElem)
        fAlphaText = doc.createTextNode("1.000")
        fAlphaElem.appendChild(fAlphaText)
        return colorValElem

    def colorFromElem(self, colorElem):
        red = float(colorElem.getElementsByTagName("fRed")[0].childNodes[0].nodeValue)
        green = float(colorElem.getElementsByTagName("fGreen")[0].childNodes[0].nodeValue)                                     
        blue = float(colorElem.getElementsByTagName("fBlue")[0].childNodes[0].nodeValue)
        return Color.fromFloats(red, green, blue)

    def getColor(self, colorName):
        return self.colors[colorName]

    def setColor(self, colorName, color):
        self.colors[colorName] = color
        (fred, fgreen, fblue) = color.frgb()
        colorElem = self.getOrCreateColorElem(colorName)
        colorElem.getElementsByTagName("fRed")[0].childNodes[0].nodeValue = ("%1.3f" % fred)
        colorElem.getElementsByTagName("fGreen")[0].childNodes[0].nodeValue = ("%1.3f" % fgreen)
        colorElem.getElementsByTagName("fBlue")[0].childNodes[0].nodeValue = ("%1.3f" % fblue)

    def save(self):
        filename = path.join(COLOR_EDITOR_CUSTOM_ASSETS, self.relpath)
        writeXmlFile(self.document, filename)

class CivInfo:

    def __init__(self):
        self.documentMap = dict()
        self.relpath = "XML/Civilizations/CIV4CivilizationInfos.xml"
        filename = findPath(self.relpath)
        if (filename):
            direc = path.join(COLOR_EDITOR_CUSTOM_ASSETS, "XML/Civilizations")
            if (not path.exists(direc)):
                makedirs(direc)
            backup = path.join(COLOR_EDITOR_CUSTOM_ASSETS, self.relpath + "-orig")
            if (not path.exists(backup)):
                shutil.copy(filename, backup)
            self.document = parseXmlFile(filename)
            self.documentMap = XmlMap(self.document, "CivilizationInfo", "Type")
        self.renamedColors = dict()
        namesInUse = []
        for civ in self.documentMap.keys():
            name = self.getPlayerColorName(civ)
            if name in namesInUse:
                newName = self.renamePlayerColor(civ)
                self.renamedColors[newName] = name
                name = newName
            namesInUse.append(name)

    def getRenamedColor(self, newName):
        if newName in self.renamedColors:
            return self.renamedColors[newName]
        else:
            return None

    def getPlayerColorName(self, playerKey):
        elem = self.documentMap.get(playerKey)
        return elem.getElementsByTagName("DefaultPlayerColor")[0].childNodes[0].nodeValue

    def getDisplayText(self, playerKey):
        # Display text seems to come from scattered config files. Punting on this for now
        return playerKey[13:]
    
    def getCivs(self):
        result = self.documentMap.keys()
        result.sort()
        return result

    def save(self):
        filename = path.join(COLOR_EDITOR_CUSTOM_ASSETS, self.relpath)
        writeXmlFile(self.document, filename)

    def renamePlayerColor(self, playerKey):
        elem = self.documentMap.get(playerKey)
        node = elem.getElementsByTagName("DefaultPlayerColor")[0].childNodes[0]
        oldValue = node.nodeValue
        node.nodeValue = "COLOR_EDITOR_%s_%s" % (oldValue, playerKey)
        return node.nodeValue

THRESHOLD_TARGET = 55
THRESHOLD_MAX_AGE = 30
THRESHOLD_DELTA = 10
TEXT_BLACK_CONTRAST = 50

class RandomColors:

    def __init__(self, names):
        self.values = []
        self.map = dict()
        self.threshold = THRESHOLD_TARGET
        self.thresholdAge = 0
        color = Color.randomColor()
        for name in names:
            while (not self.isNovel(color)):
                color = Color.randomColor()
            self.values.append(color)
            self.map[name] = color

    def isNovel(self, color):
        if (self.thresholdAge >= THRESHOLD_MAX_AGE):
            self.threshold -= THRESHOLD_DELTA
            self.thresholdAge = 0
        for col in self.values:
            if (color.distance(col) < self.threshold):
                self.thresholdAge += 1
                return False
        self.thresholdAge = 0
        return True

    def getMap(self):
        return self.map

    @classmethod
    def fillColorSets(cls, nameMap, colorMap):
        names = []
        for (key, triple) in colorMap.items():
            names.append(key)
        rc = RandomColors(names)
        for (key, color) in rc.getMap().items():
            primary = color
            secondary = Color.randomColor().movedFrom(primary, THRESHOLD_TARGET)
            text = primary.movedFrom(BLACK, TEXT_BLACK_CONTRAST)
            colorMap[key] = (primary, secondary, text)

class AdjustColors:

    def __init__(self, selected, names):
        values = selected
        self.map = dict()
        self.threshold = THRESHOLD_TARGET
        self.thresholdAge = 0
        nValues = len(selected)
        while (self.threshold > 0):
            iOffset = random.randint(0, nValues-1)
            jOffset = random.randint(0, nValues-1)
            for i in range(nValues):
                ii = (i + iOffset) % nValues
                for j in range(nValues):
                    jj = (j + jOffset) % nValues
                    if (ii != jj):
                        if (not self.areFarEnough(values[ii], values[jj])):
                            values[ii] = values[ii].nudgedFrom(values[jj])
            self.threshold -= 1
        for i in range(nValues):
            self.map[names[i]] = values[i]
                    

    def areFarEnough(self, color1, color2):
        if (self.thresholdAge >= THRESHOLD_MAX_AGE):
            self.threshold -= THRESHOLD_DELTA
            self.thresholdAge = 0
        if (color1.distance(color2) < self.threshold):
            self.thresholdAge += 1
            return False
        self.thresholdAge = 0
        return True
        
    def getMap(self):
        return self.map
        
    @classmethod
    def fillColorSets(cls, nameMap, colorMap):
        selected = []
        names = []
        for (key, triple) in colorMap.items():
            (primary, secondary, text) = triple
            selected.append(primary)
            names.append(key)
            colorMap[key] = triple
        rc = AdjustColors(selected, names)
        for (key, color) in rc.getMap().items():
            (primary, secondary, text) = colorMap[key]
            primary = color
            secondary = secondary.movedFrom(primary, THRESHOLD_TARGET)
            text = primary.movedFrom(BLACK, TEXT_BLACK_CONTRAST)
            colorMap[key] = (primary, secondary, text)

class App:

    def __init__(self, master):
        self.civInfo = CivInfo()
        self.colorInfo = ColorInfo(self.civInfo)
        self.colorVals = ColorVals(self.colorInfo)
        
        self.frame = Frame(master)
        self.frame.grid()
        self.frame.winfo_toplevel().title("Civ4 BTS Color Editor 2.0.2")
        i = 0
        self.buttons = dict()
        self.selected = dict()
        for civ in self.civInfo.getCivs():
            r = i % 12
            c = 6 * (i / 12)
            label = Label(self.frame, text=self.civInfo.getDisplayText(civ) + ":", anchor=E)
            label.grid(row=r, column=c)
            (names, colors) = self.getColorSet(civ)
            for j in range(3):
                button = Button(self.frame, width=2, height=1, background=colors[j], command=(lambda app=self,name=names[j]: app.editColor(name)))
                button.grid(row=r, column=c+j+1)
                self.buttons[names[j]] = button
            self.selected[civ] = BooleanVar()
            self.selected[civ].set(False)
            checkbox = Checkbutton(self.frame, onvalue=True, offvalue=False, variable=self.selected[civ])
            checkbox.grid(row=r, column=c+4)
            spacer = Label(self.frame, text=" ")
            spacer.grid(row=r, column=c+5)
            i += 1
        button = Button(self.frame, text="Select All", command=(lambda app=self: app.actionSelectAll()))
        button.grid(row=1, column=c+6, sticky=E)
        button = Button(self.frame, text="Clear All", command=(lambda app=self: app.actionClearAll()))
        button.grid(row=3, column=c+6, sticky=E)
        button = Button(self.frame, text="Randomize Selected", command=(lambda app=self: app.actionRandomize()))
        button.grid(row=6, column=c+6, sticky=E)
        button = Button(self.frame, text="Adjust Selected", command=(lambda app=self: app.actionAdjust()))
        button.grid(row=8, column=c+6, sticky=E)
        button = Button(self.frame, text="Save", command=(lambda app=self: app.actionSave()))
        button.grid(row=11, column=c+6, sticky=E)
        i += 1
        self.statusText = StringVar()
        self.statusLabel = Label(self.frame, textvariable = self.statusText)
        self.statusLabel.grid(row=i, column=0, columnspan=15, sticky=W)

    def getColorSet(self, civ):
        playerColorSymbol = self.civInfo.getPlayerColorName(civ)
        names = (
            self.colorInfo.getPrimaryColorName(playerColorSymbol),
            self.colorInfo.getSecondaryColorName(playerColorSymbol),
            self.colorInfo.getTextColorName(playerColorSymbol)
            )
        colors = (
            self.colorVals.getColor(names[0]),
            self.colorVals.getColor(names[1]),
            self.colorVals.getColor(names[2])
            )
        return (names, colors)

    def editColor(self, name):
        import tkColorChooser
        color = self.colorVals.getColor(name)
        (triple, hexstr) = tkColorChooser.askcolor(color)
        if (hexstr):
            self.setColorString(name, hexstr)
            self.statusText.set(name + "=" + hexstr)
        else:
            self.statusText.set("Edit cancelled")

    def setColorString(self, name, hexstr):
        self.colorVals.setColor(name, Color.parse(hexstr))
        self.buttons[name].config(background=hexstr)

    def setColor(self, name, color):
        self.setColorString(name, color.asString)

    def actionSave(self):
        self.civInfo.save()
        self.colorInfo.save()
        self.colorVals.save()
        self.statusText.set("Saved")

    def actionRandomize(self):
        nameMap = dict()
        colorMap = dict()
        for civ in self.civInfo.getCivs():
            (names, colors) = self.getColorSet(civ)
            if (self.selected[civ].get()):
                nameMap[civ] = names
                colorMap[civ] = None
        RandomColors.fillColorSets(nameMap, colorMap)
        for (key, names) in nameMap.items():
            colors = colorMap[key]
            for i in range(3):
                self.setColor(names[i], colors[i])

    def actionAdjust(self):
        nameMap = dict()
        colorMap = dict()
        for civ in self.civInfo.getCivs():
            (names, colors) = self.getColorSet(civ)
            if (self.selected[civ].get()):
                nameMap[civ] = names
                colorMap[civ] = colors
        AdjustColors.fillColorSets(nameMap, colorMap)
        for (key, names) in nameMap.items():
            colors = colorMap[key]
            for i in range(3):
                self.setColor(names[i], colors[i])

    def actionSelectAll(self):
        for civ in self.civInfo.getCivs():
            self.selected[civ].set(True)

    def actionClearAll(self):
        for civ in self.civInfo.getCivs():
            self.selected[civ].set(False)

        


root = Tk()

app = App(root)

root.mainloop()
