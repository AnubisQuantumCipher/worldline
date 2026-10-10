package body Resource_Actor_Admission with SPARK_Mode is
   function Isolation (Data : Q.Byte_Array; C : Capability_Array;
                       G, Proc_G : Group_Array) return Boolean is
   begin
      if G'Length /= 0 or else Proc_G'Length /= 0 or else C'Length = 0 then return False; end if;
      for I in C'Range loop
         pragma Loop_Invariant
           (for all J in C'First .. I - 1 => Number (Data, C (J).Index)
            and then L.Exact_Value (Data, C (J).Index) = Count_Values.To_Big_Integer (J - C'First)
            and then Is_Number (Data, C (J).Bounding, 0)
            and then Is_Number (Data, C (J).Ambient, 0));
         if not Number (Data, C (I).Index)
           or else L.Exact_Value (Data, C (I).Index) /= Count_Values.To_Big_Integer (I - C'First)
           or else not Is_Number (Data, C (I).Bounding, 0)
           or else not Is_Number (Data, C (I).Ambient, 0) then return False; end if;
      end loop;
      return True;
   end Isolation;
   function Check (Data : Q.Byte_Array; State : S.State; H : S.History_Array;
                   Rows : L.Row_Array; P : S.Projection_Array; B : S.Bucket_Array;
                   N : L.Native_Array; F : S.Facts_Array; Current : S.Current_Observation;
                   O : Observation; C : Capability_Array; G, Proc_G : Group_Array) return Status is
   begin
      if not S.Valid (Data, State, H, Rows, P, B, Current) then return Invalid_Ledger;
      elsif not S.Native_Valid (Data, State, H, Rows, N, F) then return Invalid_Native_Roster;
      elsif not Complete (Data, O) then return Credential_Invalid;
      elsif not Running_Holds (Data, State, H, Rows, N, F, O) then return Running_Row_Absent;
      elsif not Requester_Holds (Data, O) then return Requester_Mismatch;
      elsif not Source_Holds (Data, O) then return Source_Mismatch;
      elsif not Credential_Holds (Data, O) then return Credential_Invalid;
      elsif not Isolation (Data, C, G, Proc_G) then return Isolation_Not_Established;
      else return Ready_Conjunct; end if;
   end Check;
end Resource_Actor_Admission;
