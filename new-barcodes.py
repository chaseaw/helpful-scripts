#!/usr/bin/python
'''
Created April 2022
@author: chasew
Takes in a single column csv with a list of primer barcodes, calculates average hamming distance, and generates desired number of new barcodes.
Usage python new-barcodes --csv --new


'''

import os,sys,argparse
from statistics import median,mean
from random import choices

def pos_dict(barcode):
	
	pos_dict = {}
	for i in range(1,len(barcode)+1):
		pos_dict[i] = [barcode[i-1].upper()]

	return pos_dict

def merge_dicts(all_dict,item):

	bar_dict = pos_dict(item)
	new_dict = {}

	if all_dict:	
		for d in (all_dict, bar_dict): 
			for key, value in d.items():
				new_dict[key] = all_dict[key] + bar_dict[key]		
	else:
		new_dict = bar_dict.copy()

	return new_dict

def internal_list_check(lst,name):
	duplicates = []
	uniques = []

	all_dict = {}

	for item in lst:
		if lst.count(item) > 1:
			if item not in duplicates:
				print("barcode {} appears more than once in {}".format(item,name))
				duplicates += [item]
				uniques += [item]
				all_dict = merge_dicts(all_dict,item)


		else:
			uniques += [item]
			all_dict = merge_dicts(all_dict,item)

	probs_dict = {}

	for position in all_dict:
		probs_dict[position] = {"A":all_dict[position].count("A"),"T":all_dict[position].count("T"),"C":all_dict[position].count("C"),"G":all_dict[position].count("G")}

	return [duplicates,uniques,probs_dict]

def hamming_distance(test1,test2):

	assert len(test1) == len(test2), "Cannot define Hamming distance for strings of different lengths."

	distance = 0
	for i in range(len(test1)):
		if test1[i].upper() != test2[i].upper():
			distance += 1

	return distance

def get_medians(uniques,distwarn=2):

	medians = []
	mins = {}
	bad_pairs = []

	for i in range(len(uniques)-1):
		distances = []
		for j in range(i+1,len(uniques)):

			distance = hamming_distance(uniques[i],uniques[j])
			distances += [distance]
			if distance < distwarn:
				bad_pairs += [(uniques[i],uniques[j])]

		medians += [(uniques[i],median(distances))]
		mins[uniques[i]] = min(distances)

	return [medians,mins,bad_pairs]

def print_probs_dict(probs_dict):
	
	prob_list = []

	with open("barcode_nt_distributions.csv",'w') as outfile:
		outfile.write("position,A,G,C,T\n")
		
		for i in range(1,len(probs_dict)+1):

			nA,nG,nC,nT = [probs_dict[i]["A"],probs_dict[i]["G"],probs_dict[i]["C"],probs_dict[i]["T"]]
			pA,pG,pC,pT = [round((i/sum([nA,nG,nC,nT]))*100,1) for i in [nA,nG,nC,nT]]
			outfile.write("{},{},{},{},{}\n".format(i,pA,pG,pC,pT))

			prob_list += [[pA,pG,pC,pT]]

	return prob_list

def eval_list(csv,klength=8,distwarn=2):
	
	with open(csv,'r') as infile:
		lines = infile.readlines()

	barcodes = []

	for line in lines:
		barcode = line.rstrip()
		
		barcodes += [barcode]

		if len(barcode) != klength:
			print(barcode)
			assert len(barcode) == klength,"All barcodes are not expected length"

	duplicates,uniques,probs_dict = internal_list_check(barcodes,"list")

	prob_list = print_probs_dict(probs_dict)

	medians,mins,bad_pairs = get_medians(uniques,distwarn=distwarn)

	sum_of_medians = 0
	count = 0

	medians.sort(key = lambda x: x[1])

	minimum_dist = klength

	with open("barcode_distances.csv",'w') as outfile:
		outfile.write("barcode,median_hamming_dist,min_hamming_dist\n")
		
		for item in medians:
			sum_of_medians += item[1]
			count += 1
			outfile.write("{},{},{}\n".format(item[0],item[1],mins[item[0]]))
			minimum_dist = min(minimum_dist,mins[item[0]])

	median_mean = sum_of_medians/count

	print("The average median hamming distance of barcodes in the set is {}".format(median_mean))
	print("The smallest hamming distance of barcodes in the set is {}".format(minimum_dist))

	with open("bad_pairs.csv",'w') as outfile:
		for pair in bad_pairs:
			outfile.write("{},{}\n".format(pair[0],pair[1]))

	return [median_mean,uniques,prob_list]

def invert_pick(letters,probs):
	assert len(letters) == len(probs), "alphabet and probabilities are not the same length."

	combined_list = list(zip(letters,probs))
	combined_list.sort(key = lambda x: x[1])
		
	new_letters,new_probs = [[i for i,j in combined_list],[j for i,j in combined_list]]
	new_probs.reverse() # invert probabilities so less frequently appearing letters are now favored

	choice = choices(new_letters,weights=tuple(new_probs),k=1)

	return choice[0]

def create_barcode(existing,target_dist,letters,prob_list,min_ham=2,max_tries=10):
		
	count = 0
	check_pass = False
	target = target_dist

	while not check_pass:
		if count >= max_tries:
			target -= 1
			count = 0

		if target < 3:
			print("failed to create barcode")
			barcode = ""
			break

		barcode = ""

		for probs in prob_list:
			barcode += invert_pick(letters,probs)

		if barcode not in existing:
			
			if not any(x in barcode for x in ["GGG","CCC","TTT","AAA"]):

				distances = []
				for i in range(len(existing)):
					distance = hamming_distance(existing[i],barcode)
					distances += [distance]

				if (median(distances) >= target) and (min(distances) >= min_ham):

					check_pass = True

		count += 1

	return barcode

if __name__ == '__main__': # allows another python script to import the functions

	parser = argparse.ArgumentParser(description="Generates desired number of new barcodes from existing list.", usage='%(prog)s --csv --new [options]',add_help=False) # a description of the function

	required = parser.add_argument_group('Required Input', 'These specifications are necessary to run.')
	required.add_argument("--csv",type=str,help="Input csv with two barcode lists.", required=True)
	required.add_argument("--new",type=int,help="Number of new barcodes to make.", required=True)

	data_opt = parser.add_argument_group('Basic Arguments', 'These options can be used to change how the program runs.')
	data_opt.add_argument("-K","--klength",type=int,default=8,help="Set length of barcodes. All should be equal length. Default is 8.")
	data_opt.add_argument("-O","--outname",type=str,default="new_barcodes",help="Set the prefix of the output csv with new barcodes. Default is new_barcodes.")
	data_opt.add_argument("-H","--min_hamming",type=int,default=2,help="Sets the minimum hamming distance between any two pairs of barcodes. Default is 2.")

	help_opt = parser.add_argument_group('Help')
	help_opt.add_argument('-h', '--help', action="help", help="show this help message and exit")

	args = parser.parse_args()

	median_mean,uniques,prob_list = eval_list(args.csv,klength=args.klength,distwarn=args.min_hamming)

	new_codes = []

	for i in range(args.new):
		new_code = create_barcode(uniques,median_mean,["A","G","C","T"],prob_list,min_ham=args.min_hamming)
		uniques = uniques.copy() + [new_code]
		new_codes += [new_code]

	with open("{}.csv".format(args.outname),'w') as outfile:
		for barcode in new_codes:
			outfile.write("{}\n".format(barcode))
