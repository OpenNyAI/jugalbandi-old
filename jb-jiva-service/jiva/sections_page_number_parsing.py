import fitz
import os
import re
import csv
import pandas as pd
import uuid
from fuzzywuzzy import fuzz

# Local base directory path with all acts
directory = "Full English Docs"
# Regex pattern to remove page numbers which occurs at the start of the page
page_number_pattern = r"^[\n\s]*\d+[\n\s]*(?!.)"


# Function to get the section names of the given Karnataka Act
def get_karnataka_act_section_names(file_path):
    # The most common regex pattern of Karnataka Acts which is used as a delimiter to split the sections' table of content text between the two patterns
    pattern = r"statement(?:s)?\s*of\s*object(?:s)?\s*and\s*reason(?:s)?"
    doc = fitz.open(file_path)
    content = "\n"
    for i in range(len(doc)):
        # flag to check whether to finish the section names retrieval process or not
        flag = False
        page = doc[i]
        text = page.get_text("text", textpage=None, sort=False)
        text = re.sub(page_number_pattern, '', text)
        # Doing major checks and operations on the first page as it contains the sections' table of content
        if i == 0:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            # Checking if the first page contains the pattern twice meaning, the sections' table of content is fully present in the first page only
            if len(matches) == 2:
                split_text = re.split(pattern, text, flags=re.IGNORECASE)
                del split_text[-1]
                del split_text[0]
                text = " ".join(split_text)
                # Making the flag True to finish the section names retrieval process
                flag = True
            else:
                split_text = re.split(pattern, text, flags=re.IGNORECASE)
                # Check if the text is split into two parts. If yes, then the second part is the section names' table of content
                if len(split_text) == 2:
                    # Delete the first part of the split_text as it is just the title of the act
                    del split_text[0]
                    text = " ".join(split_text)
                    content += text
                    # continue to the next page
                    continue

        if flag is False:
            split_text = re.split(pattern, text, flags=re.IGNORECASE)
            # Check if the text is split into two parts. If yes, then the first part is the section names' table of content
            if len(split_text) == 2:
                # Delete the last part of the split_text as it is the rest of the act information
                del split_text[-1]
                text = " ".join(split_text)
                # Making the flag True to finish the section names retrieval process
                flag = True

        # Adding the text to the section content
        content += text
        if flag is True:
            break

    return content


# Function to write the Karnataka Acts' section names to a csv file
def writing_karnataka_act_sections():
    karnataka_directory = "Karnataka Acts"
    # Getting the list of all the files in the directory
    dir_files = os.listdir(karnataka_directory)
    csvfile = open("karnataka_acts_titles_sections.csv", "w", newline="")
    writer = csv.DictWriter(csvfile, fieldnames=["Filename", "Section"])
    writer.writeheader()
    count = 0
    for i in range(len(dir_files)):
        file = dir_files[i]
        print(file)
        file_path = os.path.join(directory, file)
        # Calling the function to get the section names of the given Karnataka Act
        sections = get_karnataka_act_section_names(file_path)
        # Removing the unnecessary text from the extracted section names
        sections = sections.replace("*", "")
        sections = sections.replace("Sections:", "")
        sections = sections.replace("SCHEDULE", "")
        sections = sections.replace("STATEMENT OF OBJECTS", "")
        data = {"Filename": file, "Section": sections}
        # Writing the individual act data to the csv file with filename and section names
        writer.writerow(data)
        count += 1


