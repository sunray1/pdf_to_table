# pdf_to_table

This repository contains code and data necessary for the development of a reusable, command-line python script to streamline the extraction and structuring of species checklists from inside PDF tables into tidy CSV files.

## Description

Species checklists are a crucial source of information for research and policy. Unfortunately, a substantial number of conventional species checklists are not conveniently available through distinct downloadable files; rather, they are often ensnared within tables embedded in PDF versions of published papers. The fact that these data are not open, findable, accessible, interoperable and reusable (FAIR) severely hampers fast and efficient information flow to policy and decision-making that are required to tackle the current biodiversity crisis. Here, I wrote a simple script designed to mobilize these species checklists into tidy, csv files for downstream use by researchers or data scientists and can be added into a larger pipeline.
 

## Getting Started

### Dependencies

* [tabula-py](https://github.com/chezou/tabula-py)
* [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF)

### Installing

To download the repository and script from GitHub, follow these steps:

1. **Clone the Repository:**
   Open your terminal and navigate to the directory where you want to download the repository. Then enter the following commands:
```
git clone https://github.com/sunray1/pdf_to_table.git
cd pdf_to_table
chmod +x pdf_to_table.py
```
2. **Download the Dependencies:**
	Download the dependencies from the necessary GitHub pages or using pip. A conda environment is available for use if preferred. Note: it is better install OCRmyPDF first and then tabula-py.
	
	**pip**

	```
	pip install ocrmypdf
	pip install tabula-py
	```
  
	**conda**
	```
	conda env create -f pdf_to_table.yml
	conda activate pdf_to_table
	```

### Executing program

The script can be executed via a standard python call with the appropriate parameters. Current parameters are detailed below.

It is **highly** recommended that parsed output tables be verified by humans. An output file with the command parameters will also be outputted in addition to the csv file(s).

```
$ python pdf_to_table.py -h

usage: pdf_to_table.py [-h] [-i PDF] -a AREA -p PAGES [-c] [-o] (-s | -l)

Parse a pdf table into a csv. Example: python pdf_to_table.py -i pdf-examples/text-based.pdf -a 109.01,60.644,751.164,293.545 -p 1 -a
109.754,303.219,753.396,533.888 -p 1 -c -l

options:
  -h, --help            show this help message and exit
  -i PDF, --pdf PDF     Path to the pdf
  -a AREA, --area AREA  Four-item list of top, left, bottom, and right of table location in a page. Must match up to number of pages.
                        Example: '406, 24, 695, 589'
  -p PAGES, --pages PAGES
                        Pages of tables in file. Must match up to number of areas. Example: '1'
  -c, --concatenate     Add flag if all parsed tables should be concatenated together
  -o, --OCR             Add flag if pdf needs to be OCRed. This will redo any OCR in the input pdf.
  -s, --stream          Add flag if table should be parsed via the Stream extraction method. Stream is used to parse tables that have
                        whitespaces between cells to simulate a table structure.
  -l, --lattice         Add flag if table should be parsed via the Lattice extraction method. Lattice is used used to parse tables that
                        have demarcated lines between cells.
```

#### Demarcating Table Areas

Each table on each page must be marked via point measurement coordinates and the page number. It is useful to use the Tabula app to grab table coordinates.

1. Download Tabula from http://tabula.technology/ if you haven't already.
2. Open Tabula and upload your PDF into the web page that appears.
3. Select your table area(s) as usual and proceed to the "Preview & Export Extracted Data" step.
4. Under Export Format, select "Script" instead of CSV, and then click "Export" to download the generated code. Save this file somewhere you can find it.
5. Open the script you downloaded in a code editor and copy and paste the area and page parameters into the command.

For example, a downloaded script may look like this:
```
java -jar tabula-java.jar  -a 109.01,60.644,751.164,293.545 -p 1 "$1" 
java -jar tabula-java.jar  -a 109.754,303.219,753.396,533.888 -p 1 "$1" 
java -jar tabula-java.jar  -a 85.943,61.388,687.916,293.545 -p 2 "$1" 
```

The area and pages can all be copied over into the command like this:
```
python tabula-test.py -i text-based.pdf -a 109.01,60.644,751.164,293.545 -p 1 -a 109.754,303.219,753.396,533.888 -p 1 -a 85.943,61.388,687.916,293.545 -p 2
```
#### Choosing Stream or Lattice Extraction

There are mainly two techniques used to detect tables: *Stream* and *Lattice*. Your choice will depend on how the table is printed in your pdf. You can toggle between the two in the Tabula app to see which is the best option for your use case.

**Stream** can be used to parse tables that have whitespaces between cells to simulate a table structure. 

**Lattice** can be used to parse tables that have demarcated lines between cells. It essentially works by looking at the shape of polygons and getting the text inside of the boxes.

#### OCRing a PDF

Depending on the type of PDF file, tables can be text or image-based. This can be discovered by highlighting the table in a PDF viewer and seeing if the text is highlighted. If so, it is text-based, if not, the table is image-based. Tables that are imaged-based must first be OCRed and the layer added onto to the PDF.

The OCRmyPDF library is used to OCR the PDF text and add its position within the PDF itself, since this is important for table extraction. Add the "-o" flag to OCR your PDF and save it as a new file. Note that this will overwrite any positional text saved in your original PDF.

You may choose the number of parallel cores to use when OCRing pages by using the -# CORES command. The default is 4 cores.

#### Table Concatenation
If the whole table is split across multiple pages or smaller tables within a page, the tables can be concatenated into one. Note that concatenation can be finicky, and works better when the parsed tables all have the same number of parsed columns (i.e. no completely empty columns with just blank space) with the same header names, since columns across tables are concatenated together according to given column headers. It is helpful to use the Tabula app to preview how the tables will be parsed.

## Help

If you have any questions, problems, or encounter issues, visit the [GitHub Issues](https://github.com/sunray1/pdf_to_table/issues) page of this repository and create a new issue.

## Authors

Chandra Earl  

## Acknowledgments and Helpful Links

* [A checklist recipe: making species data open and FAIR](https://doi.org/10.1093/database/baaa084)
* [tabula-java](https://github.com/tabulapdf/tabula-java)
* [PDFToExcel](https://tomassetti.me/how-to-convert-a-pdf-to-excel/)