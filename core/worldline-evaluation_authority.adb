package body Worldline.Evaluation_Authority with SPARK_Mode is
   --  Retain the complete original equation as a separate total proof
   --  obligation. Its Decode terms stay in this body, outside callers of
   --  the public dependency expression. No authorization result is changed.
   function Original_Dependencies (Request : C.Raw_Request)
      return Raw_Dependency is
     (if not C.Well_Formed (Request) then Invalid_Collapse
      elsif C.Decode (Request).Mode = Worldline.Collapse.Checkpoint_Return then
        (if Worldline.Collapse.Primary_Covers (C.Decode (Request))
         then No_Raw_Evidence else Staged_Only)
      elsif Worldline.Collapse.Primary_Covers (C.Decode (Request))
      then Primary_Only else Primary_And_Staged) with Ghost, Global => null;

   procedure Lemma_Dependencies_Equivalent (Request : C.Raw_Request)
     with Ghost, Global => null, Always_Terminates,
       Post => Dependencies (Request) = Original_Dependencies (Request);

   procedure Lemma_Dependencies_Equivalent (Request : C.Raw_Request) is
      use type Worldline.Identities.Optional_Content_Root;
   begin
      if not C.Well_Formed (Request) then
         pragma Assert (Dependencies (Request) = Invalid_Collapse);
         pragma Assert (Original_Dependencies (Request) = Invalid_Collapse);
      else
         declare
            Decoded : constant Worldline.Collapse.Collapse_Request :=
              C.Decode (Request);
         begin
            pragma Assert
              (Decoded.Mode =
                 (if Request.Evaluation_Mode = 1
                  then Worldline.Collapse.Checkpoint_Return
                  else Worldline.Collapse.Candidate_Evaluation));
            pragma Assert
              (Decoded.Tested_Root = C.Content_Root (Request.Tested_Root));
            pragma Assert
              (Decoded.Staged_Content_Root =
                 C.Content_Root (Request.Staged_Content_Root));
            pragma Assert
              (Worldline.Collapse.Primary_Covers (Decoded) =
                 Worldline.Identities.Same
                   (C.Content_Root (Request.Tested_Root),
                    C.Content_Root (Request.Staged_Content_Root)));
         end;
      end if;
      pragma Assert
        (Dependencies (Request) = Original_Dependencies (Request));
   end Lemma_Dependencies_Equivalent;

   function Report_Of (Raw : W.Raw_Record) return Byte is
      Value : constant W.Decode_Result := W.Decode (Raw);
   begin
      if not Value.Valid then return W.Invalid_Record; end if;
      return W.E.Report_Integrity'Pos (W.E.Report_Integrity_Of
        (Value.Value.Report_Based, W.E.Classify (Value.Value.Facts), Value.Value.Report_Facts));
   end Report_Of;
   function Decide_Envelope
     (A : T.Bytes; Journal : T.R.Journal; Current : T.Cursor;
      Capture : T.Terminal_Record; Rows : T.Result_Array;
      Retained : T.Optional_Terminal; Retained_Rows : T.Result_Array)
      return T.Decision
   is
      Reason : constant T.Decision := T.Decide
        (A, Journal, Current, Structural_Terminal (Capture),
         Structural_Results (Rows), Structural_Optional (Retained),
         Structural_Results (Retained_Rows));
   begin
      if Reason = T.Already_Retained and then
        not Carried_Replay_Equal (Capture, Rows, Retained, Retained_Rows)
      then
         return T.Terminal_Conflict;
      end if;
      return Reason;
   end Decide_Envelope;
   function Join_Context
     (A, B : T.Bytes; Capture : T.Terminal_Record; Current : T.Cursor;
      Expected_Binding : T.Attempt_Binding; Expected_Current, Prepared_Current : T.Cursor;
      Expected, Observed : Context_Fields; Before_Root, After_Root : T.Span;
      Policy, Expected_Policy : Roster.Declaration; Rows : T.Result_Array;
      Joined : Context_Rows; Required, Expected_Required : Roster.Check_Array;
      Request, Projection : C.Raw_Request) return Boolean is
   begin
      return Context_Reference
        (A, B, Capture, Current, Expected_Binding, Expected_Current, Prepared_Current,
         Expected, Observed, Before_Root, After_Root, Policy, Expected_Policy,
         Rows, Joined, Required, Expected_Required,
         Request, Projection);
   end Join_Context;
   function Join_Metadata
     (A, B : T.Bytes; Rows : T.Result_Array; Projected : Row_Metadata_Array)
      return Boolean is
   begin
      if Rows'Length /= Projected'Length then return False; end if;
      for I in Rows'Range loop
         pragma Loop_Invariant
           (for all J in Rows'First .. I - 1 => Row_Metadata_Reference
             (A, B, Rows (J), Projected (Projected'First + (J - Rows'First))));
         if not Row_Metadata_Reference
           (A, B, Rows (I), Projected (Projected'First + (I - Rows'First)))
         then return False; end if;
      end loop;
      return True;
   end Join_Metadata;
end Worldline.Evaluation_Authority;
