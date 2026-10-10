with Worldline.Custody_V2_History;
package Worldline.Custody_V2_S0_Abandon with SPARK_Mode is
   package H renames Worldline.Custody_V2_History;
   package D renames H.D;
   package C renames H.C;
   package A renames D.A;
   package M renames D.M;
   package Q renames D.Q;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type M.Root_State_Array;
   use type M.Root_Phase;
   use type M.Owner;
   use type M.Event_Kind;
   -- S0 is logical and has NO stored root row. Do not invent inactive fields
   -- of M.Root_State or persist this representation as a SQL row.
   type Logical_S0 is record
      Generation : Q.Byte_Array (1 .. 1);
      Phase : M.Root_Phase;
      Owner : M.Owner;
      Owners_Open : Boolean;
      Reattach_Epoch : Q.Byte_Array (1 .. 0);
      Head : M.Digest;
   end record;
   type S0_Status is (S0_Refused, Logical_S0_Archives_Match_JSON_Open);
   procedure Materialize_S0
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : C.E.Span;
      Events : C.Event_Rows; Heads : C.Head_Rows;
      Stored_Roots : D.F.S.Root_Rows; Stored_Subjects : D.F.S.Subject_Rows;
      Alternatives : A.Alternative_Rows;
      State : in out Logical_S0; Result : out S0_Status)
   with Global => null, Always_Terminates,
     Post => (if Result = Logical_S0_Archives_Match_JSON_Open then
       Events'Length = 0 and then Stored_Roots'Length = 0 and then
       Stored_Subjects'Length = 0 and then Alternatives'Length = 0 and then
       State.Generation (1) = 1 and then State.Phase = M.Front_Owned and then
       State.Owner = M.Front and then State.Owners_Open
       else State = State'Old);

   type Step_Status is (Chain_Or_Decode_Refused, Wrong_Event_Family,
                        Semantic_Refusal, Replay_Unchanged,
                        Abandon_Value_Applied_Prestate_Fold_Open);
   -- The actual raw chain is authenticated here. Roots/Alternatives/Expected
   -- are exact typed predecessor operands, still requiring prior X5 fold.
   -- No startup/effect permit is returned. Raw(Position) is never filtered.
   procedure Step_Abandon
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : C.E.Span;
      Raw : C.Event_Rows; Heads : C.Head_Rows; Position : Q.Byte_Index;
      Roots : in out M.Root_State_Array; Alternatives : A.Alternative_Rows;
      Expected : A.Expected_Root; Result : out Step_Status)
   with Global => null, Always_Terminates,
     Pre => Position in Raw'Range,
     Post => (if Result /= Abandon_Value_Applied_Prestate_Fold_Open then Roots = Roots'Old);
end Worldline.Custody_V2_S0_Abandon;
