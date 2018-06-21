# Dependencies
- [Multalin](http://multalin.toulouse.inra.fr/multalin/) version 5.4.1
- [Muscle](https://www.drive5.com/muscle/) version 3.8.31, 64 bits
- [blast](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/) version blast-2.6.0+


# 1. To start the server 

- if developed in a python3 Virtual environment, activate the virtual environment.
```
source ~/environments/my_env/bin/activate
```
- navigate to the project directory where the application resides
```
cd ~/IITA_PROJECTS/DeBaser
```
- start the API 
```
python manage.py runserver 
```
- on a web browser type
```
127.0.0.1:8000
```

# 2. To start the client 

- On a new terminal navigate to the client/app directory 
```
cd ~/IITA_PROJECTS/DeBaser-Client/debaser-app
```
- start the app
```
ng serve 
```
- on a web browser type
```
localhost:4200
```

# 3. Add new species and varieties 

- To ADD -> POST a new species, CLICK on the [species](http://127.0.0.1:8000/species/)
- Go to end of the page and select the HTML form
- Enter the species name e.g "Cassava 305-v6.1 (Phytozome)"
- Choose the species file 
- Click on the ```POST```

#NB: IF POSTING multiple files, REPEAT the above steps for every file

- To ADD -> POST a new variety, CLICK on the [varieties](http://127.0.0.1:8000/varieties/)
- Go to end of the page and select the HTML form
- Enter the variety name. this should be the same as the first name on the assembled consensus file. E.G if the assembled transcriptome is ```NadeleiB_Mesculenta_305_v6.1.cds.consensus.fa```, then the variety name should ONLY be named as ```NadeleiB```
- Choose the file e.g ```NadeleiB_Mesculenta_305_v6.1.cds.consensus.fa```
- From the species dropdown option, choose the APPROPRIATE species for the variety
- LEAVE varieties field BLANK
- Click on the ```POST```

#NB: IF POSTING multiple files, REPEAT the above steps for every file

#! IMPORTANT: ```DELETE``` option can be INACTIVATED on ```~IITA_PROJECTS/DeBaser/debaserapp/views.py``` by uncommenting the lines starting with ```permission_classes```

#! IMPORTANT: Once a POST is made, a DELETION of either the species or varieties results to LOSS of all data linked to the deleted species and varieties and vice-versa. BE CAREFUL 

#Be sure to ADD the correct data then inactivate the DELETE option for security measures.

# Routine CLEANUP will require DELETION of submitted data the other end-points
- [geneids](http://127.0.0.1:8000/geneids/)
- [results-geneids](http://127.0.0.1:8000/results-geneids/)
- [multi-varieties](http://127.0.0.1:8000/multi-varieties/)
- [multi-results-ids](http://127.0.0.1:8000/multi-results-ids)
- [sequences](http://127.0.0.1:8000/sequences/)


#Once a deletion is done, ensure the corresponding data on the database is also deleted. Typically the API data is mounted onto the ```media``` directory e.g, If the species list is deleted from the API, also delete/remove the species directory in ```~/IITA_PROJECTS/DeBaser/media```.


# 4.start analysis