# Function to get the section names of the given Central Act
def get_central_act_section_names(file_path):
    # The most common regex pattern of Central Acts which is used as a delimiter to split the sections' table of content text between the two patterns
    match_string = r"ARR\D{1,3}EMENT OF SECT\D{0,2}NS{0,1}"
    doc = fitz.open(file_path)
    # Extract the first page of the act
    first_page = doc[0].get_text("text", textpage=None, sort=False)
    # Check if the first page contains the match_string
    if re.search(match_string, first_page):
        # Split the first page into two parts using the match_string where the first part is the title of the act and the second part is the sections' table of content
        title, sections = re.split(match_string, first_page)
        # Remove unnecessary text from the title
        title = re.sub(r'(?:^|\s|\n)\d{1,2}(?=\s|\n|$)', '', title)
        title = title.replace("_", "").strip()
        # Remove unnecessary text from the sections data
        sections = sections.replace("SECTIONS", "").replace("_", "").strip()
        # Loop through the rest of the pages to get the remaining sections' table of content if any
        for i in range(1, len(doc)):
            page = doc[i]
            text = page.get_text("text", textpage=None, sort=False)
            text = re.sub(page_number_pattern, '', text)
            # Title is the delimiter to stop the loop. If title is present in the given text, then all the sections data have been fetched already
            if title in text:
                break
            sections += text
        # Replace any new line characters present in the title
        title = title.replace("\n", "")
    else:
        # Title might be extracted from the metadata of the pdf file. In most cases, the title is absent in the metadata
        title = doc.metadata['title']
        sections = ""
        # Add all the pages' text to the sections data as there is no heuristics to extract the section names in this case.
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text("text", textpage=None, sort=False)
            sections += text

    # Return title and sections data
    return title, sections


# Function to write Central Acts' section names to a csv file
def writing_central_act_sections():
    central_directory = "Central Acts"
    # Getting the list of all the files in the directory
    dir_files = os.listdir(central_directory)
    csvfile = open("central_acts_titles_sections.csv", "w", newline="")
    writer = csv.DictWriter(csvfile, fieldnames=["Filename", "Actname", "Section"])
    writer.writeheader()
    count = 0
    for i in range(len(dir_files)):
        file = dir_files[i]
        print(count, file)
        file_path = os.path.join(central_directory, file)
        # Calling the function to get the section names of the given Central Act
        title, sections = get_central_act_section_names(file_path)
        # Removing the unnecessary text from the extracted section names
        sections = sections.replace("THE SCHEDULE.", "")
        data = {"Filename": file, "Actname": title, "Section": sections}
        # Writing the individual act data to the csv file with filename, actname and section names
        writer.writerow(data)
        count += 1


# Function to get the starting page numbers for the given section names of the given act
def get_page_numbers(file_path, section_list):
    doc = fitz.open(file_path)
    # Initialize a dictionary with section names as keys and empty lists as values
    page_numbers_dict = {section: [] for section in section_list}
    # Loop through each page of the act
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text("text", textpage=None, sort=False)
        # Loop through each section name
        for section in section_list:
            pattern = r'\b' + re.escape(section) + r'\b'
            # Search for the exact match of the section name in the given page
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # If the exact match is found, then append the page number to the section's list
                page_numbers_dict[section].append(i+1)
            else:
                # Perform fuzzy matching if the exact match fails
                fuzzy_ratio = fuzz.token_set_ratio(section, text)
                if fuzzy_ratio >= 100:
                    # If the fuzzy matching ratio is greater than 100, then append the page number to the section's list
                    page_numbers_dict[section].append(i+1)

    # Get all the values of the dictionary which is essentially a list of lists
    page_numbers = list(page_numbers_dict.values())
    # Get the first section's page numbers. Check if the list contains only one element or not. If yes, then take the first element. Else, take the second element
    if len(page_numbers[0]) == 1:
        page_numbers[0] = page_numbers[0][0]
    else:
        page_numbers[0] = page_numbers[0][1]
    # Loop through the remaining section's page numbers
    for i in range(1, len(page_numbers)):
        prev_page_number = page_numbers[i-1]
        # If (the current section's page numbers list is empty) or (the first element of the list is less than the previous section's page number), then take the previous section's page number
        if (len(page_numbers[i]) == 1 and page_numbers[i][0] < prev_page_number) or len(page_numbers[i]) == 0:
            page_numbers[i] = prev_page_number
        else:
            flag = False
            # Loop through the current section's page numbers list
            for j in page_numbers[i]:
                # If the page number is greater than or equal to the previous section's page number, then take the page number
                if j >= prev_page_number:
                    flag = True
                    page_numbers[i] = int(j)
                    break
            # If there is no page number greater than or equal to the previous section's page number, then take the last element of the list
            if flag is False:
                page_numbers[i] = page_numbers[i][-1]

    # Return the page numbers list
    return page_numbers


