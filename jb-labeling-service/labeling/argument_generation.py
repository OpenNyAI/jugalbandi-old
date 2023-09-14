import ast
from .helper import (
    choose_openai_model_based_on_length,
    call_openai_api,
    num_tokens_from_messages
)
from .model import TokenLength


async def generate_issues(facts: str, model: str = "") -> str:
    issue_generation_system_prompt = '''You are an Indian lawyer. Your task is to create legal issues to be fought in court based on the facts.'''
    issue_generation_user_prompt = '''facts:\n"""''' + facts + '''\n"""'''

    messages = [
        {"role": "system", "content": issue_generation_system_prompt},
        {"role": "user", "content": issue_generation_user_prompt}
    ]

    model = await choose_openai_model_based_on_length(messages, max_output_len=TokenLength.MAX_GENERATED_ISSUE.value)
    generated_issues = await call_openai_api(messages, max_tokens=TokenLength.MAX_GENERATED_ISSUE.value, model=model)

    return generated_issues


async def generate_issues_split(facts: str, model: str) -> list[dict]:
    issue_generation_system_prompt = '''You are an Indian lawyer. Your task is to create legal issues to be fought in court based on the facts. Always output the issues in form of a python list. [GENERATED ISSUE 1, GENERATED ISSUE 2, ...]'''
    issue_generation_user_prompt = '''facts:\n"""''' + facts + '''\n"""'''

    messages = [
        {"role": "system", "content": issue_generation_system_prompt},
        {"role": "user", "content": issue_generation_user_prompt}
    ]

    model = await choose_openai_model_based_on_length(messages, max_output_len=TokenLength.MAX_GENERATED_ISSUE.value)
    generated_issues = await call_openai_api(messages, max_tokens=TokenLength.MAX_GENERATED_ISSUE.value, model=model)
    generated_issues = ast.literal_eval(generated_issues)

    return generated_issues


async def generate_arguments(court_name: str, petitioner_name: str, respondent_name: str, facts: str, statutes_list: list, issues: str, generate_arguments_for: str = 'petitioners', precedent_paras: list[dict] = [], other_party_arguments: str | None = None) -> str:
    if generate_arguments_for == 'petitioners':
        argument_generation_system_prompt = '''You are an Indian lawyer in {}. Your task is to represent the Petitioner - {} against the Respondent - {}. Create arguments which clearly state the facts and law on the basis of which the defendant's actions are bad in law. Use the below
         mentioned facts of the case, the legal issues involved, sections of law and any other material which supports the Petitioner's case.'''.format(
            court_name, petitioner_name, respondent_name)
    else:
        argument_generation_system_prompt = '''You are an Indian lawyer in {}. Your task is to represent the Respondent - {} against the Petitioner - {}. Create arguments which clearly state the facts and law on the basis of which the defendant's actions are justified in law. Use the below
         mentioned facts of the case, the legal issues involved, sections of law and any other material which supports the Respondents's case.'''.format(
            court_name, respondent_name, petitioner_name)

    argument_generation_user_prompt = '''\nfacts:\n"""{}\n"""\n sections of law:\n"""{}\n"""\nIssues:\n"""{}\n"""'''.format(facts, statutes_list, issues)
    if len(precedent_paras) > 0:
        argument_generation_user_prompt = argument_generation_user_prompt + '''\nMake use of the following precedent citations to back the arguments generated.\n'''
        for precedent_para in precedent_paras:
            argument_generation_user_prompt = argument_generation_user_prompt + 'source: ' + precedent_para['source'] + '\nparagraph: ' + precedent_para['para_text']

    messages = [
        {"role": "system", "content": argument_generation_system_prompt},
        {"role": "user", "content": argument_generation_user_prompt}
    ]
    if other_party_arguments and len(other_party_arguments) > 0:
        argument_generation_user_prompt_with_other_party_args = argument_generation_user_prompt + '''\nThe arguments from other party are as follows. Generate arguments which counter these. """{}""""'''.format(other_party_arguments)
        revised_messages = [
            {"role": "system", "content": argument_generation_system_prompt},
            {"role": "user", "content": argument_generation_user_prompt_with_other_party_args}
        ]
        if await num_tokens_from_messages(revised_messages, model='gpt-4') + TokenLength.MAX_GENERATED_ARGUMENTS.value <= TokenLength.MAX_GPT3_5_TURBO.value:
            messages = revised_messages

    model = await choose_openai_model_based_on_length(messages, max_output_len=TokenLength.MAX_GENERATED_ARGUMENTS.value)
    if model:
        generated_arguments = await call_openai_api(messages, max_tokens=TokenLength.MAX_GENERATED_ARGUMENTS.value, model=model)
    else:
        generated_arguments = None  # Too long to process

    return generated_arguments
