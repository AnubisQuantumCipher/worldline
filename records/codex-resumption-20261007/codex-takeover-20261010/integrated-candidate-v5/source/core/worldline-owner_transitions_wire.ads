with Evaluation_History;
with Interfaces;
with Interfaces.C;
with Worldline.Owner_Transitions;

--  Total typed wire decoding. Unbounded complete rows and full byte spans are
--  retained. Size/index representation bounds are not numeric epoch caps.
package Worldline.Owner_Transitions_Wire with SPARK_Mode is
   package E renames Evaluation_History;
   package K renames Worldline.Owner_Transitions;
   subtype U8 is Interfaces.Unsigned_8;
   subtype Size is Interfaces.C.size_t;
   use type U8;
   use type Size;
   use type E.Byte_Count;
   use type E.Evaluation_Record;
   use type K.Decision;
   type Raw_Identity is record
      Present : U8;
      First, Length : Size;
   end record with Convention => C;
   subtype Raw_Epoch is Raw_Identity;
   type Raw_Cursor is record
      Present : U8;
      Sequence : Raw_Epoch;
      Run : Raw_Identity;
   end record with Convention => C;
   type Raw_Row is record
      Subject, Content, Requirement, Run : Raw_Identity;
      Sequence : Raw_Epoch;
      State, Outcome : U8;
   end record with Convention => C;
   type Raw_Rows is array (E.Byte_Index range <>) of Raw_Row;
   type Raw_Grant is record
      Action, State : U8;
      Grant : Raw_Identity;
      Use_Id : Raw_Identity;
      Issuer : Raw_Identity;
      Principal : Raw_Identity;
      Subject : Raw_Identity;
      Content : Raw_Identity;
      Transaction : Raw_Identity;
      Current_Requirement : Raw_Identity;
      Expected_Requirement : Raw_Identity;
      Reason : Raw_Identity;
      Issued_Grant : Raw_Identity;
      Reserved_Grant : Raw_Identity;
      Reserved_Use : Raw_Identity;
      Failed_Run : Raw_Cursor;
      Prior_Head : Raw_Cursor;
      Next_Run : Raw_Cursor;
      Epoch : Raw_Epoch;
   end record with Convention => C;
   type Raw_Request is record
      Action : U8;
      Peer : Raw_Identity;
      Owner : Raw_Identity;
      Trusted_Issuer : Raw_Identity;
      Subject : Raw_Identity;
      Content : Raw_Identity;
      Transaction : Raw_Identity;
      Current_Requirement : Raw_Identity;
      Resulting_Requirement : Raw_Identity;
      Current_Head : Raw_Cursor;
      Attempt : Raw_Cursor;
      Current_Epoch : Raw_Epoch;
      Grant : Raw_Grant;
   end record with Convention => C;
   function Identity_Valid (I : Raw_Identity) return Boolean is
     (I.Present <= 1 and then (I.Present = 0 or else
        (I.First >= 1 and then I.First <= Size (E.Byte_Count'Last)
         and then I.Length <= Size (E.Byte_Count'Last)))) with Global => null;
   function Cursor_Valid (C : Raw_Cursor) return Boolean is
     (C.Present <= 1 and then (C.Present = 0 or else
       (Identity_Valid (C.Sequence) and then C.Run.Present = 1
        and then Identity_Valid (C.Run)))) with Global => null;
   function Row_Valid (R : Raw_Row) return Boolean is
     (Identity_Valid (R.Subject) and then Identity_Valid (R.Content)
      and then Identity_Valid (R.Requirement) and then Identity_Valid (R.Run)
      and then Identity_Valid (R.Sequence)
      and then R.State <= E.Lifecycle'Pos (E.Lifecycle'Last)
      and then R.Outcome <= E.Verdict'Pos (E.Verdict'Last)) with Global => null;
   function Grant_Valid (G : Raw_Grant) return Boolean is
     (G.Action <= K.Operation'Pos (K.Operation'Last)
      and then G.State <= K.Grant_State'Pos (K.Grant_State'Last)
      and then Identity_Valid (G.Grant)
      and then Identity_Valid (G.Use_Id)
      and then Identity_Valid (G.Issuer)
      and then Identity_Valid (G.Principal)
      and then Identity_Valid (G.Subject)
      and then Identity_Valid (G.Content)
      and then Identity_Valid (G.Transaction)
      and then Identity_Valid (G.Current_Requirement)
      and then Identity_Valid (G.Expected_Requirement)
      and then Identity_Valid (G.Reason)
      and then Identity_Valid (G.Issued_Grant)
      and then Identity_Valid (G.Reserved_Grant)
      and then Identity_Valid (G.Reserved_Use)
      and then Cursor_Valid (G.Failed_Run)
      and then Cursor_Valid (G.Prior_Head)
      and then Cursor_Valid (G.Next_Run)
      and then Identity_Valid (G.Epoch)) with Global => null;
   function Request_Valid (Q : Raw_Request) return Boolean is
     (Q.Action <= K.Operation'Pos (K.Operation'Last)
      and then Identity_Valid (Q.Peer)
      and then Identity_Valid (Q.Owner)
      and then Identity_Valid (Q.Trusted_Issuer)
      and then Identity_Valid (Q.Subject)
      and then Identity_Valid (Q.Content)
      and then Identity_Valid (Q.Transaction)
      and then Identity_Valid (Q.Current_Requirement)
      and then Identity_Valid (Q.Resulting_Requirement)
      and then Cursor_Valid (Q.Current_Head)
      and then Cursor_Valid (Q.Attempt)
      and then Identity_Valid (Q.Current_Epoch)
      and then Grant_Valid (Q.Grant)) with Global => null;
   function Well_Formed (H : Raw_Rows; F : Raw_Row; Final_Present : U8;
      Q : Raw_Request) return Boolean is
     (Final_Present <= 1 and then (Final_Present = 0 or else Row_Valid (F))
      and then Request_Valid (Q)
      and then (for all I in H'Range => Row_Valid (H (I)))) with Global => null;
   function Identity (I : Raw_Identity) return K.Optional_Identity
     with Global => null, Pre => Identity_Valid (I);
   function Epoch (I : Raw_Epoch) return E.Optional_Epoch
     with Global => null, Pre => Identity_Valid (I);
   function Cursor (C : Raw_Cursor) return E.Optional_Cursor
     with Global => null, Pre => Cursor_Valid (C);
   function Row (R : Raw_Row) return E.Evaluation_Record
     with Global => null, Pre => Row_Valid (R);
   function Grant (G : Raw_Grant) return K.Owner_Grant
     with Global => null, Pre => Grant_Valid (G);
   function Decode (Q : Raw_Request) return K.Request
     with Global => null, Pre => Request_Valid (Q);
   function Rows (H : Raw_Rows) return E.History
     with Global => null, Pre => (for all I in H'Range => Row_Valid (H (I))),
       Post => Rows'Result'First = H'First and then Rows'Result'Last = H'Last
         and then (for all I in H'Range => Rows'Result (I) = Row (H (I)));
   function Decide (A : E.Byte_Array; H : Raw_Rows; F : Raw_Row;
      Final_Present : U8; Q : Raw_Request) return K.Decision
     with Global => null,
       Post => (if not Well_Formed (H, F, Final_Present, Q)
         then Decide'Result = K.Input_Invalid
         else Decide'Result = K.Reference (A, Rows (H),
           (if Final_Present = 0 then (Present => False)
            else (Present => True, Value => Row (F))), Decode (Q)));
end Worldline.Owner_Transitions_Wire;
