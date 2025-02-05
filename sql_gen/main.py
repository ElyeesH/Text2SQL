import json, re
import os, sys
import time

proj_dir = os.path.dirname(os.path.dirname(__file__))
# print(proj_dir)
sys.path.append(proj_dir)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from LLMs.codestral import Codestral
from LLMs.gemini import Gemini
from LLMs.sqlcoder import SQLCoder
from LLMs.gpt4 import GPT4
from LLMs.deepseek import Deepseek
from tqdm import tqdm
import argparse
from get_example_modules import get_examples_ins
from data_preprocess import gen_ppl_from_json

import logging, sqlite3


def get_example_prefix():
    return "### Some example pairs of question and corresponding SQL query are provided based on similar problems:\n\n"


def format_example(example: dict):
    template_qa = "### {}\n{}"
    return template_qa.format(example['question'], example['gold_sql'])


def formatting_prompt(sample):
    question = sample['question']
    ddls = sample['simplified_ddl']
    db = sample['db']
    # 动态加载前三行数据
    simplified_ddl_data = []
    # 读取数据库
    mydb = sqlite3.connect(
        fr"data/test_database/{db}/{db}.sqlite")  # 链接数据库
    cur = mydb.cursor()
    # 表
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    Tables = cur.fetchall()  # Tables 为元组列表
    for table in Tables:
        # 列
        cur.execute(f"select * from `{table[0]}`")
        col_name_list = [tuple[0] for tuple in cur.description]
        # print(col_name_list)
        db_data_all = []
        # 获取前三行数据
        for i in range(3):
            db_data_all.append(cur.fetchone())
        # ddls_data
        test = ""
        for idx, column_data in enumerate(col_name_list):
            # print(list(db_data_all[2])[idx])
            try:
                test += f"{column_data}[{list(db_data_all[0])[idx]},{list(db_data_all[1])[idx]},{list(db_data_all[2])[idx]}],"
            except:
                test = test
        simplified_ddl_data.append(f"{table[0]}({test[:-1]})")
    ddls_data = "# " + ";\n# ".join(simplified_ddl_data) + ";\n"
    foreign_key = ""
    for foreign_key_data in sample["foreign_key"][0].split("\n"):
        foreign_key += f'# {foreign_key_data};\n'
    foreign_key = foreign_key[:-2]
    # evidence = "".join(sample['gt_evidence'])
    prompt = f'''### Answer the question by sqlite SQL query only and with no explanation. You must minimize SQL execution time while ensuring correctness.\n### Sqlite SQL tables, with their properties:\n#\n{ddls}#\n### Here are some data information about database references.\n#\n{ddls_data}#\n### Foreign key information of Sqlite SQL tables, used for table joins: \n#\n{foreign_key}\n#\n### Question: {question}\n### SQL: '''

    return prompt


