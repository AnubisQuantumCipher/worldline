"""Stable native custody-v2 ABI codes, never caller-created authority flags."""
from .errors import CoreUnavailable
_REFUSALS = ('InputMalformed','GenesisCorrespondence','ArchiveChainRefused','StoredRowsDiffer',
    'OwnerRosterRefused','SchemaRefused','ForeignKeyRefused','WrongGeneration','WrongActor',
    'IllegalRootTransition','IllegalRequestTransition','IllegalDescriptorTransition','CrossCondition',
    'AlternativeTaken','EvidenceMissing','JoinNotReady','SubjectUnknown','BarrierSubjectsOpen',
    'CASStale','AmbiguousHistory')
_LOAD = ('FrontStartup','RecoverRetained','RetainUnknown') + _REFUSALS
_MUTATION = ('ReadyApply','ReplayUnchanged','RetainUnknown') + _REFUSALS

def name(status, *, mutation=False):
    values = _MUTATION if mutation else _LOAD
    if type(status) is not int or not 0 <= status < len(values):
        raise CoreUnavailable('custody-v2 native ABI unknown status code')
    return values[status]
