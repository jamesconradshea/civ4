Copyright © 2018 by James Conrad Shea (duckstab)
This software is made available under the terms of the Creative Commons 
Attribution-NonCommercial-ShareAlike 3.0 License
See
	http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
for full terms. 

# Description

**Unit Naming Plus 1.0.1-beta1**

This modcomp is a partial refactoring and enhancement of the unit
naming code used in the BUG mod. I have been able to merge it
with various BUG-compatible mods such as BAT, K-Mod, and
RevoluctionDCM. 

Features include:
* Custom naming code for all of the civs in BtS. I've
  made an effort to be faithful to the naming customs of
  each civ where known.
* Support for the ^nav^ unit naming convention for naval
  units. For some civs this draws ship names from
  historical lists of the corresponding
  navies. Otherwise it behaves like the ^rc^
  convention. 
* Female names are generated for missionaries and
  executives for mods such as BAT that create such
  units. 

# Installation

1) Back up your mod's Assets/Python/Contrib directory.
2) Unzip the contents of unitNamingPlus.zip to the mod
   directory. 

# Notes 

* New in 1.0.1-beta1:
  * Attempted fix at multiplayer bug. I tested with hotseat only but I am cautiously optimistic this will make the modcomp multiplayer-compatible.

# Giving feedback

* Comments, suggestions, and bug reports are welcome. Just send
  me a PM on CivFanatics. 

# Credits

Thanks and credit go to all whose work has formed the basis for
this project, especially:
  * RuffHi, author of the original UnitNameEventManager
  * The Lopez, for the original RandomNameUtils
  * Peter Corbett, whose public-domain code forms the basis of
    the Markov chain generator used for some civs
  * LemonMerchant, whose BAT mod provided both inspiration and a
    test bed for this code

If I have left anyone out, please let me know so I can give
appropriate acknowledgement!



