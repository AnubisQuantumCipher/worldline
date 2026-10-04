#!/usr/bin/env python3
"""Packet 14 (candidate): Worldline.Chain_Authority.Replay - D1554 (loop invariant preservation) and D1555 (Post =
Replay_Reference). Additive only (ruling 7b: independently proved induction lemma and checked call-site facts):
a body-local Ghost induction lemma Prefix_Settled (total, conditional Post); before each in-loop early return an
assertion that the returned value is Prefix_Reference at Count + 1 and a Prefix_Settled call extending it to
Rows'Length; after the case statement the accepted predecessor/link facts; before the count step the next
invariant instance. No statement, contract, reference, variant or return value changes."""
import hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.dirname(os.path.dirname(HERE))
W = os.path.dirname(os.path.dirname(WF))
BASE = W + '/work/reviewed-common-proof-source-composition-v4/source/core/worldline-chain_authority.adb'
BASE_SHA = 'a72d60bd07d5d591b4232c1e3d7857ecd67b6613e1f3e0ea0bccf9e891abbbe4'
data = open(BASE, 'rb').read()
assert hashlib.sha256(data).hexdigest() == BASE_SHA
src = data.decode('latin-1')
original = src

def replace_once(text, old, new, tag):
    assert text.count(old) == 1, (tag, text.count(old))
    return text.replace(old, new)

LEMMA_ANCHOR = '''   end Replay_Reference;
'''
LEMMA = '''   end Replay_Reference;

   --  Packet 14 (additive induction lemma; ruling 7b): Prefix_Step returns a
   --  non-Ready Before unchanged, so once a prefix result is not Ready every
   --  longer prefix of the unchanged reference equals it. Total, conditional
   --  Post; the reference equations and variants are unchanged.
   procedure Prefix_Settled
     (Kind : Chain_Kind; Rows : Retained_Rows; Genesis : Hash;
      From, To : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Subprogram_Variant => (Decreases => To),
     Post => (if From <= To and then To <= Rows'Length
                and then Prefix_Reference (Kind, Rows, Genesis, From).Disposition
                  /= Ready
              then Prefix_Reference (Kind, Rows, Genesis, To) =
                Prefix_Reference (Kind, Rows, Genesis, From))
   is
   begin
      if From < To and then To <= Rows'Length then
         Prefix_Settled (Kind, Rows, Genesis, From, To - 1);
      end if;
   end Prefix_Settled;
'''

def settle(indent, value):
    pad = ' ' * indent
    return (pad + 'pragma Assert                                                --  packet 14\n'
            + pad + '  (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =\n'
            + pad + '     ' + value + ');\n'
            + pad + 'Prefix_Settled                                               --  packet 14\n'
            + pad + '  (Kind, Rows, Observed_Genesis.Value, Count + 1, Rows\'Length);\n')

OLD_ABSENT = '''            if not Present (Row) then
               return (Disposition => Row_Absent, Head => Current,
                       Accepted_Count => Count);
            elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
               return (Disposition => Payload_Mismatch, Head => Current,
                       Accepted_Count => Count);
            end if;
'''
NEW_ABSENT = ('''            if not Present (Row) then
''' + settle(15, '(Disposition => Row_Absent, Head => Current, Accepted_Count => Count)') + '''               return (Disposition => Row_Absent, Head => Current,
                       Accepted_Count => Count);
            elsif not R.Same (Row.Actual_Payload_Root, Row.Stored_Payload_Root) then
''' + settle(15, '(Disposition => Payload_Mismatch, Head => Current, Accepted_Count => Count)') + '''               return (Disposition => Payload_Mismatch, Head => Current,
                       Accepted_Count => Count);
            end if;
''')
OLD_RECEIPT = '''                  if not Receipts.Accepted (Receipt) then
                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
'''
NEW_RECEIPT = ('''                  if not Receipts.Accepted (Receipt) then
''' + settle(21, '(Disposition => Predecessor_Mismatch, Head => Current, Accepted_Count => Count)') + '''                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
''')
OLD_CAUSAL = '''                  if not Causal_Graph.Accepted (Causal) then
                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
'''
NEW_CAUSAL = ('''                  if not Causal_Graph.Accepted (Causal) then
''' + settle(21, '(Disposition => Predecessor_Mismatch, Head => Current, Accepted_Count => Count)') + '''                     return (Disposition => Predecessor_Mismatch, Head => Current,
                             Accepted_Count => Count);
                  end if;
''')
OLD_TAIL = '''            end case;
            if Current /= Row.Stored_Head.Value then
               return (Disposition => Stored_Head_Mismatch, Head => Before,
                       Accepted_Count => Count);
            end if;
            Count := Count + 1;
'''
NEW_TAIL = ('''            end case;
            pragma Assert                                                 --  packet 14
              (Row.Previous.Value = Before
               and then Current = Link (Kind, Before, Row.Actual_Payload_Root.Value));
            if Current /= Row.Stored_Head.Value then
''' + settle(15, '(Disposition => Stored_Head_Mismatch, Head => Before, Accepted_Count => Count)') + '''               return (Disposition => Stored_Head_Mismatch, Head => Before,
                       Accepted_Count => Count);
            end if;
            pragma Assert                                                 --  packet 14
              (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                 (Disposition => Ready, Head => Current, Accepted_Count => Count + 1));
            Count := Count + 1;
''')
src = replace_once(src, LEMMA_ANCHOR, LEMMA, 'lemma')
src = replace_once(src, OLD_ABSENT, NEW_ABSENT, 'absent/payload')
src = replace_once(src, OLD_RECEIPT, NEW_RECEIPT, 'receipt predecessor')
src = replace_once(src, OLD_CAUSAL, NEW_CAUSAL, 'causal predecessor')
src = replace_once(src, OLD_TAIL, NEW_TAIL, 'stored head and step')
# additive check: deleting every line marked or introduced by packet 14 gives back the original text
added_blocks = [LEMMA[len(LEMMA_ANCHOR):]]
for indent, value in ((15, '(Disposition => Row_Absent, Head => Current, Accepted_Count => Count)'),
                      (15, '(Disposition => Payload_Mismatch, Head => Current, Accepted_Count => Count)'),
                      (21, '(Disposition => Predecessor_Mismatch, Head => Current, Accepted_Count => Count)'),
                      (15, '(Disposition => Stored_Head_Mismatch, Head => Before, Accepted_Count => Count)')):
    added_blocks.append(settle(indent, value))
reverted = src.replace(LEMMA[len(LEMMA_ANCHOR):], '', 1)
for block in added_blocks[1:]:
    reverted = reverted.replace(block, '')
reverted = reverted.replace('''            pragma Assert                                                 --  packet 14
              (Row.Previous.Value = Before
               and then Current = Link (Kind, Before, Row.Actual_Payload_Root.Value));
''', '').replace('''            pragma Assert                                                 --  packet 14
              (Prefix_Reference (Kind, Rows, Observed_Genesis.Value, Count + 1) =
                 (Disposition => Ready, Head => Current, Accepted_Count => Count + 1));
''', '')
assert reverted == original, 'packet 14 is not purely additive'
out = HERE + '/files/core/worldline-chain_authority.adb'
os.makedirs(os.path.dirname(out), exist_ok=True)
raw = src.encode('latin-1')
with open(out, 'xb') as handle:
    handle.write(raw)
print(out, len(raw), hashlib.sha256(raw).hexdigest())
