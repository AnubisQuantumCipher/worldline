package body Resource_Observation_Classification_Wire with SPARK_Mode is
   function Current (Data : Q.Byte_Array; Raw : Raw_Input) return Boolean is
   begin
      if not W.Well_Formed (Data, Raw.State) or else not Well_Formed (Data, Raw.Captured) then return False; end if;
      return K.Current (Data, W.Decode (Data, Raw.State), Decode (Data, Raw.Captured));
   end Current;
   function Genesis_Current (Data : Q.Byte_Array; Raw : Raw_Input) return Boolean is
   begin
      if not W.Well_Formed (Data, Raw.State) or else not Well_Formed (Data, Raw.Captured) then return False; end if;
      return K.Genesis_Current (Data, W.Decode (Data, Raw.State), Decode (Data, Raw.Captured));
   end Genesis_Current;
   function Classify (Data : Q.Byte_Array; Raw : Raw_Input) return L.Liveness is
   begin
      if not W.Well_Formed (Data, Raw.State) or else not W.Well_Formed (Data, Raw.Item)
        or else not Well_Formed (Data, Raw.Captured) then return L.Unknown; end if;
      return K.Classify (Data, W.Decode (Data, Raw.State), W.Decode (Data, Raw.Item), Decode (Data, Raw.Captured));
   end Classify;
end Resource_Observation_Classification_Wire;
