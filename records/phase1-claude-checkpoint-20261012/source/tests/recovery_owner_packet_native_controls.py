"""Actual retained owner-packet controls against the exact selected library.

Inputs are original accepted protected-producer archives, never constructed
row-only substitutes. No effects, provisioning or authority issuance occurs.
"""
from dataclasses import replace
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from worldline.core import Core
from worldline.recovery_observation import archive, restore_archive, _native_packet
from worldline.errors import WorldlineError


def check_owner_packets(core, packets, *, syntax_facts=None):
    modes = set()
    exercised = []

    def refused(value, label):
        try:
            reason = _native_packet(archive(value), core=core, syntax_facts=syntax_facts)
        except WorldlineError as error:
            exercised.append((label, error.code))
        else:
            assert reason != 'AUTHORIZED', label
            exercised.append((label, reason))

    for raw in packets:
        packet = restore_archive(raw)
        owner = packet['owner']
        mode = owner.mode
        assert mode in ('RETRY_EVALUATION', 'ADOPT_REQUIREMENT', 'CHECKPOINT_EQUAL')
        assert _native_packet(raw, core=core, syntax_facts=syntax_facts) == 'AUTHORIZED', mode
        modes.add(mode)
        exercised.append((mode + ':original', 'AUTHORIZED'))

        def changed(label, **fields):
            refused(dict(packet, owner=replace(owner, **fields)), mode + ':' + label)

        if mode != 'CHECKPOINT_EQUAL':
            changed('world', world=replace(owner.world, instance_id=owner.world.instance_id + ':changed'))
            changed('before-missing', before_material=None)
            changed('requirement', requirement='changed-owner-requirement')
            for field in ('peer', 'owner', 'trusted_issuer', 'subject', 'content',
                          'transaction', 'current_requirement', 'resulting_requirement'):
                changed('request-' + field,
                        request=replace(owner.request, **{field: 'changed-owner-value'}))
            changed('request-epoch', request=replace(owner.request,
                    current_epoch=owner.request.current_epoch + 1))
            for field in ('subject', 'content', 'transaction'):
                changed('scope-' + field, scope=replace(owner.scope, **{field: 'changed-owner-scope'}))

        if mode == 'RETRY_EVALUATION':
            changed('after-missing', after_material=None)
            changed('request-missing', request=None)
            for field in ('before_material', 'after_material'):
                material = getattr(owner, field)
                journal, current, rows, streams = material.terminal
                assert current is not None and rows, (mode, field)
                stale = (current[0], current[1] + b':changed')
                changed(field + '-stale-cursor', **{field: replace(material,
                        terminal=(journal, stale, rows, streams))})
                changed(field + '-missing-row', **{field: replace(material,
                        terminal=(journal, current, rows[:-1], streams))})
            changed('before-after-exchanged', before_material=owner.after_material,
                    after_material=owner.before_material)
            changed('current-epoch', current_epoch=owner.current_epoch + 1)
            changed('current-epoch-absent', current_epoch=None)
            changed('prepared-run', prepared=dict(owner.prepared, run=owner.prepared['run'] + ':changed'))
            changed('prepared-epoch', prepared=dict(owner.prepared, epoch=owner.prepared['epoch'] + 1))
            changed('receipt-missing', receipt=None)
            for field in ('issued_event', 'reserved_event', 'consumed_event',
                          'consumed_issue', 'consumed_reservation'):
                changed('receipt-' + field, receipt=replace(owner.receipt, **{field: None}))
            for field in ('grant', 'use_id', 'issuer', 'principal', 'subject', 'content',
                          'transaction', 'current_requirement', 'expected_requirement',
                          'reason', 'issued_grant', 'reserved_grant', 'reserved_use'):
                consumed = replace(owner.receipt.consumed, **{field: 'changed-consumed-value'})
                changed('consumed-' + field, receipt=replace(owner.receipt, consumed=consumed))
            for state in ('ISSUED', 'RESERVED', 'REVOKED'):
                changed('consumed-' + state, receipt=replace(owner.receipt,
                        consumed=replace(owner.receipt.consumed, state=state)))
            for field in ('current_head', 'attempt'):
                cursor = getattr(owner.request, field)
                changed('request-' + field, request=replace(owner.request,
                        **{field: replace(cursor, run=cursor.run + ':changed')}))
            # Carried roster flags are not authority. Genuine raw native PASS
            # material still admits after the saved Boolean is removed.
            carried = dict(packet, values=replace(packet['values'], roster_complete=False))
            assert _native_packet(archive(carried), core=core) == 'AUTHORIZED'
            exercised.append((mode + ':native-not-carried-roster', 'AUTHORIZED'))
        else:
            changed('resulting-absent', resulting=None)
            resulting = bytes([owner.resulting[0] ^ 1]) + owner.resulting[1:]
            changed('resulting-changed', resulting=resulting)

    assert modes == {'RETRY_EVALUATION', 'ADOPT_REQUIREMENT', 'CHECKPOINT_EQUAL'}, modes
    return tuple(exercised)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--packet', type=Path, action='append', required=True,
                        help='Original accepted protected owner archive; include all three modes')
    parser.add_argument('--syntax-facts', type=Path,
                        help='Actual independently acquired complete capsule arena for these packets')
    args = parser.parse_args()
    core = Core(args.library)
    packets = tuple(path.read_bytes() for path in args.packet)
    facts = None if args.syntax_facts is None else args.syntax_facts.read_bytes()
    exercised = check_owner_packets(core, packets, syntax_facts=facts)
    print(json.dumps({'library': str(core.library_path),
                      'packets': [str(path.resolve()) for path in args.packet],
                      'controls': exercised}, ensure_ascii=True, sort_keys=True))


if __name__ == '__main__':
    main()
