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
	parser.add_argument("-o", "--output", type=str, default=".", help="Path for output processed files")
	parser.add_argument("-a", "--area", type=str, action='append', help="Four-item list of top, left, bottom, and right of table location in a page. \
						Must match up to number of pages.\
						Example: '406, 24, 695, 589'")
	# python arg.py -a [406, 24, 695, 589] -a [406, 24, 695, 589]
	parser.add_argument("-p", "--pages", action='append', help="Pages of tables in file. Must match up to number of areas.\
						Example: '1'")
	# python arg.py -p 1 -p 2 -p 2 -p 3
	parser.add_argument("-c", "--concatenate", action='store_true', help="Add flag if all parsed tables should be concatenated together")
	parser.add_argument("-ocr", "--OCR", action='store_true', help="Add flag if pdf needs to be OCRed. This will redo any OCR in the input pdf.")
	parser.add_argument("-#", "--cores", default="4", help="Number of cores used in parallel when concurrently OCRing pages. Default is 4.")
	parser.add_argument("-f", "--forceocr", action='store_true', help="Add flag if the OCR needs to be forced")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-s", "--stream", action='store_true', help="Add flag if table should be parsed via the Stream extraction method. \
					   Stream is used to parse tables that have whitespaces between cells to simulate a table structure.")
	group.add_argument("-l", "--lattice", action='store_true', help="Add flag if table should be parsed via the Lattice extraction method. \
					   Lattice is used used to parse tables that have demarcated lines between cells.")
	
	args = parser.parse_args()
	if args.area is not None:
		args.area = [list(map(float, item.split(','))) for item in args.area]
	
	if args.area and not args.pages:
		parser.error("If using -a AREA, you must provide corresponding -p PAGES arguments")
	elif args.pages and not args.area:
		parser.error("If using -p PAGES, you must provide corresponding -a AREA arguments")
	
	if not args.OCR and not args.area:
		parser.error("No option for OCRing or parsing tables has been inputted. If OCRing, please add -o OCR flag. \
					 If parsing, please add -a AREA, -p PAGES and (-s STREAM | -l LATTICE) flags.")
		
	if args.area and args.pages and len(args.area) != len(args.pages):
		parser.error("Number of -a AREA arguments must match the number of -p PAGES arguments")
	
	if args.area and args.pages and not (args.stream or args.lattice):
		parser.error("-a AREA and -p PAGES flags detected, please select parsing method -s STREAM or -l LATTICE")

	if args.output:
		args.output = os.path.normpath(args.output)

	return(args)

def create_output_folder(args):
	if not os.path.exists(args.output):
			os.makedirs(args.output)
			
def ocrmypdf(args, output_file_names):
	base_name, extension = os.path.splitext(args.pdf)
	output_path = args.output if args.output else os.path.dirname(args.pdf)
	ocred_pdf = os.path.join(output_path, f"{os.path.basename(base_name)}_ocr.pdf")
	
	output_file_names.append(ocred_pdf)
	if args.forceocr:
		ocr_type = "--force-ocr"
	else:
		ocr_type = "--redo-ocr"
	subprocess.run(["ocrmypdf", "-l", "eng", args.pdf, ocred_pdf, ocr_type, "-j", args.cores], check=True)
	return ocred_pdf, output_file_names

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

def saveoutputfile(args, dataframes, output_file_names):
	base_name, extension = os.path.splitext(args.pdf)
	output_path = args.output if args.output else os.path.dirname(args.pdf)

	if args.concatenate:
		# Concatenate dataframes
		#right now this concatenates across headers, so make sure they are the same for each table
		###Add warning if headers are not the same
		concatenated_df_file = os.path.join(output_path, f"{os.path.basename(base_name)}_tables_parsed_concatenated.csv")
		print(f"CSV file: {concatenated_df_file}")
		concatenated_df = pd.concat(dataframes, ignore_index=True)
		concatenated_df.to_csv(concatenated_df_file, index=False)
		output_file_names.append(concatenated_df_file)
	else:
		print(f"CSV file(s):")
		# Save dataframes separately
		for idx, df in enumerate(dataframes, start=1):
			individual_df = os.path.join(output_path, f"{os.path.basename(base_name)}_tables_parsed_{idx}.csv")
			print(f"\t{individual_df}")
			df.to_csv(individual_df, index=False)
			output_file_names.append(individual_df)
	return output_file_names

def save_parameters(args, outputs):
	base_name, extension = os.path.splitext(args.pdf)
	output_path = args.output if args.output else os.path.dirname(args.pdf)
	parameter_file = os.path.join(output_path, f"{os.path.basename(base_name)}_parameters.txt")	
	
	current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(f"\nRun Details: {parameter_file}")
	with open(parameter_file, 'w') as f:
		f.write("Script Execution Summary\n")
		f.write(f"Date and Time: {current_datetime}\n")
		f.write("------------------------------\n")
		
		f.write("Command Entered:\n")
		f.write(f"{' '.join(sys.argv)}\n\n")
		
		f.write("Script Arguments:\n")
		for arg in vars(args):
			if arg != "ocr_pdf":
				f.write(f"{arg}: {getattr(args, arg)}\n")
		f.write("\n")
		
		f.write("Outputs:\n")
		for output_name in outputs:
			f.write(f"{output_name}\n")
		f.write(f"{parameter_file}")

def main():
	args = parseargs()
	output_file_names = []
	create_output_folder(args)
	current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print("\nScript Execution Summary")
	print(f"Date and Time: {current_datetime}")
	print("------------------------------\n")
	print(f"PDF input: {args.pdf}")

	if args.OCR:
		print(f"Perform OCR: {args.OCR}")
		print(f"Number of Cores: {args.cores}")

	if args.area:
		print("Perform Table Parsing: TRUE")
		print("Selected Areas:")
		for idx, area in enumerate(args.area, start=1):
			print(f"  Area {idx}: {area}")
		print(f"Pages: {', '.join(args.pages)}")
		print(f"Concatenate: {args.concatenate}")	
		print(f"Stream Extraction: {args.stream}")
		print(f"Lattice Extraction: {args.lattice}")
	else:
		print("Perform Table Parsing: FALSE")
	
	if args.OCR:
		print("\nOCRing PDF")
		print("------------------------------\n")
		args.ocr_pdf, output_file_names = ocrmypdf(args, output_file_names)
		
	if args.area:	
		print("\nParsing Tables")
		print("------------------------------\n")	
		cleaned_dfs = [tabula_parse(args, area, page) for page, area in zip(args.pages, args.area)]
		
		print("\nSaving to CSV")	
		output_file_names = saveoutputfile(args, cleaned_dfs, output_file_names)
		print("------------------------------\n")
	
	
	save_parameters(args, output_file_names)
	print("Finished")

if __name__ == "__main__":
	main()