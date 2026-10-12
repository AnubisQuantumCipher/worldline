package body Resource_Actor_Admission_Wire with SPARK_Mode is
   function Decode_Capabilities (Data : Q.Byte_Array; V : Raw_Capability_Array) return A.Capability_Array is
      R : A.Capability_Array (V'Range);
   begin
      for I in V'Range loop
         pragma Loop_Invariant (for all J in V'Range => (if J < I then R (J) = Decode (Data, V (J))));
         R (I) := Decode (Data, V (I));
      end loop;
      return R;
   end Decode_Capabilities;
   function Decode_Groups (Data : Q.Byte_Array; V : Raw_Group_Array) return A.Group_Array is
      R : A.Group_Array (V'Range);
   begin
      for I in V'Range loop
         pragma Loop_Invariant (for all J in V'Range => (if J < I then R (J) = W.Decode (Data, V (J))));
         R (I) := W.Decode (Data, V (I));
      end loop;
      return R;
   end Decode_Groups;
end Resource_Actor_Admission_Wire;
