# calami

##### Developing calibration methods for NIRISS AMI mode data using 1516 CM data

Develop process when calibrating APT Program 1516 data.  Apply to other calibration development for AMI.

* Keep repo up-to-date even while developing code
* Useful short program & observation summaries: keep APT info and important header info close or together (use & add to existing DT code generated from apt or headers)
* Plan data file manipulation/cleaning, develop in notebooks, then put into single (eg) calutil.py module and remove from notebooks.  Avoid repeated code blocks in different notebooks & scripts
* Use in-line function documentation
* Develop convenient mapping of data file names to descriptive names (as done in AMI COM). 

**Result of a cal program analysis**:  

* In pipeline processing, (non-default?) flags summarized
* Mnemonic-filename translation, eg  
* Useful data handling/analysis functions available to the group, with helpful docstrings in functions to enable easy re-use  
* Clear plots/tables for cal documentation
* Low overhead to re-analysis 
* Program and data view modules, get target brightness & spectrum (simbad call?), count rates in peak, dates of observations executed 

--


### General

"Tables" can be pandas tables - mixed types of columns, pd methods & attributes come for free

Incoming data sets real/fake/grafted hdrs, ... but MAST format

### Class Dataset

		Dataset.__init__(aptget=None/(aptid, token), 
		              datadir=location_on_disk,
		              level='', 
		              kwdlist=None):
			(if required gets MAST dataset)
			creates and writes list of datafile names for Data.associate()
			creates table and writes out summary (like DT code)
			
			initializes as many Data instances as files
			
			
			 

### Class Data

	Data.level  
	Data.associate(tbd): creates map from user-supplied understandable name to aptx-supplied filename  
	regardless of the level (uncal/rateints/cal/calints/whatever) of the data
	    eg: 1068_f480_dith3 -> jw01509002001_06101_00002_nis
	
	Data.
	
	