# -*- coding: utf-8 -*-

Copyright © 2010-2017 by James Conrad Shea (duckstab)
This software is made available under the terms of the Creative Commons 
Attribution-NonCommercial-ShareAlike 2.0 License
See
	http://creativecommons.org/licenses/by-nc-sa/2.0/legalcode
for full terms. 

# Description

**BtS Color Editor v. 2.0.1**

This is a simple player color editor for Civ 4 Beyond the
Sword. It allows you to set the primary, secondary, and text
colors for each civ and for the barbs. You can also have it
select random colors using an algorithm that tries to make sure
each civ's borders are clearly distinguishable. Or you can have
it adjust any selected civs' colors to apply the same algorithm. 

It may work with other flavors of Civ 4 and with various mods if
you set up the config properly. I myself have been able to use it
successfully with BAT, K-Mod, Sword of Islam, FFH2, etc. However,
I can't make any guarantees so if you want to be safe you should
back up your CustomAssets folder first.

# Installation

0) Unzip the files to any convenient location.
1) Download and install Python 2.X from
   http://python.org/download/. I developed this using Python
   2.6.5 and did some basic testing with Python 2.7. I'd
   recommend trying 2.7 first.
2) Important: Edit btsColorEditorConfig.py to set the
   CustomAssets (output) directory and search path for existing
   assets. 

# Running

1) Run btsColorEditor.py with python.exe. Normally the Python
   installer will register itself to open Python files so you can
   probably just double-click. This will back up your existing
   color definitions to CIV4PlayerColorInfos.xml-orig and
   CIV4ColorVals.xml-orig, just in case you need to get them
   back. Note that CIV4PlayerColorInfos.xml and CIV4ColorVals.xml
   are the only files the editor writes.
2) To edit the colors for each civ, just click on the colored
   buttons next to their names. When done, click "Save".
3) If you want to use the randomizer, select one or more
   checkboxes and click "Randomize Selected". You can keep doing
   this as many times as you want until you're happy with the
   result. And then click "Save".
4) Alternately, if you want to just adjust the existing civ color
   selections to move them "as far apart" as possible, select one
   or more checkboxes and click "Adjust Selected".
5) Start/restart BtS. (Note that the XML files are only read on
   startup, so a restart is needed.)

# Notes

* The color editor creates new color names for each civ, which is
  necessary to make each color separately editable. For example,
  England's color is normally the same white that is used as a
  secondary color for several other civs. So England's primary
  color is renamed to COLOR_EDITOR_ENGLAND_PRIMARY while
  America's secondary color is COLOR_EDITOR_AMERICA_SECONDARY. 
* The randomization algorithm proved trickier than expected. It
  turns out it's pretty hard to find 30-odd colors that are
  sufficiently far apart so that any two of them are clearly
  distinguishable border colors, although of course this is
  somewhat subjective. The program basically generates colors at
  random and measures each candidate color's distance from all
  other colors. If it passes a certain threshold, it's added to
  the set. If not, another color is generated. To ensure the
  algorithm terminates the threshold is gradually lowered after a
  number of successive failures.

# Known issues

* If you edit a color and then click on it again the color
  chooser still shows the original color.
* The output XML is not very readable. Surprisingly there are no
  good choices in the Python 2.X world for generating
  human-readable XML. I tried several and Civ's in-game XML
  parser choked on the output of each one.
* The Minor civ is not supported. For some reason it not only
  shares the color white with England but the color set name as
  well, and this wasn't easy to work around.
* When the leader splash screen pops up you'll see the original
  colors for the flag icons. They're probably images not
  generated from the XML.

# Giving feedback

* Comments, suggestions, and bug reports are welcome. Just send
  me a PM on CivFanatics.
