from __future__ import annotations

from typing import Dict, Tuple, Literal

import argparse
import ijson
import json


def search_in_json_file(filepath, terms: Dict[str, str| Tuple[str, str]], operator: Literal['OR', 'AND'] = 'OR'):
    with open(filepath, 'rb') as file:
        parser = ijson.parse(file)
        record = {}
        for prefix, event, value in parser:
            if event == 'end_map':
                found = None
                for key, search_term in terms.items():
                    operation = 'full'
                    if isinstance(search_term, tuple):
                        search_term, operation = search_term
                    if operation == 'part':
                        condition = search_term.lower().strip() in record.get(key, '').lower().strip()
                    else:
                        condition = search_term.lower().strip() == record.get(key, '').lower().strip()
                    if condition:
                        found = record
                        if operator == 'OR':
                            break
                    else:
                        found = None
                        break
                if found:
                    yield found

                record = {}
            elif event == 'string' or event == 'number':
                record[prefix.split('.')[-1]] = str(value)


def args_parse():
    parser = argparse.ArgumentParser(description='JSON finder')
    parser.add_argument('-f', dest="filepath", required=True, help="path to file")
    parser.add_argument('-t', '--term', dest="terms", action="append", required=True, help="Term, example: 'name:Some test' or 'name:Some te:part'")
    parser.add_argument('-o', '--operator', dest="operator", default='OR', help="Search operator, OR (default) | AND")
    return parser.parse_args()


if __name__ == '__main__':
    args = args_parse()
    filepath = args.filepath
    terms_raw = args.terms
    operator = args.operator.upper()
    terms = {}

    for term_raw in terms_raw:
        try:
            key, term = term_raw.split(':', 1)
            opt = term.rsplit(':', 1)
            if len(opt) > 1:
                term, operation = opt
                if operation not in {'full', 'part'}:
                    print(f'Invalid operation {operation}, valid operations: full, part')
                    exit(1)
                else:
                    terms[key.strip()] = term
                terms[key.strip()] = tuple(opt)
            else:
                terms[key.strip()] = term
        except IndexError:
            print(f'Invalid term {term_raw}, valid example "name:Some string"')
            exit(1)
    results = search_in_json_file(filepath=filepath, terms=terms, operator=operator)
    print(json.dumps(list(results), indent=2))
