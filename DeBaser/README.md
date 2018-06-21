
###### TO START THE API/SERVER DEVELOPED IN DJANGO #########################

#If developed in a Python3 Virtual Environment and running in test mode

#To start the API, on a terminal, activate the virtual environment:
source ~/environments/my_env/bin/activate

#navigate to the project directory where the application resides
cd ~/IITA_PROJECTS/DeBaser

# start the API 
python manage runserver # this will start the API on your machine's localhost port 8000

# on a tab in web browser type 
127.0.0.1:8000

###### TO START THE APP/CLIENT DEVELOPED IN ANGULAR #########################

# On a new terminal navigate to the client/app directory 
cd ~/IITA_PROJECTS/DeBaser-Client/debaser-app

# start the app
ng serve # default start opens in localhost port 4200 

# on a tab in the web browser type
localhost:4200



##### ADD NEW SPECIES AND VARIETIES ########################################

# To ADD -> POST a new species, CLICK on the link "http://127.0.0.1:8000/species/"
# Go to end of the page and select the HTML form
# Enter the species name e.g "Cassava 305-v6.1 (Phytozome)"
# Choose the species file 
# POST
# NB: IF POSTING multiple files, REPEAT the above steps for every file


# To ADD -> POST a new variety, CLICK on the link "http://127.0.0.1:8000/varieties/"
# Go to end of the page and select the HTML form
# Enter the variety name. this should be the same as the first name on the assembled consensus file.
# example if the assembled transcriptome is "NadeleiB_Mesculenta_305_v6.1.cds.consensus.fa", then the variety name should ONLY be named as "NadeleiB"
# Choose the file e.g "NadeleiB_Mesculenta_305_v6.1.cds.consensus.fa"
# From the species dropdown option, choose the APPROPRIATE species for the variety
# LEAVE varieties field BLANK
# POST the file

# NB: IF POSTING multiple files, REPEAT the above steps for every file

# ! IMPORTANT: DELETE option can be INACTIVATED on ~IITA_PROJECTS/DeBaser/debaserapp/views.py by uncommenting the lines starting with "permission_classes" BE CAREFUL.

# ! IMPORTANT: Once a POST is made, a DELETION of either the species or varieties results to LOSS of all data linked to the deleted species and varieties and vice-versa. BE CAREFUL 

# Be sure to ADD the correct data then inactivate the DELETE option for security measures.

# Routine CLEANUP will require DELETION of submitted data the other end-points:
    # "geneids": "http://127.0.0.1:8000/geneids/"
    # "results-geneids": "http://127.0.0.1:8000/results-geneids/"
    # "multi-varieties": "http://127.0.0.1:8000/multi-varieties/"
    # "multi-results-ids": "http://127.0.0.1:8000/multi-results-ids/"
    # "sequences": "http://127.0.0.1:8000/sequences/"


# Once a deletion is done, ensure the corresponding data on the database is also deleted. Typically the API data is mounted onto the "media" directory
# example, If the species list is deleted from the API, also delete/remove the species directory in "~/IITA_PROJECTS/DeBaser/media".


# once api is ready and running, start analysis on the client/app.