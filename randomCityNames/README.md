Copyright &copy; 2018 by James Conrad Shea (duckstab)
Except as otherwise noted in specific files, this software is
made available under the terms of the Creative Commons
Attribution-NonCommercial-ShareAlike 3.0 License 
See
	http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
for full terms. 

# Description

**Random City Names 1.1**

This modcomp generates random city names for all the regular civs
in BtS as well as the barbarians. Genrally speaking, it should be easy to merge with any BUG-based mod. I have been able to merge it with the following:
* BAT 4.1
* K-Mod

Note that it will *not* work with unmodded BtS. The core BUG mod code must at least be present.
     
City names are generated using a Markov Chain algorithm, using city 
name lists that are found in Assets/Python/Contrib/CityNameLists.py. 
No filtering is applied so I cannot guarantee that it won't produce
something inappropriate or offensive. Use, or not, at your discretion.

Barbarian city names are generated from civs that are not in the current
game. If you're playing a game using an enhanced DLL that allows all 
civs to be active, this will probably cause issues.

**New in 1.1: **

* Ensure that state is persisted across sessions.
* When a city is conquered, a new name will be generated based on the old name, but compatible with the names of the conquering civ. On reconquest, the old name is restored.

# Installation

1) Back up your mod's Assets/Python directory.
2) Unzip the contents of randomCityNames.zip to the mod
   directory. 

# Notes 

* This mod replaces the default CvEventManager.py. If you are concerned 
that might break something, you will need to merge that file by hand.

# Giving feedback

* Comments, suggestions, and bug reports are welcome. Just send
  me a PM on CivFanatics. 

# Credits

Thanks and credit go to all whose work has formed the basis for
this project, especially:
  * Peter Corbett, whose public-domain code forms the basis of
    the Markov chain generator used for some civs
  * LemonMerchant, whose BAT mod provided both inspiration and a
    test bed for this code

If I have left anyone out, please let me know so I can give
appropriate acknowledgement!



