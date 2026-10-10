package body Worldline.Custody_V2_Event_Joins with SPARK_Mode is
   use type Q.Byte;
   use type D.Decode_Status;
   function Same (Data : C.E.Bytes; Left, Right : C.E.Span) return Boolean is
     (C.E.C.P.Valid (Data, Left) and then C.E.C.P.Valid (Data, Right) and then
      Left.Length = Right.Length and then
      (if Left.Length > 0 then
         (for all Offset in Q.Byte_Count range 0 .. Left.Length - 1 =>
            Data (Left.First + Offset) = Data (Right.First + Offset))));

   function Reference_Matches
     (Data : C.E.Bytes; Reference : C.E.Span; Raw : C.Event_Row)
      return Boolean
   is
      function Field_Same (Name : String) return Boolean is
        (S.A.Same_Encoding (Data, S.Field (Data, Reference, Name),
                           S.Field (Data, Raw.Base_Archive, Name)));
   begin
      return C.Base_Matches (Data, Raw) and then S.Valid (Data, Reference) and then
        S.Member_Count (Data, Reference) = 11 and then
        S.Member_Name_Is (Data, Reference, 0, "previous") and then
        S.Member_Name_Is (Data, Reference, 1, "generation") and then
        S.Member_Name_Is (Data, Reference, 2, "operation") and then
        S.Member_Name_Is (Data, Reference, 3, "subject_kind") and then
        S.Member_Name_Is (Data, Reference, 4, "subject") and then
        S.Member_Name_Is (Data, Reference, 5, "subgeneration") and then
        S.Member_Name_Is (Data, Reference, 6, "kind") and then
        S.Member_Name_Is (Data, Reference, 7, "actor") and then
        S.Member_Name_Is (Data, Reference, 8, "record") and then
        S.Member_Name_Is (Data, Reference, 9, "event_id") and then
        S.Member_Name_Is (Data, Reference, 10, "mac") and then
        Field_Same ("previous") and then Field_Same ("generation") and then
        Field_Same ("operation") and then Field_Same ("subject_kind") and then
        Field_Same ("subject") and then Field_Same ("subgeneration") and then
        Field_Same ("kind") and then Field_Same ("actor") and then
        Field_Same ("record") and then
        S.Text_Matches (Data, S.Field (Data, Reference, "event_id"), Raw.Event_Id) and then
        S.Text_Matches (Data, S.Field (Data, Reference, "mac"), Raw.Mac);
   end Reference_Matches;

   function Prior_Reference
     (Data : C.E.Bytes; Reference : C.E.Span; Events : C.Event_Rows;
      Consumer : Q.Byte_Index; Required : M.Event_Kind;
      Generation, Operation : C.E.Span) return Boolean
   is
   begin
      if Consumer not in Events'Range then return False; end if;
      for I in Events'Range loop
         pragma Loop_Variant (Increases => I);
         pragma Loop_Invariant
           (for all J in Events'First .. I - 1 =>
              not (J < Consumer and then
                   Same (Data, Events (J).Generation, Generation) and then
                   Same (Data, Events (J).Operation, Operation) and then
                   D.Decode (Data, Events (J)).Status = D.Decoded and then
                   D.Decode (Data, Events (J)).Value.Kind = Required and then
                   Reference_Matches (Data, Reference, Events (J))));
         if I < Consumer and then Same (Data, Events (I).Generation, Generation) and then
            Same (Data, Events (I).Operation, Operation) then
            declare
               Decoded : constant D.Decoded_Event := D.Decode (Data, Events (I));
            begin
               if Decoded.Status = D.Decoded and then Decoded.Value.Kind = Required and then
                  Reference_Matches (Data, Reference, Events (I)) then return True; end if;
            end;
         end if;
      end loop;
      return False;
   end Prior_Reference;
end Worldline.Custody_V2_Event_Joins;
