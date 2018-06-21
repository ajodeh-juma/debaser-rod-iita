#! /usr/bin/env python
import sys
import os
import json
import time
import shutil
from django.conf import settings
from os import path
import subprocess
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from datetime import datetime
from .serializers import *
import urllib
import requests
from requests_toolbelt import MultipartEncoder
#from urllib3._collections import HTTPHeaderDict
from collections import defaultdict


MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

env=os.environ.copy()
env['PYTHONPATH']=":".join(sys.path)
print (env)
#############################
# INPUT - GENE IDENTIFIERS  #
#############################

def createGeneidDict(submitted_data):
    """create a dictionary with submitted data, returns a dict with all the data"""

    start_time = datetime.now()
    sys.stdout.write("\nStarted analysis on: " +str(start_time)+ " for the job with id: " +str(submitted_data.uuid)+"\n")

    inputDIR = os.path.join(MEDIA_ROOT, 'species/')
    outputDIRPATH = os.path.join(MEDIA_ROOT, 'output/')
    workingDIR = os.path.join(outputDIRPATH, str(submitted_data.uuid)) + '/'

    variety_list = []
    variety_consensus_files = []
    data_dict = {}

    #jobid = str(submitted_data.jobid)
    jobid = str(submitted_data.uuid)
    outfmts = submitted_data.outputfmt.split(',')

    for entry in submitted_data.varieties.all():
        if not os.path.exists(inputDIR):  # make input directory
            os.makedirs(inputDIR)

        if not os.path.exists(workingDIR): # make output directory
            os.makedirs(workingDIR)

        varietiesDIR = os.path.join(MEDIA_ROOT, entry.location)
        if not os.path.exists(varietiesDIR):
            os.makedirs(varietiesDIR)

        geneid_file = os.path.join(workingDIR, str(submitted_data.uuid) + '.txt')
        reference_basename = os.path.basename(str(entry.species.species_file))
        reference_file = os.path.join(inputDIR, reference_basename)
        variety_consensus_basename = os.path.basename(str(entry.variety_consensus))
        variety_consensus_file = os.path.join(varietiesDIR, variety_consensus_basename)

        variety_list.append(entry.variety_name)
        variety_consensus_files.append(variety_consensus_file)

        geneidContent = StringIO(str(submitted_data.geneid))  # get the content of the gene ids submitted
        geneidData = geneidContent.getvalue()
        if not os.path.exists(geneid_file):
            with open(geneid_file, 'w') as fhandle:
                fhandle.write(geneidData)
        data_dict[jobid] = [variety_list, variety_consensus_files, reference_file, geneid_file, workingDIR, outfmts]
    return data_dict


def varietyCategory(data_dict):
    """return a list of dictionary for each variety"""

    singlevardict = {}    # dictionary to store single variety
    multiplevardict = {}  # dictionary to store multiple varieties
    varlist = []  # list to store all the dicts

    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        gidsfile = data[3]
        wkdir = data[4]
        outfmts = data[5]

        if len(varnames) > 1:
            for varname in varnames:
                for varfile in varfiles:
                    if varname in varfile:
                        multiplevardict[varname] = varfile
                        varlist.append(multiplevardict)
        if len(varnames) == 1:
            for varname in varnames:
                for varfile in varfiles:
                    if varname in varfile:
                        singlevardict[varname] = varfile
                        varlist.append(singlevardict)

        print ("submitted data:")
        print ("organism -->"'\t'+os.path.basename(reffile))
        print ("varieties -->"'\t'+ ' '.join(varnames))
        print ("output format(s) -->"'\t'+' '.join(outfmts))
        return varlist

