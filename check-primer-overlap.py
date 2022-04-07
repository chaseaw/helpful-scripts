#!/usr/bin/python
'''
Created April 2022
@author: chasew
Takes in a csv with two lists of primer barcodes and checks for duplicates.
Usage python check-primer-overlap.py --csv


'''

import os,sys,argparse

def internal_list_check(lst,name):
	duplicates = []

	for item in lst:
		if lst.count(item) > 1:
			if item not in duplicates:
				print("barcode {} appears more than once in {}".format(item,name))
				duplicates += [item]

	return duplicates

def overlapping_lists(lst1,lst2):
	duplicates = []

	for item in lst2:
		if item in lst1:
			if item not in duplicates:
				print("barcode {} is in both lists".format(item))
				duplicates += [item]

	return duplicates

def assert_length(lst_list,klength):
	
	for lst in lst_list:	
	
		for barcode in lst:
	
			if len(barcode) != klength:
				print("{}".format(barcode))
				assert len(barcode) == klength, "All barcodes are not of the specified length ({})".format(klength)

def check_lists(csv,klength=8):
	
	with open(csv,'r') as infile:
		lines = infile.readlines()

	list1,list2 = [[],[]]

	for line in lines:
		info = line.rstrip().split(',')
		if len(info[0]):
			list1 += [info[0].strip()]
		if len(info[1]):
			list2 += [info[1].strip()]

	print("comparing lists of {} and {} barcodes".format(len(list1),len(list2)))

	assert_length([list1,list2],klength)

	dup_1 = internal_list_check(list1,"list 1")

	dup_2 = internal_list_check(list2,"list 2")
	
	overlap = overlapping_lists(list1,list2)

	print("{} barcodes are repeated in list 1, {} barcodes are repeated in list 2, and {} barcodes are shared between lists".format(len(dup_1),len(dup_2),len(overlap)))
	print("barcode checking complete.")

if __name__ == '__main__': # allows another python script to import the functions

	parser = argparse.ArgumentParser(description="Checks if barcodes in two lists (two column csv) overlap.", usage='%(prog)s --csv [options]',add_help=False) # a description of the function

	required = parser.add_argument_group('Required Input', 'These specifications are necessary to run.')
	required.add_argument("--csv",type=str,help="Input csv with two barcode lists.", required=True)

	data_opt = parser.add_argument_group('Basic Arguments', 'These options can be used to change how the program runs.')
	data_opt.add_argument("-K","--klength",type=int,default=8,help="Set length of barcodes. All should be equal length. Default is 8.")

	help_opt = parser.add_argument_group('Help')
	help_opt.add_argument('-h', '--help', action="help", help="show this help message and exit")

	args = parser.parse_args()

	check_lists(args.csv,klength=args.klength)