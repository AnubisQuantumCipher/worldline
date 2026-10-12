"""Lossless source representation; decoding does not establish source authority."""
from . import resource_scoped_run_ledger as S
from .root_worker_codec import raw_archive, raw_restore_archive
from .protected_startup import require

SCHEMA = 'worldline.scoped-source-image-v1'


def source_record(source):
    """Retain the entire actual source, including byte-keyed physical evidence."""
    require(type(source) is dict, 'SCOPED_SOURCE_COMPLETE_DICTIONARY_REQUIRED')
    return S.record({'schema': SCHEMA, 'image': raw_archive(source)})


def source_restore(encoded):
    """Read new declared images and every retained original scoped source."""
    source = S.restore(encoded)
    if type(source) is dict and source.get('schema') == SCHEMA:
        require(set(source) == {'schema', 'image'} and type(source['image']) is bytes,
                'SCOPED_SOURCE_IMAGE_EXACT_GRAMMAR_REQUIRED')
        restored = raw_restore_archive(source['image'])
        require(type(restored) is dict and raw_archive(restored) == source['image'],
                'SCOPED_SOURCE_IMAGE_COMPLETE_CANONICAL_DICTIONARY_REQUIRED')
        return restored
    return source