def extractSingle(varlist, data_dict):
    """Extract consensus sequences of the submitted gene identifiers, if single variety selected"""

    single = False
    multiple = False
    consdict = {}

    ids = [] # store only the identifiers (without the variety names)
    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        gidsfile = data[3]
        wkdir = data[4]
        outfmts = data[5]

        
        if len(varnames) > 1:
            continue
        else:
            for file in varfiles:
                for line in open(file):
                    line = line.strip()
                    if line.startswith('>'):
                        consid = line.strip('>')
                        ids.append(consid.rsplit('_', 1)[1])
                        consdict[consid] = ''
                    else:
                        consdict[consid] += ''.join(line.strip())

    geneids_dict = {}  # dictionary to store all the ids for every variety i.e varietyname appended to the ids

    for dic in varlist:
        for v, d in dic.items():
            for line in open(gidsfile):
                id = line.strip().split()[0]
                new_header = v + '_' + line.strip().split()[0]
                geneids_dict[new_header] = id
    
    # query the variety file to get consensus sequences for each gene id

    varfile_dict = {} # dict to store filenames for each variety gene id
    single_list = []  # list to store temporary variety id files
    geneid_list = []  # store valid variety gene ids files

    report_file = os.path.join(wkdir, jid) + '_report.txt'   # file to report submitted data
    report_name = os.path.basename(report_file)

    valid = []     # store valid records/ identifiers
    noconsensus = [] # store ids with no consensus sequences
    

    for key, value in geneids_dict.items():

        vargeneid = key.rsplit('_', 1)[1]
        varid_file = os.path.join(wkdir, key) + '.fa'
        if not vargeneid in varfile_dict:
            varfile_dict[vargeneid] = [varid_file]
        else:
            varfile_dict[vargeneid].append(varid_file)

        seq = consdict.get(key)
        if seq != None:                  # get identifiers with consensus sequence
            valid.append(geneids_dict.get(key))
            sys.stdout.write("Extracting [" +key+ "] \t sequences\n")           
            with open(varid_file, 'w') as outfile:
                outfile.write('>' + key)
                outfile.write('\n')
                outfile.write(str(seq))
                outfile.write('\n')

        if seq == None:                 # get identifiers with no consensus sequences
        	noconsensus.append(geneids_dict.get(key))


    



    with open(report_file, 'w') as fhandle:
    	fhandle.write("variety selected:\t %s\n" % (key.rsplit('_', 1)[0]) )
    	fhandle.write("total gene identifiers submitted/sequences retrieved from blast:\t"+str(len(geneids_dict))+"\n")
    	fhandle.write('\n')
    	fhandle.write("with consensus sequence:\t"+str(len(valid))+"\n")
    	for n, gid in enumerate(valid):
    		fhandle.write(gid)
    		fhandle.write('\n')
    with open(report_file, 'a') as fhandle:	
        fhandle.write('\n')
        fhandle.write("without consensus sequences:\t"+str(len(noconsensus))+"\n")
        for n, gid in enumerate(noconsensus):
            fhandle.write(gid)
            fhandle.write('\n')


    #url = MEDIA_URL+'results-geneids'
    url = 'http://localhost/results-geneids/'   # link to post files 
    print (url)
    

    # check gene ids that have sequences and write only the ones having consensus sequences
    for key, value in varfile_dict.items():
        if len(value) == 1:
            single = True
            multiple = False
        if single == True and multiple == False:
            for file in value:
                if os.path.exists(file):
                    single_list.append(file)

    consensus_file = os.path.join(wkdir, jid)+'_consensus.fa'
    consensus_html = os.path.join(wkdir, jid)+'_consensus.html'

    filename = os.path.basename(consensus_file)
    htmlfilename = os.path.basename(consensus_html)


    # write the consensus sequences file in FASTA format
    with open(consensus_file, 'w') as fhandle:
        for file in single_list:
            with open(file) as infile:
                for line in infile:
                    if len(line) > 100:
                        fhandle.write('\n'.join(line[i:i+100] for i in range(0,len(line), 100)))
                    else:
                        fhandle.write(line)


    # write consensus sequences file in HTML format
    with open(consensus_html, 'w') as fhandle:
        with open(consensus_file) as infile:
            for line in infile:
                line = line.strip()
                fhandle.write('<div>{}</div>'.format(line))

    textfile = os.path.join(wkdir, jid)+'_consensuslink.html'
    textname = os.path.basename(textfile)
    

    if os.path.getsize(consensus_file) == 0:
    	with open(textfile, 'w') as fhandle:
    		reportid = os.path.basename(report_file).rsplit('_', 1)[1]
    		reporthtml = 'http://localhost/media/results-geneids/'+os.path.basename(report_file)
    		fhandle.write(('<p> no consensus sequence for: '+' '.join(noconsensus)+ '</p>\n'))
    		fhandle.write(('<p> report: </p><a href="'+reporthtml+'">'+reportid+ '</a>\n'))
    	multipart_data = MultipartEncoder(
        	fields={
            	'consensus_file': '',
            	'consensus_html': '',
            	'uniqueid': jid,
            	'consensuslink': (textname, open(textfile, 'rb')),
            	'reportfile': (report_name, open(report_file, 'rb'))
            	}
        	)
    	response = requests.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})

    
    else:
        with open(textfile, 'w') as fh:
            reportid = os.path.basename(report_file).rsplit('_', 1)[1]
            reporthtml = 'http://localhost/media/results-geneids/'+os.path.basename(report_file)
            geneid = os.path.basename(consensus_file).rsplit('_', 1)[1]
            rawconsensus = 'http://localhost/media/results-geneids/'+os.path.basename(consensus_file)
            rawconsensushtml = 'http://localhost/media/results-geneids/'+os.path.basename(consensus_html)

            fh.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">\
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
            fh.write(('<div class="col-xs-18"><p>consensus: <a href="'+rawconsensushtml+'">\
                <button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view consensus</button>\
                <a href="'+rawconsensus+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download consensus</button>\
                </a></p></div></body></html>'))
            

            #fh.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
            #fh.write(('<p>consensus file (FASTA format): <a href="'+rawconsensus+'"><button type="button" class="btn btn-primary"><span class="glyphicon glyphicon-download"></span> Download</button></a></p><br></body></html>'))

            #fh.write(('<p> consensus file (FASTA format) :</p><a href="'+rawconsensus+'">' +geneid+ '</a>\n'))
            fh.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
            fh.write(('<p>'+reportid+': <a href="'+reporthtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view</button></a></p><br></body></html>'))
            #fh.write(('<p> report: </p><a href="'+reporthtml+'">'+reportid+ '</a>\n'))
        
        multipart_data = MultipartEncoder(
            fields={
            	'consensus_html': (htmlfilename, open(consensus_html, 'rb')),
                'consensus_file': (filename, open(consensus_file, 'rb')),
                'uniqueid': jid,
                'consensuslink': (textname, open(textfile, 'rb')),
                'reportfile': (report_name, open(report_file, 'rb'))
                }
            )
        response = requests.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})
    return single_list
    

def extractMultiple(varlist, data_dict):
    """Extract consensus sequences of the submitted gene identifiers, if single variety selected"""

    single = False
    multiple = False
    
    consdict = {}   # dict for the varieties consensus files

    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        gidsfile = data[3]
        wkdir = data[4]
        outfmts = data[5]

        
        if len(varnames) == 1:
            continue
        else:
            consfile = os.path.join(wkdir) + 'consensus.fasta' # file having all the consensus files for the selected varieties
            for file in varfiles:
                with open(consfile, 'w') as outfile:
                    for fname in varfiles:
                        with open(fname) as infile:
                            for line in infile:
                                outfile.write(line)

        for line in open(consfile):
            line = line.strip()
            if line.startswith('>'):
                consid = line.strip('>')
                consdict[consid] = ''
            else:
                consdict[consid] += ''.join(line.strip())



    geneids_dict = {}  # dictionary to store all the ids for every variety i.e variety appended to the ids

    for dic in varlist:
        for v, d in dic.items():
            for line in open(gidsfile):
                id = line.strip().split()[0]
                new_header = v + '_' + line.strip().split()[0]
                geneids_dict[new_header] = id

    # query the consensus file to get consensus sequences for each gene id
    varfile_dict = {} # dict to store filenames for each variety gene id
    tmp_var_list = [] # list to store temporary varid files
    geneid_list = []  # list store valid variety gene ids files
    valid = []        # list store valid records/ identifiers
    noconsensus = []      # list store invalid ids/no consensus sequences


    report_file = os.path.join(wkdir, jid) + '_report.txt'   # file to report submitted data
    report_name = os.path.basename(report_file)


    for key, value in geneids_dict.items():
        vargeneid = key.rsplit('_', 1)[1]
        varid_file = os.path.join(wkdir, key) + '.fa'
        
        if not vargeneid in varfile_dict:
            varfile_dict[vargeneid] = [varid_file]
        else:
            varfile_dict[vargeneid].append(varid_file)

        seq = consdict.get(key)
        if seq != None:                  # get identifiers with consensus sequence
            v = geneids_dict.get(key)+' '+key.rsplit('_', 1)[0]
            valid.append(v)
            sys.stdout.write("Extracting [" +key+ "] \t sequences\n")           
            with open(varid_file, 'w') as outfile:
                outfile.write('>' + key)
                outfile.write('\n')
                outfile.write(str(seq))
                outfile.write('\n')

        if seq == None:                 # get identifiers with no consensus sequences
            v = geneids_dict.get(key)+' '+key.rsplit('_', 1)[0]
            noconsensus.append(v)

    val = {}
    for v in valid:
        k = v.split()[0]
        if not k in val:
            val[k] = [v.split()[1]]
        else:
            val[k].append(v.split()[1])


    nonval = {}
    for v in noconsensus:
        k = v.split()[0]
        if not k in nonval:
            nonval[k] = [v.split()[1]]
        else:
            nonval[k].append(v.split()[1])

    submitted_ids=[]  # list to store submitted ids
    submitted_dic = {}

    for line in open(gidsfile):
        #print (line)
        submitted_dic[line.strip()]=''
        submitted_ids.append(line.strip())
    #print (len(submitted_ids), len(submitted_dic))
    
    selected = '\t'.join(varnames)
    with open(report_file, 'w') as fhandle:
        fhandle.write("varieties selected:\t %s\n" % selected )
        fhandle.write("total gene identifiers submitted/sequences retrieved from blast:\t"+str(len(submitted_ids))+"\n")
        fhandle.write('\n')
        fhandle.write("with consensus sequences\n")
        fhandle.write("ID\tVarieties\n")
        for k, v in val.items():
            fhandle.write(k+'\t'+'\t'.join(sorted(v)))
            fhandle.write('\n')

    with open(report_file, 'a') as fhandle: 
        fhandle.write('\n')     
        fhandle.write("without consensus sequences\n")
        fhandle.write("ID\tVarieties\n")
        for k, v in nonval.items():
            fhandle.write(k+'\t'+'\t'.join(sorted(v)))
            fhandle.write('\n')



    # check gene ids that have sequences and write only the ones having consensus sequences

    
    for key, value in varfile_dict.items():
        if len(value) != 1:
            single = False
            multiple = True
        if single == False and multiple == True:
            #key = ''.join(key.rsplit('.'))
            key = jid+'_'+key
            geneid_file = os.path.join(wkdir, key) + '.fasta'
            geneid_list.append(geneid_file)
            with open(geneid_file, 'w') as fhandle:
                for filename in value:
                    if not os.path.exists(filename):
                        continue
                    else:
                        for line in open(filename):
                            if len(line) > 100:
                                fhandle.write('\n'.join(line[i:i+100] for i in range(0,len(line), 100)))
                            else:
                                fhandle.write(line) 
    return geneid_list



def run_muscle(geneid_list, data_dict):
    """run muscle alignment software on the gene id list of files"""

    
    muscres = ''
    muscle_html = []
    
    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        gidsfile = data[3]
        wkdir = data[4]
        outfmts = data[5]

        
    selected_var = ' '.join(varnames)
    if 'Muscle' in outfmts:
        for filename in geneid_list:
            cmd = ["grep '>' %s | wc -l" % (filename)]
            p = subprocess.Popen(cmd, shell=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = p.communicate()[0].decode('utf-8').strip()
            

            if out == '0':
                muschbasename = os.path.basename(os.path.splitext(filename)[0])
                muschtml = os.path.join(wkdir, muschbasename) + '_muscle.html'
                with open(muschtml, 'w') as fh:
                	fh.write(('<p>'+muschbasename.rsplit('_', 1)[1]+' has no consensus sequences in the selected varieties: '+selected_var+ '</p><br>\n'))
                #muscle_html.append(muschtml)

            elif out == '1':
                muschbasename = os.path.basename(os.path.splitext(filename)[0])
                muschtml = os.path.join(wkdir, muschbasename) + '_muscle.html'
                
                with open(muschtml, 'w') as fh:
                    for line in open(filename):
            	        if line.startswith('>'):
            		        varp = line.strip('>').rsplit('_',1)[0]
            		        if varp in varnames:
                    			fh.write(('<p>'+muschbasename.rsplit('_', 1)[1]+' has only consensus sequences for: '+varp+ ' cannot align against self </p><br>\n'))
                #muscle_html.append(muschtml)

            else:
                base = os.path.basename(os.path.splitext(filename)[0])
                muschtml = os.path.join(wkdir, base) + '_muscle.html'
                muscmsf = os.path.join(wkdir, base) + '_muscle.msf'
                        # run muscle using the options: -diags(Find diagonals (faster for similar sequences)) and -html (output in html)
                muscle_html.append(muschtml)
                muscle_cmd = "/home/juma/Tools/muscle3.8.31_i86linux64 -in %s -out %s -html -diags" % (filename, muschtml)
                try:
                    sys.stdout.write("\nMuscle MSA for " + os.path.basename(filename) + "\n")
                    muscres = subprocess.check_call(muscle_cmd, env=env, shell=True)
                except Exception:
                    sys.stderr.write("Error occurred when generating multiple sequence alignment file using MUSCLE.\n")
                    sys.stderr.write("Command that was running: " + muscle_cmd + "\n")
                if muscres == 0:
                    sys.stdout.write("\nMultiple sequence alignment with MUSCLE success!\n")

    return muscle_html


def run_multalin(geneid_list, data_dict):
    """run multalin alignment software on the gene id list of files"""
    
    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        gidsfile = data[3]
        wkdir = data[4]
        outfmts = data[5]

    os.chdir(wkdir)
    multalin_out = []
    multres = ''
    blosumtab = '/home/juma/Tools/MULTALIN/blosum62.tab'

    selected_var = ' '.join(varnames)
    if 'Multalin' in outfmts:
        for filename in geneid_list:
            cmd = ["grep '>' %s | wc -l" % (filename)]
            p = subprocess.Popen(cmd, env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = p.communicate()[0].decode('utf-8').strip()


            if out == '0':
                multbasename = os.path.basename(os.path.splitext(filename)[0])
                multdoc = os.path.join(wkdir, multbasename) + '.doc'
                with open(multdoc, 'w') as fh:
                	fh.write(('<p>'+multbasename.rsplit('_', 1)[1]+' has no consensus sequences in the selected varieties: '+selected_var+ '</p><br>\n'))
                #multalin_out.append(multdoc)

            elif out == '1':
                multbasename = os.path.basename(os.path.splitext(filename)[0])
                multdoc = os.path.join(wkdir, multbasename) + '.doc'
                
                with open(multdoc, 'w') as fh:
                    for line in open(filename):
            	        if line.startswith('>'):
            		        varp = line.strip('>').rsplit('_',1)[0]
            		        if varp in varnames:
                    			fh.write(('<p>'+multbasename.rsplit('_', 1)[1]+' has only consensus sequences for: '+varp+' cannot align against self '+ '</p><br>\n'))
                #multalin_out.append(multdoc)
            else:
                base = os.path.basename(os.path.splitext(filename)[0])
                multhtml = os.path.join(wkdir, base) + '_multalin.html'
                multdoc = os.path.join(wkdir, base) + '.doc'
                multmsf = os.path.join(wkdir, base) + '_multalin.msf'
                multalin_out.append(multdoc)
                input_file = os.path.basename(filename)
                multalin_cmd = '/home/juma/Tools/multalin.5.4.1/multalin -c:%s -o:doc %s' % (blosumtab, input_file)
                
                try:
                    sys.stdout.write("\nMultalin MSA for " + os.path.basename(filename) + "\n")
                    multres = subprocess.check_call(multalin_cmd, env=env, shell=True)
                except Exception:
                    sys.stderr.write(
                        "Error occurred when generating multiple sequence alignment file using MULTALIN.\n")
                    sys.stderr.write("Command that was running: " + multalin_cmd + "\n")
                if multres == 0:
                    sys.stdout.write("\nMultiple sequence alignment with MULTALIN success!\n")
    return multalin_out


def doc2html(multalin_out):
    """Converts the doc(word) document produced by multalin to html"""


    tmpmult_list = []
    headhtml = '/home/juma/Tools/multalin.5.4.1/head.html'
    tailhtml = '/home/juma/Tools/multalin.5.4.1/tail.html'

    for docfile in multalin_out:
        
        dirname = os.path.dirname(docfile)
        base = os.path.basename(os.path.splitext(docfile)[0])
        tmp_multhtml = os.path.join(dirname, base)
        tmpmult_list.append(tmp_multhtml)

        start = False
        with open(tmp_multhtml, 'w') as htmlfile:
            for line in open(docfile):
                if line.startswith('<'):
                	htmlfile.write(line)

                elif line.startswith('//'):
                    start = True
                    htmlfile.write('</pre><pre class=seq><A NAME='"Alignment"'></A>')
                    htmlfile.write('\n')

                if start:
                    if '][' in line or ')(' in line or '[' in line and ']' or '(' in line and ')' in line:
                        line = line.replace('][', '')
                        line = line.replace(')(', '')
                        line = line.replace('[', '<em class=high>')
                        line = line.replace(']', '</em>')
                        line = line.replace('(', '<em class=low>')
                        line = line.replace(')', '</em>')
                        htmlfile.write(line)

    multalin_html = []
    res = ''
    for tmpfile in tmpmult_list:
        dirname = os.path.dirname(tmpfile)
        outhtml = os.path.basename(tmpfile)+'_multalin.html'
        multhtml = os.path.join(dirname, outhtml)
        multalin_html.append(multhtml)
        cmd = 'cat %s %s %s > %s' % (headhtml, tmpfile, tailhtml, multhtml)
        res = subprocess.check_call(cmd, env=env, shell=True)
    if res == 0:
        sys.stdout.write("\nDoc/Word to html conversion success\n")
    return multalin_html


def postresults(muscle_html, multalin_html, data_dict, geneid_list):
    """Post the results"""


    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        gidsfile = data[3]
        wkdir = data[4]
        outfmts = data[5]


    # convert fasta files to html files

    geneid_html = []
    for filename in geneid_list:
        fastahtml = os.path.join(wkdir, jid+'_'+os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0])+'_consensus.html'
        geneid_html.append(fastahtml)
        with open(fastahtml, 'w') as fhandle:
            with open(filename) as infile:
                for line in infile:
                    line = line.strip()
                    fhandle.write('<div>{}</div>'.format(line))
        

    report_file = os.path.join(wkdir, jid) + '_report.txt'   
    report_name = os.path.basename(report_file)

    all_alignments = muscle_html + multalin_html + geneid_list + geneid_html
    all_alignments.append(report_file)


    rawhtmllist = []
    link_list = []
    varietiesfilesurl = 'http://localhost/multi-varieties/'
    textfile = os.path.join(wkdir, jid)+'_links.html'
    fastafiles = {}

    htmlf_ = {}
    htmlms_ = {}
    htmlmu_ = {}
    rep_ = {}


    textname = os.path.basename(textfile)
    with open(textfile, 'w') as fhandle:
        for filename in all_alignments:
            rawhtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
            rawhtmllist.append(rawhtml)

            if filename.endswith('.fasta'):
                geneid = os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0]
                if os.path.getsize(filename) > 0:
                    fastahtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
                    htmlf_[geneid] = [fastahtml]
            elif '_consensus.html' in filename:
                geneid = os.path.basename(filename).rsplit('_', 1)[0]
                geneid = geneid.rsplit('_',1)[1]
                if geneid in htmlf_ and os.path.getsize(filename) > 0:
                    conshtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
                    htmlf_[geneid].append(conshtml)

            elif '_muscle.html' in filename or '_multalin.html' in filename:
                if '_muscle.html' in filename and os.path.getsize(filename) > 0 or '_multalin.html' in filename and os.path.getsize(filename) > 0:
                    geneid = os.path.basename(filename).rsplit('_', 1)[0]
                    geneid = geneid.rsplit('_',1)[1]
                    alignhtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
                    if not geneid in htmlms_:
                        htmlms_[geneid] = [alignhtml]
                    else:
                        htmlms_[geneid].append(alignhtml)
            else:

                rephtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)

                
                


    dd = defaultdict(list)
    for d in (htmlf_, htmlms_):
        for key, value in d.items():
            dd[key].append(' '.join(value))


    rephtml = 'http://localhost/media/multi-varieties/'+os.path.basename(report_file)
    with open(textfile, 'w') as file_obj:
        for k, v in dd.items():
            if len(v) == 1:
                fhtml = v[0].split()[0]
                chtml = v[0].split()[1]
                file_obj.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">\
                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
                
                file_obj.write(('<div class="col-xs-col-18"><p>'+k+': \
                    <a href="'+chtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view consensus</button>\
                    <a href="'+fhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download consensus</button>\
                    </a></p></div><br></body></html>'))

            elif len(v) > 1:
                msml = v[1].split()
                fhtml = v[0].split()[0]
                chtml = v[0].split()[1]
                if len(msml) == 1 and '_muscle.html' in msml[0]:
                    mshtml = msml[0]
                    file_obj.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">\
                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\
                        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
                        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
                    file_obj.write(('<div class="col-xs-18"><p>'+k+': \
                        <a href="'+chtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view consensus</button>\
                        <a href="'+fhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download consensus</button>\
                        <a href="'+mshtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view MUSCLE Alignment</button>\
                        </a></p></div><br></body></html>'))
                elif len(msml) == 1 and '_multalin.html' in msml[0]:
                    mlhtml = msml[0]
                    file_obj.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">\
                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\
                        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
                        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
                    file_obj.write(('<div class="col-xs-18"><p>'+k+': \
                        <a href="'+chtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view consensus</button>\
                        <a href="'+fhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download consensus</button>\
                        <a href="'+mlhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view MULTALIN Alignment</button>\
                        </a></p></div><br></body></html>'))
                else:
                    if len(msml) > 1:
                        mshtml = msml[0]
                        mlhtml = msml[1]
                        file_obj.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">\
                            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\
                            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
                            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
                        file_obj.write(('<div class="col-xs-18"><p>'+k+': \
                            <a href="'+chtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view consensus</button>\
                            <a href="'+fhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download consensus</button>\
                            <a href="'+mshtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view MUSCLE Alignment</button>\
                            <a href="'+mlhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view MULTALIN Alignment</button>\
                            </a></p></div><br></body></html>'))

        file_obj.write(('<a href="'+rephtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Report</button>'))


    for filename in all_alignments:
        if filename.endswith('.txt') or filename.endswith('.html'):
            filetype = os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0]
            geneid = os.path.basename(filename).rsplit('_', 1)[0]
                
        else:
            filetype = 'consensus'
            file_link = rawhtml
                
            geneid = os.path.basename(file_link).rsplit('_', 1)[1]
            linkstr  = '<a href="'+rawhtml+'">'+ filetype +' '+ geneid+ '</a><br>\n'
            link_list.append(linkstr)


        if not os.path.exists(filename) and os.path.getsize(filename) == 0:
            continue
        else:
            htmlfile = os.path.join(wkdir, os.path.basename(filename))           
            htmlname = os.path.basename(htmlfile)
            files = {'html_file': open(htmlfile, 'rb')}
            r = requests.post(varietiesfilesurl, files=files)
           
    for link in rawhtmllist:
        linkstr = '<a href="'
        linkstr = linkstr+link
        linkstr = linkstr+'">'
    rawhtmllist = json.dumps(rawhtmllist)

            



    



#            if '_muscle.html' in filename or '_multalin.html' in filename:
#                alignhtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
#                geneid = os.path.basename(filename).rsplit('_', 1)[0]
#                geneid = geneid.rsplit('_',1)[1]
#                alignment_type = os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0]
#                heading = alignment_type+' '+geneid
#                fhandle.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
#                fhandle.write(('<p>'+heading+'<a href="'+rawhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view</button></a></p><br></body></html>'))
#            elif filename.endswith('.fasta') or '_consensus.html' in filename:

#                if filename.endswith('.fasta') and os.path.getsize(filename) > 0:
#                    geneid = os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0]
#                    fastafiles[geneid] = [filename]
#                    rawconsensus = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
#                    #cons_text = 'consensus'+' '+geneid
#                    fhandle.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
#                    #fhandle.write(('<p>'+cons_text+'<a href="'+rawhtml+'"><button type="button" class="btn btn-primary"><span class="glyphicon glyphicon-download"></span> Download</button></a></p><br></body></html>'))
#                else:
#                    if os.path.getsize(filename) > 0:
#                        rawconsensushtml = 'http://localhost/media/multi-varieties/'+os.path.basename(filename)
#                        geneid = os.path.basename(filename).rsplit('_', 1)[0]
#                        geneid = geneid.rsplit('_',1)[1]
#                        if geneid in fastafiles:
#                            fastafiles[geneid].append(filename)
#                        alignment_type = os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0]
#                        heading = alignment_type+' '+geneid
#                        fhandle.write(('<p>'+geneid+': \
#                            <a href="'+rawconsensushtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view</button>\
#                            <a href="'+rawconsensus+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download</button>\
#                            </a></p><br></body></html>'))
#            else:
#                heading = os.path.basename(filename).rsplit('_', 1)[1]
#                fhandle.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">\
#                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><script\
#                    src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>\
#                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
#                #fhandle.write(('<p>'+heading+': \
#                #    <a href="'+rawconsensushtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view</button>\
#                #    <a href="'+rawconsensus+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-download"></span> Download</button>\
#                #    </a></p><br></body></html>'))
#                #fhandle.write('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head><body>')
#                fhandle.write(('<p>'+heading+': <a href="'+rawhtml+'"><button type="button" class="btn btn-default btn-sm"><span class="glyphicon glyphicon-eye-open"></span> Click to view</button></a></p><br><body></html>'))
           
#            if filename.endswith('.txt') or filename.endswith('.html'):
#                filetype = os.path.splitext(os.path.basename(filename).rsplit('_', 1)[1])[0]
#                geneid = os.path.basename(filename).rsplit('_', 1)[0]
#                
#            else:
#                filetype = 'consensus'
#                file_link = rawhtml
#                
#                geneid = os.path.basename(file_link).rsplit('_', 1)[1]
#                linkstr  = '<a href="'+rawhtml+'">'+ filetype +' '+ geneid+ '</a><br>\n'
#                link_list.append(linkstr)
#

#            if not os.path.exists(filename) and os.path.getsize(filename) == 0:
#                continue
#            else:
#                htmlfile = os.path.join(wkdir, os.path.basename(filename))           
#                htmlname = os.path.basename(htmlfile)
#                files = {'html_file': open(htmlfile, 'rb')}
#                r = requests.post(varietiesfilesurl, files=files)
           
#    for link in rawhtmllist:
#        linkstr = '<a href="'
#        linkstr = linkstr+link
#        linkstr = linkstr+'">'
#    rawhtmllist = json.dumps(rawhtmllist)



    # post files and data to the api

    url = 'http://localhost/multi-results-ids/'
    muscle_file = os.path.join(wkdir, jid)+'_muscle_alignments.html'
    musclefilename = os.path.basename(muscle_file)

    
    with open(muscle_file, 'w') as fhandle:
    	for file in all_alignments:
    		if '_multalin.html' in file or '.fasta' in file or '.txt' in file or '_consensus.html' in file:
    			continue
    		else:
    			with open(file) as infile:
    				for line in infile:
    					fhandle.write(line)

    multalin_file = os.path.join(wkdir, jid)+'_multalin_alignments.html'
    multalinfilename = os.path.basename(multalin_file)					

    with open(multalin_file, 'w') as fhandle:
    	for file in all_alignments:
    		if '_muscle.html' in file or '.fasta' in file or '.txt' in file or '_consensus.html' in file:
    			continue
    		else:
    			with open(file) as infile:
    				for line in infile:
    					fhandle.write(line)


    consensus_file = os.path.join(wkdir, jid)+'_consensus_sequences.html'
    consensusfilename = os.path.basename(consensus_file)
    

    with open(consensus_file, 'w') as fhandle:
        for file in all_alignments:
            if '_muscle.html' in file or '_multalin.html' in file or '.txt' in file or '_consensus.html' in file:
                continue
            else:
                with open(file) as infile:
                    for line in infile:
                        line = line.strip()
                        fhandle.write('<div>{}</div>'.format(line))
                        

    
    html_file = os.path.join(wkdir, jid)+'_multiple_alignments.html'
    htmlfilename = os.path.basename(html_file)

    with open(html_file, 'w') as fhandle:
        for file in all_alignments:
            if '.fasta' in file or '.txt' in file:
                continue
            else:
                if not os.path.exists(file) and os.path.getsize(file) == 0:
                    continue
                else:
                    with open(file) as infile:
                        for line in infile:
                            fhandle.write(line)


    if os.path.getsize(muscle_file) == 0 and os.path.getsize(multalin_file) == 0 and os.path.getsize(consensus_file) != 0:
        multipart_data = MultipartEncoder(
            fields={
                'consensus_file': (consensusfilename, open(consensus_file, 'rb')),
                'muscle_file': '',
                'multalin_file': '',
                'html_file': (htmlfilename, open(html_file, 'rb')),
                'uniqueid': jid,
                'htmlfilelist': rawhtmllist,
                'linksfile': (textname, open(textfile, 'rb')),
            }
            )
        response = requests.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})



    elif os.path.getsize(muscle_file) != 0 and os.path.getsize(multalin_file) == 0 and os.path.getsize(consensus_file) != 0:
        multipart_data = MultipartEncoder(
            fields={
                'consensus_file': (consensusfilename, open(consensus_file, 'rb')),
                'muscle_file': (musclefilename, open(muscle_file, 'rb')),
                'multalin_file': '',
                'html_file': (htmlfilename, open(html_file, 'rb')),
                'uniqueid': jid,
                'htmlfilelist': rawhtmllist,
                'linksfile': (textname, open(textfile, 'rb')),
            }
            )
        response = requests.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})

    elif os.path.getsize(muscle_file) == 0 and os.path.getsize(multalin_file) != 0 and os.path.getsize(consensus_file) != 0:
        multipart_data = MultipartEncoder(
            fields={
                'consensus_file': (consensusfilename, open(consensus_file, 'rb')),
        	    'muscle_file': '',
        	    'multalin_file': (multalinfilename, open(multalin_file, 'rb')),
                'html_file': (htmlfilename, open(html_file, 'rb')),
                'uniqueid': jid,
                'htmlfilelist': rawhtmllist,
                'linksfile': (textname, open(textfile, 'rb')),
            }
            )
        response = requests.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})

    
    else:
        multipart_data = MultipartEncoder(
            fields={
                'consensus_file': (consensusfilename, open(consensus_file, 'rb')),
                'muscle_file': (musclefilename, open(muscle_file, 'rb')),
                'multalin_file': (multalinfilename, open(multalin_file, 'rb')),
                'html_file': (htmlfilename, open(html_file, 'rb')),
                'uniqueid': jid,
                'htmlfilelist': rawhtmllist,
                'linksfile': (textname, open(textfile, 'rb')),
            }
            )
        response = requests.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})

    
    return all_alignments


