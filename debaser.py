#!/usr/bin/env python

from __future__ import print_function
import os
import re
import sys
import time
import glob
import argparse
import subprocess
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from os import path
from datetime import datetime
import logging
import os

logging.basicConfig(filename='debaser.log', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger().addHandler(logging.StreamHandler())





BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# set start time format
format = "%a %b %d %H:%M:%S %Y"
start_time = datetime.now()
s = start_time.strftime(format)
print("\nStarted analysis on: " +s+  "\n")

##########################################################################
#       FUNCTIONS
##########################################################################


def read_input(input_file, reference):
    """
    read in the input file

    parameters:
        - input_file : file containing gene identifiers of sequences in FASTA format
        - reference :  reference file for the organism (contains only CDS sequences)
    returns:
        - input file : if input file contains gene identifiers, returns a FASTA format file (else return input FASTA)
    """
    fasta=False
    geneID=False
    geneID_dict={}
    reference_dict={}
    validIDs=[]
    invalidIDs=[]
    matches=[]

    for line in open(os.path.join(input_file)):
        line = line.rstrip()
        if not '>' in line:
            geneID = True
            fasta = False
            gID_file = os.path.join(input_file)

        elif '>' in line.strip():
            fasta = True
            geneID = False
            input_file = os.path.join(input_file)
            if fasta == True and geneID == False:
                return input_file

    if geneID == True and fasta == False:
        gID_file = os.path.join(input_file)
        print(
            "\nGenerating FASTA format sequences -> ["+os.path.basename(gID_file)+ "]\n")
    for line in open(gID_file):
        header = line.strip().split()[0]
        geneID_dict['>' + header] = ''

    for line in open(reference):
        line = line.rstrip()
        if line.startswith('>'):
            line = line.strip()
            header = line.split()[0]
            reference_dict[header] = line
        else:
            sequence = ''.join(line.strip())
            reference_dict[header] += ' ' + sequence

    geneIDSEQ={}
    for k, v in geneID_dict.items():
        
        if reference_dict.get(k) == None:
            continue
        else:
            value = reference_dict.get(k)
            header = value.split()[0]
            
            sequence = ''.join(value.split()[6:])
            geneIDSEQ[header] = sequence
        if k in reference_dict:
            validIDs.append(k)         # append valid gene ids
        if k not in reference_dict:
            invalidIDs.append(k)       # append invalid gene ids

    print(str(len(geneID_dict.keys()))+ " submitted gene identifiers; of these:")
    print(" "+str(len(validIDs))+ " valid gene identifiers")
    print(" "+str(len(invalidIDs))+ " invalid gene identifiers\n")
    for id in invalidIDs:
        sys.stdout.write("\n " + id + " \n")

    # write the FASTA format file for input gene identifiers

    geneid_out=StringIO()
    geneid_basename = os.path.splitext(os.path.basename(gID_file))[0] + '.fa'
    geneid_filename = os.path.join(os.path.dirname(input_file), geneid_basename)

    for key, value in geneIDSEQ.items():
        if value != None:
            geneid_out.write(key + '\n' + value + '\n')
    fas = geneid_out.getvalue()

    with open(geneid_filename, 'w') as fhandle:
        fhandle.write(fas)
    return geneid_filename


def build_index(input_file):
    """
    build index for the input data using bowtie2

    parameters:
        - input_file : file containing sequences in FASTA format

    returns:
        idx : bt2 index files
    """
    res=''
    matches=[]
    inputDIR=os.path.dirname(os.path.join(input_file))

    for filename in os.listdir(inputDIR):
        pattern = str(os.path.basename(os.path.join(input_file)))+'.'
        idx = os.path.dirname(input_file)+'/'+os.path.basename(os.path.join(input_file))+'.1.bt2'
        if os.path.exists(os.path.join(idx)):
            continue
        else:
            print("Building the index files for" +os.path.join(input_file)+ "\n")
            command = 'bowtie2-build %s %s' % (os.path.join(input_file), os.path.join(input_file))
        try:
            res = subprocess.check_call(command, shell=True)
        except Exception:
            print("Error occurred while running the program!")
            print("Command that was running: " +command+ "\n")
    return res


def read_type(varDIR):
    """
    determine the read type : single of paired-end

    parameters:
        - varDIR : directory/folder containing the varieties (.fastq, .fq or .fastq.gz or fq.gz files)

    returns:
        reads - list of reads
    """

    reads=[]
    variety_dict = {}
    ext = 'fastq fq gz'.split()

    for variety in os.listdir(varDIR):
        if not os.path.splitext(variety)[1][1:] in ext:
            continue
        variety_filename = os.path.join(varDIR, variety)
        variety_pattern = os.path.basename(variety_filename)

        variety_name = variety_pattern.rsplit('_', 1)[0]
        if '.' in variety_name:
            try:
                raise ValueError(": filenames should have any of these suffixes "
                                 "[ _1.fastq/_2.fastq, _1.fq/_2.fq, _1.fastq.gz/_2.fastq.gz ]\n")
            except ValueError as exception:
                print("%s has incorrect suffix" % variety_name, exception)
            continue
        if not variety_name in variety_dict:
            variety_dict[variety_name]=[variety_filename]
        else:
            variety_dict[variety_name].append(variety_filename)
    for k, v in variety_dict.items():
        reads.append(v)
    return reads


def align_single(input_file, reads, outputDIR):
    """
    align single-end reads using bowtie2

    parameters:
        - input_file : file containing sequences in FASTA format
        - reads : list of lists having reads categorised as either single or paired
        - threads : number of processors required by the program (bowtie2)
        - outputDIR : directory/folder to store the program output
        -
    returns:
        -single_alignments - list of single-end sorted binary alignment files (.sorted.bam)
    """

    prg1="bowtie2"
    prg2="samtools"
    p1=8
    p2=8
    p3=8
    mxmem='2G'
    se_procs=[]
    se_alignments=[]

    for read_id in reads:
        if len(read_id) == 1:
            se = read_id[0]
            se_name = os.path.splitext(os.path.basename(se))[0].rsplit('_',1)[0]
            bam_out = se_name + '_' + os.path.splitext(os.path.basename(input_file))[0] + '.bam'
            bamfilename = os.path.join(outputDIR, bam_out)
            sorted_bam = os.path.splitext(bamfilename)[0] + '.sorted'
            sortedbamfile = os.path.join(sorted_bam) + '.bam'
            se_alignments.append(sortedbamfile)

            if os.path.exists(sortedbamfile) and os.path.getsize(sortedbamfile) > 0:
                sys.stdout.write("\t -> [" +se+ "] already processed!\n")
                continue
            else:
                #print("-> Processing [" + se + "]\n")
                #proc1 = subprocess.Popen([prg1, '-p', str(p1), '-x', input_file, '-U', se], stdout=subprocess.PIPE)
                #proc2 = subprocess.Popen([prg2, 'view', '-bS', '-@', str(p2), '-'], stdin=proc1.stdout, stdout=subprocess.PIPE)
                #proc3 = subprocess.Popen([prg2, 'sort', '-@', str(p3), '-m', mxmem, '-', sorted_bam], stdin=proc2.stdout, stdout=subprocess.PIPE)
                #se_procs.append(proc3)
            #[proc3.wait() for proc3 in se_procs]


                print("-> Processing [" +se+ "]\n")
                cmd = 'bowtie2 -p %d -x %s -U %s | samtools view -bS -@ %d - | samtools sort -@ %d -m %s - %s' % \
                      (p1, input_file, se, p2, p3, mxmem, sorted_bam)
            try:
                res = subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
                if res == 0:
                    print("\t -> Wrote " +str(os.path.getsize(sortedbamfile))+ " bytes to " +sortedbamfile+ "\n")
            except Exception:
                print("Error occurred while running the program!\n")
                print("Command that was running: " + cmd + "\n")
    return se_alignments

def align_paired(input_file, reads, outputDIR):
    """
    align paired-end reads using bowtie2

    parameters:
        - input_file : file containing sequences in FASTA format
        - reads : list of lists having reads categorised as either single or paired
        - threads : number of processors required by the program (bowtie2)
        - outputDIR : directory/folder to store the program output
    returns:
        -pe_alignments : list of paired-end sorted binary alignment files (.sorted.bam)
    """

    p1=8
    p2=8
    p3=8
    mxmem='2G'
    pe_procs=[]
    pe_alignments=[]

    for read_id in reads:
        if len(read_id) == 2:
            pe = os.path.basename(read_id[0])
            pe_name = os.path.splitext(os.path.basename(pe))[0].rsplit('_',1)[0]
            pe_read1, pe_read2 = read_id[0], read_id[1]
            bam_out = pe_name + '_' + os.path.splitext(os.path.basename(input_file))[0] + '.bam'
            bamfilename = os.path.join(outputDIR, bam_out)
            sorted_bam = os.path.splitext(bamfilename)[0]+'.sorted'
            sortedbamfile = os.path.join(sorted_bam)+'.bam'
            pe_alignments.append(sortedbamfile)
            if os.path.exists(sortedbamfile) and os.path.getsize(sortedbamfile) > 0:
                print("\t -> ["+os.path.basename(pe_read1)+ ' , ' +os.path.basename(pe_read2)+ " already processed!\n")
                continue
            else:
                print("-> Processing [" +pe_read1+' , '+pe_read2+ "]\n")
                cmd = 'bowtie2 -p %d -x %s -1 %s -2 %s | samtools view -bS -@ %d - | samtools sort -@ %d - %s' % \
                      (p1, input_file, pe_read1, pe_read2, p2, p3, sorted_bam)
            try:
                res = subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
                if res == 0:
                    sys.stdout.write("\t -> Wrote " +str(os.path.getsize(sortedbamfile))+ " bytes to " +sortedbamfile+ "\n")
            except Exception:
                print("Error occurred while running the program!")
                print("Command that was running: " + cmd + "\n")
    return pe_alignments


def angsd2fasta(se_alignments, pe_alignments):

    """
    create gzipped consensus FASTA format file

    parameters:
        - se_alignments : list of all single-end binary alignment files
        - pe-alignments : list of all single-end binary alignment files
    returns:
        - angsd_list : list of compressed consensus files
        - args : file containing the arguments/parameters used in running the program (.arg)
    """


    angsd_list=[]
    all_alignments=se_alignments+pe_alignments

    for bamfile in all_alignments: 
        angsd_outfile = os.path.splitext(bamfile)[0]
        angsd_zipped = angsd_outfile + '.fa.gz'
        angsd_list.append(angsd_zipped)
        if os.path.exists(angsd_zipped) and os.path.getsize(angsd_zipped) > 0:
            print("Compressed consensus file " +os.path.basename(angsd_zipped)+ " already exists!\n")
            continue
        else:
            print("Generating ["+os.path.basename(angsd_zipped)+ "] consensus\n")
            cmd = 'angsd -i %s -doFasta 2 -doCounts 1 -out %s' % (bamfile, angsd_outfile)
            res = subprocess.check_call(cmd, shell=True)

    return angsd_list

def uncompressANGSD(angsd_list):
    """
    uncompress the consensus files (.fa.gz) using gunzip

    parameters:
        - angsd_list : list of all compressed (.fa.gz) consensus files
    returns:
        - uncompressed_files : list of uncompressed consensus files (FASTA format)
    """

    res=''
    uncompressed_files=[]
    for gzfile in angsd_list:
        consensus = os.path.splitext(gzfile)[0]
        uncompressed_files.append(consensus)
        if os.path.exists(consensus) and os.path.getsize(consensus) > 0:
            print(os.path.basename(consensus)+ " already exists!\n")
            continue
        else:
            sys.stdout.write("-> uncompressing "+os.path.basename(gzfile)+ "\n")
            cmd = 'gunzip -c %s > %s' % (gzfile, consensus)
            res = subprocess.check_call(cmd, shell=True)
    return uncompressed_files

def remove_completelymasked(uncompressed_files):
    """
    get rid of completely masked sequences, append variety name(s)

    parameters:
        - uncompressed_files : list of all uncompressed (.fa) consensus files
    returns:
        - consensus_files : list of consensus files (FASTA format) without completely masked sequences
    """

    dict = {}
    consensus_files = []
    for filename in uncompressed_files:
        if os.path.getsize(filename) == 0:
            sys.stdout.write("\t -> NO CONSENSUS SEQUENCES : [ "+filename+" ]\n")
        else:
            name_to_append = os.path.basename(filename).split('_')[0]
            dict[name_to_append] = filename
            files_list = [file for file in dict.values()]

    for key, filename in dict.items():
        consensus = os.path.splitext(os.path.splitext(filename)[0])[0]+'.consensus.fa'
        consensus_files.append(consensus)
        if os.path.exists(consensus):
            print("\t-> ["+os.path.basename(consensus)+ "] already exists!\n")
        else:
            print("removing totally masked sequences in \t"+filename+"\n")
            with open(consensus, 'w') as outfile:
                for line in open(filename):
                    line = line.strip()
                    if line.startswith('>'):
                        newheader = '>'+key+'_'+line.strip('>')
                        outfile.write(newheader)
                        outfile.write('\n')
                    else:
                        if not 'A' and 'C' and 'G' and 'T' in line:
                            continue
                        else:
                            outfile.write(line)
                            outfile.write('\n')
            print("\t -> Wrote "+str(os.path.getsize(consensus))+" bytes to \t"+consensus+ "\n")
    return consensus_files

##########################################################################
#       PARSE COMMANDLINE OPTIONS
##########################################################################

parser=argparse.ArgumentParser()
helpstr = """python debaser.py [options]"""
parser.add_argument('-i', '--infile',    help="file having gene identifiers or FASTA format sequences")
parser.add_argument('-r', '--reference', help="Reference file (CDS only)")
parser.add_argument('-v', '--variety',   help="varieties directory/folder")
parser.add_argument('-o', '--output',    help="output directory")
args=parser.parse_args()

# open input file:
if args.infile != None:
    inputfilename = args.infile
else:
    sys.stderr.write("Please specify input file!\n")
    sys.exit(2)

# open the reference file
if args.reference != None:
    referencefilename = args.reference
else:
    sys.stderr.write("Please specify the reference sequence file!\n")
    sys.exit(2)

# open the varieties directory
if args.variety != None:
    varietydir = args.variety
else:
    sys.stderr.write("Please provide the directory/folder containing the variety files (.fastq/.fastq.gz, .fq/fq.gz!\n")
    sys.exit(2)

# open the output directory
if args.output != None:
    outputdir = args.output
    if not os.path.exists(args.output):
        os.makedirs(args.output)
else:
    sys.stderr.write("Please specify the output directory!\n")
    sys.exit(2)


# write STDOUT to a log file
class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self) :
        for f in self.files:
            f.flush()

