1) Files in folder 'Raw'  contain original data for testing/preparing input parameters for 'matouqin' model.

2) File 'data_structure' in folder 'Temp' contains the parameter composition of the whole model.
    Other files in folder 'Temp' contain original and processed parameters for checking the correctness of data processing process.

3) Folders 'Raw' and 'Temp' are in ignore on GitHub.

4) Files 'xxx.dat' are ampl format files, generated by dat_process.py. They contain parameters used in 'matouqin' main model.

5) 'dat1.dat' is real data, unit in parameters related to finance is million CNY.
    'dat2.dat' is real data too, unit in parameters related to finance is thousand CNY.
    'test1.dat' is a version of test data. Intermittent inflow shows 10 MW every 12 hours and 0 MW every 12 hours.
