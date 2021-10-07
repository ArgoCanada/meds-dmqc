
from pathlib import Path
import regex as re

import pandas as pd
import datetime

today = str(datetime.date.today())
document_name = f'argo_canada_bgc_dmqc_report_{today}.tex'
def start_doc(path=today, doc_name=document_name):
    if type(path) is str:
        path = Path(path)

    if not path.exists():
        path.mkdir()
    f = open(path / doc_name, 'w')
    f.write(f'\\input{{../style.tex}}\n\n')

    lines = [
        f'\\title{{DMQC Report on Dissolved Oxygen}}',
        f'\\author{{Christopher Gordon, DMQC Operator}}',
        f'\\date{{\\today}}\n',
        f'\\begin{{document}}',
        f'\t\\maketitle'
        f'\t\\clearpage'
    ]

    [f.write(l + '\n') for l in lines]

    return f


def insert_figure(fn, width=0.8, caption=''):

    lines = [
        f'\\begin{{figure}}',
        f'\t\\centering',
        f'\t\\includegraphics[width={width}\\textwidth]{{{fn}}}',
        f'\t\\caption{{{caption}}}',
        f'\\end{{figure}}'
    ]

    s = ''
    for l in lines:
        s = s + l + '\n'
    
    return s

# def list_figures(flt):

# def write_caption(figure_name):

# def parse_comment(comment):

if __name__ == '__main__':

    # load tracker file
    df = pd.read_csv(Path('../dmqc_tracker.csv'))
    # drop any floats that haven't been DMQC'ed yet
    df = df[df['gain'].notna()]

    # start the document, named for todays date
    f = start_doc()
    # populate subsection for each float
    for flt in df['wmo']:
        f.write(f'\t\\section{{Float {int(flt)}}}\n')

    # end document
    f.write(f'\\end{{document}}\n')
    f.close()
    print('Done')
    

