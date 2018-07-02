# debaser
# replace all the paths and urls in the scripts appropriately 
# Dependencies
- [Multalin] version 5.4.1
- [Muscle] version 3.8.31, 64 bits
- [blast] version blast-2.6.0+
- [angsd] version 0.910
- [bowtie2] version 2.2.5
- [htslib] version 1.2.1

# A. Assembly pipeline for consensus sequence generation
1. To start run the assembly pipeline run the ```debaser.py```. Use ```debaser.py --help``` for more details on I/O

# B. Debaser tool web interface
1. Ensure that the backend data API is running
2. Build the html files for serving the debaser app ```ng build --prod```
3. This compiles the app in the ```/dist``` directory which can be added to the Apache2 configuration file as a document root on a different port.
4. Restart the apache2 ```sudo /etc/init.d/apache2 restart```
5. Check the error log ```tail -f /var/log/apache2/error.log```
6. Monitor the requests ```tail -f /var/log/apache2/access.log```
