from pathlib import Path
import hashlib
import json
import re
import shutil

SOURCE = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP02')
WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/focused-FP02-primary')
COPY = WORK / 'inspection-copy'
COPY.mkdir(exist_ok=True)

# All validation below uses disposable copies. Source access only copies files.
for label in ['R17', 'R28', 'R44', 'R63']:
    for relative in [f'{label}/package', f'{label}/ordinary/observed-final-skill',
                     f'{label}/challenging/observed-final-skill',
                     f'{label}/ordinary/final-input-state',
                     f'{label}/challenging/final-input-state']:
        shutil.copytree(SOURCE / relative, COPY / relative, dirs_exist_ok=True)
    fmt = SOURCE / label / 'creator-format-observation.json'
    if fmt.exists():
        shutil.copy2(fmt, COPY / label / fmt.name)
shutil.copytree(SOURCE / 'original-consumer-inputs', COPY / 'original-consumer-inputs', dirs_exist_ok=True)

for label in ['R17', 'R28', 'R44', 'R63']:
    files = [f for f in (COPY / label / 'package').rglob('*') if f.is_file()]
    assert len(files) == 1 and files[0].name == 'SKILL.md'
    skill = files[0]
    text = skill.read_text()
    assert text.startswith('---\n')
    front, body = text[4:].split('\n---\n', 1)
    fields = dict(line.split(': ', 1) for line in front.splitlines())
    assert set(fields) == {'name', 'description'}
    assert fields['name'] == skill.parent.name
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name'])
    assert len(fields['name']) <= 64 and 0 < len(fields['description']) <= 1024
    assert ': ' not in fields['description'] and ' #' not in fields['description']
    assert body.strip()
    print(f'{label}: basic frontmatter/inventory PASS; description chars={len(fields["description"])}')
    fmt = COPY / label / 'creator-format-observation.json'
    if fmt.exists():
        expected = json.loads(fmt.read_text())['file_sha256']['SKILL.md']
        assert hashlib.sha256(skill.read_bytes()).hexdigest() == expected
        print(f'{label}: supplied format-observation package hash MATCH')
    for condition in ['ordinary', 'challenging']:
        app = COPY / label / condition
        observed = list((app / 'observed-final-skill').rglob('SKILL.md'))
        assert len(observed) == 1 and skill.read_bytes() == observed[0].read_bytes()
        original = COPY / 'original-consumer-inputs' / condition / 'input'
        final = app / 'final-input-state'
        assert sorted(f.name for f in original.iterdir()) == sorted(f.name for f in final.iterdir())
        count = 0
        for file in original.iterdir():
            actual = (final / file.name).read_text()
            if file.name == 'request.md':
                actual = re.sub(r'/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/[^/\s]+/input',
                                '{{INPUT_DIR}}', actual)
            assert file.read_text() == actual
            count += 1
        print(f'{label}/{condition}: final Skill byte-identical; {count} final input texts MATCH (request directory normalized only)')
print('Scope: static copies; narrow frontmatter checks, hashes and text equality only. No official validator, behavioral consumer or operational action.')
