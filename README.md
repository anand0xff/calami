# calami

##### Developing calibration methods for NIRISS AMI mode data using 1516 CM data

Develop process when calibrating APT Program 1516 data.  Apply to other calibration development for AMI.

* Keep repo up-to-date even while developing code
* Useful short program & observation summaries: keep APT info and important header info close or together (use & add to existing DT code generated from apt or headers)
* Plan data file manipulation/cleaning, develop in notebooks, then put into single (eg) calutil.py module and remove from notebooks.  Avoid repeated code blocks in different notebooks & scripts
* Use in-line function documentation
* Develop convenient mapping of data file names to descriptive names (as done in AMI COM). 

**Result of a cal program analysis**:  

* Pipeline processing flags clearly summarized
* Useful data handling/analysis functions available to the group, with helpful docstrings in functions to enable easy re-use  
* Clear plots/tables for cal documentation
* Low overhead to re-analysis with cut & pasteable instructions