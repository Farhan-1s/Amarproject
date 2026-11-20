from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'DEMO_L': ['SEQN', 'RIDAGEYR', 'RIAGENDR', 'RIDEXPRG', 'INDFMPIR', 'WTINT2YR', 'WTMEC2YR', 'SDMVPSU', 'SDMVSTRA'],
    'BMX_L': ['SEQN', 'BMXBMI', 'BMXWAIST', 'BMXHT'],
    'TCHOL_L': ['SEQN', 'LBXTC', 'WTPH2YR'],
    'HDL_L': ['SEQN', 'LBDHDD'],
    'BPQ_L': ['SEQN', 'BPQ080', 'BPQ101D'],
    'SMQ_L': ['SEQN', 'SMQ020', 'SMQ040'],
}


def prepare_data():
    sources, source_rows, merge_rows, quality = {}, [], [], []
    for name, columns in FILES.items():
        path = next((p for p in (ROOT / 'data').iterdir() if p.name.lower() == f'{name}.xpt'.lower()), None)
        if path is None:
            raise FileNotFoundError(f'Missing {name}.xpt. Run python src/download_data.py first.')
        frame = pd.read_sas(path, format='xport')[columns].copy()
        numeric = frame.select_dtypes(include='number').columns
        tiny = (frame[numeric].abs() < 1e-50) & frame[numeric].ne(0)
        quality.append((name, 'Tiny floating values normalized to zero', int(tiny.sum().sum())))
        frame[numeric] = frame[numeric].mask(tiny, 0)
        if frame.SEQN.isna().any() or frame.SEQN.duplicated().any():
            raise ValueError(f'{name}: missing or duplicated participant identifier')
        frame.SEQN = frame.SEQN.astype(int)
        sources[name] = frame
        source_rows.append((name, len(frame), frame.SEQN.nunique(), 0))
    df = sources['DEMO_L'].copy()
    for name in list(FILES)[1:]:
        matched = int(df.SEQN.isin(sources[name].SEQN).sum())
        before = len(df)
        df = df.merge(sources[name], on='SEQN', how='left', validate='one_to_one')
        merge_rows.append((name, before, len(df), matched, before - matched))
    for col, allowed in {'BPQ080': [1, 2], 'BPQ101D': [1, 2], 'SMQ020': [1, 2], 'SMQ040': [1, 2, 3]}.items():
        special = df[col].isin([7, 9, 77, 99])
        quality.append((col, 'Refused or unknown codes set to missing', int(special.sum())))
        df.loc[special, col] = np.nan
        invalid = df[col].notna() & ~df[col].isin(allowed)
        quality.append((col, 'Unexpected categories set to missing', int(invalid.sum())))
        df.loc[invalid, col] = np.nan
    bounds = {'RIDAGEYR': (0, 80), 'INDFMPIR': (0, 5), 'BMXBMI': (0, np.inf), 'BMXWAIST': (0, np.inf), 'BMXHT': (0, np.inf), 'LBXTC': (0, np.inf), 'LBDHDD': (0, np.inf)}
    for col, (low, high) in bounds.items():
        bad = df[col].notna() & ((df[col] < low) | (df[col] > high))
        if col not in ['RIDAGEYR', 'INDFMPIR']:
            bad |= df[col].eq(0)
        quality.append((col, 'Impossible range set to missing', int(bad.sum())))
        df.loc[bad, col] = np.nan
    bad = df.LBXTC.notna() & df.LBDHDD.notna() & (df.LBXTC < df.LBDHDD)
    quality.append(('Lipids', 'Total cholesterol below HDL set to missing', int(bad.sum())))
    df.loc[bad, ['LBXTC', 'LBDHDD']] = np.nan
    adult = df.loc[(df.WTMEC2YR > 0) & (df.RIDAGEYR >= 20)].copy()
    flow = [('Interview sample', len(df), 0)]
    rules = [
        ('MEC examined', lambda d: d.WTMEC2YR > 0),
        ('Age 20 or older', lambda d: d.RIDAGEYR >= 20),
        ('Known pregnancies excluded', lambda d: d.RIDEXPRG.ne(1)),
        ('Complete anthropometry', lambda d: d[['BMXBMI', 'BMXWAIST', 'BMXHT']].notna().all(axis=1)),
        ('Complete lipid measurements', lambda d: d[['LBXTC', 'LBDHDD']].notna().all(axis=1)),
        ('Positive phlebotomy weight', lambda d: d.WTPH2YR > 0),
    ]
    for label, rule in rules:
        before = len(df)
        df = df.loc[rule(df)].copy()
        flow.append((label, len(df), before - len(df)))
    df['WHtR'] = df.BMXWAIST / df.BMXHT
    df['Non_HDL_C'] = df.LBXTC - df.LBDHDD
    df['BMI_Category'] = pd.cut(df.BMXBMI, [0, 18.5, 25, 30, np.inf], labels=['Underweight', 'Normal', 'Overweight', 'Obese'], right=False)
    df['High_WHtR'] = (df.WHtR >= 0.50).astype(int)
    df['High_Lipid'] = (df.Non_HDL_C >= 160).astype(int)
    df['Sex'] = df.RIAGENDR.map({1: 'Male', 2: 'Female'})
    df['Age_Group'] = pd.cut(df.RIDAGEYR, [20, 40, 60, np.inf], labels=['20-39', '40-59', '60+'], right=False)
    df['Smoking_Status'] = pd.Series(index=df.index, dtype='object')
    df.loc[df.SMQ020.eq(2), 'Smoking_Status'] = 'Never'
    df.loc[df.SMQ020.eq(1) & df.SMQ040.eq(3), 'Smoking_Status'] = 'Former'
    df.loc[df.SMQ020.eq(1) & df.SMQ040.isin([1, 2]), 'Smoking_Status'] = 'Current'
    missing = []
    for label, frame in [('Examined adults before exclusions', adult), ('Final analytical sample', df)]:
        for col in frame.columns:
            missing.append((label, col, len(frame), int(frame[col].notna().sum()), int(frame[col].isna().sum()), frame[col].isna().mean() * 100))
    audits = {
        'source_counts': pd.DataFrame(source_rows, columns=['File', 'Rows', 'Unique_SEQN', 'Duplicate_SEQN']),
        'merge_audit': pd.DataFrame(merge_rows, columns=['File', 'Before', 'After', 'Matched', 'Unmatched']),
        'quality_audit': pd.DataFrame(quality, columns=['Variable', 'Action', 'Count']),
        'sample_flow': pd.DataFrame(flow, columns=['Stage', 'Retained', 'Excluded_at_stage']),
        'missingness': pd.DataFrame(missing, columns=['Sample', 'Variable', 'N', 'Valid', 'Missing', 'Missing_percent']),
    }
    return df, audits


def save_table(table, name, index=False):
    (ROOT / 'tables').mkdir(exist_ok=True)
    table.to_csv(ROOT / 'tables' / f'{name}.csv', index=index, float_format='%.10g')
