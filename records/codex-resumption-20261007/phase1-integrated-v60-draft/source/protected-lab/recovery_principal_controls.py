"""Actual protected-lab control entry points, unrun and not installed.

These controls require the real principal, its native use-reservation successor,
actual kernel mapping custody, protected store/peer and authorized disposable lab.
A caller-supplied fake principal, fixture verdict or unsigned packet cannot pass.
"""
from recovery_principal import ProtectedRecoveryPrincipal
from intent_gate import require

def accepted_settlement(principal,connection,transaction_id):
    require(type(principal) is ProtectedRecoveryPrincipal,'CONTROL_ACTUAL_PRINCIPAL_REQUIRED')
    issued=principal.issue(connection,transaction_id)
    operation=issued['capture']['pending']['operation_id']
    settled=principal.claim(connection,operation)
    require(settled['state']=='SETTLED','CONTROL_ACCEPTED_SETTLEMENT_REQUIRED')
    require(principal.recover(connection,operation)==settled,'CONTROL_SAME_OPERATION_REPLAY_REQUIRED')
    return settled

def revoked_after_effect_settlement(principal,connection,operation):
    # Fixture must establish/revoke through the real protected issuer after the
    # authenticated effect and before settlement, never by editing packet facts.
    require(type(principal) is ProtectedRecoveryPrincipal,'CONTROL_ACTUAL_PRINCIPAL_REQUIRED')
    before=principal.journal.latest[operation]
    require(before['state'] in ('EFFECT_INTENT','EFFECT_OBSERVED'),'CONTROL_EFFECT_WINDOW_REQUIRED')
    capability=before['capture']['pending']['capability']
    current=principal.gate.issuer.check(capability['capability_id'],capability['request'],
        capability['target_world_id'],principal.gate.issuer.head()['event_head'])
    require(current['kind']!='ELIGIBLE_WORLDLINE','CONTROL_FRESH_REVOCATION_REQUIRED')
    settled=principal.recover(connection,operation)
    require(settled['state']=='SETTLED','CONTROL_REVOCATION_MUST_NOT_ERASE_EFFECT')
    recorded=principal.gate.issuer.store.recorded_use(operation)
    require(recorded is not None and recorded['transaction_id']==before['capture']['record']['transactionId'],
            'CONTROL_EXACT_RETAINED_USE_REQUIRED')
    return settled

def lost_abort_close_acknowledgement(principal,connection,operation):
    """Real fixture kills after durable Gate abort close, before principal ACK.

    The fixture must produce this window through the protected service. It may
    not edit journals or substitute packet verdicts. This entrypoint only reads
    the resulting real state and exercises same-operation recovery.
    """
    from worldline.recovery_observation import archive
    require(type(principal) is ProtectedRecoveryPrincipal,'CONTROL_ACTUAL_PRINCIPAL_REQUIRED')
    before=principal.journal.latest[operation]
    require(before['state'] in ('ISSUED','EFFECT_INTENT') and principal.gate.journal['pending'] is None,
            'CONTROL_ACTUAL_ABORT_CLOSE_ACK_WINDOW_REQUIRED')
    gate_before=archive(principal.gate.journal);uses_before=archive(principal.uses.events)
    aborted=principal.recover(connection,operation)
    require(aborted['state']=='ABORTED','CONTROL_ABORT_RESTART_MUST_COMPLETE')
    require(archive(principal.gate.journal)==gate_before and archive(principal.uses.events)==uses_before,
            'CONTROL_CLOSED_ABORT_MUST_NOT_RELEASE_AGAIN')
    require(principal.gate.issuer.store.recorded_use(operation) is None,'CONTROL_ABORT_MUST_NOT_CHARGE_USE')
    require(principal.recover(connection,operation)==aborted,'CONTROL_DIRECT_ABORT_REPLAY_REQUIRED')
    diagnosis=principal.restart()
    require(diagnosis['operations'][operation]=='ABORTED','CONTROL_STARTUP_ABORT_REPLAY_REQUIRED')
    return aborted


def retained_reservation_consumption(principal,connection,operation):
    """Actual authenticated effect then fresh revocation/policy denial fixture."""
    from worldline.recovery_observation import archive
    require(type(principal) is ProtectedRecoveryPrincipal,'CONTROL_ACTUAL_PRINCIPAL_REQUIRED')
    row=principal.journal.latest[operation]
    require(principal.uses.rows[operation]['state']=='RESERVED','CONTROL_REAL_HELD_USE_REQUIRED')
    bound=archive(principal.uses.rows[operation]['bound'])
    settled=revoked_after_effect_settlement(principal,connection,operation)
    require(principal.uses.rows[operation]['state']=='CONSUMED' and
            archive(principal.uses.rows[operation]['bound'])==bound,'CONTROL_SAME_USE_CONSUMPTION_REQUIRED')
    events=archive(principal.uses.events)
    require(principal.recover(connection,operation)==settled and archive(principal.uses.events)==events,
            'CONTROL_SETTLEMENT_REPLAY_MUST_NOT_CHARGE_ANOTHER_USE')
    return settled


def missing_journal_during_live_custody(principal,connection,operation):
    """A real disposable-lab fault removes a protected journal after issue/claim.

    This control never deletes protected files itself. The outside authorized
    crash laboratory selects the physical fault and retains its fault receipt.
    """
    import os
    from intent_gate import Refusal
    require(type(principal) is ProtectedRecoveryPrincipal,'CONTROL_ACTUAL_PRINCIPAL_REQUIRED')
    row=principal.journal.latest[operation]
    require(row['state'] in ('ISSUED','EFFECT_INTENT') and not os.path.lexists(principal.journal.path),
            'CONTROL_ACTUAL_CUSTODY_DELETION_REQUIRED')
    try:principal.journal.append(row,'REPLAY','FAULT_CONTROL')
    except Refusal as exc:
        require(str(exc)=='RECOVERY_PRIOR_JOURNAL_MISSING','CONTROL_EXACT_DELETION_REFUSAL_REQUIRED')
    else:raise AssertionError('missing protected journal was recreated')
    require(not os.path.lexists(principal.journal.path),'CONTROL_DELETED_JOURNAL_MUST_STAY_MISSING')