def formatting_prompt_sl(sample):
    linked_tables = [i.lower() for i in sample['linked_tables_gpt']]
    tbs = []
    for tb in sample['simplified_ddl'].split("\n"):
        t = tb.split("(")[0].strip("#").strip()
        if t.lower() in linked_tables:
            tbs.append(t)
    sc_tables = tbs
    ddl = sample['simplified_ddl'][:-2]
    split_ddl = ddl.split(";\n")
    fk_all = sample["foreign_key"][0].split("\n")
    ddl_sc = []
    fk_sc = []
    db = sample['db']
    # 动态加载前三行数据
    simplified_ddl_data = []
    # 读取数据库
    mydb = sqlite3.connect(
        fr"data/test_database/{db}/{db}.sqlite")  # 链接数据库
    cur = mydb.cursor()
    # 外键
    for fk_test in fk_all:
        num = 0
        for tab in sc_tables:
            if str(" " + tab + "(").lower() in " " + str(fk_test).lower():
                num += 1
        if num == 2:
            fk_sc.append(fk_test)
    fk_sc = list(set(fk_sc))
    for table in sc_tables:
        # ddl
        for ddl_test in split_ddl:
            if str(" " + table + "(").lower() in str(ddl_test).lower():
                ddl_sc.append(ddl_test)
        # 前三行数据
        try:
            cur.execute(f"select * from `{table}`")
            col_name_list = [tuple[0] for tuple in cur.description]
            db_data_all = []
            # 获取前三行数据
            for i in range(3):
                db_data_all.append(cur.fetchone())
            # ddls_data
            test = ""
            for idx, column_data in enumerate(col_name_list):
                try:
                    test += f"{column_data}[{list(db_data_all[0])[idx]},{list(db_data_all[1])[idx]},{list(db_data_all[2])[idx]}],"
                except:
                    test = test
            simplified_ddl_data.append(f"{table}({test[:-1]})")
        except:
            print()
    # res_ddl = []
    # tables = []
    # for test in ddl_sc:
    #     tables.append(test.split("(")[0].replace("# ",""))
    # for one_ddl in split_ddl:
    #     hit = 0
    #     for one_table in linked_tables:
    #         if f" {one_table.lower()}(" in one_ddl.lower():
    #             hit = 1
    #     if hit:
    #         res_ddl.append(one_ddl)
    ddl = ";\n".join(ddl_sc) + '.'
    ddls_data = "# " + ";\n# ".join(simplified_ddl_data) + ";\n"
    foreign_key = ""
    if len(fk_sc) > 0:
        for foreign_key_data in fk_sc:
            foreign_key += f'# {foreign_key_data};\n'
        foreign_key = "\n### Foreign key information of Sqlite SQL tables, used for table joins: \n#\n" + foreign_key[:-2]
    else:
        foreign_key = ""

    # prompt=f'''### Answer the question by sqlite SQL query only and with no explanation\n### Sqlite SQL tables, with their properties:\n{ddl}\n### Question: {sample['question']}\n### SQL: '''
    if foreign_key:
        prompt = f'''### Answer the question by sqlite SQL query only and with no explanation. You must minimize SQL execution time while ensuring correctness.\n### Sqlite SQL tables, with their properties:\n#\n{ddl}\n#\n### Here are some data information about database references.\n#\n{ddls_data}#{foreign_key}\n#\n### Question: {sample['question']}\n### SQL: '''
    else:
        prompt = f'''### Answer the question by sqlite SQL query only and with no explanation. You must minimize SQL execution time while ensuring correctness.\n### Sqlite SQL tables, with their properties:\n#\n{ddl}\n#\n### Here are some data information about database references.\n#\n{ddls_data}#\n### Question: {sample['question']}\n### SQL: '''
    return prompt


def run_sql_generation(model,
                       input_data,
                       out_file,
                       log,
                       k_shot=0,
                       select_type="Euclidean_mask",
                       pool_num=1,
                       sl=False):

    domain = False

    # load_libray
    if k_shot != 0:
        examples_libary = get_examples_ins(select_type)
        print(f"select type: {select_type}, k shot: {k_shot}")
    # read file

    if model == "codestral":
        llmapi = Codestral()
    elif model == "gpt":
        llmapi = GPT4()
    elif model == "sqlcoder":
        llmapi = SQLCoder()
    elif model == "gemini":
        llmapi = Gemini()
    elif model == 'deepseek':
        llmapi = Deepseek()
    else:
        raise Exception("no llm selected!")

    all_prompts = []
    # get all prompts for parallel
    for i, sample in enumerate(input_data):
        prompt_target = formatting_prompt(sample) if not sl else formatting_prompt_sl(sample)

        if k_shot != 0:
            examples = examples_libary.get_examples(sample,
                                                    k_shot,
                                                    cross_domain=domain)
            prompt_example = [format_example(exm) for exm in examples]
            prompt = get_example_prefix() + "\n\n".join(prompt_example +
                                                        [prompt_target])
        else:
            prompt = prompt_target
        all_prompts.append(prompt)

    result = []
    for i,it in enumerate(all_prompts):
        response=llmapi(it)
        with open(log, 'a', encoding='utf-8') as log_file:
            log_file.write(it + '\n')
            log_file.write('response:'+str(response) + '\n')
        #print(f"response {i} generated waiting for 20s")
        #time.sleep(20) if API limit is reached
        result.append(response)
    result = '~~'.join(result[i].replace("\n", " ")
                       for i in range(len(result)))

    with open(out_file, 'w', encoding='utf-8') as file:
        file.write(str(result) + '\n')

    


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--model", type=str, default="deepseek")
    parser.add_argument("--dataset", type=str, default="ppl_dev.json")
    parser.add_argument("--out_file", type=str, default="raw.txt")
    parser.add_argument("--kshot", type=int, default=2)
    parser.add_argument("--pool", type=int, default=1)
    parser.add_argument("--sl", action="store_true")
    parser.add_argument("--select_type", type=str, default="Euclidean_mask")
    
    args = parser.parse_args()
    if args.sl == False:
        input_data = gen_ppl_from_json(args.dataset, args.model[:-3])
    else:
        input_data = json.load(open(args.dataset, 'r'))
    print("schema linking: ", args.sl)
    print(args.dataset)
    run_sql_generation(args.model, input_data, "out.txt", "log.txt", args.kshot,
                       args.select_type,  args.pool, args.sl)
