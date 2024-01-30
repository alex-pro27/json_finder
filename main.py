from __future__ import annotations, generators

import time
from decimal import Decimal
from typing import Dict, Tuple, List, Literal, TypeAlias

import argparse
import ijson
import json

Term: TypeAlias = str | Tuple[str, str]
Terms: TypeAlias = Dict[str, Term | List[Term]]
Operations: TypeAlias = Literal['full', 'part', 'lt', 'gt', 'lte', 'gte']
Operator: TypeAlias = Literal['OR', 'AND']


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def match_value(term: Term, value: str | int | float | Decimal):
    operation = 'full'

    if not isinstance(term, list):
        term = [term]
    condition = False
    for search_term in term:
        if isinstance(search_term, tuple):
            search_term, operation = search_term
        if operation == 'full':
            condition = search_term == str(value).lower()
        elif operation == 'part':
            condition = search_term in str(value).lower()
        else:
            try:
                value = float(value)
                search_term = float(search_term)
            except (ValueError, TypeError):
                condition = False
                break
            if operation == 'lt':
                condition = value < search_term
            elif operation == 'gt':
                condition = value > search_term
            elif operation == 'lte':
                condition = value <= search_term
            elif operation == 'gte':
                condition = value >= search_term
        if not condition:
            break

    return condition


def search_in_json_file(filepath, terms: Terms, operator: Operator = 'OR'):
    with open(filepath, 'rb') as file:
        parser = ijson.parse(file)
        record = {}
        for prefix, event, value in parser:
            if event == 'end_map':
                found = None
                for key, search_term in terms.items():
                    _value = record.get(key, '')
                    if _value is None:
                        continue
                    if match_value(search_term, _value):
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
                record[prefix.split('.')[-1]] = value


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
            key = key.strip()
            term_ = None
            if len(opt) > 1:
                term, operation = opt
                if operation not in {'full', 'part', 'lt', 'gt', 'lte', 'gte'}:
                    print(f'Invalid operation {operation}, valid operations: full, part')
                    exit(1)
                term_ = tuple([term.strip().lower(), operation])
            else:
                term_ = term.strip().lower()
            if key not in terms:
                terms[key] = term_
            else:
                if isinstance(terms[key], list):
                    terms[key].append(term_)
                else:
                    terms[key] = [terms[key], term_]
        except (IndexError, ValueError):
            print(f'Invalid term {term_raw}, valid example "name:Some string"')
            exit(1)
    results = search_in_json_file(filepath=filepath, terms=terms, operator=operator)
    t = time.time()
    count_results = 0
    for res in results:
        print(json.dumps(res, indent=2, cls=JSONEncoder))
        count_results += 1
    print(f'Found {count_results} records in {time.time() - t} seconds')
