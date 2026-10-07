# SPARK diagnostic snapshot repair

The terminal D7 full-strict stream rejects `Evaluation_Completion_C.Diagnostic_Enabled` as a function with an output global (E0005) and the handler constants initialized by that function. The exact same source bytes are in integrated v17. The installed GNATprove E0005 explanation prescribes `Side_Effects` for an effectful function and restricts its calls to assignment right-hand sides.

V18 adds `Side_Effects` while retaining `Volatile_Function` on the diagnostic-only reader. Each affected exception handler now declares a Boolean initialized to False and assigns the function result once before the original conditional. It still captures the original exception information lexically inside that handler and retains the original diagnostic calls and failure return. No authority input, public authority contract, accepted case, fixture, assertion policy, proof setting, or output ABI changes. The diagnostic enable state remains an atomic read from the same variable.

This is an affected-source candidate, not proof or runtime acceptance. The installed toolchain must compile/analyze it; full strict proof, handler behavior, diagnostic I/O and all Phase One guarantees remain open until the actual checks and independent review establish them. V17 and its retained runtime outputs are untouched.
