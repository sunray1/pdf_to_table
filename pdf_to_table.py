#!/usr/bin/env python

import tabula
import argparse
import os, sys
import pandas as pd
from datetime import datetime
import subprocess

def parseargs():
	parser = argparse.ArgumentParser(description="Parse a pdf table into a csv. Example: python pdf_to_table.py -i pdf-examples/text-based.pdf -a 109.01,60.644,751.164,293.545 -p 1 -a 109.754,303.219,753.396,533.888 -p 1 -c -l")
	parser.add_argument("-i", "--pdf", type=str, help="Path to the pdf")
	parser.add_argument("-a", "--area", type=str, action='append', required=True, help="Four-item list of top, left, bottom, and right of table location in a page. \
						Must match up to number of pages.\
						Example: '406, 24, 695, 589'")
	# python arg.py -a [406, 24, 695, 589] -a [406, 24, 695, 589]
	parser.add_argument("-p", "--pages", action='append', required=True, help="Pages of tables in file. Must match up to number of areas.\
						Example: '1'")
	# python arg.py -p 1 -p 2 -p 2 -p 3
	parser.add_argument("-c", "--concatenate", action='store_true', help="Add flag if all parsed tables should be concatenated together")
	parser.add_argument("-o", "--OCR", action='store_true', help="Add flag if pdf needs to be OCRed. This will redo any OCR in the input pdf.")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-s", "--stream", action='store_true', help="Add flag if table should be parsed via the Stream extraction method. \
					   Stream is used to parse tables that have whitespaces between cells to simulate a table structure.")
	group.add_argument("-l", "--lattice", action='store_true', help="Add flag if table should be parsed via the Lattice extraction method. \
					   Lattice is used used to parse tables that have demarcated lines between cells.")
	
	args = parser.parse_args()
	args.area = [list(map(float, item.split(','))) for item in args.area]
	#args.pages = [[item] for item in args.pages]
	return(args)

def ocrmypdf(args):
	base_name, extension = os.path.splitext(args.pdf)
	ocred_pdf = base_name + "_ocr.pdf"
	subprocess.run(["ocrmypdf", "-l", "eng", args.pdf, ocred_pdf, "--redo-ocr"], check=True)
	return ocred_pdf

def tabula_parse(args, area, page):
	if args.OCR:
		inputpdf = args.ocr_pdf
	else:
		inputpdf = args.pdf
	df = tabula.read_pdf(inputpdf,
						 lattice=args.lattice,
						 stream=args.stream,
						 pages=page,
						 area=area,
						 multiple_tables=False,
						 silent=True)
	clean_df = df[0].replace('\r',' ', regex=True)
	clean_df.columns = [col.replace('\r', ' ') for col in clean_df.columns]
	return(clean_df)

def saveoutputfile(args, dataframes):
	base_name, extension = os.path.splitext(args.pdf)
	output_file_names = []
	if args.concatenate:
		# Concatenate dataframes
		#right now this concatenates across headers, so make sure they are the same for each table
		###Add warning if headers are not the same
		print(f"CSV file: {base_name}_tables_parsed_concatenated.csv")
		concatenated_df = pd.concat(dataframes, ignore_index=True)
		concatenated_df.to_csv(base_name + "_tables_parsed_concatenated.csv", index=False)
		output_file_names.append(base_name + "_tables_parsed_concatenated.csv")
	else:
		print(f"CSV file(s):")
		# Save dataframes separately
		for idx, df in enumerate(dataframes, start=1):
			print(f"\t{base_name}_table_parsed_{idx}.csv")
			df.to_csv(f'{base_name}_table_parsed_{idx}.csv', index=False)
			output_file_names.append(f'{base_name}_table_parsed_{idx}.csv')
	save_parameters(args, output_file_names)

def save_parameters(args, outputs):
	base_name, extension = os.path.splitext(args.pdf)
	current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(f"Run Details: {base_name}_parameters.txt")
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
			f.write(f"{base_name}_parameters.txt")

def main():
	args = parseargs()
	current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print("\nScript Execution Summary")
	print(f"Date and Time: {current_datetime}")
	print("------------------------------\n")
	
	print(f"PDF input: {args.pdf}")
	print("Selected Areas:")
	for idx, area in enumerate(args.area, start=1):
		print(f"  Area {idx}: {area}")
	print(f"Pages: {', '.join(args.pages)}")
	print(f"Concatenate: {args.concatenate}")
	print(f"Perform OCR: {args.OCR}")
	print(f"Stream Extraction: {args.stream}")
	print(f"Lattice Extraction: {args.lattice}")
	
	if args.OCR:
		print("\nOCRing PDF")
		print("------------------------------\n")
		args.ocr_pdf = ocrmypdf(args)
		
	print("\nParsing Tables")
	print("------------------------------\n")	
	cleaned_dfs = [tabula_parse(args, area, page) for page, area in zip(args.pages, args.area)]
	
	print("\nSaving to CSV")	
	saveoutputfile(args, cleaned_dfs)
	print("------------------------------\n")
	
	print("Finished")

if __name__ == "__main__":
	main()