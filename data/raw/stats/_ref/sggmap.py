"""
sggmap.py -- 시군구 name -> 5-digit 행정표준코드(법정동코드 앞 5자리) helper.

Source of truth: 행정안전부 행정표준코드관리시스템(code.go.kr) '법정동코드 전체자료'
(downloaded 2026-09-24; file dated 2026-09-17) -> _ref/법정동코드_전체자료.txt

Two code "vintages" matter for 2020-2026 data:
  * sgg_cd_ref : the code valid at the source's reference date (may be 폐지 now,
                 e.g. 29110 광주광역시 동구, 42110 강원도 춘천시, 47720 경상북도 군위군)
  * sgg_cd     : harmonised to the current (2026-09) code system when the unit maps 1:1
                 (29/46 -> 12 전남광주통합특별시 [2026-07-01], 42 -> 51 강원특별자치도 [2023-06-11],
                  45 -> 52 전북특별자치도 [2024-01-18], 47720 -> 27720 군위군 [2023-07-01],
                  28170 -> 28177 미추홀구 [2018-07-01]).
                 Units that were split have NO 1:1 successor -> sgg_cd = sgg_cd_ref and map_note says why:
                  - 인천 중구(28110)+동구(28140) -> 제물포구(28125)+영종구(28155)  [2026-07-01]
                  - 인천 서구(28260) -> 서해구(28275)+검단구(28290)                 [2026-07-01]
                  - 화성시(41590) -> 만세구/효행구/병점구/동탄구(41591/3/5/7)      [2026-02-01]
                  - 부천시(41190) -> 원미구/소사구/오정구(41192/4/6)               [2024-01-01]
Usage:
    import sys; sys.path.insert(0, '<...>/data/raw/stats/_ref'); import sggmap
    m = sggmap.Mapper()
    r = m.lookup('강원도', '춘천시', ref_date='2020-11-01')  # -> sgg_cd_ref='42110', sgg_cd='51110', sgg_nm='강원특별자치도 춘천시'
    df2 = m.attach(df, sido_col='시도', sgg_col='시군구', ref_date='2024-12-31')  # adds 5 standard columns
"""
import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BJD_TXT = os.path.join(HERE, '법정동코드_전체자료.txt')

# sido short key -> list of 2-digit prefixes that may hold it (old first, new last)
SIDO_PREFIX = {
    '서울': ['11'], '부산': ['26'], '대구': ['27'], '인천': ['28'], '광주': ['29', '12'],
    '대전': ['30'], '울산': ['31'], '세종': ['36'], '경기': ['41'], '강원': ['42', '51'],
    '충북': ['43'], '충남': ['44'], '전북': ['45', '52'], '전남': ['46', '12'], '경북': ['47'],
    '경남': ['48'], '제주': ['50'], '전남광주': ['12', '29', '46'],
}
SIDO_NORMALIZE = [
    (r'^전남광주.*', '전남광주'), (r'^광주전남.*', '전남광주'),
    (r'^서울.*', '서울'), (r'^부산.*', '부산'), (r'^대구.*', '대구'), (r'^인천.*', '인천'),
    (r'^광주.*', '광주'), (r'^대전.*', '대전'), (r'^울산.*', '울산'), (r'^세종.*', '세종'),
    (r'^경기.*', '경기'), (r'^강원.*', '강원'), (r'^충청북.*|^충북.*', '충북'),
    (r'^충청남.*|^충남.*', '충남'), (r'^전라북.*|^전북.*', '전북'), (r'^전라남.*|^전남.*', '전남'),
    (r'^경상북.*|^경북.*', '경북'), (r'^경상남.*|^경남.*', '경남'), (r'^제주.*', '제주'),
]
SPLIT_NOTES = {
    '28110': 'split_2026-07-01: 인천 중구+동구 -> 제물포구(28125)+영종구(28155); no 1:1 successor',
    '28140': 'split_2026-07-01: 인천 중구+동구 -> 제물포구(28125)+영종구(28155); no 1:1 successor',
    '28260': 'split_2026-07-01: 인천 서구 -> 서해구(28275)+검단구(28290); no 1:1 successor',
    '41590': 'parent_si: 화성시 has 일반구 since 2026-02-01 (41591/41593/41595/41597)',
    '41190': 'parent_si: 부천시 has 일반구 since 2024-01-01 (41192/41194/41196)',
}
# explicit old->new 1:1 renames that are not simple prefix swaps
EXTRA_RENAME = {'28170': '28177', '47720': '27720'}

