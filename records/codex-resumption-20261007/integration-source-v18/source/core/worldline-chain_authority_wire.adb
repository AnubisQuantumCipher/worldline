package body Worldline.Chain_Authority_Wire with SPARK_Mode is
   function Decide (Rows : A.Retained_Rows; Raw : Raw_Anchors) return Raw_Result is
      Verdict : constant A.Result := A.Replay
        (A.Chain_Kind'Val (Raw.Kind), Rows, Decode (Raw.Observed_Genesis),
         Decode (Raw.Witnessed_Genesis), Decode (Raw.Witnessed_Head));
   begin
      return (Disposition => A.Reason'Pos (Verdict.Disposition),
              Head => Raw_Hash (Verdict.Head),
              Accepted_Count => Interfaces.Integer_64 (Verdict.Accepted_Count));
   end Decide;
end Worldline.Chain_Authority_Wire;
