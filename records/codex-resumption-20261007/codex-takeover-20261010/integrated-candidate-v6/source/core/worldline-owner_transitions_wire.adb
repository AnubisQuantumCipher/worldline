package body Worldline.Owner_Transitions_Wire with SPARK_Mode is
   function Span (I : Raw_Identity) return E.Identity_Span is
     (First => E.Byte_Index (I.First), Length => E.Byte_Count (I.Length))
     with Global => null, Pre => Identity_Valid (I) and then I.Present = 1;
   function Identity (I : Raw_Identity) return K.Optional_Identity is
   begin
      if I.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value => Span (I));
      end if;
   end Identity;
   function Epoch (I : Raw_Epoch) return E.Optional_Epoch is
   begin
      if I.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value => E.Epoch_Id (Span (I)));
      end if;
   end Epoch;
   function Cursor (C : Raw_Cursor) return E.Optional_Cursor is
   begin
      if C.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value =>
           (Sequence => Epoch (C.Sequence), Run => E.Evaluation_Id (Span (C.Run))));
      end if;
   end Cursor;
   function Subject (I : Raw_Identity) return E.Optional_Subject
     with Global => null, Pre => Identity_Valid (I)
   is
   begin
      if I.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value => E.Subject_Id (Span (I)));
      end if;
   end Subject;
   function Content (I : Raw_Identity) return E.Optional_Content
     with Global => null, Pre => Identity_Valid (I)
   is
   begin
      if I.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value => E.Content_Id (Span (I)));
      end if;
   end Content;
   function Requirement (I : Raw_Identity) return E.Optional_Requirement
     with Global => null, Pre => Identity_Valid (I)
   is
   begin
      if I.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value => E.Requirement_Id (Span (I)));
      end if;
   end Requirement;
   function Run (I : Raw_Identity) return E.Optional_Evaluation
     with Global => null, Pre => Identity_Valid (I)
   is
   begin
      if I.Present = 0 then
         return (Present => False);
      else
         return (Present => True, Value => E.Evaluation_Id (Span (I)));
      end if;
   end Run;
   function Row (R : Raw_Row) return E.Evaluation_Record is
     (Subject => Subject (R.Subject), Content => Content (R.Content),
      Requirement => Requirement (R.Requirement), Run => Run (R.Run),
      Sequence => Epoch (R.Sequence), State => E.Lifecycle'Val (R.State),
      Outcome => E.Verdict'Val (R.Outcome));
   function Grant (G : Raw_Grant) return K.Owner_Grant is
     (Action => K.Operation'Val (G.Action), State => K.Grant_State'Val (G.State),
      Grant => Identity (G.Grant),
      Use_Id => Identity (G.Use_Id),
      Issuer => Identity (G.Issuer),
      Principal => Identity (G.Principal),
      Subject => Identity (G.Subject),
      Content => Identity (G.Content),
      Transaction => Identity (G.Transaction),
      Current_Requirement => Identity (G.Current_Requirement),
      Expected_Requirement => Identity (G.Expected_Requirement),
      Reason => Identity (G.Reason),
      Issued_Grant => Identity (G.Issued_Grant),
      Reserved_Grant => Identity (G.Reserved_Grant),
      Reserved_Use => Identity (G.Reserved_Use),
      Failed_Run => Cursor (G.Failed_Run),
      Prior_Head => Cursor (G.Prior_Head),
      Next_Run => Cursor (G.Next_Run),
      Epoch => Epoch (G.Epoch));
   function Decode (Q : Raw_Request) return K.Request is
     (Action => K.Operation'Val (Q.Action),
      Peer => Identity (Q.Peer),
      Owner => Identity (Q.Owner),
      Trusted_Issuer => Identity (Q.Trusted_Issuer),
      Subject => Identity (Q.Subject),
      Content => Identity (Q.Content),
      Transaction => Identity (Q.Transaction),
      Current_Requirement => Identity (Q.Current_Requirement),
      Resulting_Requirement => Identity (Q.Resulting_Requirement),
      Current_Head => Cursor (Q.Current_Head),
      Attempt => Cursor (Q.Attempt),
      Current_Epoch => Epoch (Q.Current_Epoch), Grant => Grant (Q.Grant));
   function Rows (H : Raw_Rows) return E.History is
      Result : E.History (H'Range) with Relaxed_Initialization;
   begin
      for I in H'Range loop
         Result (I) := Row (H (I));
         pragma Loop_Invariant (for all J in H'First .. I => Result (J)'Initialized);
         pragma Loop_Invariant (for all J in H'First .. I => Result (J) = Row (H (J)));
      end loop;
      pragma Assert (Result'Initialized);
      return Result;
   end Rows;
   function Decide (A : E.Byte_Array; H : Raw_Rows; F : Raw_Row;
      Final_Present : U8; Q : Raw_Request) return K.Decision is
   begin
      if not Well_Formed (H, F, Final_Present, Q) then
         return K.Input_Invalid;
      end if;
      declare
         Final : constant E.Optional_Record :=
           (if Final_Present = 1 then (Present => True, Value => Row (F))
            else (Present => False));
      begin
         return K.Authorize (A, Rows (H), Final, Decode (Q));
      end;
   end Decide;
end Worldline.Owner_Transitions_Wire;
