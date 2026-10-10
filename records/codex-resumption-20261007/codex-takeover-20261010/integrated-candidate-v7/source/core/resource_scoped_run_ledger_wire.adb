package body Resource_Scoped_Run_Ledger_Wire with SPARK_Mode is
   use type S.K.Facts;
   function Decode_History (Data : Q.Byte_Array; Raw : Raw_History_Array) return S.History_Array is
      Result : S.History_Array (Raw'Range);
   begin
      for I in Raw'Range loop
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J) = Decode (Data, Raw (J))));
         Result (I) := Decode (Data, Raw (I));
      end loop;
      return Result;
   end Decode_History;
   function Decode_Bucket (Data : Q.Byte_Array; Raw : Raw_Bucket_Array) return S.Bucket_Array is
      Result : S.Bucket_Array (Raw'Range);
   begin
      for I in Raw'Range loop
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J) = Decode (Data, Raw (J))));
         Result (I) := Decode (Data, Raw (I));
      end loop;
      return Result;
   end Decode_Bucket;
   function Decode_Projection (Data : Q.Byte_Array; Raw : Raw_Projection_Array) return S.Projection_Array is
      Result : S.Projection_Array (Raw'Range);
   begin
      for I in Raw'Range loop
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J) = Decode (Data, Raw (J))));
         Result (I) := Decode (Data, Raw (I));
      end loop;
      return Result;
   end Decode_Projection;
   function Decode_Facts (Data : Q.Byte_Array; Raw : Raw_Facts_Array) return S.Facts_Array is
      Result : S.Facts_Array (Raw'Range);
   begin
      for I in Raw'Range loop
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J) = O.Decode (Data, Raw (J))));
         Result (I) := O.Decode (Data, Raw (I));
      end loop;
      return Result;
   end Decode_Facts;
   function Decide (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return W.Raw_Result is
     (Status => S.Status'Pos (S.Check (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History),
        W.Decode_Rows (Data, Rows), Decode_Projection (Data, Projection), Decode_Bucket (Data, Buckets),
        Decode (Data, Raw.Proposed_State), Decode_History (Data, Proposed_History),
        W.Decode_Rows (Data, Proposed_Rows), Decode_Projection (Data, Proposed_Projection),
        Decode_Bucket (Data, Proposed_Buckets), W.Decode_Native (Data, Observed), Decode_Facts (Data, Facts),
        Decode_Bucket (Data, Actual_Buckets), Decode (Data, Raw.Current), Decode (Data, Raw.Request))));
   function Validate (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return W.Raw_Result is
     (Status => Boolean'Pos (S.Valid (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History), W.Decode_Rows (Data, Rows), Decode_Projection (Data, Projection), Decode_Bucket (Data, Buckets), Decode (Data, Raw.Current))));
   function Classify_Selected (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return W.Raw_Result
   is
   begin
      if Rows'Length /= Facts'Length or else not S.Shape (Data, Decode (Data, Raw.Before_State),
          Decode_History (Data, History), W.Decode_Rows (Data, Rows)) then return (Status => S.L.Liveness'Pos (S.L.Unknown)); end if;
      for I in reverse Rows'Range loop
         pragma Loop_Invariant
           (for all J in Rows'Range => (if J > I then not S.L.Same (Data,
             W.Decode (Data, Rows (J)).Bound.Reservation, W.Decode (Data, Raw.Request.Original).Reservation)));
         if S.L.Same (Data, W.Decode (Data, Rows (I)).Bound.Reservation,
                      W.Decode (Data, Raw.Request.Original).Reservation) then
            return (Status => S.L.Liveness'Pos (S.Classify
              (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History),
               W.Decode (Data, Rows (I)), O.Decode (Data, Facts (Facts'First + (I - Rows'First))))));
         end if;
      end loop;
      return (Status => S.L.Liveness'Pos (S.L.Unknown));
   end Classify_Selected;
end Resource_Scoped_Run_Ledger_Wire;
