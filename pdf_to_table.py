#!/usr/bin/env python

import tabula
import argparse
import os


def parseargs():
	parser = argparse.ArgumentParser(description="Parse a pdf table into a csv. Example: python tabula-test.py -i text-based.pdf -a 109.01,60.644,751.164,293.545 -p 1 -a 109.754,303.219,753.396,533.888 -p 1 -c")
	parser.add_argument("-i", "--pdf", type=str, help="Path to the pdf")
	parser.add_argument("-a", "--area", type=str, action='append', required=True, help="Four-item list of top, left, bottom, and right of table location in a page. \
						Must match up to number of pages.\
						Example: '406, 24, 695, 589'")
	# python arg.py -a [406, 24, 695, 589] -a [406, 24, 695, 589]
	parser.add_argument("-p", "--pages", action='append', required=True, help="Pages of tables in file. Must match up to number of areas.\
						Example: '1'")
	# python arg.py -p 1 -p 2 -p 2 -p 3
	parser.add_argument("-c", "--concatenate", action='store_true', help="Add flag if all parsed tables should be concatenated together")
	parser.add_argument("-o", "--OCR", action='store_true', help="Add flag if pdf needs to be OCRed")
	
	args = parser.parse_args()
	args.area = [list(map(float, item.split(','))) for item in args.area]
	#args.pages = [[item] for item in args.pages]
	return(args)

def saveoutputfile(inputfile):
	base_name, extension = os.path.splitext(inputfile)
	new_name = base_name + "_tables_parsed.csv"
	return new_name


def tabula_parse(inputfile, area, page):
	df = tabula.read_pdf(inputfile,
						 lattice=True,
						 pages=page,
						 area=area,
						 multiple_tables=False)
	clean_df = df[0].replace('\r',' ', regex=True)
	return(clean_df)


def main():
	args = parseargs()
	print(args)
	#exit()
	
	#clean_df = tabula_parse(args.pdf, args.area, args.pages)
	cleaned_dfs = [tabula_parse(args.pdf, area, page) for page, area in zip(args.pages, args.area)]
	print(cleaned_dfs)
	print("Done")

if __name__ == "__main__":
	main()