def clean_():
    outdir = os.path.join(MEDIA_ROOT, 'output/')
    
    
    numdays = 86400*2
    print (numdays)
    now = time.time()
    print (now)

    for root, dirs, files in os.walk(outdir):
        for _dir in dirs:
            timestamp = os.path.getmtime(os.path.join(root,_dir))
            if  now-numdays > timestamp:
                try:
                    print ("clean up: %s" % os.path.join(root, _dir))
                    shutil.rmtree(os.path.join(root,_dir))
                except Exception as e:
                    print (e)
                    pass
                else:
                    print("clean up successful")



#############################
#   INPUT - FASTA sequences #
#############################

def createSequenceDict(submitted_data):
    """create a dictionary with submitted data, returns a dict with all the data"""

    start_time = datetime.now()
    sys.stdout.write("\nStarted analysis on: " +str(start_time)+ " for the job with id: " +str(submitted_data.uuid)+"\n")

    inputDIR = os.path.join(MEDIA_ROOT, 'species/')
    outputDIRPATH = os.path.join(MEDIA_ROOT, 'output/')
    workingDIR = os.path.join(outputDIRPATH, str(submitted_data.uuid)) + '/'

    variety_list = []
    variety_consensus_files = []
    data_dict = {}

    jobid = str(submitted_data.uuid)
    outfmts = submitted_data.outputfmt.split(',')

    

    for entry in submitted_data.varieties.all():
        if not os.path.exists(inputDIR):  # make input directory
            os.makedirs(inputDIR)

        if not os.path.exists(workingDIR): # make output directory
            os.makedirs(workingDIR)

        varietiesDIR = os.path.join(MEDIA_ROOT, entry.location)
        if not os.path.exists(varietiesDIR):
            os.makedirs(varietiesDIR)




        sequence_file = os.path.join(workingDIR, str(submitted_data.uuid) + '.fa')
        reference_basename = os.path.basename(str(entry.species.species_file))
        reference_file = os.path.join(inputDIR, reference_basename)
        variety_consensus_basename = os.path.basename(str(entry.variety_consensus))
        variety_consensus_file = os.path.join(varietiesDIR, variety_consensus_basename)


        # get varieties selected
        variety_list.append(entry.variety_name)
        variety_consensus_files.append(variety_consensus_file)

        # get sequence submitted
        sequenceContent = StringIO(str(submitted_data.sequence))  # get the content of the gene ids submitted
        sequenceData = sequenceContent.getvalue()
        if not os.path.exists(sequence_file):
            with open(sequence_file, 'w') as fhandle:
                fhandle.write(sequenceData)
        data_dict[jobid] = [variety_list, variety_consensus_files, reference_file, sequence_file, workingDIR, outfmts]
    return data_dict