# code validity windows [start, end) for codes that changed after 2010 (YYYY-MM-DD strings)
PREFIX_VALID = {'42': (None, '2023-06-11'), '51': ('2023-06-11', None),
                '45': (None, '2024-01-18'), '52': ('2024-01-18', None),
                '29': (None, '2026-07-01'), '46': (None, '2026-07-01'), '12': ('2026-07-01', None)}
CODE_VALID = {
    '47720': (None, '2023-07-01'), '27720': ('2023-07-01', None),
    '28110': (None, '2026-07-01'), '28140': (None, '2026-07-01'), '28260': (None, '2026-07-01'),
    '28125': ('2026-07-01', None), '28155': ('2026-07-01', None), '28275': ('2026-07-01', None), '28290': ('2026-07-01', None),
    '28170': (None, '2018-07-01'), '28177': ('2018-07-01', None),
    '41591': ('2026-02-01', None), '41593': ('2026-02-01', None), '41595': ('2026-02-01', None), '41597': ('2026-02-01', None),
    '41192': ('2024-01-01', None), '41194': ('2024-01-01', None), '41196': ('2024-01-01', None),
    '41195': (None, '2016-07-04'), '41197': (None, '2016-07-04'), '41199': (None, '2016-07-04'),
    '43710': (None, '2014-07-01'), '43111': ('2014-07-01', None), '43112': ('2014-07-01', None),
    '43113': ('2014-07-01', None), '43114': ('2014-07-01', None),
}


def code_valid(cd, exists, date):
    """Is 5-digit code cd valid at date (YYYY-MM-DD)? date None -> use current existence."""
    if date is None:
        return exists
    win = CODE_VALID.get(cd) or PREFIX_VALID.get(cd[:2])
    if win is None:
        return exists  # unchanged units (폐지 before 2010 are treated as invalid)
    s, e = win
    return (s is None or date >= s) and (e is None or date < e)


def norm_sido(s):
    s = re.sub(r'\s+', '', str(s or ''))
    for pat, key in SIDO_NORMALIZE:
        if re.match(pat, s):
            return key
    return None


def norm_sgg(s):
    s = str(s or '')
    s = re.sub(r'\(.*?\)', '', s)  # drop '(강원)' etc
    s = re.sub(r'\s+', '', s)
    return s


def load_bjd5():
    df = pd.read_csv(BJD_TXT, sep='\t', dtype=str)
    df.columns = ['code', 'name', 'status']
    df['name'] = df['name'].str.strip().str.replace(r'\s+', ' ', regex=True)
    d5 = df[(df.code.str[5:] == '00000') & (df.code.str[2:5] != '000')].copy()
    d5['cd5'] = d5.code.str[:5]
    d5['exists'] = d5.status.eq('존재')
    tok = d5['name'].str.split(' ')
    d5['sido_nm'] = tok.str[0]
    d5['sgg_part'] = tok.str[1:].str.join(' ')
    d5['n_tok'] = tok.str.len()
    return d5[['cd5', 'name', 'status', 'exists', 'sido_nm', 'sgg_part', 'n_tok']].reset_index(drop=True)


