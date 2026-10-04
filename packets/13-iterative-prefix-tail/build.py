#!/usr/bin/env python3
"""Packet 13 (candidate): the body-level witness Prefix_Tail in resource_reservation_transition.adb becomes
iterative, so its two notices (contracts-recursive and numeric-variant at :85) no longer apply to a recursive
function. Stacks on packet 09's file. Pre unchanged; Post keeps its conjunct and ADDS the decomposition that
determines the value uniquely; termination moves from the removed Subprogram_Variant to a Loop_Variant.
Prefix_Decomposition: spec unchanged and in place; its body moves verbatim below Positive_Factor_Cancellation
(which it now calls) with additive lines only; every original statement and assertion is kept."""
import hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.dirname(os.path.dirname(HERE))
P09 = WF + '/packets/09-reservation-transition-proof-repairs/files/core/resource_reservation_transition.adb'
BASE_SHA = '705f7102a64c06e4e03ab354fc3deac928129249fcb054146a486291ff1f04f3'
data = open(P09, 'rb').read()
assert hashlib.sha256(data).hexdigest() == BASE_SHA, 'packet 09 output changed'
src = data.decode('latin-1')

def replace_once(text, old, new, tag):
    assert text.count(old) == 1, (tag, text.count(old))
    return text.replace(old, new)

