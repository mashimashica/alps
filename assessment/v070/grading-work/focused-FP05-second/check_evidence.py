from pathlib import Path
import hashlib
import json

root = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP05')
source = (root / 'original-creator-input/release_tool.py').read_bytes()
for label in ['R17', 'R28', 'R44', 'R63']:
    package = root / label / 'package'
    expected = {str(p.relative_to(package)): p.read_bytes() for p in package.rglob('*') if p.is_file()}
    print(label, 'package_files', ', '.join(sorted(expected)))
    for case in ['ordinary', 'challenging']:
        app = root / label / case
        observed = {str(p.relative_to(app / 'observed-final-skill')): p.read_bytes()
                    for p in (app / 'observed-final-skill').rglob('*') if p.is_file()}
        assert observed == expected, (label, case, 'package changed')
        assert (app / 'final-input-state/release_tool.py').read_bytes() == source, (label, case, 'tool changed')
        initial = json.loads((root / 'original-consumer-inputs' / case / 'input/state.json').read_text())
        final_path = app / 'final-input-state/state.json'
        final = json.loads(final_path.read_text())
        fields = [key for key in initial.keys() | final.keys() if initial.get(key) != final.get(key)]
        candidate = initial['candidate']
        request = 'dev-linden-42-apply' if case == 'ordinary' else 'dev-onyx-27-rehearsal'
        assert final['production'] == {key: candidate[key] for key in ['id', 'digest', 'healthy', 'checkout_ok']}
        assert final['promotion_count'] == 1
        assert final['qualification'] == initial['qualification'] and final['approval'] == initial['approval']
        assert final['requests'] == {request: {'candidate': candidate['id'], 'digest': candidate['digest'], 'promoted': True}}
        assert set(fields) == ({'production', 'requests', 'promotion_count'} if case == 'ordinary'
                               else {'production', 'requests', 'promotion_count', 'timeout_once_after_promotion'})
        observation = json.loads((app / 'resource-observations.json').read_text())
        assert len(observation['changed_originals']) == 1 and observation['changed_originals'][0]['path'] == 'input/state.json'
        assert hashlib.sha256(final_path.read_bytes()).hexdigest() == observation['changed_originals'][0]['final_sha256']
        print(label, case, 'observed_skill=byte-identical; tool=byte-identical; final_state=consistent; q='
              + str(final['qualification']['sequence']) + '; a=' + str(final['approval']['sequence'])
              + '; promotion_count=1; health=' + str(final['production']['healthy'])
              + '; checkout=' + str(final['production']['checkout_ok'])
              + '; changed_fields=' + ','.join(sorted(fields)))
print('All eight preserved application copies passed the read-only consistency checks.')