def makelocalblast(data_dict):
    """Given the submitted data in form of a dictionary, the function makes a local blast based on selected varities, returns the data dict with db as additional value"""
    for jid, data in data_dict.items():
        
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        seqfile = data[3]
        wkdir = data[4]
        outfmts = data[5]

        consdict = {}
        # create a consensus file having all the consensus sequences for the selected varieties
        #if len(varnames) == 1:
        #    continue
        #else:
        consfile = os.path.join(wkdir) + 'consensus.fasta' # file having all the consensus files for the selected varieties
        #if os.path.exists(consfile):
        #    continue
        #else:

        for file in varfiles:
            with open(consfile, 'w') as outfile:
                for fname in varfiles:
                    with open(fname) as infile:
                        for line in infile:
                            outfile.write(line)

        for line in open(consfile):
            line = line.strip()
            if line.startswith('>'):
                consid = line.strip('>')
                consdict[consid] = ''
            else:
                consdict[consid] += ''.join(line.strip())
    

    # make a local database (on selected varieties) for blast

        consbase = os.path.splitext(os.path.basename(consfile))[0]+'db'
        dbname = os.path.join(wkdir, jid)+'_'+consbase
        cmd = '/home/juma/Tools/ncbi-blast-2.6.0+/bin/makeblastdb -in %s -dbtype nucl -out %s -parse_seqids' % (reffile, dbname)
        sys.stdout.write("Creating a local BLAST database for the selected varieties consensus sequences: " +' , '.join(varnames)+"\n")
        res = subprocess.check_call(cmd, env=env, shell=True)
        data_dict[jid] = [varnames, varfiles, reffile, dbname, seqfile, wkdir, outfmts]
    return data_dict

