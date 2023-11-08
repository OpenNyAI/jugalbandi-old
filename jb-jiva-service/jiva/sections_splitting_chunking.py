import os
import re
import fitz
from oauth2client.service_account import ServiceAccountCredentials
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import gspread
import regex
import json


# Regex pattern to remove page numbers from parsed PDF text
page_number_pattern = r'^[\n\s]*\d+[\n\s]*(?!.)'
# Regex pattern to remove extra spaces from parsed PDF text
spaces_regex = r"(?<!\n\s)\n(?!\n| \n)"


def get_data_from_google_sheets(required_sheet_name: str):
    credentials_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet_url = os.environ["GOOGLE_SHEET_URL"]
    sheet = client.open_by_url(sheet_url)

    sheet_names = sheet.worksheets()
    for worksheet in sheet_names:
        if worksheet.title == required_sheet_name:
            data = worksheet.get_all_values()
            keys = data[0]
            values = data[1:]
            section_names_data = [dict(zip(keys, row)) for row in values]
            return section_names_data


def get_data_from_sheet_data(filename: str, section_names_data: list):
    pattern = r'(\n*\d+-?\[?[A-Z]{0,3}\..*)'
    for section in section_names_data:
        if section['Filename'] == filename:
            matches = re.findall(pattern, section['Section'])
            section_list = [match.replace("\n", "") for match in matches]
            return section_list


def fuzzy_substring_search(minor: str, major: str, errs: int = 10):
    errs_ = 0
    s = regex.search(f"({minor}){{e<={errs_}}}", major)
    while s is None and errs_ <= errs:
        errs_ += 1
        s = regex.search(f"({minor}){{e<={errs_}}}", major)
    return s


def find_string_with_fuzzy(A_string: str, B_string: str,
                           large_string: str, is_first_section: bool, is_last_section: bool):
    match_a = re.search(A_string, large_string, re.IGNORECASE)
    if match_a is None:
        match_a = fuzzy_substring_search(A_string, large_string)
    if is_last_section is False:
        match_b = re.search(B_string, large_string, re.IGNORECASE)
        if match_b is None:
            match_b = fuzzy_substring_search(B_string, large_string)
    else:
        match_b = re.search(B_string, large_string)
        if match_b is None:
            return large_string[match_a.start():]
        else:
            return [large_string[match_a.start():match_b.start()], large_string[match_b.start():]]

    if is_first_section:
        return [large_string[0: match_a.start()], large_string[match_a.start():match_b.start()]]

    result = large_string[match_a.start():match_b.start()]
    return result


