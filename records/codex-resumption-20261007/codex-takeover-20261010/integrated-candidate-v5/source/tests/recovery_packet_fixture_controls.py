"""Consume the actual transaction actor export, never a fabricated verdict."""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from worldline.core import Core
from worldline.errors import WorldlineError
from worldline.model import WorldState
from worldline.recovery_observation import archive, restore_archive, restore_packet, redecide_packet
from worldline.raw_completion_kernel import PreparedRawEvaluation
from worldline.finalization_kernel import PreparedFinalization


def check(packet_file, *, core, syntax_facts=None):
    raw = Path(packet_file).read_bytes()
    assert redecide_packet(raw, core=core, syntax_facts=syntax_facts) == 'AUTHORIZED'
    packet = restore_archive(raw)
    assert archive(packet) == raw
    observation = restore_packet(raw, core=core, syntax_facts=syntax_facts)
    assert observation.packet == raw
    assert observation.decide(core) == 'AUTHORIZED'
    for role in ('primary', 'staged'):
        if packet[role] is not None:
            assert type(getattr(observation, role)) in (PreparedRawEvaluation, PreparedFinalization)
    # Original top-level schema accepts insertion-order changes; this must not
    # be replaced by a packet digest/byte whitelist or a projected DTO shortcut.
    permuted = {key: packet[key] for key in reversed(tuple(packet))}
    assert redecide_packet(archive(permuted), core=core, syntax_facts=syntax_facts) == 'AUTHORIZED'
    enum_packet = dict(packet)
    enum_packet['values'] = replace(packet['values'],
                                   candidate_state=WorldState(packet['values'].candidate_state))
    assert redecide_packet(archive(enum_packet), core=core, syntax_facts=syntax_facts) == 'AUTHORIZED'
    # Complete original fields cannot be omitted merely because the collapse
    # mode does not read one of their projections.
    for missing in tuple(packet):
        changed = dict(packet)
        del changed[missing]
        try:
            redecide_packet(archive(changed), core=core, syntax_facts=syntax_facts)
        except WorldlineError:
            pass
        else:
            raise AssertionError(('missing original full packet field admitted', missing))
    return len(raw)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('packet', type=Path)
    parser.add_argument('--syntax-facts', type=Path,
                        help='actual independently acquired complete operation-archive capsule list')
    arguments = parser.parse_args()
    facts = None if arguments.syntax_facts is None else arguments.syntax_facts.read_bytes()
    print({'complete_original_packet_bytes': check(arguments.packet, core=Core.shared(),
                                                   syntax_facts=facts)})