f = open('debaser.log', 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)

##########################################################################
#	CALL FUNCTIONS
##########################################################################

in_data=read_input(inputfilename, referencefilename)
index=build_index(in_data)
readtype_filelist=read_type(varietydir)
single_filelist=align_single(in_data, readtype_filelist, outputdir)
paired_filelist=align_paired(in_data, readtype_filelist, outputdir)
angsdout_filelist=angsd2fasta(single_filelist, paired_filelist)
uncompressed_filelist=uncompressANGSD(angsdout_filelist)
consensus_filelist=remove_completelymasked(uncompressed_filelist)

# remove unwanted files
for f in os.listdir(outputdir):
    if not 'consensus' in f:
        os.remove(os.path.join(outputdir, f))

print("# Done!")

# set end time format
end_time = datetime.now()
e = end_time.strftime(format)
tdelta = end_time - start_time

print("\nCompleted analysis on: "+e+ "\n" )

# format the time delta object to human readable form
d = dict(days=tdelta.days)
d['hrs'], rem = divmod(tdelta.seconds, 3600)
d['min'], d['sec'] = divmod(rem, 60)

if d['min'] is 0:
    fmt = '{sec} sec'
elif d['hrs'] is 0:
    fmt = '{min} min {sec} sec'
elif d['days'] is 0:
    fmt = '{hrs} hr(s) {min} min {sec} sec'
else:
    fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'
print("[ALL done] Runtime: " +'\t'+fmt.format(**d))