def get_karnataka_section_splits(root_dir: str, section_names_data: list):
    section_dict = {}
    file_names = os.listdir(root_dir)
    pattern = r'statement(?:s)?\s*of\s*object(?:s)?\s*and\s*reason(?:s)?'
    for filename in file_names:
        if filename not in ["THE KARNATAKA STAMP ACT, 1957-ENG.pdf", "21 of 1964 (E).pdf", "32 of 1963 (E).pdf",
                            "THE KARNATAKA SCHEDULED CASTES SUB-ALLOCATION AND TRIBAL...ETC 2013-ENG.pdf", "THE KARNATAKA SALES TAX ACT, 1957-ENG.pdf", "11of1959(E).pdf",
                            "A1860-45 (E).pdf", "THE KARNATAKA LEGISLATURE SALARIES, PENSIONS AND ALLOWANCES ACT, 1956 -ENG.pdf",
                            "THE KARNATAKA HOUSING BOARD ACT, 1962-ENG.pdf", "THE KARNATAKA LAND REVENUE ACT, 1964-ENG.pdf", "A1908-05 (E).pdf", "27 of 1966 (E) emblem.pdf",
                            "19 of 1979 Rules (E) Debt.pdf", "17 of 2019 Rules (E).pdf", "23 of 2013 Rules (E).pdf", "A1974-02 (E).pdf", "COI (E).pdf"]:
            print("\nFilename:", filename)
            doc = fitz.open(os.path.join(root_dir, filename))
            content = "\n"
            content_list = []
            for i in range(len(doc)):
                flag = False
                page = doc[i]
                text = page.get_text("text", textpage=None, sort=False)
                text = re.sub(page_number_pattern, '', text)
                if i == 0:
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    if len(matches) == 2:
                        split_text = re.split(pattern, text, flags=re.IGNORECASE)
                        new_text = split_text.pop(-1)
                        text = " ".join(split_text)
                        flag = True

                if flag is False:
                    split_text = re.split(pattern, text, flags=re.IGNORECASE)
                    if len(split_text) == 2:
                        new_text = split_text.pop(-1)
                        text = " ".join(split_text)
                        flag = True

                content += text
                if flag is True:
                    content_list.append(content)
                    content = new_text

            content_list.append(content)
            # print(repr(content)[:200], end="\n")
            if len(content_list) > 1:
                text = content_list.pop(-1)
                text = re.sub(spaces_regex, '', text)
                sections_list = [" ".join(content_list)]
            else:
                text = re.sub(spaces_regex, '', content_list[0])
                sections_list = []

            data = get_data_from_sheet_data(filename, section_names_data)
            for i in range(len(data)):
                exception_encounter = False
                if i == 0:
                    is_first_section = True
                else:
                    is_first_section = False

                A_section_name = data[i].split(" ")
                A_section_string = r"\s*".join(A_section_name)
                if i == len(data)-1:
                    is_last_section = True
                    B_section_string = "SCHEDULE"
                else:
                    is_last_section = False
                    B_section_name = data[i+1].split(" ")
                    B_section_string = r"\s*".join(B_section_name)
                # print(A_section_string,"----", B_section_string)
                try:
                    extracted_text = find_string_with_fuzzy(A_section_string.strip(" "),
                                                            B_section_string.strip(" "),
                                                            text, is_first_section, is_last_section)
                    if isinstance(extracted_text, list):
                        sections_list += extracted_text
                    else:
                        sections_list.append(extracted_text)
                except Exception:
                    exception_encounter = True
                    print(filename, "is problematic and not fully done")
                    print("Remaining Uncompleted Sections:", len(data)-i)
                    break

            print("Total Completed Sections:", len(sections_list))
            if exception_encounter is False:
                section_dict[filename] = sections_list

    with open("karnataka_section_splits.json", 'w') as json_file:
        json.dump(section_dict, json_file)


def get_central_section_splits(root_dir: str, section_names_data: list):
    section_dict = {}
    pattern = r"ARR\D{1,3}EMENT OF SECT\D{0,2}NS{0,1}"
    file_names = os.listdir(root_dir)
    for filename in file_names:
        print("\nFilename:", filename)
        data_list = []
        doc = fitz.open(os.path.join(root_dir, filename))
        first_page = doc[0].get_text("text", textpage=None, sort=False)
        if re.search(pattern, first_page):
            title, sections = re.split(pattern, first_page)
            title = re.sub(r'(?:^|\s|\n)\d{1,2}(?=\s|\n|$)', '', title)
            title = title.replace("_", "").strip()
            title = title.replace("\n", "")
            sections = title + sections
            sections = sections.replace("SECTIONS", "").replace("_", "").strip()
            for i in range(1, len(doc)):
                page = doc[i]
                text = page.get_text("text", textpage=None, sort=False)
                text = re.sub(page_number_pattern, '', text)
                if title in text:
                    data_list.append(sections)
                    sections = ""
                sections += text
            data_list.append(sections)
        else:
            print("CANNOT FIND TITLES INSIDE THIS FILE: ", filename)
            continue

        if len(data_list) > 1:
            text = data_list.pop(-1)
            sections_list = [" ".join(data_list)]
        else:
            text = data_list[0]
            sections_list = []

        text = re.sub(spaces_regex, '', text)
        data = get_data_from_sheet_data(filename, section_names_data)
        for i in range(len(data)):
            if i == 0:
                is_first_section = True
            else:
                is_first_section = False

            A_section_name = data[i].split()
            A_section_string = r"\s*".join(A_section_name)
            if i == len(data)-1:
                is_last_section = True
                B_section_string = "THE SCHEDULE"
            else:
                is_last_section = False
                B_section_name = data[i+1].split()
                B_section_string = r"\s*".join(B_section_name)
            # print(A_section_string,"----", second_section_string)
            try:
                extracted_text = find_string_with_fuzzy(A_section_string.strip(" "),
                                                        B_section_string.strip(" "),
                                                        text, is_first_section, is_last_section)
                if isinstance(extracted_text, list):
                    sections_list += extracted_text
                else:
                    sections_list.append(extracted_text)
            except Exception:
                print(filename, "is problematic and not fully done")
                print("Remaining Uncompleted Sections:", len(data)-i)
                break

        print("Total Completed Sections:", len(sections_list))
        section_dict[filename] = sections_list

    with open("central_section_splits.json", 'w') as json_file:
        json.dump(section_dict, json_file)


