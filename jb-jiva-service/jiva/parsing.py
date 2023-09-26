import fitz
import os
import re
import csv
import pandas as pd
import uuid
from fuzzywuzzy import fuzz

# Base directory with all karnataka acts
directory = "Full English Docs"


def get_karnataka_act_sections(file_path):
    end_string = "and reason"
    pattern = re.compile(re.escape(end_string), re.IGNORECASE)
    doc = fitz.open(file_path)
    content = "\n"
    for i in range(len(doc)):
        flag = False
        page = doc[i]
        text = page.get_text("text", textpage=None, sort=False)
        # text = re.sub(r'\n\d+\s*\n', '\n', text)
        if i == 0:
            occurences = text.lower().count(end_string)
            if occurences == 2:
                text = pattern.split(text)[1]
                flag = True
        else:
            if end_string in text.lower():
                text = pattern.split(text)[0]
                text = pattern.sub(text, "")
                flag = True

        content += text
        if flag is True:
            break

    return content


def writing_karnataka_act_sections():
    dir_files = os.listdir(directory)
    csvfile = open("karnataka_acts_titles_sections.csv", "w", newline="")
    writer = csv.DictWriter(csvfile, fieldnames=["Filename", "Section"])
    writer.writeheader()
    count = 0
    for i in range(len(dir_files)):
        file = dir_files[i]
        print(file)
        file_path = os.path.join(directory, file)
        sections = get_karnataka_act_sections(file_path)
        sections = sections.replace("*", "")
        sections = sections.replace("SCHEDULE", "")
        sections = sections.replace("STATEMENT OF OBJECTS", "")
        data = {"Filename": file, "Section": sections}
        writer.writerow(data)
        count += 1


# TODO: Remove page numbers and make it generic
def get_central_act_sections(file_path):
    match_string = r"ARR\D{1,2}EMENT OF SECT\D{0,2}NS"
    doc = fitz.open(file_path)
    first_page = doc[0].get_text("text", textpage=None, sort=False)
    if re.match(match_string, first_page):
        title, sections = first_page.split(match_string)
        title = re.sub(r'(?:^|\s|\n)\d{1,2}(?=\s|\n|$)', '', title)
        title = title.replace("_", "").strip()
        sections = sections.replace("SECTIONS", "").replace("_", "").strip()
        for i in range(1, len(doc)):
            page = doc[i]
            text = page.get_text("text", textpage=None, sort=False)
            if title in text:
                break
            sections += text
        title = title.replace("\n", "")
    else:
        title = doc.metadata['title']
        sections = ""
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text("text", textpage=None, sort=False)
            sections += text

    return title, sections


def writing_central_act_sections():
    central_directory = "Central Acts"
    dir_files = os.listdir(central_directory)
    csvfile = open("central_acts_titles_sections.csv", "w", newline="")
    writer = csv.DictWriter(csvfile, fieldnames=["Filename", "Actname", "Section"])
    writer.writeheader()
    count = 0
    for i in range(len(dir_files)):
        file = dir_files[i]
        print(count, file)
        file_path = os.path.join(central_directory, file)
        title, sections = get_central_act_sections(file_path)
        sections = sections.replace("THE SCHEDULE.", "")
        data = {"Filename": file, "Actname": title, "Section": sections}
        writer.writerow(data)
        count += 1


def get_page_numbers(file_path, section_list):
    doc = fitz.open(file_path)
    page_numbers_dict = {section: [] for section in section_list}
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text("text", textpage=None, sort=False)
        for section in section_list:
            pattern = r'\b' + re.escape(section) + r'\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                page_numbers_dict[section].append(i+1)
            else:
                # Perform fuzzy matching if the exact match fails
                fuzzy_ratio = fuzz.token_set_ratio(section, text)
                if fuzzy_ratio >= 100:
                    page_numbers_dict[section].append(i+1)

    page_numbers = list(page_numbers_dict.values())
    if len(page_numbers[0]) == 1:
        page_numbers[0] = page_numbers[0][0]
    else:
        page_numbers[0] = page_numbers[0][1]
    for i in range(1, len(page_numbers)):
        prev_page_number = page_numbers[i-1]
        if (len(page_numbers[i]) == 1 and page_numbers[i][0] < prev_page_number) or len(page_numbers[i]) == 0:
            page_numbers[i] = prev_page_number
        else:
            flag = False
            for j in page_numbers[i]:
                if j >= prev_page_number:
                    flag = True
                    page_numbers[i] = int(j)
                    break
            if flag is False:
                page_numbers[i] = page_numbers[i][-1]

    return page_numbers


def writing_page_numbers():
    # Checking with the extracted section names csv
    csv_file = open("Karnataka Acts - Section names - titles_sections.csv", "r", newline="")
    reader = csv.DictReader(csv_file)
    pattern = r'(\n*\d+[A-Z]{0,3}\..*)'
    counter = 1
    for row in reader:
        file_name = row['Filename']
        print(counter, file_name)
        file_path = os.path.join(directory, file_name)
        section_data = row['Section']
        matches = re.findall(pattern, section_data)
        section_list = [match.replace("\n", "") for match in matches]
        section_numbers = []
        section_names = []
        for section in section_list:
            section = section.split(".")
            section_numbers.append(section[0])
            section_names.append(" ".join(section[1:]).strip())
        page_numbers = get_page_numbers(file_path, section_list)

        new_file_name, _ = os.path.splitext(file_name)
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


def writing_csv_files_to_excel():
    directory = "Karnataka CSV files"
    csv_files = os.listdir(directory)
    writer = pd.ExcelWriter('karnataka_output.xlsx', engine='xlsxwriter')

    # Loop through each CSV file and copy data to a new worksheet
    for index, csv_file in enumerate(csv_files):
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