OLD_TAIL = '''   function Prefix_Tail
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count)
      return Valid_Big_Integer is
     (if First = Stop then To_Big_Integer (0)
      else Prefix_Tail (Data, Q, First, Stop - 1)
        + To_Big_Integer (Digit (Data, Q, Stop - 1))
          * Power_Reference ((Stop - First) - 1))
   with Ghost, Global => null,
     Pre => First <= Stop,
     Subprogram_Variant => (Decreases => Stop),
     Post => Prefix_Tail'Result >= 0;
'''
NEW_TAIL = '''   --  Iterative (packet 13): the tail is accumulated digit by digit, so the
   --  witness is not recursive and its contract is available at every call.
   --  The Post keeps the original conjunct and adds the decomposition, which
   --  determines the value uniquely (Power_Reference (First) >= 1); the
   --  original recurrence step is derived in Prefix_Decomposition.
   function Prefix_Tail
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count)
      return Valid_Big_Integer
   with Ghost, Global => null,
     Pre => First <= Stop,
     Post => Prefix_Tail'Result >= 0 and then
       Prefix_Reference (Data, Q, Stop) =
         Prefix_Reference (Data, Q, First)
           + Power_Reference (First) * Prefix_Tail'Result
   is
      Tail : Valid_Big_Integer := To_Big_Integer (0);
      Reached : Byte_Count := First;
   begin
      while Reached < Stop loop
         pragma Loop_Invariant (First <= Reached and then Reached < Stop);
         pragma Loop_Invariant (Tail >= 0);
         pragma Loop_Invariant
           (Prefix_Reference (Data, Q, Reached) =
              Prefix_Reference (Data, Q, First)
                + Power_Reference (First) * Tail);
         pragma Loop_Variant (Decreases => Stop - Reached);
         Power_Factor (First, Reached);
         pragma Assert
           (Prefix_Reference (Data, Q, Reached + 1) =
              Prefix_Reference (Data, Q, Reached)
                + To_Big_Integer (Digit (Data, Q, Reached))
                  * Power_Reference (Reached));
         pragma Assert
           (To_Big_Integer (Digit (Data, Q, Reached))
              * Power_Reference (Reached) =
            Power_Reference (First)
              * (To_Big_Integer (Digit (Data, Q, Reached))
                   * Power_Reference (Reached - First)));
         pragma Assert
           (Prefix_Reference (Data, Q, Reached + 1) =
              Prefix_Reference (Data, Q, First)
                + Power_Reference (First)
                  * (Tail + To_Big_Integer (Digit (Data, Q, Reached))
                       * Power_Reference (Reached - First)));
         Tail := Tail + To_Big_Integer (Digit (Data, Q, Reached))
           * Power_Reference (Reached - First);
         Reached := Reached + 1;
      end loop;
      return Tail;
   end Prefix_Tail;
'''
OLD_BODY = '''   procedure Prefix_Decomposition
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count) is
   begin
      if First < Stop then
         Prefix_Decomposition (Data, Q, First, Stop - 1);
         Power_Factor (First, Stop - 1);
         pragma Assert
           (Prefix_Reference (Data, Q, Stop) =
              Prefix_Reference (Data, Q, Stop - 1)
                + To_Big_Integer (Digit (Data, Q, Stop - 1))
                  * Power_Reference (Stop - 1));
         pragma Assert
           (Prefix_Tail (Data, Q, First, Stop) =
              Prefix_Tail (Data, Q, First, Stop - 1)
                + To_Big_Integer (Digit (Data, Q, Stop - 1))
                  * Power_Reference ((Stop - First) - 1));
      else
         pragma Assert (Prefix_Tail (Data, Q, First, Stop) = 0);
      end if;
   end Prefix_Decomposition;

'''
NEW_BODY = '''   --  Body moved verbatim below Positive_Factor_Cancellation (packet 13);
   --  the lines marked "packet 13" are additive.
   procedure Prefix_Decomposition
     (Data : Byte_Array; Q : Quantity; First, Stop : Byte_Count) is
   begin
      if First < Stop then
         Prefix_Decomposition (Data, Q, First, Stop - 1);
         Power_Factor (First, Stop - 1);
         pragma Assert
           (Prefix_Reference (Data, Q, Stop) =
              Prefix_Reference (Data, Q, Stop - 1)
                + To_Big_Integer (Digit (Data, Q, Stop - 1))
                  * Power_Reference (Stop - 1));
         pragma Assert ((Stop - First) - 1 = (Stop - 1) - First);  --  packet 13
         pragma Assert                                              --  packet 13
           (Prefix_Tail (Data, Q, First, Stop) * Power_Reference (First) =
              (Prefix_Tail (Data, Q, First, Stop - 1)
                 + To_Big_Integer (Digit (Data, Q, Stop - 1))
                   * Power_Reference ((Stop - First) - 1))
                * Power_Reference (First));
         Positive_Factor_Cancellation                                --  packet 13
           (Prefix_Tail (Data, Q, First, Stop),
            Prefix_Tail (Data, Q, First, Stop - 1)
              + To_Big_Integer (Digit (Data, Q, Stop - 1))
                * Power_Reference ((Stop - First) - 1),
            Power_Reference (First));
         pragma Assert
           (Prefix_Tail (Data, Q, First, Stop) =
              Prefix_Tail (Data, Q, First, Stop - 1)
                + To_Big_Integer (Digit (Data, Q, Stop - 1))
                  * Power_Reference ((Stop - First) - 1));
      else
         Positive_Factor_Cancellation                                --  packet 13
           (Prefix_Tail (Data, Q, First, Stop), To_Big_Integer (0),
            Power_Reference (First));
         pragma Assert (Prefix_Tail (Data, Q, First, Stop) = 0);
      end if;
   end Prefix_Decomposition;
'''
ANCHOR = '''      pragma Assert (Difference = 0);
   end Positive_Factor_Cancellation;
'''
src = replace_once(src, OLD_TAIL, NEW_TAIL, 'prefix tail')
src = replace_once(src, OLD_BODY, '', 'old decomposition body')
src = replace_once(src, ANCHOR, ANCHOR + '\n' + NEW_BODY, 'insertion after Positive_Factor_Cancellation')
# every original body line survives, in order, in the moved body
old_lines = [l for l in OLD_BODY.splitlines() if l.strip()]
new_lines = NEW_BODY.splitlines()
position = 0
for line in old_lines:
    while position < len(new_lines) and new_lines[position] != line:
        position += 1
    assert position < len(new_lines), ('original line lost', line)
    position += 1
# the spec of Prefix_Decomposition and every other original declaration stay
assert src.count('procedure Prefix_Decomposition') == 2   # spec and moved body
assert src.count('Prefix_Decomposition (Data, Q, First, Stop - 1);') == 1   # the recursive call, once
assert src.index('procedure Prefix_Decomposition') < src.index('procedure Magnitude_Columns')   # spec still before its caller
assert src.index('procedure Positive_Factor_Cancellation') < src.index('Positive_Factor_Cancellation                                --  packet 13')
out = HERE + '/files/core/resource_reservation_transition.adb'
os.makedirs(os.path.dirname(out), exist_ok=True)
assert not os.path.exists(out), 'create-only'
raw = src.encode('latin-1')
with open(out, 'xb') as handle:
    handle.write(raw)
print(out, len(raw), hashlib.sha256(raw).hexdigest())
