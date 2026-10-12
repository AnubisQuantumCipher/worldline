with Worldline.Root_Custody_Phase_Values;

--  V5-F.6 step 2 only. This selector never establishes X4 authentication or
--  X5 fold equality. Call it after both in the SAME retained transaction.
--  Found means return the original event unchanged, with NO action/Next.
package Worldline.Root_Custody_Replay with SPARK_Mode is
   package P renames Worldline.Root_Custody_Phase_Values;
   package M renames P.M;
   package Q renames M.Q;
   package L renames M.L;
   use type Q.Byte_Count;
   use type Q.Ordering;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Event_Record;
   use type Worldline.Hash;

   --  Semantic view plus the original archives and chain authentication
   --  fields: no reconstruction substitutes for returned retained bytes.
   type Retained_Event is record
      Event : M.Event_Record;
      Previous, Mac : M.Digest;
      Record_Bytes, Base_Archive : M.Identity;
   end record;
   type Retained_Events is array (Q.Byte_Index range <>) of Retained_Event;

   function Key (Item : M.Event_Record) return M.Replay_Identity is
     ((Generation => Item.Generation, Operation => Item.Operation,
       Kind_Of_Subject => Item.Kind_Of_Subject, Subject => Item.Subject,
       Subgeneration => Item.Subgeneration, Kind => Item.Kind,
       Record_Digest => Item.Record_Digest)) with Global => null;

   function Key_Valid (Data : Q.Byte_Array; Item : M.Replay_Identity)
      return Boolean is
     (Q.Span_Valid (Data, Item.Generation) and then
      Q.Span_Valid (Data, Item.Subgeneration) and then
      (not Item.Operation.Present or else L.Id_Valid (Data, Item.Operation)) and then
      (not Item.Subject.Present or else L.Id_Valid (Data, Item.Subject)))
   with Global => null;
   --  Only memory-domain validation. Canonical magnitude, subject/operation
   --  nullability, digest computation and enum/archive correspondence are X4/X5.
   function Inputs_Valid
     (Data : Q.Byte_Array; Events : Retained_Events; Wanted : M.Replay_Identity)
      return Boolean is
     (Key_Valid (Data, Wanted) and then
      (for all Item of Events => Key_Valid (Data, Key (Item.Event)) and then
        L.Id_Valid (Data, Item.Record_Bytes) and then
        L.Id_Valid (Data, Item.Base_Archive))) with Global => null;
   function Matches (Data : Q.Byte_Array; Item : Retained_Event;
                     Wanted : M.Replay_Identity) return Boolean is
     (P.Replay_Matches (Data, Key (Item.Event), Wanted)) with Global => null;
   function Any_Match (Data : Q.Byte_Array; Events : Retained_Events;
                       Wanted : M.Replay_Identity) return Boolean is
     (for some Item of Events => Matches (Data, Item, Wanted)) with Global => null;
   function Multiple_Matches (Data : Q.Byte_Array; Events : Retained_Events;
                             Wanted : M.Replay_Identity) return Boolean is
     (for some I in Events'Range => Matches (Data, Events (I), Wanted) and then
       (for some J in Events'Range => J /= I and then
          Matches (Data, Events (J), Wanted))) with Global => null;

   type Replay_Status is (Invalid_Operands, Ambiguous_History, No_Replay, Found);
   type Replay_Result (Status : Replay_Status := No_Replay) is record
      case Status is
         when Found => Position : Q.Byte_Index;
         when others => null;
      end case;
   end record;
   function Resolve
     (Data : Q.Byte_Array; Events : Retained_Events; Wanted : M.Replay_Identity)
      return Replay_Result
   with Global => null,
     Post =>
       (if not Inputs_Valid (Data, Events, Wanted) then
           Resolve'Result.Status = Invalid_Operands
        elsif Multiple_Matches (Data, Events, Wanted) then
           Resolve'Result.Status = Ambiguous_History
        elsif not Any_Match (Data, Events, Wanted) then
           Resolve'Result.Status = No_Replay
        else Resolve'Result.Status = Found and then
           Resolve'Result.Position in Events'Range and then
           Matches (Data, Events (Resolve'Result.Position), Wanted) and then
           (for all I in Events'Range =>
              (if I /= Resolve'Result.Position then
                  not Matches (Data, Events (I), Wanted))));
   --  Ambiguous_History is a malformed-roster diagnostic, never a new public
   --  refusal/domain rule. A valid append history cannot append a replay twice.
   --  No_Replay authorizes only continuing F.6 steps 3..9, not a mutation.
end Worldline.Root_Custody_Replay;