class Mapper:
    def __init__(self):
        self.d5 = load_bjd5()
        cur = self.d5[self.d5.exists]
        self.cur_name = dict(zip(cur.cd5, cur.name))
        self.all_name = {}
        for r in self.d5.itertuples():
            # prefer 존재 name when duplicate code (should not happen)
            if r.cd5 not in self.all_name or r.exists:
                self.all_name[r.cd5] = r.name
        # parents of 일반구 in current system
        gu = cur[cur.n_tok == 3]
        self.parents_2026 = set(gu.cd5.str[:4] + '0')
        self.parents_2026 |= {c for c in cur.cd5 if any(g[:4] == c[:4] and g != c and self.cur_name[g].startswith(self.cur_name[c] + ' ') for g in gu.cd5)}
        # build keys: (prefix2, key) -> list of (cd5, exists)
        self.keys = {}
        for r in self.d5.itertuples():
            p2 = r.cd5[:2]
            full = norm_sgg(r.sgg_part)
            self._add(p2, full, r.cd5, r.exists)
            if r.n_tok == 3:  # 일반구: also allow bare 구 name and '시 구' w/o space
                self._add(p2, norm_sgg(r.sgg_part.split(' ')[1]), r.cd5, r.exists, short=True)
        # sejong
        self._add('36', '세종시', '36110', True)
        self._add('36', '세종특별자치시', '36110', True)
        self._add('36', '', '36110', True)

    def _add(self, p2, key, cd5, exists, short=False):
        self.keys.setdefault((p2, key), []).append((cd5, exists, short))

    def to_2026(self, cd):
        """1:1 successor in the 2026-09 system, or None if split/unknown."""
        if cd in SPLIT_NOTES and cd not in self.cur_name:
            return None
        if cd in self.cur_name:
            return cd
        if cd in EXTRA_RENAME:
            return EXTRA_RENAME[cd]
        old_nm = self.all_name.get(cd)
        if old_nm is None:
            return None
        p2 = cd[:2]
        newp = {'29': '12', '46': '12', '42': '51', '45': '52'}.get(p2)
        if newp is None:
            return None
        sggp = ' '.join(old_nm.split(' ')[1:])
        cands = [c for c, n in self.cur_name.items() if c[:2] == newp and ' '.join(n.split(' ')[1:]) == sggp]
        return cands[0] if len(cands) == 1 else None

    def lookup(self, sido, sgg, ref_date=None):
        """Map (시도명, 시군구명) -> dict(sgg_cd, sgg_nm, sgg_cd_ref, sgg_nm_ref, map_note) or None.
        ref_date 'YYYY-MM-DD' = reference date of the source; codes valid at that date are preferred
        (e.g. ref_date='2024-12-31': 광주광역시 동구 -> ref 29110, harmonised 12210).
        ref_date None -> prefer currently existing codes."""
        sk = norm_sido(sido)
        g = norm_sgg(sgg)
        if sk is None:
            return None
        if sk == '세종':
            cands = [('36110', True, False)]
        elif g == '군위군' and sk in ('경북', '대구'):
            cands = [('47720', False, False), ('27720', True, False)]
        else:
            cands = []
            for p2 in SIDO_PREFIX[sk]:
                cands += self.keys.get((p2, g), [])
            if not cands and sk == '전남광주':
                for p2 in ('29', '46'):
                    cands += self.keys.get((p2, g), [])
        if not cands:
            return None
        seen = {}
        for c, ex, sh in cands:
            if c in seen:
                seen[c] = (seen[c][0] or ex, seen[c][1] and sh)
            else:
                seen[c] = (ex, sh)
        items = list(seen.items())
        full = [(c, v) for c, v in items if not v[1]]
        if full:
            items = full
        # keep codes valid at ref_date (if any)
        valid = [(c, v) for c, v in items if code_valid(c, v[0], ref_date)]
        if valid:
            items = valid
        elif ref_date is not None:
            # e.g. sido name implies an older vintage; fall back to existing
            ex_items = [(c, v) for c, v in items if v[0]]
            items = ex_items or items
        if len(items) > 1:
            ex_items = [(c, v) for c, v in items if v[0]]
            if ex_items and ref_date is None:
                items = ex_items
        if len(items) > 1:
            # prefer old-vintage prefix if the sido NAME is an old one (강원도/전라북도/광주광역시/전라남도)
            s = re.sub(r'\s+', '', str(sido))
            oldname = s in ('강원도', '전라북도', '광주광역시', '전라남도')
            order = SIDO_PREFIX.get(sk, [])
            items.sort(key=lambda cv: order.index(cv[0][:2]) if cv[0][:2] in order else 99, reverse=not oldname)
            items = items[:1]
        cd_ref = items[0][0]
        nm_ref = self.all_name.get(cd_ref)
        cd26 = self.to_2026(cd_ref)
        note = SPLIT_NOTES.get(cd_ref, '')
        if cd26 is None:
            cd_out, nm_out = cd_ref, nm_ref
            if not note:
                note = 'no_1to1_2026_successor'
        else:
            cd_out, nm_out = cd26, self.cur_name[cd26]
            if cd26 in self.parents_2026 and not note:
                note = 'parent_si_of_ilbangu_2026'
            if cd26 != cd_ref and not note:
                note = f'recoded {cd_ref}->{cd26}'
        return dict(sgg_cd=cd_out, sgg_nm=nm_out, sgg_cd_ref=cd_ref, sgg_nm_ref=nm_ref, map_note=note)

    def attach(self, df, sido_col, sgg_col, ref_date=None):
        out = df.copy()
        res = [self.lookup(a, b, ref_date=ref_date) or {} for a, b in zip(out[sido_col], out[sgg_col])]
        for k in ['sgg_cd', 'sgg_nm', 'sgg_cd_ref', 'sgg_nm_ref', 'map_note']:
            out[k] = [r.get(k) for r in res]
        return out

    def master_2026(self):
        cur = self.d5[self.d5.exists].copy()
        cur['is_parent_si'] = cur.cd5.isin(self.parents_2026)
        cur['is_ilbangu'] = cur.n_tok.eq(3)
        cur['is_unit'] = ~cur.is_parent_si
        return cur.rename(columns={'cd5': 'sgg_cd', 'name': 'sgg_nm'})[
            ['sgg_cd', 'sgg_nm', 'sido_nm', 'is_parent_si', 'is_ilbangu', 'is_unit']]


