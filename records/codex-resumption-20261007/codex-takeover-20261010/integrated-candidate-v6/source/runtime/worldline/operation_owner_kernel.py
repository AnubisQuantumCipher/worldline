"""Original operation/chain decisions under the actual selected owner mapping.

This wrapper adds no policy or verdict. Every native record, ownership copy,
layout check and original semantic decision stays in the preserved callers.
"""
from .errors import CoreUnavailable
from .protected_startup import require
from .retained_chain_kernel import _mapped
from .operation_authority_kernel import OperationAuthorityKernel
from .chain_authority import replay_chain

OPERATION_SYMBOLS = ('wl_operation_authority_version_v1',
                     'wl_operation_authority_layout_v1', 'wl_operation_authority_decide_v1')
CHAIN_SYMBOLS = ('wl_chain_authority_version_v1', 'wl_chain_authority_layout_v1',
                 'wl_chain_authority_replay_v1')
RECOVERY_SYMBOLS = ('wl_recovery_authorization_version_v3',
                    'wl_recovery_authorization_layout_v3', 'wl_recovery_authorization_decide_v3')
# Existing principal.intact requires this independent boundary; no new authority.
CANONICAL_SYMBOLS = ('wl_canonical_operation_version_v1',
                    'wl_canonical_operation_layout_v1', 'wl_canonical_operation_decide_v1')
SYMBOLS = OPERATION_SYMBOLS + CHAIN_SYMBOLS + RECOVERY_SYMBOLS + CANONICAL_SYMBOLS


RESOURCE_SYMBOLS = ('wl_resource_run_ledger_version_v1',
                    'wl_resource_run_ledger_layout_v1', 'wl_resource_run_ledger_check_v1')


def _owner_mapping(principal, extra_symbols=()):
    from .protected_operations import CanonicalOperationPrincipal
    require(type(principal) is CanonicalOperationPrincipal,
            'OPERATION_ACTUAL_OWNER_PRINCIPAL_REQUIRED')
    # Resolve without calling ANY foreign query. Only missing-export lookup is
    # translated; no broad exception handler masks unrelated ownership failures.
    try:
        functions = tuple(getattr(principal.core._lib, name) for name in SYMBOLS + extra_symbols)
    except AttributeError as exc:
        raise CoreUnavailable('complete protected operation/chain boundary unavailable') from exc
    principal.intact()
    # The real startup lease owns the executed source envelope and native role.
    # Reuse exact selected-file/map_files/address custody, not name-only lookup.
    _mapped(principal.lease, principal.core, functions)


def initialize_owner_kernel(principal):
    _owner_mapping(principal)
    kernel = OperationAuthorityKernel(principal.core)
    _owner_mapping(principal)
    return kernel


def observe_operation(principal, snapshot, command):
    _owner_mapping(principal)
    require(type(principal.kernel) is OperationAuthorityKernel and
            principal.kernel.core is principal.core, 'OPERATION_NATIVE_KERNEL_SPLIT')
    result = principal.kernel.observe(snapshot, command)
    _owner_mapping(principal)
    return result


def replay_owner_chain(principal, rows, anchors):
    _owner_mapping(principal)
    result = replay_chain(rows, anchors, core=principal.core)
    _owner_mapping(principal)
    return result


def observe_canonical(principal, snapshot, state, rows, observed, request,
                      peer_uid, collapse_values):
    """Actual protected pre-effect conjunction; no Python decision substitute."""
    from .canonical_operation_kernel import CanonicalOperationKernel
    _owner_mapping(principal, RESOURCE_SYMBOLS)
    kernel = CanonicalOperationKernel(principal.core)
    _owner_mapping(principal, RESOURCE_SYMBOLS)
    result = kernel.observe(snapshot, state, rows, observed, request, peer_uid, collapse_values)
    _owner_mapping(principal, RESOURCE_SYMBOLS)
    return result