def sections_chunking():
    with open("karnataka_section_splits.json", 'r') as file:
        json_data = file.read()

    sections_dict = json.loads(json_data)
    # Regex pattern to find section numbers paragraph from parsed PDF text
    digit_pattern = r'^(\n*\d+-?\[?[A-Z]{0,3}\..*)'
    # Regex pattern to find section numbers from parsed PDF text
    section_number_pattern = r'^(\n*\d+-?\[?[A-Z]{0,3}\.)'
    precursor_sentence_one = "The following contents are part of the {}"
    precursor_sentence_two = "The following sections are part of the {}"
    precursor_sentence_three = "The following section is part of the {}"
    precursor_sentence_four = "The following contents are continuation of section {} of the {}"

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=0,
        separators=["\n \n", "\n\n", "\n", ".", " "]
    )

    meta_data_list = get_data_from_google_sheets("All Acts")
    result_dict = {}
    for key, value in sections_dict.items():
        print("Filename:", key)
        for meta_data in meta_data_list:
            if meta_data['File Name'] == key:
                title = meta_data['Doc title']

        section_doc = value
        new_chunks = [section_doc[0]]
        i = 1
        while i < len(section_doc):
            section = section_doc[i]
            matches = re.findall(digit_pattern, section)
            if len(matches) == 1:
                if len(section) < 4000:
                    flag = False
                    section = precursor_sentence_two.format(title) + "\n\n\nSection " + section
                    if i == len(section_doc)-1:
                        new_chunks.append(section)
                        break

                    new_section = section
                    j = 1
                    while True:
                        if i+j >= len(section_doc):
                            flag = True
                            break
                        new_section += "\n\n\nSection " + section_doc[i+j]
                        if len(new_section) > 4000:
                            new_section = new_section.replace("\n\n\nSection " + section_doc[i+j], "")
                            flag = True
                            j -= 1
                            break
                        j += 1
                    if flag is True:
                        new_chunks.append(new_section)
                        # print(i, "---------", repr(new_section), "---------", len(new_section))
                        i += j
                    else:
                        new_chunks.append(section)
                        # print(i, "---------", repr(section), "---------", len(section))
                else:
                    section_number_match = re.search(section_number_pattern, section)
                    section_number = section[section_number_match.start():section_number_match.end()]
                    section_splits = text_splitter.split_text(section)
                    sections_list = []
                    for k in range(len(section_splits)):
                        if k == 0:
                            section_split = precursor_sentence_three.format(title) + "\n\n\nSection " + section_splits[k]
                        else:
                            section_split = precursor_sentence_four.format(section_number, title) + "\n\n\n" + section_splits[k]
                        sections_list.append(section_split)
                    new_chunks += sections_list
            else:
                if len(section) > 4000:
                    section_splits = text_splitter.split_text(section)
                    section_splits = [precursor_sentence_one.format(title) + "\n\n\n" + section_split for section_split in section_splits]
                    new_chunks += section_splits
                else:
                    section = precursor_sentence_one.format(title) + "\n\n\n" + section
                    new_chunks.append(section)
            i += 1
        result_dict[key] = new_chunks

    with open("central_docs_chunks.json", 'w') as json_file:
        json.dump(result_dict, json_file)


if __name__ == "__main__":
    load_dotenv()
    root_dir = os.environ["ROOT_DIR"]
    section_names_data = get_data_from_google_sheets("Sheet Name")
    # get_karnataka_section_splits(root_dir, section_names_data)
    # get_central_section_splits(root_dir, section_names_data)
    # sections_chunking()
