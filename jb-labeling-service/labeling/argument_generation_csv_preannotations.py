import ast
import sys
import pandas as pd
import math
import csv
import os
from pathlib import Path
from tqdm import tqdm
import re
from .argument_generation import generate_issues, generate_arguments
# import asyncio
from .db import LabelingRepository
from dotenv import load_dotenv
load_dotenv()
tqdm.pandas()
csv.field_size_limit(sys.maxsize)


def generate_issues_if_none(row, model: str) -> str:
    if row.get('generated_issues_gpt4') and not pd.isna(row.get('generated_issues_gpt4')):
        generated_issues = row['generated_issues_gpt4']
    else:
        facts_to_generate_issues = row['facts_of_case']
        # facts_chunks = text_chunking_based_on_sentence_boundaries(facts, max_chunk_tokens=8192)
        # facts_to_generate_issues = facts_chunks[0]  # use only the first chunk
        generated_issues = generate_issues(facts_to_generate_issues, model=model)
    return generated_issues


def extract_petitioners_respondent_names_from_NER_results(legal_nlp_result: str) -> dict:
    legal_nlp_dict = ast.literal_eval(legal_nlp_result)
    petitioner_names = []
    respondent_names = []
    for sent in legal_nlp_dict['annotations']:
        if sent['labels'][0] == 'PREAMBLE':
            if sent.get('entities') and len(sent['entities']) > 0:
                for ent in sent['entities']:
                    if ent['labels'][0] == 'PETITIONER':
                        petitioner_names.append(ent['text'])
                    elif ent['labels'][0] == 'RESPONDENT':
                        respondent_names.append(ent['text'])
    return {'petitioner_names': petitioner_names, 'respondent_names': respondent_names}


def extract_petitioners_respondent_names_from_title(case_title: str) -> dict:
    case_title = re.sub(r' on .*$', '', case_title)
    case_title = re.sub(r'\.\.\.', '', case_title)
    parties = case_title.split(' vs ', maxsplit=1)
    return {'petitioner_names': [parties[0].strip()], 'respondent_names': [parties[1].strip()]}


def extract_petitioners_respondent_names(row: pd.Series) -> list:
    party_dict = extract_petitioners_respondent_names_from_NER_results(row['legal_nlp_results'])
    if len(party_dict['petitioner_names']) == 0 or len(party_dict['respondent_names']) == 0:
        party_dict = extract_petitioners_respondent_names_from_title(row['Titles'])
    return [', '.join(party_dict['petitioner_names']), ', '.join(party_dict['respondent_names'])]


def generate_arguments_if_none(row) -> list[str]:
    # sample_data.to_csv(os.path.join(Path(__file__).parents[3], "data/sample_argument_generation_105_24july.csv"),index=False)
    if row.get('generated_arguments_gpt4') and not pd.isna(row.get('generated_arguments_gpt4')):
        generated_arguments_party1 = row['generated_arguments_party1_gpt4']
        generated_arguments_party2 = row['generated_arguments_party2_gpt4']
    else:
        statutes_list = row['statutes_of_case'].replace('&&&', 'of').split('\n')
        if row.get('generated_issues_gpt4') and not pd.isna(row.get('generated_issues_gpt4')) and len(statutes_list) > 0:
            issues = row['generated_issues_gpt4']

            generated_arguments_party1 = generate_arguments(court_name=row['Court_Name'],
                                                            facts=row['facts_of_case'],
                                                            statutes_list=statutes_list,
                                                            issues=issues,
                                                            petitioner_name=row['petitioners'],
                                                            respondent_name=row['respondents'],
                                                            generate_arguments_for='petitioners')
            generated_arguments_party2 = generate_arguments(court_name=row['Court_Name'],
                                                            facts=row['facts_of_case'],
                                                            statutes_list=statutes_list, issues=issues,
                                                            petitioner_name=row['petitioners'],
                                                            respondent_name=row['respondents'],
                                                            generate_arguments_for='respondents',
                                                            other_party_arguments=generated_arguments_party1)

        else:
            generated_arguments_party1 = None
            generated_arguments_party2 = None

    return [generated_arguments_party1, generated_arguments_party2]


def generate_sample():
    file_path = os.path.join(Path(__file__).parents[3], "data/Judgement_sample_processed_FINAL.csv")
    data = pd.read_csv(file_path)

    sample_percentage = 0.1
    sample_data = data.groupby(['Case_Type', 'Court_Type']).apply(lambda x: x.sample(n=math.ceil(sample_percentage * x.shape[0]), random_state=0)).reset_index(drop=True)
    sample_data.to_csv(os.path.join(Path(__file__).parents[3], "data/sample_105_judgments.csv"), index=False)