if __name__ == '__main__':
    m = Mapper()
    ms = m.master_2026()
    print(len(ms), 'current codes;', ms.is_unit.sum(), 'analysis units (일반구 instead of parent 시)')
    tests = [('강원도', '춘천시'), ('강원특별자치도', '춘천시'), ('광주광역시', '동구'), ('전라남도', '목포시'),
             ('경상북도', '군위군'), ('대구광역시', '군위군'), ('인천광역시', '중구'), ('인천광역시', '미추홀구'),
             ('인천광역시', '남구'), ('경기도', '수원시 장안구'), ('경기도', '장안구'), ('경기도', '화성시'),
             ('경기도', '부천시'), ('경기도', '부천시원미구'), ('경상북도', '포항시 남구'), ('경상북도', '남구'),
             ('세종특별자치시', '세종특별자치시'), ('전라북도', '전주시 완산구'), ('전남광주통합특별시', '광산구'),
             ('경상남도', '창원시 마산합포구'), ('강원', '고성군'), ('경남', '고성군'), ('대구', '남구'), ('서울', '중구')]
    for d in (None, '2020-11-01', '2024-12-31', '2026-08-31'):
        print('=== ref_date', d)
        for t in tests:
            r = m.lookup(*t, ref_date=d)
            print(t, r and (r['sgg_cd_ref'], r['sgg_nm_ref'], '->', r['sgg_cd'], r['sgg_nm'], r['map_note']))
