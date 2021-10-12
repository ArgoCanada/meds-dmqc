
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
        f'\\maketitle',
        f'\\clearpage'
    ]

    [f.write(l + '\n') for l in lines]

    return f


def insert_figure(fn, width=0.8, caption=''):

    lines = [
        f'\n\\begin{{figure}}[H]',
        f'\t\\centering',
        f'\t\\includegraphics[width={width}\\textwidth]{{{fn}}}',
        f'\t\\caption{{{caption}}}',
        f'\\end{{figure}}\n'
    ]

    s = ''
    for l in lines:
        s = s + l + '\n'
    
    return s

def list_figures(flt):

    figures = [f.as_posix() for f in Path(f'/Users/GordonC/Documents/projects/meds-dmqc/figures/{int(flt)}/').glob('*.png')]
    return figures

# def write_caption(figure_name):

def parse_comment(comment):

    # separate at semi colons
    pts = comment.split(';')
    # get rid of any leading whitespace
    pts = [p.strip() for p in pts]
    # check if second level of bullets
    lvl = [re.match('--.*', p) is not None for p in pts]
    # get rid of the leading dash for those now
    pts = [p.replace('--', '') if l else p for p,l in zip(pts, lvl)]
    # parse exponent units
    pts = [p.replace('m-3', 'm$^{-3}$') for p in pts]
    # escape character for underscores
    pts = [p.replace('_', '\\_') for p in pts]

    return pts, lvl

def write_bullets(bullets, indent):

    i = 0
    lines = [f'\\begin{{itemize}}']
    while i < len(bullets):
        if indent[i]:
            lines.append(f'\t\\begin{{itemize}}')
            while i < len(bullets) and indent[i]:
                lines.append(f'\t\t\\item {bullets[i]}')
                i += 1
            lines.append(f'\t\\end{{itemize}}')
        else:
            lines.append(f'\t\\item {bullets[i]}')
            i += 1
    lines.append(f'\\end{{itemize}}\n')

    s = ''
    for l in lines:
        s = s + l + '\n'
    
    return s

if __name__ == '__main__':

    # load tracker file
    df = pd.read_csv(Path('../dmqc_tracker.csv'))
    # drop any floats that haven't been DMQC'ed yet
    df = df[df['gain'].notna()]

    # start the document, named for todays date
    f = start_doc()
    # populate subsection for each float
    for i in df.index:
        f.write(f'\\section{{Float {int(df.wmo[i])}}}\n\n')
        f.write(f'Gain ({df.reference_data[i]}): ${df.gain[i]:.3f} \\pm {df.gain_std[i]:.3f}$\n')
        if df.sage_gain.notna()[i]:
            f.write(f'SAGE Gain: ${df.sage_gain[i]:.3f} \\pm {df.sage_gain_std[i]:.3f}$\n')
        f.write('\n')
        f.write(write_bullets(*parse_comment(df.comments[i])))

        for figure in list_figures(df.wmo[i]):
            f.write(insert_figure(figure))
        

    # end document
    f.write(f'\\end{{document}}\n')
    f.close()
    print('Done')
    

