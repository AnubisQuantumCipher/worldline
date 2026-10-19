with Interfaces;
with Worldline.Collapse;
with Worldline.Identities;
with Worldline.Transitions;

--  The collapse request as it crosses the C boundary (ABI generation 6), and
--  its decoding into Worldline.Collapse's typed request. Decoding is proved:
--  only the null check and the pointer dereference stay outside SPARK (in
--  Worldline.C_API). A request that is not Well_Formed is answered 255, and
--  nothing about it is interpreted.
package Worldline.Collapse_Wire with SPARK_Mode is
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_64;

   subtype Byte is Interfaces.Unsigned_8;
   type Raw_Bytes_32 is array (0 .. 31) of Byte with Convention => C;
   --  Preserve compiler-observed C array layout.
   for Raw_Bytes_32'Component_Size use 8;
   for Raw_Bytes_32'Size use 256;
   for Raw_Bytes_32'Object_Size use 256;
   for Raw_Bytes_32'Alignment use 1;
   type Raw_Bytes_8 is array (0 .. 7) of Byte with Convention => C;
   --  Preserve compiler-observed C array layout.
   for Raw_Bytes_8'Component_Size use 8;
   for Raw_Bytes_8'Size use 64;
   for Raw_Bytes_8'Object_Size use 64;
   for Raw_Bytes_8'Alignment use 1;

   --  present is 0 or 1. Absent: every value byte is 0. Present: the value is
   --  not all zero, so no zero digest can pass for a real identity.
   type Raw_Optional_Hash is record
      Present : Byte;
      Value   : Raw_Bytes_32;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Optional_Hash use record
      Present at 0 range 0 .. 7;
      Value at 1 range 0 .. 255;
   end record;
   for Raw_Optional_Hash'Size use 264;
   for Raw_Optional_Hash'Object_Size use 264;
   for Raw_Optional_Hash'Alignment use 1;

   --  A little-endian 64-bit counter with the same presence rule (a present
   --  counter may be zero).
   type Raw_Optional_Counter is record
      Present  : Byte;
      Value_LE : Raw_Bytes_8;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Optional_Counter use record
      Present at 0 range 0 .. 7;
      Value_Le at 1 range 0 .. 63;
   end record;
   for Raw_Optional_Counter'Size use 72;
   for Raw_Optional_Counter'Object_Size use 72;
   for Raw_Optional_Counter'Alignment use 1;

   type Raw_Request is record
      Candidate_State        : Byte;
      Phase                  : Byte;  --  0 commit, 1 prepare
      Evaluation_Mode        : Byte;  --  0 candidate evaluation, 1 checkpoint return
      Conflicts              : Byte;  --  0 unmeasured, 1 none found, 2 found
      Foreign_Writes         : Byte;  --  0 unmeasured, 1 none found, 2 found
      Roster_Complete        : Byte;
      Staged_Roster_Complete : Byte;
      Expected_Parent              : Raw_Optional_Hash;
      Candidate_Parent             : Raw_Optional_Hash;
      Expected_Subject             : Raw_Optional_Hash;
      Evidence_Subject             : Raw_Optional_Hash;
      Expected_Base                : Raw_Optional_Hash;
      Candidate_Base               : Raw_Optional_Hash;
      Expected_Delta               : Raw_Optional_Hash;
      Candidate_Delta              : Raw_Optional_Hash;
      Expected_Root_Set            : Raw_Optional_Hash;
      Candidate_Root_Set           : Raw_Optional_Hash;
      Expected_Staged_Root         : Raw_Optional_Hash;
      Actual_Staged_Root           : Raw_Optional_Hash;
      Staged_Content_Root          : Raw_Optional_Hash;
      Tested_Root                  : Raw_Optional_Hash;
      Current_Requirement          : Raw_Optional_Hash;
      Resulting_Requirement        : Raw_Optional_Hash;
      Evaluated_Requirement        : Raw_Optional_Hash;
      Declared_Verifiers           : Raw_Optional_Hash;
      Executed_Verifiers           : Raw_Optional_Hash;
      Staged_Evaluated_Requirement : Raw_Optional_Hash;
      Staged_Executed_Verifiers    : Raw_Optional_Hash;
      Staged_Examined_Root         : Raw_Optional_Hash;
      Expected_Checkpoint          : Raw_Optional_Hash;
      Witnessed_Checkpoint         : Raw_Optional_Hash;
      Registered_Watch_Set         : Raw_Optional_Hash;
      Watched_Set                  : Raw_Optional_Hash;
      Generation_Before            : Raw_Optional_Counter;
      Generation_After             : Raw_Optional_Counter;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Request use record
      Candidate_State at 0 range 0 .. 7;
      Phase at 1 range 0 .. 7;
      Evaluation_Mode at 2 range 0 .. 7;
      Conflicts at 3 range 0 .. 7;
      Foreign_Writes at 4 range 0 .. 7;
      Roster_Complete at 5 range 0 .. 7;
      Staged_Roster_Complete at 6 range 0 .. 7;
      Expected_Parent at 7 range 0 .. 263;
      Candidate_Parent at 40 range 0 .. 263;
      Expected_Subject at 73 range 0 .. 263;
      Evidence_Subject at 106 range 0 .. 263;
      Expected_Base at 139 range 0 .. 263;
      Candidate_Base at 172 range 0 .. 263;
      Expected_Delta at 205 range 0 .. 263;
      Candidate_Delta at 238 range 0 .. 263;
      Expected_Root_Set at 271 range 0 .. 263;
      Candidate_Root_Set at 304 range 0 .. 263;
      Expected_Staged_Root at 337 range 0 .. 263;
      Actual_Staged_Root at 370 range 0 .. 263;
      Staged_Content_Root at 403 range 0 .. 263;
      Tested_Root at 436 range 0 .. 263;
      Current_Requirement at 469 range 0 .. 263;
      Resulting_Requirement at 502 range 0 .. 263;
      Evaluated_Requirement at 535 range 0 .. 263;
      Declared_Verifiers at 568 range 0 .. 263;
      Executed_Verifiers at 601 range 0 .. 263;
      Staged_Evaluated_Requirement at 634 range 0 .. 263;
      Staged_Executed_Verifiers at 667 range 0 .. 263;
      Staged_Examined_Root at 700 range 0 .. 263;
      Expected_Checkpoint at 733 range 0 .. 263;
      Witnessed_Checkpoint at 766 range 0 .. 263;
      Registered_Watch_Set at 799 range 0 .. 263;
      Watched_Set at 832 range 0 .. 263;
      Generation_Before at 865 range 0 .. 71;
      Generation_After at 874 range 0 .. 71;
   end record;
   for Raw_Request'Size use 7064;
   for Raw_Request'Object_Size use 7064;
   for Raw_Request'Alignment use 1;

   Invalid_Request : constant Byte := 255;

   function All_Zero (Value : Raw_Bytes_32) return Boolean is
     (for all I in Value'Range => Value (I) = 0)
     with Global => null;

   function Hash_Well_Formed (H : Raw_Optional_Hash) return Boolean is
     (H.Present <= 1
      and then (if H.Present = 0 then All_Zero (H.Value)
                else not All_Zero (H.Value)))
     with Global => null;

   function Counter_Well_Formed (C : Raw_Optional_Counter) return Boolean is
     (C.Present <= 1
      and then (if C.Present = 0 then
                  (for all I in C.Value_LE'Range => C.Value_LE (I) = 0)))
     with Global => null;

   function Well_Formed (R : Raw_Request) return Boolean is
     (R.Candidate_State <=
        Transitions.World_State'Pos (Transitions.World_State'Last)
      and then R.Phase <= 1
      and then R.Evaluation_Mode <= 1
      and then R.Conflicts <= 2
      and then R.Foreign_Writes <= 2
      and then R.Roster_Complete <= 1
      and then R.Staged_Roster_Complete <= 1
      and then Hash_Well_Formed (R.Expected_Parent)
      and then Hash_Well_Formed (R.Candidate_Parent)
      and then Hash_Well_Formed (R.Expected_Subject)
      and then Hash_Well_Formed (R.Evidence_Subject)
      and then Hash_Well_Formed (R.Expected_Base)
      and then Hash_Well_Formed (R.Candidate_Base)
      and then Hash_Well_Formed (R.Expected_Delta)
      and then Hash_Well_Formed (R.Candidate_Delta)
      and then Hash_Well_Formed (R.Expected_Root_Set)
      and then Hash_Well_Formed (R.Candidate_Root_Set)
      and then Hash_Well_Formed (R.Expected_Staged_Root)
      and then Hash_Well_Formed (R.Actual_Staged_Root)
      and then Hash_Well_Formed (R.Staged_Content_Root)
      and then Hash_Well_Formed (R.Tested_Root)
      and then Hash_Well_Formed (R.Current_Requirement)
      and then Hash_Well_Formed (R.Resulting_Requirement)
      and then Hash_Well_Formed (R.Evaluated_Requirement)
      and then Hash_Well_Formed (R.Declared_Verifiers)
      and then Hash_Well_Formed (R.Executed_Verifiers)
      and then Hash_Well_Formed (R.Staged_Evaluated_Requirement)
      and then Hash_Well_Formed (R.Staged_Executed_Verifiers)
      and then Hash_Well_Formed (R.Staged_Examined_Root)
      and then Hash_Well_Formed (R.Expected_Checkpoint)
      and then Hash_Well_Formed (R.Witnessed_Checkpoint)
      and then Hash_Well_Formed (R.Registered_Watch_Set)
      and then Hash_Well_Formed (R.Watched_Set)
      and then Counter_Well_Formed (R.Generation_Before)
      and then Counter_Well_Formed (R.Generation_After)
      --  A slot the question does not consult must be empty, so no value can
      --  ride along in a field its mode or phase ignores.
      and then (if R.Phase = 1 then R.Actual_Staged_Root.Present = 0)
      and then (if R.Evaluation_Mode = 0 then
                  R.Expected_Checkpoint.Present = 0
                  and then R.Witnessed_Checkpoint.Present = 0)
      and then (if R.Evaluation_Mode = 1 then
                  R.Resulting_Requirement.Present = 0
                  and then R.Evaluated_Requirement.Present = 0
                  and then R.Executed_Verifiers.Present = 0
                  and then R.Roster_Complete = 0))
     with Global => null;

   function Counter_Value (V : Raw_Bytes_8) return Interfaces.Unsigned_64 is
     (Interfaces.Unsigned_64 (V (0))
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (1)), 8)
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (2)), 16)
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (3)), 24)
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (4)), 32)
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (5)), 40)
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (6)), 48)
      or Interfaces.Shift_Left (Interfaces.Unsigned_64 (V (7)), 56))
     with Global => null;

   function Digest (V : Raw_Bytes_32) return Hash is
     ([for I in Hash'Range => V (I)])
     with Global => null;

   function Content (H : Raw_Optional_Hash) return Identities.Optional_Content_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Content_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Subject (H : Raw_Optional_Hash) return Identities.Optional_Subject_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Subject_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function State (H : Raw_Optional_Hash) return Identities.Optional_State_Root is
     (if H.Present = 1
      then (Present => True, Value => Identities.State_Root (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Content_Root (H : Raw_Optional_Hash) return Identities.Optional_Content_Root is
     (if H.Present = 1
      then (Present => True, Value => Identities.Content_Root (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Delta_Of (H : Raw_Optional_Hash) return Identities.Optional_Delta_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Delta_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Root_Set (H : Raw_Optional_Hash) return Identities.Optional_Root_Set_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Root_Set_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Requirement (H : Raw_Optional_Hash) return Identities.Optional_Requirement_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Requirement_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Verifiers (H : Raw_Optional_Hash) return Identities.Optional_Verifier_Set_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Verifier_Set_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Watch_Set (H : Raw_Optional_Hash) return Identities.Optional_Watch_Set_Id is
     (if H.Present = 1
      then (Present => True, Value => Identities.Watch_Set_Id (Digest (H.Value)))
      else (Present => False, Value => [others => 0]))
     with Global => null;
   function Counter (C : Raw_Optional_Counter) return Identities.Optional_Generation is
     (if C.Present = 1
      then (Present => True, Value => Counter_Value (C.Value_LE))
      else (Present => False, Value => 0))
     with Global => null;

   function Measure (B : Byte) return Collapse.Measurement is
     (if B = 2 then Collapse.Found
      elsif B = 1 then Collapse.None_Found
      else Collapse.Unmeasured)
     with Global => null;

   --  Transparent: every field of the typed request is exactly the decoding of
   --  its wire field.
   function Decode (R : Raw_Request) return Collapse.Collapse_Request is
     ((Candidate_State => Transitions.World_State'Val (Integer (R.Candidate_State)),
       Request_Phase   => (if R.Phase = 1 then Collapse.Prepare else Collapse.Commit),
       Mode            => (if R.Evaluation_Mode = 1 then Collapse.Checkpoint_Return
                           else Collapse.Candidate_Evaluation),
       Conflicts       => Measure (R.Conflicts),
       Foreign_Writes  => Measure (R.Foreign_Writes),
       Roster_Complete        => R.Roster_Complete = 1,
       Staged_Roster_Complete => R.Staged_Roster_Complete = 1,
       Expected_Parent        => Content (R.Expected_Parent),
       Candidate_Parent       => Content (R.Candidate_Parent),
       Expected_Subject       => Subject (R.Expected_Subject),
       Evidence_Subject       => Subject (R.Evidence_Subject),
       Expected_Base          => State (R.Expected_Base),
       Candidate_Base         => State (R.Candidate_Base),
       Expected_Delta         => Delta_Of (R.Expected_Delta),
       Candidate_Delta        => Delta_Of (R.Candidate_Delta),
       Expected_Root_Set      => Root_Set (R.Expected_Root_Set),
       Candidate_Root_Set     => Root_Set (R.Candidate_Root_Set),
       Expected_Staged_Root   => State (R.Expected_Staged_Root),
       Actual_Staged_Root     => State (R.Actual_Staged_Root),
       Staged_Content_Root    => Content_Root (R.Staged_Content_Root),
       Tested_Root            => Content_Root (R.Tested_Root),
       Current_Requirement    => Requirement (R.Current_Requirement),
       Resulting_Requirement  => Requirement (R.Resulting_Requirement),
       Evaluated_Requirement  => Requirement (R.Evaluated_Requirement),
       Declared_Verifiers     => Verifiers (R.Declared_Verifiers),
       Executed_Verifiers     => Verifiers (R.Executed_Verifiers),
       Staged_Evaluated_Requirement => Requirement (R.Staged_Evaluated_Requirement),
       Staged_Executed_Verifiers    => Verifiers (R.Staged_Executed_Verifiers),
       Staged_Examined_Root         => Content_Root (R.Staged_Examined_Root),
       Expected_Checkpoint    => Content (R.Expected_Checkpoint),
       Witnessed_Checkpoint   => Content (R.Witnessed_Checkpoint),
       Registered_Watch_Set   => Watch_Set (R.Registered_Watch_Set),
       Watched_Set            => Watch_Set (R.Watched_Set),
       Generation_Before      => Counter (R.Generation_Before),
       Generation_After       => Counter (R.Generation_After)))
     with Global => null,
          Pre    => Well_Formed (R);

   --  The whole C entry point, proved: 255 for anything malformed, otherwise
   --  the decision's ordinal.
   function Decide_Wire (R : Raw_Request) return Byte
     with Global => null,
          Post => Decide_Wire'Result =
                    (if Well_Formed (R)
                     then Byte (Collapse.Decision'Pos (Collapse.Decide (Decode (R))))
                     else Invalid_Request);

end Worldline.Collapse_Wire;
