#!/usr/bin/env python

import tabula
import argparse
import os, sys
import pandas as pd
from datetime import datetime

def parseargs():
	parser = argparse.ArgumentParser(description="Parse a pdf table into a csv. Example: python python pdf_to_table.py -i pdf-examples/text-based.pdf -a 109.01,60.644,751.164,293.545 -p 1 -a 109.754,303.219,753.396,533.888 -p 1 -c")
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


def tabula_parse(inputfile, area, page):
	df = tabula.read_pdf(inputfile,
						 lattice=True,
						 pages=page,
						 area=area,
						 multiple_tables=False)
	clean_df = df[0].replace('\r',' ', regex=True)
	clean_df.columns = [col.replace('\r', ' ') for col in clean_df.columns]
	return(clean_df)

def saveoutputfile(args, dataframes):
	base_name, extension = os.path.splitext(args.pdf)
	output_file_names = []
	if args.concatenate:
		# Concatenate dataframes
		#right now this concatenates across headers, so make sure they are the same for each table
		concatenated_df = pd.concat(dataframes, ignore_index=True)
		concatenated_df.to_csv(base_name + "_tables_parsed_concatenated.csv", index=False)
		output_file_names.append(base_name + "_tables_parsed_concatenated.csv")
	else:
		# Save dataframes separately
		for idx, df in enumerate(dataframes, start=1):
			df.to_csv(f'{base_name}_table_parsed_{idx}.csv', index=False)
			output_file_names.append(f'{base_name}_table_parsed_{idx}.csv')
	save_parameters(args, output_file_names)

def save_parameters(args, outputs):
	base_name, extension = os.path.splitext(args.pdf)
	current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	with open(base_name + "_parameters.txt", 'w') as f:
		f.write("Script Execution Summary\n")
		f.write(f"Date and Time: {current_datetime}\n")
		f.write("------------------------------\n")
		
		f.write("Command Entered:\n")
		f.write(f"{' '.join(sys.argv)}\n\n")
		
		f.write("Script Arguments:\n")
		for arg in vars(args):
			f.write(f"{arg}: {getattr(args, arg)}\n")
		f.write("\n")
		
		f.write("Outputs:\n")
		for output_name in outputs:
			f.write(f"{output_name}\n")

def main():
	args = parseargs()
	print(args)
	cleaned_dfs = [tabula_parse(args.pdf, area, page) for page, area in zip(args.pages, args.area)]
	print(cleaned_dfs)
	saveoutputfile(args, cleaned_dfs)
	
	print("Saved File; Done")

if __name__ == "__main__":
	main()