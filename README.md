# calami


### Developing calibration methods for NIRISS AMI mode data using 1516 CM data

Design code at high level first and walk-through by one other AMI team member

Keep repo up-to-date with code during development (even partially-written code)

Include design into code in docstring comment

Encapsulate related sets of quantities (parameters for big processing steps, eg implaneia run, median filtering raw data, etc)?

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

SLM notes Sep 25:  
Charge migration (CAL-NIS-026; APT 1516, but can include additional data)    
•	Goals   
a.	Quantify ADU level at onset of charge migration. Use various thresholds for non-linearity effects, e.g., 0.5%, 1%, 2%, 3%?   
b.	Test charge migration mitigation in pipeline. What contrast level can be achieved with and without charge migration mitigation?  
c.	Identify ADU level for “effective saturation,” the limit at which we advise users to stay below when designing programs. Consider:    
i.	At what level of charge migration does the pipeline fix not recover good enough PSF sampling to allow better contrast sampling? Should that be the limit? Or should we use a limit at which charge migration occurs?   
•	What’s the metric for completion?    
o	Consider analysis program “complete” when the answers to the above are determined?   
o	 Or will further analysis to improve charge migration correction be part of this analysis program if the contrast levels aren’t deep enough?  

Other calibration programs/analysis needs to prioritize. What’s the next most important project to focus on in the coming quarter. Note that data for these calibration programs are already available:   
•	Updates to ImPlaneIA algorithm  
•	CAL-NIS-011 (APT 1504) NIRISS AMI Intra-pixel Response Calibration  
o	Small offsets of star to different relative pixel positions to calibrate intra-pixel sensitivity of PSF.   
•	APT 4478: Test AMI filter offsets to bring target at pixel center   
•	APT 4480: AMI Calibrator Requirements    


--


### General

"Tables" could be pandas (pd) tables - mixed types of columns, pd methods & attributes & flexible formatting come for free.  Some coder learnig overhead initially.  Stick with astropy tables?

Mapping human readable names to disk filenames: text? pandas? Use low-learning-overhead easy-to implement code.

Incoming data sets real/fake/grafted hdrs, ... but MAST format

Let's think about dataset needs:

	forddataset = Dataset(newdirfordata, (1260,'4346045ccd2c42d9b438b192cf412a32', 'uncal')
	fordataset.create_summary('dt_type_file.txt') # or make this a param in the __init__?
	# User creates the 'my_mapping.txt' file by looking at the dt_type_file.txt or other way(?)
	
	forddataset.create_mapping('my_mapping.txt', 'my_mapping.txt')
	# Now we have easily understood 'pointers;' in 'my_mapping.txt' file for further processing
	

≈        

		def __init__(self, datafrom, 
		                   filetypes=(),
		                   infodir = ,
		                   verbose=False):
		   """ Finds data on file or downloads with shell call to jwst_download.py """ 
		   ****************************************************
		   *  Is generalizing to get data two ways overkill?  *
		   *  Restrict to one filetype at a time?             *
		   ****************************************************
		   
			datafrom - location_on_disk or (aptid, token, datadir 
			             --- use jwst_download.py, put data in datadir)
			filetypes - use jwstdownload arg(s) syntax.
			infodir - where to log details of driver input, running, etc.
			
			creates
				self.rootlist = self.getdataset(dataset) # as many rootnames as exposures
				self.filetypes
				infodir
				
				
				Questions:
			         - how do we treat specifying 'level' of data calibration?
			         - writes rootlist items to disk file (format? .txt?) 
			         - stores directory where data reside in self.datadir
			self.summary =  create_summary(rootlist) 
			
			
		def create_summary(self, rootlist):
			creates and stores information table like Deepashri's table 
			    - get info by looking at headers only?
			    - read full headers into memory and just retrieve from them by keyword?

			
		def create_mapping(self, user_file, association_file):
			like Rachel's mapping for COM data: created from  self.rootlist and user_file
			maps  association_file (eg 'abdor_72ke') given by user to a mast(like) filename
			
		def info(self,...):
			write out dataset info in requested formats
				- Deepashri's big table output
				- associations between human-requested string ('abdor_obs1') and mast-like filename
			
### Class Data

	each exposure (eg mast file) is an instance of Data.
	methods to be developed as we ingest some com analyses and cal analyses tasks  


Let's think about data manipulation needs.  

Use mapped names that are relevant to the analysis/investigation, assuming the right stage of data (uncal, rate, ...) for the data analysis task. 

Tasks can be done: 

	def prep_data(self, {datasetname: ...):
		Examples: 
		data cleaning with rejecting 2, 3, or 4 std devs from a median   
		dicing for CM examination as in commissioning CM analysis8  
		fixing bad pixels with a certain set of parameters (rejection, max iterations)
		Includes putting extracted data into mast-like files for eg calibration using early vs late groups, 

	def pipe_data(self, ...):
		apply particular jwst pipeline steps or more atomic processing included in pipeline  
		
	def rearrange_data(self, ...):
	
### Org questions:

	Where do we store useful 'meta-information' if we want to easily reprocess with the same ref files and different algorithm (eg changed threshold or max iteration in bp_fix) E.g., CRDS_VER, CRDS_CTX,, jwst software branch info,... 
	
--
--

## Prototyping using CAL_1516 design

###Quantify CM in data

Top level driver - set-up allows for using multiple datasets later.:

	userhomedir = ...
	outputdir = ...
	analysisname = "CMquantification"
	dataset = Dataset(datafrom = userhomedir+ + "/niriss/cal_1516/pipeline_calibrated_data/",
                       filetypes = ("ramp"),
                       outputdir = ...,
                       verbose=True)
--