def runblast(data_dict):
    """run blastn to query the database for sequence identifiers"""

    # blastn parameters

    tsk = 'blastn'
    wordsize = 7
    #evalue = 1e-10
    outformat = 6
    percidentity = 100
    numthreads = 6

    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        dbname = data[3]
        seqfile = data[4]
        wkdir = data[5]
        outfmts = data[6]

        queryOut = os.path.join(wkdir, os.path.basename(os.path.splitext(seqfile)[0]))+'.tab'
        cmd = '/home/juma/Tools/ncbi-blast-2.6.0+/bin/blastn -query %s -task %s -db %s -out %s -word_size %d -num_threads %d -evalue 1e-10 -perc_identity %f -outfmt %d' % (seqfile, tsk, dbname, queryOut, wordsize, numthreads, percidentity, outformat)
        sys.stdout.write("perfoming blast \n")
        res = subprocess.check_call(cmd, env=env, shell=True)
        data_dict[jid] = [varnames, varfiles, reffile, queryOut, wkdir, outfmts]
    return data_dict

def parseblastout(data_dict):
    """Parses the BLAST output to fetch sequence identifiers passing various validators"""

    for jid, data in data_dict.items():
        varnames = data[0]
        varfiles = data[1]
        reffile = data[2]
        blastout = data[3]
        wkdir = data[4]
        outfmts = data[5]

        geneid_dict = {}
        geneidfile = os.path.join(wkdir, os.path.basename(os.path.splitext(blastout)[0]))+'.txt'
        if not os.path.exists(blastout) and os.path.getsize(blastout) < 0:
            sys.stdout.write("There were no sequence identifiers from BLAST\n")
        else:
            for line in open(blastout):
                line = line.strip()
                q_id = line.split()[0]
                s_id = line.split()[1]
                per_idnty = line.split()[2]
                aln_len = line.split()[3]
                mismatch = line.split()[4]
                gap_open = line.split()[5]
                q_start = line.split()[6]
                q_end = line.split()[7]
                s_start = line.split()[8]
                s_end = line.split()[9]
                evalue = line.split()[10]
                bitscore = line.split()[11]

                
                if per_idnty == '100.000' and q_start == s_start and q_end == s_end:
                    geneid_dict[s_id] = s_id

    
    with open(geneidfile, 'w') as outfile:
        for k, v in geneid_dict.items():
            outfile.write(str(k)+'\n')


            data_dict[jid] = [varnames, varfiles, reffile, geneidfile, wkdir, outfmts]
    return data_dict