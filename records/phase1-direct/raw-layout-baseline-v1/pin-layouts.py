"""Pin the already compiled layouts; never infer offsets from language models."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
META = ROOT / 'obj/core/direct-proof-custody-next-line/gnatprove/data_representation'


def selected():
    body = (ROOT / 'core/worldline-retained_raw_decode.adb').read_text()
    spec = (ROOT / 'core/worldline-retained_raw_decode.ads').read_text()
    aliases = dict(re.findall(r'package (\w+) renames ([\w.]+);', spec))
    names = re.findall(r'^   function Load \(Data : Q.Byte_Array\) return ([\w.]+)', body, re.M)
    assert len(names) == 58 and len(set(names)) == len(names)
    rows = []
    for name in names:
        alias, short = name.split('.')
        unit = aliases[alias]
        filename = unit.lower().replace('.', '-') + '.ads'
        items = json.loads((META / (filename + '.json')).read_text())
        entry = next(x for x in items if x['name'].lower() == (unit + '.' + short).lower())
        value_size = entry.get('Size', entry.get('Value_Size'))
        object_size = entry.get('Size', entry.get('Object_Size'))
        assert isinstance(value_size, int) and value_size > 0 and value_size % 8 == 0
        assert isinstance(object_size, int) and object_size >= value_size
        assert isinstance(entry['Alignment'], int)
        target = OUT / (filename + '.json')
        if not target.exists():
            shutil.copyfile(META / (filename + '.json'), target)
        rows.append({'alias': name, 'file': filename, 'representation': entry,
                     'source_sha256': hashlib.sha256((ROOT / 'core' / filename).read_bytes()).hexdigest()})
    return rows


def pin(row):
    name = row['alias'].split('.')[1]
    path = ROOT / 'core' / row['file']
    source = path.read_text()
    entry = row['representation']
    if re.search(r'for\s+' + re.escape(name) + r'\s+use\s+record', source, re.I):
        return
    if 'record' in entry:
        pattern = r'(   type ' + re.escape(name) + r' is record\b.*?end record\s+with\s+Convention\s*=>\s*C;)'
        lines = ['   --  Preserve compiler-observed C field layout.', f'   for {name} use record']
        for field in entry['record']:
            assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', field['name'])
            assert all(isinstance(field[k], int) for k in ('Position', 'First_Bit', 'Size'))
            lines.append(f"      {field['name']} at {field['Position']} range {field['First_Bit']} .. {field['First_Bit'] + field['Size'] - 1};")
        lines.append('   end record;')
    else:
        pattern = r'(   type ' + re.escape(name) + r' is array\b.*?;)'
        lines = ['   --  Preserve compiler-observed C array layout.',
                 f"   for {name}'Component_Size use {entry['Component_Size']};"]
    match = re.search(pattern, source, re.S | re.I)
    assert match, row['alias']
    lines += [f"   for {name}'Size use {entry.get('Size', entry.get('Value_Size'))};",
              f"   for {name}'Object_Size use {entry.get('Size', entry.get('Object_Size'))};",
              f"   for {name}'Alignment use {entry['Alignment']};"]
    path.write_text(source[:match.end()] + '\n' + '\n'.join(lines) + source[match.end():])


rows = selected()
(OUT / 'selected-types.json').write_text(json.dumps(rows, indent=2) + '\n')
shutil.copyfile(ROOT / 'tests/raw_decode_tests.adb', OUT / 'raw-id-test.adb')
for row in rows:
    pin(row)
path = ROOT / 'core/worldline-retained_raw_decode.adb'
body = path.read_text()
body, record_count = re.subn(
    r"Data'First \+ ((?:Result|Raw)\.[A-Za-z_]+)'Position \+ \1'Size / System.Storage_Unit - 1",
    r"Data'First + (\1'Position + \1'Size / System.Storage_Unit - 1)", body)
lines = []
array_count = 0
for line in body.splitlines():
    if " .. Data'First + Q.Byte_Count" in line and ' - 1)' in line:
        start = line.index(" .. Data'First + ") + len(" .. Data'First + ")
        end = line.rfind(' - 1)') + len(' - 1')
        line = line[:start] + '(' + line[start:end] + ')' + line[end:]
        array_count += 1
    lines.append(line)
path.write_text('\n'.join(lines) + '\n')
(OUT / 'generation-result.json').write_text(json.dumps({
    'record_slice_rewrites': record_count, 'array_slice_rewrites': array_count,
    'scope': 'all58 original Load return types; preserve Size and Object_Size distinctly',
    'status': 'candidate; compiler comparison, runtime and proof pending'}, indent=2) + '\n')
print('Pinned', len(rows), 'types; repaired end offsets:', record_count, array_count)
