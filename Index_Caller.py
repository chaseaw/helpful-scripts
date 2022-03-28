#!/usr/bin/env python

'''
Created March 2022
@author: chasew
Mines barcodes from MiSeq Read Index Files

Usage: python Index_Caller.py --R1 R1.fastq.gz [--R2 R2.fastq.gz]  

'''

import os,sys,argparse,gzip,shutil,operator

## Unzips gzipped fastqs ##
def unzip_file(gz): 
	
	filename,fileext = os.path.splitext(gz)
	assert fileext == ".gz", "File extension should be in .fastq.gz format."

	with gzip.open(gz, 'rb') as infile:
		with open(filename, 'wb') as outfile:
			shutil.copyfileobj(infile, outfile)

	return filename

## Accommodates multiple common extensions for fastqs ##
def checkformat(file):
	ext = os.path.splitext(file)[1]

	if ext == ".gz":
		outfile = unzip_file(file)
	elif ext in [".fastq",".fq",".FASTQ",".FQ"]:
		outfile = file
	else:
		assert ext == ".gz", "File format not recognized. Must be fastq.gz or .fastq."

	return outfile

## Parses the index fastq into a dictionary of {readID: "sequence"} ##
def read_barcodes(index_fastq):
	
	code_dict = {}
	
	with open(index_fastq,"r") as infile:
		
		end_of_lines = False
		line_count = 1

		read = ""
		barcode = ""
		
		while not end_of_lines:

			line = infile.readline()
			
			if not line:
				end_of_lines = True
				break
			
			if line_count == 1:
				read = line.rstrip().split(' ')[0]
			elif line_count == 2:
				barcode = line.rstrip()
			elif line_count == 4:
				code_dict[read] = barcode
				read = ""
				barcode = ""
				line_count = 0

			line_count += 1

	return code_dict

## Counts barcode appearances in either single read or dual read format ##
## Outputs a list of tuples with [(barcode,highest_count),...,(barcode,lowest_count)] format ##
def get_barcodes(index_fastq,R2=None):

	I1 = read_barcodes(index_fastq)

	barcode_counts = {}

	if R2 is not None:

		I2 = read_barcodes(R2)

		for read in I1:
			pair = "{}:{}".format(I1[read],I2[read])
			
			if pair not in barcode_counts:
				barcode_counts[pair] = 1
			else:
				barcode_counts[pair] += 1

	else:
		for read in I1:
			barcode = I1[read]

			if barcode not in barcode_counts:
				barcode_counts[barcode] = 1
			else:
				barcode_counts[barcode] += 1

	sorted_barcodes = sorted(barcode_counts.items(), key=operator.itemgetter(1))
	sorted_barcodes.reverse()

	return sorted_barcodes

## Takes in the ordered barcode tuple list and prints to a .csv file ##
## The n argument specifies how many barcodes should be printed ##
def print_barcodes(sorted_barcodes,n=20,outname="TOP_BARCODES"):
	
	iterations = min(n,len(sorted_barcodes))

	with open("{}.csv".format(outname),'w') as outfile:

		outfile.write("BARCODE,COUNT\n")
		
		for i in range(iterations):
			outfile.write("{},{}\n".format(sorted_barcodes[i][0],sorted_barcodes[i][1]))

if __name__ == '__main__': # allows another python script to import the functions

	parser = argparse.ArgumentParser(description="Gives list of most frequently appearing barcodes in fastq index files", usage='%(prog)s --R1 R1.fastq.gz [--R2 R2.fastq.gz] [options]',add_help=False) # a description of the function

	required = parser.add_argument_group('Required Input', 'Specify the index fastqs to harvest barcodes.')

	required.add_argument("--R1",help="Input index fastq", required=True)

	data_opt = parser.add_argument_group('Basic Arguments', 'These options can be used to change how the program runs.')
	data_opt.add_argument('-R',"--R2",default=None,help="Specify a matched read 2 index fastq.")
	data_opt.add_argument('-N',"--Niter",type=int,default=20,help="Specify the number of barcodes to look for. Default = 20.")
	data_opt.add_argument('-O',"--Outname",default="TOP_BARCODES",help="Specify a file prefix for the output csv. Default is TOP_BARCODES.")

	help_opt = parser.add_argument_group('Help')
	help_opt.add_argument('-h', '--help', action="help", help="show this help message and exit")

	args = parser.parse_args()

	## get read 1 barcodes ##
	R1 = checkformat(args.R1)

	## get read 2 barcodes ##
	if args.R2 is not None:
		R2 = checkformat(args.R2)
	else:
		R2 = args.R2

	## makes ordered list of barcodes by frequency ##
	barcodes = get_barcodes(R1,R2=R2)

	## prints desired number of found barcodes ##
	print_barcodes(barcodes,n=args.Niter,outname=args.Outname)



