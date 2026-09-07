#!/usr/bin/env python3.12
"""Additional unchanged-package CLI checks; use only fresh cases."""
import json
import probe


def main():
    results = {}
    for c in ('R17', 'R63'):
        observations = {}
        s, l = probe.new_case(c + '-retained-rejection')
        first, rc = probe.wrap(c, s, l, 'reserve', c + ':retained-rejection:first', key='rejected', seats=7)
        other, other_rc = probe.wrap(c, s, l, 'reserve', c + ':retained-rejection:other', key='other', seats=2)
        replay, replay_rc = probe.wrap(c, s, l, 'reserve', c + ':retained-rejection:replay', key='rejected', seats=7)
        observations['retained-rejection'] = {'first': [first, rc], 'other': [other, other_rc],
                                             'replay': [replay, replay_rc],
                                             'final': probe.inspect_case(s, l, ['rejected', 'other'], c + ':retained-rejection:final')}
        s, l = probe.new_case(c + '-same-key-recover-race', initialized=False)
        probe.wrap(c, s, l, 'reserve', c + ':same-key-recover-race:create-ledger', key='continue')
        probe.raw(s, ['init', '--fixture', probe.FIXTURE], c + ':same-key-recover-race:init')
        calls = [(probe.wrapper_argv(c, s, l, 'recover', key='continue'), c + ':same-key-recover-race:' + str(i))
                 for i in range(2)]
        observations['same-key-recover-race'] = {'calls': probe.parallel_calls(calls),
                                                'final': probe.inspect_case(s, l, ['continue'], c + ':same-key-recover-race:final')}
        results[c] = observations
    print(json.dumps({'summary': results, 'exact_calls': probe.LOG}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
