"""Additive real installed-generator controls; reviewed native route only."""
import textwrap
import unittest

import test_examiner_native_guard as native_controls


GENERATOR_BOOTSTRAP = r'''
import collections, dataclasses, inspect, reprlib, typing, keyword, copy, weakref
from pathlib import Path
COLLECTIONS_PATH = '/usr/lib/python3.14/collections/__init__.py'
DATACLASSES_PATH = '/usr/lib/python3.14/dataclasses.py'
AST_PATH = '/usr/lib/python3.14/ast.py'
def generators(entry=b'value = None\n', *, bind=True):
    rows = ((COLLECTIONS_PATH, Path(COLLECTIONS_PATH).read_bytes()),
            (DATACLASSES_PATH, Path(DATACLASSES_PATH).read_bytes()),
            (AST_PATH, Path(AST_PATH).read_bytes()),
            ('/verifier/entry.py', entry))
    guard.configure('native-generator-control', rows)
    modules = {}
    for name, path in (('collections', COLLECTIONS_PATH), ('dataclasses', DATACLASSES_PATH),
                       ('ast', AST_PATH)):
        module = types.ModuleType(name)
        module.__file__ = path
        sys.modules[name] = module
        code = guard.compile_source(path)
        exec(code, module.__dict__)
        modules[name] = module
    # Cached inspect remains recorded as startup code. Its AST dependency is
    # replaced explicitly during the trusted bootstrap, before activation.
    inspect.ast = modules['ast']
    if bind:
        guard.bind_generator('collections.namedtuple', modules['collections'].namedtuple, COLLECTIONS_PATH)
        guard.bind_generator('dataclasses._FuncBuilder.add_fns_to_class',
                             modules['dataclasses']._FuncBuilder.add_fns_to_class, DATACLASSES_PATH)
        guard.bind_generator('ast.parse', modules['ast'].parse, AST_PATH)
    code = guard.compile_source('/verifier/entry.py')
    return modules['collections'], modules['dataclasses'], code
def run_entry(source):
    collection_module, dataclass_module, code = generators(source.encode('utf-8'))
    module = types.ModuleType('native_generator_target')
    module.__dict__.update(collections=collection_module, dataclasses=dataclass_module)
    sys.modules[module.__name__] = module
    guard.activate()
    exec(code, module.__dict__)
    return module
'''


class NativeGeneratorControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native_controls.NativeGuardControls.setUpClass.__func__(cls)

    def child(self, body):
        return native_controls.NativeGuardControls.child(
            self, GENERATOR_BOOTSTRAP + textwrap.dedent(body))

    def test_empty_single_multiple_namedtuple_and_defaults(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            guard.activate()
            Empty = collections.namedtuple('Empty', ())
            One = collections.namedtuple('One', 'value', defaults=('fallback',))
            Pair = collections.namedtuple('Pair', 'left right', defaults=('right-default',))
            value = Pair('left-value')
            emit({'empty': list(Empty()), 'one': list(One()), 'pair': list(value),
                  'replace': value._replace(right='changed')._asdict(),
                  'registered': guard.contains(Pair.__new__.__code__), 'state': guard.status()})
        ''')
        self.assertEqual(result['empty'], [])
        self.assertEqual(result['one'], ['fallback'])
        self.assertEqual(result['pair'], ['left-value', 'right-default'])
        self.assertEqual(result['replace'], {'left': 'left-value', 'right': 'changed'})
        self.assertTrue(result['registered'])
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['confinementEstablished'])

    def test_namedtuple_unicode_and_renamed_fields(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            guard.activate()
            Value = collections.namedtuple('Café', ['café', 'class', 'café', '_hidden'], rename=True)
            value = Value('unicode', 'keyword', 'duplicate', 'leading')
            emit({'fields': Value._fields, 'value': value._asdict(), 'state': guard.status()})
        ''')
        self.assertEqual(result['fields'], ['café', '_1', '_2', '_3'])
        self.assertEqual(result['value'], {'café': 'unicode', '_1': 'keyword', '_2': 'duplicate', '_3': 'leading'})
        self.assertFalse(result['state']['violated'])

    def test_namedtuple_duplicate_normalization_preserves_syntax_error(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            guard.activate()
            try:
                collections.namedtuple('Normalized', ['K', '\u212a'])
            except SyntaxError as error:
                emit({'exception': type(error).__name__, 'state': guard.status()})
        ''')
        self.assertEqual(result['exception'], 'SyntaxError')
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_dataclass_standard_and_independent_field_subsets(self):
        result = self.child(r'''
            target = run_entry("""
            @dataclasses.dataclass(order=True, unsafe_hash=True)
            class Value:
                visible: str
                quiet: str = dataclasses.field(repr=False, compare=False, hash=False)
                compared: str = dataclasses.field(repr=False, hash=False)
            left = Value('a', 'first', 'b')
            right = Value('a', 'second', 'c')
            answer = {'repr': repr(left), 'less': left < right, 'same': left == Value('a', 'other', 'b'),
                      'hash_same': hash(left) == hash(right)}
            """)
            emit({'answer': target.answer, 'registered': guard.contains(target.Value.__init__.__code__),
                  'state': guard.status()})
        ''')
        self.assertEqual(result['answer'], {'repr': "Value(visible='a')", 'less': True, 'same': True, 'hash_same': True})
        self.assertTrue(result['registered'])
        self.assertFalse(result['state']['violated'])

    def test_dataclass_frozen_slots_and_original_exception(self):
        result = self.child(r'''
            target = run_entry("""
            @dataclasses.dataclass(frozen=True, slots=True, order=True)
            class Value:
                café: str
                tail: str = 'tail'
            value = Value('coffee')
            try:
                value.café = 'changed'
            except dataclasses.FrozenInstanceError as error:
                failure = type(error).__name__
            answer = {'value': value.café, 'tail': value.tail, 'failure': failure,
                      'hash_present': isinstance(hash(value), int), 'has_dict': hasattr(value, '__dict__')}
            """)
            emit({'answer': target.answer, 'state': guard.status()})
        ''')
        self.assertEqual(result['answer'], {'value': 'coffee', 'tail': 'tail', 'failure': 'FrozenInstanceError',
                                          'hash_present': True, 'has_dict': False})
        self.assertFalse(result['state']['violated'])

    def test_dataclass_keyword_only_initvar_postinit_and_self_field(self):
        result = self.child(r'''
            target = run_entry("""
            @dataclasses.dataclass
            class Value:
                self: str
                setup: dataclasses.InitVar[str]
                _: dataclasses.KW_ONLY
                tail: str = 'default'
                def __post_init__(self, setup):
                    self.tail = setup + ':' + self.tail
            value = Value('field-self', 'initvar', tail='keyword')
            answer = {'self': value.self, 'tail': value.tail}
            """)
            emit({'answer': target.answer, 'state': guard.status()})
        ''')
        self.assertEqual(result['answer'], {'self': 'field-self', 'tail': 'initvar:keyword'})
        self.assertFalse(result['state']['violated'])

    def test_dataclass_init_false_fields_factories_and_slots(self):
        result = self.child(r'''
            target = run_entry("""
            calls = []
            def factory():
                calls.append('called')
                return ['factory']
            @dataclasses.dataclass(slots=True)
            class Value:
                supplied: str
                default: str = dataclasses.field(default='stored', init=False)
                generated: list = dataclasses.field(default_factory=factory, init=False)
                optional: list = dataclasses.field(default_factory=factory)
            value = Value('provided')
            answer = {'supplied': value.supplied, 'default': value.default,
                      'generated': value.generated, 'optional': value.optional, 'calls': calls}
            """)
            emit({'answer': target.answer, 'state': guard.status()})
        ''')
        self.assertEqual(result['answer'], {'supplied': 'provided', 'default': 'stored',
            'generated': ['factory'], 'optional': ['factory'], 'calls': ['called', 'called']})
        self.assertFalse(result['state']['violated'])

    def test_dataclass_inheritance_empty_class_and_disabled_methods(self):
        result = self.child(r'''
            target = run_entry("""
            @dataclasses.dataclass
            class Base:
                first: str
            @dataclasses.dataclass
            class Child(Base):
                second: str = 'second'
            @dataclasses.dataclass
            class Empty:
                pass
            @dataclasses.dataclass(init=False, repr=False, eq=False)
            class Disabled:
                pass
            value = Child('first')
            answer = {'child': dataclasses.asdict(value), 'empty': repr(Empty()),
                      'disabled': isinstance(Disabled(), Disabled)}
            """)
            emit({'answer': target.answer, 'state': guard.status()})
        ''')
        self.assertEqual(result['answer'], {'child': {'first': 'first', 'second': 'second'},
                                         'empty': 'Empty()', 'disabled': True})
        self.assertFalse(result['state']['violated'])

    def test_dataclass_empty_builder_and_target_builtins_insertion(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            target_globals = {'marker': object()}
            class Empty:
                pass
            builder = dataclasses._FuncBuilder(target_globals)
            guard.activate()
            builder.add_fns_to_class(Empty)
            emit({'inserted': '__builtins__' in target_globals, 'state': guard.status()})
        ''')
        self.assertTrue(result['inserted'])
        self.assertFalse(result['state']['violated'])

    def test_dataclass_original_user_factory_exception_is_preserved(self):
        result = self.child(r'''
            target = run_entry("""
            class Expected(Exception):
                pass
            def factory():
                raise Expected('original factory')
            @dataclasses.dataclass
            class Value:
                content: str = dataclasses.field(default_factory=factory)
            try:
                Value()
            except Expected as error:
                answer = str(error)
            """)
            emit({'answer': target.answer, 'state': guard.status()})
        ''')
        self.assertEqual(result['answer'], 'original factory')
        self.assertFalse(result['state']['violated'])

    def test_original_generated_exec_audit_follows_registration(self):
        result = self.child(r'''
            audited = []
            def observe(event, args):
                if event == 'exec' and args[0].co_filename == '<string>':
                    audited.append(guard.contains(args[0]))
            sys.addaudithook(observe)
            collections, dataclasses, code = generators()
            guard.activate()
            Value = collections.namedtuple('Value', 'text')
            emit({'audited': audited, 'value': Value('content').text, 'state': guard.status()})
        ''')
        self.assertEqual(result['audited'], [True])
        self.assertEqual(result['value'], 'content')
        self.assertFalse(result['state']['violated'])

    def test_missing_native_route_does_not_gain_compile_authority(self):
        result = self.child(r'''
            collections, dataclasses, code = generators(bind=False)
            guard.activate()
            try:
                collections.namedtuple('Value', 'text')
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_direct_route_call_has_wrong_immediate_origin(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            callback = collections.__dict__['eval']
            namespace = {'_tuple_new': tuple.__new__, '__builtins__': {}, '__name__': 'namedtuple_Value'}
            guard.activate()
            try:
                callback('lambda _cls, text,: _tuple_new(_cls, (text,))', namespace)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_bound_route_cannot_be_replaced(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            try:
                guard.bind_generator('collections.namedtuple', collections.namedtuple, COLLECTIONS_PATH)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])

    def test_source_selector_must_match_owned_generator(self):
        result = self.child(r'''
            collections, dataclasses, code = generators(bind=False)
            try:
                guard.bind_generator('collections.namedtuple', collections.namedtuple, DATACLASSES_PATH)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_unregistered_cached_generator_cannot_be_bound(self):
        result = self.child(r'''
            old_function = collections.namedtuple
            collections, dataclasses, code = generators(bind=False)
            try:
                guard.bind_generator('collections.namedtuple', old_function, COLLECTIONS_PATH)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])

    def test_dataclass_unknown_method_template_refuses(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('unrecognized', ['self'], ['  return None'])
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit({'state': guard.status(), 'added': hasattr(Value, 'unrecognized')})
        ''')
        self.assertFalse(result['added'])
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['generatedCompilations'], 0)

    def test_dataclass_complete_template_rejects_extra_line(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('__init__', ['self'], ['  pass', '  pass'])
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)
        self.assertFalse(result['permitActive'])

    def test_dataclass_method_order_must_match_installed_template(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('__hash__', ['self'], ['  return hash(())'])
            builder.add_fn('__init__', ['self'], ['  pass'])
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_dataclass_fixed_object_operand_is_not_just_a_key(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('__init__', ['self'], ['  pass'],
                           locals={'__dataclass_builtins_object__': object()})
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_dataclass_fixed_factory_marker_identity(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('__init__', ['self'], ['  pass'],
                           locals={'__dataclass_HAS_DEFAULT_FACTORY__': object()})
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_dataclass_fixed_decorator_refuses_without_calling_substitute(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            calls = []
            def substitute(*args, **kwargs):
                calls.append('called')
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('__repr__', ['self'], ['  return f"{self.__class__.__qualname__}()"'],
                           locals={'__dataclasses_recursive_repr': substitute},
                           decorator='@__dataclasses_recursive_repr()')
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit({'calls': calls, 'state': guard.status()})
        ''')
        self.assertEqual(result['calls'], [])
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['generatedCompilations'], 0)

    def test_dataclass_fixed_frozen_exception_identity(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            dataclasses._frozen_set_del_attr(Value, [], builder)
            builder.locals['FrozenInstanceError'] = ValueError
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit(guard.status())
        ''')
        self.assertTrue(result['violated'])
        self.assertEqual(result['generatedCompilations'], 0)

    def test_original_audit_refusal_has_registered_code_and_clean_permit(self):
        result = self.child(r'''
            seen = []
            def observe(event, args):
                if event == 'exec' and args[0].co_filename == '<string>':
                    seen.append(guard.contains(args[0]))
                    raise RuntimeError('retained audit refusal')
            sys.addaudithook(observe)
            collections, dataclasses, code = generators()
            guard.activate()
            try:
                collections.namedtuple('Value', 'field')
            except RuntimeError as error:
                emit({'error': str(error), 'seen': seen, 'state': guard.status()})
        ''')
        self.assertEqual(result['error'], 'retained audit refusal')
        self.assertEqual(result['seen'], [True])
        self.assertFalse(result['state']['permitActive'])

    def test_binding_rejects_nonstring_authority_keys_without_conversion(self):
        result = self.child(r'''
            calls = []
            class Key:
                def __str__(self):
                    calls.append('str')
                    raise AssertionError('authority key conversion')
                def __eq__(self, other):
                    calls.append('eq')
                    raise AssertionError('authority key equality')
                __hash__ = object.__hash__
            collections, dataclasses, code = generators(bind=False)
            collections.__dict__[Key()] = 'unrelated'
            try:
                guard.bind_generator('collections.namedtuple', collections.namedtuple, COLLECTIONS_PATH)
            except PermissionError:
                emit({'calls': calls, 'state': guard.status()})
        ''')
        self.assertEqual(result['calls'], [])
        self.assertTrue(result['state']['violated'])

    def test_closure_subclass_key_refuses_without_python_key_callbacks(self):
        result = self.child(r'''
            calls = []
            class Key(str):
                def __str__(self):
                    calls.append('str')
                    raise AssertionError('closure key conversion')
                def __eq__(self, other):
                    calls.append('eq')
                    raise AssertionError('closure key equality')
                __hash__ = str.__hash__
            collections, dataclasses, code = generators()
            class Value:
                pass
            builder = dataclasses._FuncBuilder({})
            builder.add_fn('__init__', ['self'], ['  pass'])
            builder.locals = {Key('__dataclass_builtins_object__'): object}
            guard.activate()
            try:
                builder.add_fns_to_class(Value)
            except PermissionError:
                emit({'calls': calls, 'state': guard.status()})
        ''')
        self.assertEqual(result['calls'], [])
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['generatedCompilations'], 0)

    def test_unrelated_target_global_keys_and_values_remain_supported(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            key, value = object(), object()
            target_globals = {key: value}
            class Value:
                pass
            builder = dataclasses._FuncBuilder(target_globals)
            guard.activate()
            builder.add_fns_to_class(Value)
            emit({'preserved': target_globals[key] is value,
                  'builtins': '__builtins__' in target_globals, 'state': guard.status()})
        ''')
        self.assertTrue(result['preserved'])
        self.assertTrue(result['builtins'])
        self.assertFalse(result['state']['violated'])


    def test_ast_signature_parsing_preserves_builtin_signatures(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            guard.activate()
            emit({'object': str(inspect.signature(object)),
                  'length': list(inspect.signature(len).parameters),
                  'dict_default': inspect.signature(dict.get).parameters['default'].default,
                  'state': guard.status()})
        ''')
        self.assertEqual(result['object'], '()')
        self.assertEqual(result['length'], ['obj'])
        self.assertIsNone(result['dict_default'])
        self.assertFalse(result['state']['violated'])

    def test_ast_modes_and_text_encodings_remain_data(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            before = guard.status()['registeredCodeCount']
            text = ast.parse("# coding: ascii\nvalue = 'café'\n")
            encoded = ast.parse(b"# coding: latin-1\nvalue = 'caf\xe9'\n")
            expression = ast.parse('left + right', mode='eval')
            single = ast.parse("value = 'single'", mode='single')
            function = ast.parse('(int, str) -> bool', mode='func_type')
            emit({'values': [text.body[0].value.value, encoded.body[0].value.value],
                  'modes': [type(tree).__name__ for tree in (expression, single, function)],
                  'registered': [guard.contains(tree) for tree in (text, encoded, expression, single, function)],
                  'registry_unchanged': before == guard.status()['registeredCodeCount'],
                  'state': guard.status()})
        ''')
        self.assertEqual(result['values'], ['café', 'café'])
        self.assertEqual(result['modes'], ['Expression', 'Interactive', 'FunctionType'])
        self.assertEqual(result['registered'], [False, False, False, False, False])
        self.assertTrue(result['registry_unchanged'])
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_feature_version_type_comments_and_bool_optimization(self):
        result = self.child(r'''
            # Capture the actual installed parser before native configuration.
            # Optimization removes assert bytecode, not the Assert AST node.
            original_ast = inspect.ast
            expected = {
                'optimized': original_ast.dump(original_ast.parse('assert True\n', optimize=True),
                                               include_attributes=True),
                'ordinary': original_ast.dump(original_ast.parse('assert True\n', optimize=False),
                                              include_attributes=True),
            }
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            failure = None
            try:
                ast.parse("match value:\n    case _:\n        pass\n", feature_version=(3, 9))
            except SyntaxError as error:
                failure = type(error).__name__
            modern = ast.parse("match value:\n    case _:\n        pass\n", feature_version=(3, 10))
            comment = ast.parse("value = 1 # type: int\n", type_comments=True)
            optimized = ast.parse('assert True\n', optimize=True)
            ordinary = ast.parse('assert True\n', optimize=False)
            legacy = ast.parse('pass', feature_version=False)
            emit({'failure': failure, 'modern': type(modern.body[0]).__name__,
                  'comment': comment.body[0].type_comment,
                  'optimized': type(optimized.body[0]).__name__,
                  'expected': expected,
                  'actual': {'optimized': ast.dump(optimized, include_attributes=True),
                             'ordinary': ast.dump(ordinary, include_attributes=True)},
                  'ordinary': type(ordinary.body[0]).__name__,
                  'legacy': type(legacy.body[0]).__name__, 'state': guard.status()})
        ''')
        self.assertEqual(result['failure'], 'SyntaxError')
        self.assertEqual(result['modern'], 'Match')
        self.assertEqual(result['comment'], 'int')
        self.assertEqual(result['actual'], result['expected'])
        self.assertEqual(result['optimized'], 'Assert')
        self.assertEqual(result['ordinary'], 'Assert')
        self.assertEqual(result['legacy'], 'Pass')
        self.assertFalse(result['state']['violated'])

    def test_ast_original_data_errors_preserve_later_valid_parsing(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            failures = []
            for source, options in [
                ('if', {}), ('value = None\0', {}),
                ('pass', {'filename': 'invalid\0name'}),
                ('pass', {'mode': 'invalid'}),
                ('pass', {'optimize': -2}),
                ('pass', {'feature_version': sys.maxsize}),
            ]:
                try:
                    ast.parse(source, **options)
                except (SyntaxError, ValueError, OverflowError) as error:
                    failures.append(type(error).__name__)
            valid = ast.parse('pass', filename='surrogate-\udcff')
            emit({'failures': failures, 'valid': type(valid.body[0]).__name__,
                  'state': guard.status()})
        ''')
        self.assertEqual(result['failures'], ['SyntaxError', 'SyntaxError', 'ValueError',
                                             'ValueError', 'ValueError', 'OverflowError'])
        self.assertEqual(result['valid'], 'Pass')
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_route_requires_its_actual_parser_caller(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            try:
                ast.compile('pass', '<unknown>', 'exec', ast.PyCF_ONLY_AST,
                            _feature_version=-1, optimize=-1)
            except PermissionError:
                emit({'state': guard.status()})
        ''')
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_route_cannot_remove_only_ast_flag(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            ast.PyCF_ONLY_AST = 0
            guard.activate()
            before = guard.status()['registeredCodeCount']
            try:
                ast.parse('value = None')
            except PermissionError:
                emit({'registry_unchanged': before == guard.status()['registeredCodeCount'],
                      'state': guard.status()})
        ''')
        self.assertTrue(result['registry_unchanged'])
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_missing_route_does_not_gain_compile_authority(self):
        result = self.child(r'''
            collections, dataclasses, code = generators(bind=False)
            ast = sys.modules['ast']
            guard.activate()
            try:
                ast.parse('pass')
            except PermissionError:
                emit({'state': guard.status()})
        ''')
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_binding_is_one_shot(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            try:
                guard.bind_generator('ast.parse', ast.parse, AST_PATH)
            except PermissionError:
                emit({'state': guard.status()})
        ''')
        self.assertTrue(result['state']['violated'])

    def test_ast_binding_requires_owned_parser_code(self):
        result = self.child(r'''
            cached = sys.modules['ast'].parse
            collections, dataclasses, code = generators(bind=False)
            try:
                guard.bind_generator('ast.parse', cached, AST_PATH)
            except PermissionError:
                emit({'state': guard.status()})
        ''')
        self.assertTrue(result['state']['violated'])

    def test_ast_audit_exception_preserved_and_permit_cleared(self):
        result = self.child(r'''
            def observe(event, args):
                if event == 'compile' and args[1] == '<ast-control>':
                    raise LookupError('original parser audit refusal')
            sys.addaudithook(observe)
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            try:
                ast.parse('pass', filename='<ast-control>')
            except LookupError as error:
                emit({'error': str(error), 'state': guard.status()})
        ''')
        self.assertEqual(result['error'], 'original parser audit refusal')
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])


    def test_ast_early_data_failures_retain_attempts(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            rows = []
            for source, options in [
                ('pass', {'feature_version': sys.maxsize}),
                ('pass', {'mode': 'invalid'}),
                ('pass', {'optimize': -2}),
                ('\udcff', {}),
            ]:
                before = guard.status()['astParseAttempts']
                try:
                    ast.parse(source, **options)
                except (OverflowError, ValueError, UnicodeEncodeError) as error:
                    rows.append({'exception': type(error).__name__,
                                 'retained': guard.status()['astParseAttempts'] > before})
            parsed = ast.parse('pass', feature_version=-2)
            emit({'rows': rows, 'valid': type(parsed.body[0]).__name__, 'state': guard.status()})
        ''')
        self.assertEqual([row['exception'] for row in result['rows']],
                         ['OverflowError', 'ValueError', 'ValueError', 'UnicodeEncodeError'])
        self.assertTrue(all(row['retained'] for row in result['rows']))
        self.assertEqual(result['valid'], 'Pass')
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_audit_syntax_error_is_not_ordinary_parser_rejection(self):
        result = self.child(r'''
            def observe(event, args):
                if event == 'compile' and args[1] == '<ast-control>':
                    raise SyntaxError('original syntax-class audit refusal')
            sys.addaudithook(observe)
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            try:
                ast.parse('pass', filename='<ast-control>')
            except SyntaxError as error:
                emit({'error': str(error), 'state': guard.status()})
        ''')
        self.assertEqual(result['error'], 'original syntax-class audit refusal')
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_data_cannot_be_compiled_into_executable_authority(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            ast = sys.modules['ast']
            guard.activate()
            tree = ast.parse('pass')
            before = guard.status()['registeredCodeCount']
            try:
                compile(tree, '<ast-data>', 'exec')
            except PermissionError:
                emit({'registry_unchanged': before == guard.status()['registeredCodeCount'],
                      'state': guard.status()})
        ''')
        self.assertTrue(result['registry_unchanged'])
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_completion_hook_installation_must_be_observed(self):
        result = self.child(r'''
            def observe(event, args):
                if event == 'sys.addaudithook':
                    raise RuntimeError('original hook installation refusal')
            sys.addaudithook(observe)
            try:
                generators()
            except PermissionError:
                emit({'state': guard.status()})
        ''')
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ast_completion_hook_order_is_sealed_before_activation(self):
        result = self.child(r'''
            collections, dataclasses, code = generators()
            def later(event, args):
                pass
            # CPython suppresses the raised registration refusal; native status
            # must still retain it and prevent a later clean activation.
            sys.addaudithook(later)
            emit({'state': guard.status()})
        ''')
        self.assertTrue(result['state']['violated'])
        self.assertEqual(result['state']['phase'], 'configured')
        self.assertFalse(result['state']['permitActive'])


class NativeFrozenControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native_controls.NativeGuardControls.setUpClass.__func__(cls)

    def child(self, body):
        return native_controls.NativeGuardControls.child(self, body)

    def test_original_frozen_objects_match_without_transferring_identity(self):
        result = self.child(r'''
            import _imp
            names = ('__hello__', '__hello_alias__', '__phello_alias__',
                     '__phello_alias__.spam', '__phello__', '__phello__.__init__',
                     '__phello__.ham', '__phello__.ham.__init__',
                     '__phello__.ham.eggs', '__phello__.spam', '__hello_only__',
                     '_frozen_importlib', 'abc')
            original = {name: _imp.get_frozen_object(name) for name in names}
            prepared()
            comparisons = []
            for name in names:
                current = guard.frozen_code(name)
                comparisons.append({'name': name, 'equal': current == original[name],
                    'identical': current is original[name], 'owned': guard.contains(current),
                    'original_owned': guard.contains(original[name]),
                    'filename': current.co_filename == original[name].co_filename})
            emit({'comparisons': comparisons, 'state': guard.status()})
        ''')
        self.assertTrue(result['comparisons'])
        for row in result['comparisons']:
            with self.subTest(name=row['name']):
                self.assertTrue(row['equal'])
                self.assertFalse(row['identical'])
                self.assertTrue(row['owned'])
                self.assertFalse(row['original_owned'])
                self.assertTrue(row['filename'])
        self.assertEqual(result['state']['frozenReturns'], len(result['comparisons']))
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])
        self.assertFalse(result['state']['confinementEstablished'])

    def test_actual_frozen_execution_and_nested_strong_retention(self):
        result = self.child(r'''
            prepared()
            code = guard.frozen_code('__hello__')
            nested = [value for value in code.co_consts if type(value) is types.CodeType]
            namespace = {'__name__': '__hello__'}
            exec(code, namespace)
            del code
            gc.collect()
            emit({'initialized': namespace['initialized'],
                  'docs': [namespace[name].__doc__ for name in
                           ('TestFrozenUtf8_1', 'TestFrozenUtf8_2', 'TestFrozenUtf8_4')],
                  'nested_present': bool(nested),
                  'nested_owned': all(guard.contains(value) for value in nested),
                  'function_owned': guard.contains(namespace['main'].__code__),
                  'state': guard.status()})
        ''')
        self.assertTrue(result['initialized'])
        self.assertEqual(result['docs'], ['¶', 'π', '😀'])
        self.assertTrue(result['nested_present'])
        self.assertTrue(result['nested_owned'])
        self.assertTrue(result['function_owned'])
        self.assertFalse(result['state']['violated'])

    def test_configured_then_active_acquisitions_return_actual_distinct_code(self):
        result = self.child(r'''
            configured()
            first = guard.frozen_code('__hello__')
            guard.activate()
            second = guard.frozen_code('__hello__')
            namespace = {'__name__': '__hello__'}
            exec(second, namespace)
            emit({'equal': first == second, 'identical': first is second,
                  'owned': [guard.contains(first), guard.contains(second)],
                  'initialized': namespace['initialized'], 'state': guard.status()})
        ''')
        self.assertTrue(result['equal'])
        self.assertFalse(result['identical'])
        self.assertEqual(result['owned'], [True, True])
        self.assertTrue(result['initialized'])
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_missing_lookup_preserves_original_error_class_and_later_acquisition(self):
        result = self.child(r'''
            import _imp
            try:
                _imp.get_frozen_object('worldline_missing_frozen_control')
            except ImportError as error:
                original = {'type': type(error).__name__, 'name': error.name, 'path': error.path}
            prepared()
            before = guard.status()['registeredCodeCount']
            try:
                guard.frozen_code('worldline_missing_frozen_control')
            except ImportError as error:
                current = {'type': type(error).__name__, 'name': error.name, 'path': error.path}
            unchanged = before == guard.status()['registeredCodeCount']
            valid = guard.frozen_code('__hello__')
            emit({'original': original, 'current': current, 'unchanged': unchanged,
                  'later_owned': guard.contains(valid), 'state': guard.status()})
        ''')
        self.assertEqual(result['original']['type'], 'ImportError')
        self.assertEqual(result['current'], result['original'])
        self.assertEqual(result['current']['name'], 'worldline_missing_frozen_control')
        self.assertIsNone(result['current']['path'])
        self.assertTrue(result['unchanged'])
        self.assertTrue(result['later_owned'])
        self.assertFalse(result['state']['violated'])

    def test_original_disabled_selection_and_bootstrap_exception_are_preserved(self):
        result = self.child(r'''
            import _imp
            _imp._override_frozen_modules_for_tests(-1)
            try:
                _imp.get_frozen_object('__hello__')
            except ImportError as error:
                original = {'type': type(error).__name__, 'name': error.name, 'path': error.path}
            configured()
            try:
                guard.frozen_code('__hello__')
            except ImportError as error:
                current = {'type': type(error).__name__, 'name': error.name, 'path': error.path}
            bootstrap = guard.frozen_code('_frozen_importlib')
            guard.activate()
            _imp._override_frozen_modules_for_tests(1)
            later = guard.frozen_code('__hello__')
            _imp._override_frozen_modules_for_tests(0)
            emit({'original': original, 'current': current,
                  'bootstrap_owned': guard.contains(bootstrap),
                  'later_owned': guard.contains(later), 'state': guard.status()})
        ''')
        self.assertEqual(result['original']['type'], 'ImportError')
        self.assertEqual(result['current'], result['original'])
        self.assertEqual(result['current']['name'], '__hello__')
        self.assertIsNone(result['current']['path'])
        self.assertTrue(result['bootstrap_owned'])
        self.assertTrue(result['later_owned'])
        self.assertFalse(result['state']['violated'])

    def test_python_availability_replacement_cannot_change_native_provider(self):
        result = self.child(r'''
            import _imp
            prepared()
            _imp.is_frozen = lambda name: False
            code = guard.frozen_code('__hello__')
            emit({'owned': guard.contains(code), 'state': guard.status()})
        ''')
        self.assertTrue(result['owned'])
        self.assertFalse(result['state']['violated'])

    def test_later_thread_uses_its_own_frozen_permit(self):
        result = self.child(r'''
            prepared()
            outcomes = []
            def worker():
                try:
                    code = guard.frozen_code('__hello__')
                    namespace = {'__name__': '__hello__'}
                    exec(code, namespace)
                    outcomes.append(namespace['initialized'] and guard.contains(code))
                except BaseException as error:
                    outcomes.append(type(error).__name__)
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
            emit({'outcomes': outcomes, 'state': guard.status()})
        ''')
        self.assertEqual(result['outcomes'], [True])
        self.assertFalse(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_malformed_selector_refuses_without_callback_or_code_authority(self):
        result = self.child(r'''
            class Selector(str):
                def __str__(self):
                    raise AssertionError('selector callback must not run')
            prepared()
            before = guard.status()['registeredCodeCount']
            try:
                guard.frozen_code(Selector('__hello__'))
            except PermissionError as error:
                failure = type(error).__name__
            emit({'failure': failure,
                  'unchanged': before == guard.status()['registeredCodeCount'],
                  'state': guard.status()})
        ''')
        self.assertEqual(result['failure'], 'PermissionError')
        self.assertTrue(result['unchanged'])
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_ordinary_deserialization_has_no_configured_or_active_authority(self):
        for active in (False, True):
            with self.subTest(active=active):
                body = r'''
                    payload = marshal.dumps(None)
                    configured()
                    code = guard.compile_source('/verifier/entry.py')
                    if ACTIVE:
                        guard.activate()
                    try:
                        marshal.loads(payload)
                    except PermissionError as error:
                        failure = type(error).__name__
                    emit({'failure': failure, 'state': guard.status()})
                '''.replace('ACTIVE', repr(active))
                result = self.child(body)
                self.assertEqual(result['failure'], 'PermissionError')
                self.assertTrue(result['state']['violated'])
                self.assertFalse(result['state']['permitActive'])

    def test_audit_failure_preserves_primary_and_clears_frozen_permit(self):
        result = self.child(r'''
            original = LookupError('retained frozen audit primary')
            def audit(event, arguments):
                if event == 'marshal.loads' and guard.status()['phase'] == 'active':
                    raise original
            sys.addaudithook(audit)
            prepared()
            before = guard.status()['registeredCodeCount']
            try:
                guard.frozen_code('__hello__')
            except LookupError as error:
                same = error is original
            emit({'same': same, 'unchanged': before == guard.status()['registeredCodeCount'],
                  'state': guard.status()})
        ''')
        self.assertTrue(result['same'])
        self.assertTrue(result['unchanged'])
        self.assertTrue(result['state']['violated'])
        self.assertFalse(result['state']['permitActive'])

    def test_nested_native_operations_refuse_in_both_directions(self):
        for event, nested, outer in (
                ('marshal.loads', "guard.compile_source('/verifier/entry.py')", "guard.frozen_code('__hello__')"),
                ('compile', "guard.frozen_code('__hello__')", "guard.compile_source('/verifier/entry.py')"),
                ('marshal.loads', "guard.frozen_code('__hello__')", "guard.frozen_code('__hello__')")):
            with self.subTest(event=event, nested=nested):
                body = r'''
                    nested_errors = []
                    def audit(event, arguments):
                        if event == EVENT and guard.status()['phase'] == 'active':
                            try:
                                NESTED
                            except PermissionError as error:
                                nested_errors.append(type(error).__name__)
                    sys.addaudithook(audit)
                    prepared()
                    before = guard.status()['registeredCodeCount']
                    try:
                        OUTER
                    except PermissionError as error:
                        failure = type(error).__name__
                    emit({'nested': nested_errors, 'failure': failure,
                          'unchanged': before == guard.status()['registeredCodeCount'],
                          'state': guard.status()})
                '''.replace('EVENT', repr(event)).replace('NESTED', nested).replace('OUTER', outer)
                result = self.child(body)
                self.assertEqual(result['nested'], ['PermissionError'])
                self.assertEqual(result['failure'], 'PermissionError')
                self.assertTrue(result['unchanged'])
                self.assertTrue(result['state']['violated'])
                self.assertFalse(result['state']['permitActive'])


if __name__ == '__main__':
    unittest.main()