# TODO: get list of case_id & is_completed and check for updation during every new data import
async def write_csv_file_into_db(file_path):
    pattern = r"/(\d+)/?$"
    labeling_repository = LabelingRepository()

    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        headers = next(csvreader)  # Read the first row as headers
        print("Headers:", headers)
        row_list = list(csv.reader(csvfile))

        for i in range(0, len(row_list)):
            row = row_list[i]
            case_name = row[0]
            court_name = row[1]
            doc_url = row[4]
            match = re.search(pattern, doc_url)
            case_id = match.group(1)
            raw_text = row[5]
            doc_size = int(row[6])
            case_type = row[7]
            court_type = row[8]
            facts = row[11]
            issues = [row[12]]
            sections = row[13]
            precedents = row[14]
            is_precedent = True
            generated_issues = row[15]
            petitioner_arguments = []
            respondent_arguments = []
            petitioner_name = row[16]
            respondent_name = row[17]
            generated_petitioner_arguments = row[18]
            generated_respondent_arguments = row[19]
            new_sections = sections.split("\n")
            sections = []
            for section in new_sections:
                section_data = section.split(" &&& ")
                sections.append({
                    "section_number": section_data[0],
                    "act_title": section_data[1],
                    "reason": ""
                })
            if precedents != "":
                new_precedents = precedents.split("\n")
                precedents = []
                for precedent in new_precedents:
                    precedents.append({
                        "precedent_name": precedent,
                        "precedent_url": "",
                        "paragraphs": []
                    })
            else:
                is_precedent = False

            print("\nROW NUMBER:", i+1)
            print("DONE EXTRACTING INFORMATION: ", case_name)
            await labeling_repository.insert_into_tables(case_id=case_id,
                                                         case_name=case_name,
                                                         case_type=case_type,
                                                         court_name=court_name,
                                                         court_type=court_type,
                                                         doc_url=doc_url,
                                                         raw_text=raw_text,
                                                         doc_size=doc_size,
                                                         facts=facts,
                                                         issues=issues,
                                                         generated_issues=generated_issues,
                                                         petitioner_arguments=petitioner_arguments,
                                                         respondent_arguments=respondent_arguments,
                                                         generated_petitioner_arguments=generated_petitioner_arguments,
                                                         generated_respondent_arguments=generated_respondent_arguments,
                                                         sections=sections,
                                                         precedents=precedents,
                                                         is_precedent=is_precedent,
                                                         petitioner_name=petitioner_name,
                                                         respondent_name=respondent_name)


async def calculate_change_percentage(text, edited_text):
    differences = 0
    longer_length = max(len(text), len(edited_text))

    for i in range(longer_length):
        if i >= len(text) or i >= len(edited_text) or text[i] != edited_text[i]:
            differences += 1

    change_percentage = (differences / longer_length) * 100
    return change_percentage


async def compare_case_details(file_path):
    pattern = r"/(\d+)/?$"
    labeling_repository = LabelingRepository()

    with open(file_path, 'r', newline='') as csvfile:
        row_list = list(csv.reader(csvfile))

        for i in range(1, len(row_list)):
            row = row_list[i]
            doc_url = row[4]
            match = re.search(pattern, doc_url)
            case_id = match.group(1)
            facts = row[11]
            issues = row[12]

            case_details = await labeling_repository.get_case_from_case_id(case_id=case_id)
            precedent_details = await labeling_repository.get_precedents_from_case_id(case_id=case_id)
            edited_facts = case_details.get("facts")
            edited_issues = "".join(case_details.get("issues"))
            facts_change_percentage = await calculate_change_percentage(facts, edited_facts)
            issues_change_percentage = await calculate_change_percentage(issues, edited_issues)
            precedent_para_count = 0
            for precedent in precedent_details:
                precedent_para_count += len(precedent.get("paragraphs"))

            await labeling_repository.update_change_percentages(facts_change_percentage=facts_change_percentage,
                                                                issues_change_percentage=issues_change_percentage,
                                                                precedent_para_count=precedent_para_count)


if __name__ == "__main__":
    # Run the sample judgments through NER and RHetorical roles
    sample_data = pd.read_csv(os.path.join(Path(__file__).parents[3], "data/sample_105_judgments.csv"))
    sample_data = sample_data.iloc[0:5]
    sample_data[['petitioners', 'respondents']] = sample_data.progress_apply(
        lambda x: extract_petitioners_respondent_names(x), axis='columns',
        result_type='expand')

    sample_data['generated_issues_gpt4'] = sample_data.progress_apply(
        lambda x: generate_issues_if_none(x, 'gpt-4'), axis='columns')

    sample_data[['generated_arguments_party1_gpt4', 'generated_arguments_party2_gpt4']] = sample_data.progress_apply(
        lambda x: generate_arguments_if_none(x), axis='columns',
        result_type='expand')
    # sample_data['generated_issues_gpt4'] = sample_data['facts_of_case'].progress_apply(lambda x: generate_issues(x,'gpt-4'))

    sample_data.to_csv(os.path.join(Path(__file__).parents[3], "data/sample_argument_generation_5_4Aug.csv"), index=False)

    # # Code to import csv data to db
    # file_path = "data/sample_argument_generation_105_24july_1.csv"
    # asyncio.run(write_csv_file_into_db(file_path=file_path))

    # # Code to compare user edited data in db with original data in csv
    # file_path = "data/sample_argument_generation_105_24july_1.csv"
    # asyncio.run(compare_case_details(file_path=file_path))