# Function to write the section names and their starting page numbers to a csv file
def writing_page_numbers():
    # Read the csv file which contains the section names of the Acts
    csv_file = open("Karnataka Acts - Section names - titles_sections.csv", "r", newline="")
    reader = csv.DictReader(csv_file)
    # Pattern to take only the section name strings which starts with it (eg: 1-A. Section name, 26. Section name, 43A. Section name)
    pattern = r'(\n*\d+-?[A-Z]{0,3}\..*)'
    counter = 1
    # Loop through each row of the csv file
    for row in reader:
        file_name = row['Filename']
        print(counter, file_name)
        file_path = os.path.join(directory, file_name)
        section_data = row['Section']
        # Find all the section names which starts with the pattern
        matches = re.findall(pattern, section_data)
        section_list = [match.replace("\n", "") for match in matches]
        section_numbers = []
        section_names = []
        for section in section_list:
            section = section.split(".")
            section_numbers.append(section[0])
            section_names.append(" ".join(section[1:]).strip())
        # Calling the function to get the starting page numbers for the given section names of the given act
        page_numbers = get_page_numbers(file_path, section_list)

        new_file_name, _ = os.path.splitext(file_name)
        # Writing the section names and their starting page numbers to individual csv file for every act
        csv_file_name = new_file_name + ".csv"
        csv_path = os.path.join("Karnataka CSV files", csv_file_name)
        csvfile = open(csv_path, "w", newline="")
        writer = csv.DictWriter(csvfile, fieldnames=["Full section name", "Section number", "Section name", "Start page"])
        writer.writeheader()
        for i in range(len(section_list)):
            data = {"Full section name": section_list[i],
                    "Section number": section_numbers[i],
                    "Section name": section_names[i],
                    "Start page": page_numbers[i]}
            writer.writerow(data)
        counter += 1


# Function to combine and convert the individual csv files to an excel file
def writing_csv_files_to_excel():
    directory = "Karnataka CSV files"
    csv_files = os.listdir(directory)
    writer = pd.ExcelWriter('karnataka_output.xlsx', engine='xlsxwriter')

    # Loop through each CSV file and copy data to a new worksheet
    for _, csv_file in enumerate(csv_files):
        # Read the CSV file using pandas
        print(csv_file)
        full_path = os.path.join(directory, csv_file)
        df = pd.read_csv(full_path)

        file_name, _ = os.path.splitext(csv_file)
        file_name += ".pdf"

        # Write the dataframe to a new worksheet in the Excel file
        try:
            worksheet = writer.book.add_worksheet(file_name[:31])
            worksheet.write(0, 0, file_name)  # Write the title to the first cell
            worksheet.set_column(0, df.shape[1] - 1, 12)
            df.to_excel(writer, sheet_name=file_name[:31], startrow=1, header=True, index=False)
        except Exception:
            try:
                worksheet = writer.book.add_worksheet(file_name[10:41])
                worksheet.write(0, 0, file_name)  # Write the title to the first cell
                worksheet.set_column(0, df.shape[1] - 1, 12)
                df.to_excel(writer, sheet_name=file_name[10:41], startrow=1, header=True, index=False)
            except Exception:
                new_uuid = str(uuid.uuid4())
                worksheet = writer.book.add_worksheet(new_uuid[12:])
                worksheet.write(0, 0, file_name)  # Write the title to the first cell
                worksheet.set_column(0, df.shape[1] - 1, 12)
                df.to_excel(writer, sheet_name=new_uuid[12:], startrow=1, header=True, index=False)

    # Save the Excel file
    writer._save()
