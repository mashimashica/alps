from pathlib import Path
import hashlib
import json
import re
import yaml

ROOT = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP05')
OUT = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/focused-FP05-primary/check-results.json')
LABELS = {'R17': 'release-checkout-service', 'R28': 'checkout-release', 'R44': 'release-checkout-service', 'R63': 'checkout-release'}
tool_bytes = (ROOT / 'original-creator-input/release_tool.py').read_bytes()
result = {'scope': 'Read-only packet consistency, JSON/YAML parsing, and final-state delta checks; no simulator invocation or historical trace reconstruction.', 'packages': [], 'applications': []}
for label, name in LABELS.items():
    package = ROOT / label / 'package' / name
    files = {p.relative_to(package): p.read_bytes() for p in package.rglob('*') if p.is_file()}
    skill = files[Path('SKILL.md')].decode()
    frontmatter = yaml.safe_load(skill.split('---', 2)[1])
    interface = yaml.safe_load(files[Path('agents/openai.yaml')])['interface']
    assert frontmatter['name'] == name and isinstance(frontmatter['description'], str) and frontmatter['description']
    assert all(isinstance(interface[k], str) and interface[k] for k in ('display_name', 'short_description', 'default_prompt'))
    assert '$' + name in interface['default_prompt']
    links = []
    for rel, content in files.items():
        if rel.suffix != '.md':
            continue
        for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', content.decode()):
            local = target.split('#', 1)[0]
            assert '://' not in local
            target_path = (package / rel.parent / local).resolve()
            assert target_path.is_relative_to(package.resolve()) and target_path.is_file()
            links.append(target)
    result['packages'].append({'label': label, 'files_read': [str(p) for p in sorted(files)], 'yaml_parse_and_identity': 'passed', 'relative_links_exist': links})
    for case in ('ordinary', 'challenging'):
        app = ROOT / label / case
        observed = app / 'observed-final-skill' / name
        observed_files = {p.relative_to(observed): p.read_bytes() for p in observed.rglob('*') if p.is_file()}
        assert observed_files == files
        assert (app / 'final-input-state/release_tool.py').read_bytes() == tool_bytes
        initial_bytes = (ROOT / 'original-consumer-inputs' / case / 'input/state.json').read_bytes()
        final_bytes = (app / 'final-input-state/state.json').read_bytes()
        initial = json.loads(initial_bytes)
        final = json.loads(final_bytes)
        observations = json.loads((app / 'resource-observations.json').read_text())
        expected_request = 'dev-linden-42-apply' if case == 'ordinary' else 'dev-onyx-27-rehearsal'
        candidate = initial['candidate']
        expected = json.loads(initial_bytes)
        expected['production'] = {k: candidate[k] for k in ('id', 'digest', 'healthy', 'checkout_ok')}
        expected['requests'] = {expected_request: {'candidate': candidate['id'], 'digest': candidate['digest'], 'promoted': True}}
        expected['promotion_count'] = 1
        if case == 'challenging':
            expected.pop('timeout_once_after_promotion')
        assert final == expected
        changes = observations['changed_originals']
        assert len(changes) == 1 and changes[0]['path'] == 'input/state.json'
        assert changes[0]['initial_sha256'] == hashlib.sha256(initial_bytes).hexdigest()
        assert changes[0]['final_sha256'] == hashlib.sha256(final_bytes).hexdigest()
        assert observations['added_resources_sha256'] == {}
        result['applications'].append({'label': label, 'case': case, 'skill_bytes_match': True, 'tool_bytes_match': True, 'resource_hashes_match': True, 'only_expected_final_state_delta': True, 'qualification_sequence': final['qualification']['sequence'], 'approval_sequence': final['approval']['sequence'], 'request_ids': list(final['requests']), 'promotion_count': final['promotion_count'], 'production': final['production']})
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'packages_checked': len(result['packages']), 'applications_checked': len(result['applications']), 'snapshot_skill_files_matched': sum(len(p['files_read']) * 2 for p in result['packages']), 'simulator_copies_matched': 8, 'json_and_yaml_checks': 'passed', 'final_state_delta_checks': 'passed', 'output': str(OUT)}, indent=2))
