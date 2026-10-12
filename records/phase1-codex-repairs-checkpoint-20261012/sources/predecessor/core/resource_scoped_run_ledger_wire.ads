with Resource_Run_Ledger_Wire;
with Resource_Observation_Classification_Wire;
with Resource_Scoped_Run_Ledger;
package Resource_Scoped_Run_Ledger_Wire with SPARK_Mode is
   package W renames Resource_Run_Ledger_Wire;
   package O renames Resource_Observation_Classification_Wire;
   package S renames Resource_Scoped_Run_Ledger;
   package Q renames W.Q;
   package L renames W.L;
   use type W.U8;
   use type W.U32;
   use type Q.Byte_Count;
   use type S.K.Facts;
   type Raw_State is record
      Current : W.Raw_Context;
      Resource_Epoch : W.Raw_Epoch;
      Universe_Head : W.Raw_Id;
      Ledger_Head : W.Raw_Id;
      History_Head : W.Raw_Id;
      Physical_Head : W.Raw_Id;
   end record with Convention => C;
   use type S.State;
   type Raw_Scope_Frame is record
      Scope : W.Raw_Context;
      First_Epoch : W.Raw_Epoch;
      Universe_Head : W.Raw_Id;
      Frame_Head : W.Raw_Id;
      Prior_Frame : W.Raw_Id;
      Store_Genesis : W.Raw_Id;
      Store_Id : W.Raw_Id;
      Root_Head : W.Raw_Id;
      Prime : W.Raw_Id;
      Root_Count : W.Raw_Quantity;
      Cause : W.Raw_Id;
      Requester : W.Raw_Id;
      Receipt : W.Raw_Id;
      Catalogue_Head : W.Raw_Id;
      Observation_Head : W.Raw_Id;
   end record with Convention => C;
   use type S.Scope_Frame;
   type Raw_Physical_Key is record
      Machine : W.Raw_Id;
      Resource : W.Raw_Id;
      Unit : W.Raw_Id;
   end record with Convention => C;
   use type S.Physical_Key;
   type Raw_Bucket is record
      Key : Raw_Physical_Key;
      Capacity : W.Raw_Quantity;
      Held_Total : W.Raw_Quantity;
      Charged_Total : W.Raw_Quantity;
      Capacity_Source : W.Raw_Id;
      Catalogue_Head : W.Raw_Id;
      Observation_Head : W.Raw_Id;
   end record with Convention => C;
   use type S.Bucket;
   type Raw_Projection is record
      Key : Raw_Physical_Key;
      Bound : W.Raw_Binding;
      Origin : W.Raw_Context;
      Catalogue_Head : W.Raw_Id;
      Numerator : W.Raw_Quantity;
      Denominator : W.Raw_Quantity;
      Amount : W.Raw_Quantity;
   end record with Convention => C;
   use type S.Projection;
   type Raw_Current_Observation is record
      Scope : W.Raw_Context;
      Resource_Epoch : W.Raw_Epoch;
      Universe_Head : W.Raw_Id;
      Ledger_Head : W.Raw_Id;
      History_Head : W.Raw_Id;
      Physical_Head : W.Raw_Id;
      Store_Genesis : W.Raw_Id;
      Store_Id : W.Raw_Id;
      Root_Head : W.Raw_Id;
      Prime : W.Raw_Id;
      Root_Count : W.Raw_Quantity;
      Cause : W.Raw_Id;
      Requester : W.Raw_Id;
      Receipt : W.Raw_Id;
      Catalogue_Head : W.Raw_Id;
      Observation_Head : W.Raw_Id;
   end record with Convention => C;
   use type S.Current_Observation;
   type Raw_Intent is record
      Kind : W.U8;
      Original : W.Raw_Request;
      Expected_Epoch : W.Raw_Epoch;
      Expected_Ledger_Head : W.Raw_Id;
      Request_Id : W.Raw_Id;
      Cause : W.Raw_Id;
      Requester : W.Raw_Id;
      Receipt : W.Raw_Id;
   end record with Convention => C;
   use type S.Intent;
   type Raw_History_Array is array (Q.Byte_Index range <>) of Raw_Scope_Frame;
   type Raw_Bucket_Array is array (Q.Byte_Index range <>) of Raw_Bucket;
   type Raw_Projection_Array is array (Q.Byte_Index range <>) of Raw_Projection;
   type Raw_Facts_Array is array (Q.Byte_Index range <>) of O.Raw_Facts;
   type Raw_Packet is record
      Schema_Version : W.U32;
      Before_State, Proposed_State : Raw_State;
      Current : Raw_Current_Observation;
      Request : Raw_Intent;
   end record with Convention => C;
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_State) return Boolean is
     (W.Well_Formed (Data, Raw.Current)
      and then W.Well_Formed (Data, Raw.Resource_Epoch)
      and then W.Well_Formed (Data, Raw.Universe_Head)
      and then W.Well_Formed (Data, Raw.Ledger_Head)
      and then W.Well_Formed (Data, Raw.History_Head)
      and then W.Well_Formed (Data, Raw.Physical_Head)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_State) return S.State is
     (Current => W.Decode (Data, Raw.Current),
      Resource_Epoch => W.Decode (Data, Raw.Resource_Epoch),
      Universe_Head => W.Decode (Data, Raw.Universe_Head),
      Ledger_Head => W.Decode (Data, Raw.Ledger_Head),
      History_Head => W.Decode (Data, Raw.History_Head),
      Physical_Head => W.Decode (Data, Raw.Physical_Head))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Current => W.Decode (Data, Raw.Current),
      Resource_Epoch => W.Decode (Data, Raw.Resource_Epoch),
      Universe_Head => W.Decode (Data, Raw.Universe_Head),
      Ledger_Head => W.Decode (Data, Raw.Ledger_Head),
      History_Head => W.Decode (Data, Raw.History_Head),
      Physical_Head => W.Decode (Data, Raw.Physical_Head));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Scope_Frame) return Boolean is
     (W.Well_Formed (Data, Raw.Scope)
      and then W.Well_Formed (Data, Raw.First_Epoch)
      and then W.Well_Formed (Data, Raw.Universe_Head)
      and then W.Well_Formed (Data, Raw.Frame_Head)
      and then W.Well_Formed (Data, Raw.Prior_Frame)
      and then W.Well_Formed (Data, Raw.Store_Genesis)
      and then W.Well_Formed (Data, Raw.Store_Id)
      and then W.Well_Formed (Data, Raw.Root_Head)
      and then W.Well_Formed (Data, Raw.Prime)
      and then W.Well_Formed (Data, Raw.Root_Count)
      and then W.Well_Formed (Data, Raw.Cause)
      and then W.Well_Formed (Data, Raw.Requester)
      and then W.Well_Formed (Data, Raw.Receipt)
      and then W.Well_Formed (Data, Raw.Catalogue_Head)
      and then W.Well_Formed (Data, Raw.Observation_Head)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Scope_Frame) return S.Scope_Frame is
     (Scope => W.Decode (Data, Raw.Scope),
      First_Epoch => W.Decode (Data, Raw.First_Epoch),
      Universe_Head => W.Decode (Data, Raw.Universe_Head),
      Frame_Head => W.Decode (Data, Raw.Frame_Head),
      Prior_Frame => W.Decode (Data, Raw.Prior_Frame),
      Store_Genesis => W.Decode (Data, Raw.Store_Genesis),
      Store_Id => W.Decode (Data, Raw.Store_Id),
      Root_Head => W.Decode (Data, Raw.Root_Head),
      Prime => W.Decode (Data, Raw.Prime),
      Root_Count => W.Decode (Data, Raw.Root_Count),
      Cause => W.Decode (Data, Raw.Cause),
      Requester => W.Decode (Data, Raw.Requester),
      Receipt => W.Decode (Data, Raw.Receipt),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Observation_Head => W.Decode (Data, Raw.Observation_Head))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Scope => W.Decode (Data, Raw.Scope),
      First_Epoch => W.Decode (Data, Raw.First_Epoch),
      Universe_Head => W.Decode (Data, Raw.Universe_Head),
      Frame_Head => W.Decode (Data, Raw.Frame_Head),
      Prior_Frame => W.Decode (Data, Raw.Prior_Frame),
      Store_Genesis => W.Decode (Data, Raw.Store_Genesis),
      Store_Id => W.Decode (Data, Raw.Store_Id),
      Root_Head => W.Decode (Data, Raw.Root_Head),
      Prime => W.Decode (Data, Raw.Prime),
      Root_Count => W.Decode (Data, Raw.Root_Count),
      Cause => W.Decode (Data, Raw.Cause),
      Requester => W.Decode (Data, Raw.Requester),
      Receipt => W.Decode (Data, Raw.Receipt),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Observation_Head => W.Decode (Data, Raw.Observation_Head));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Physical_Key) return Boolean is
     (W.Well_Formed (Data, Raw.Machine)
      and then W.Well_Formed (Data, Raw.Resource)
      and then W.Well_Formed (Data, Raw.Unit)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Physical_Key) return S.Physical_Key is
     (Machine => W.Decode (Data, Raw.Machine),
      Resource => W.Decode (Data, Raw.Resource),
      Unit => W.Decode (Data, Raw.Unit))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Machine => W.Decode (Data, Raw.Machine),
      Resource => W.Decode (Data, Raw.Resource),
      Unit => W.Decode (Data, Raw.Unit));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Bucket) return Boolean is
     (Well_Formed (Data, Raw.Key)
      and then W.Well_Formed (Data, Raw.Capacity)
      and then W.Well_Formed (Data, Raw.Held_Total)
      and then W.Well_Formed (Data, Raw.Charged_Total)
      and then W.Well_Formed (Data, Raw.Capacity_Source)
      and then W.Well_Formed (Data, Raw.Catalogue_Head)
      and then W.Well_Formed (Data, Raw.Observation_Head)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Bucket) return S.Bucket is
     (Key => Decode (Data, Raw.Key),
      Capacity => W.Decode (Data, Raw.Capacity),
      Held_Total => W.Decode (Data, Raw.Held_Total),
      Charged_Total => W.Decode (Data, Raw.Charged_Total),
      Capacity_Source => W.Decode (Data, Raw.Capacity_Source),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Observation_Head => W.Decode (Data, Raw.Observation_Head))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Key => Decode (Data, Raw.Key),
      Capacity => W.Decode (Data, Raw.Capacity),
      Held_Total => W.Decode (Data, Raw.Held_Total),
      Charged_Total => W.Decode (Data, Raw.Charged_Total),
      Capacity_Source => W.Decode (Data, Raw.Capacity_Source),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Observation_Head => W.Decode (Data, Raw.Observation_Head));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Projection) return Boolean is
     (Well_Formed (Data, Raw.Key)
      and then W.Well_Formed (Data, Raw.Bound)
      and then W.Well_Formed (Data, Raw.Origin)
      and then W.Well_Formed (Data, Raw.Catalogue_Head)
      and then W.Well_Formed (Data, Raw.Numerator)
      and then W.Well_Formed (Data, Raw.Denominator)
      and then W.Well_Formed (Data, Raw.Amount)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Projection) return S.Projection is
     (Key => Decode (Data, Raw.Key),
      Bound => W.Decode (Data, Raw.Bound),
      Origin => W.Decode (Data, Raw.Origin),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Numerator => W.Decode (Data, Raw.Numerator),
      Denominator => W.Decode (Data, Raw.Denominator),
      Amount => W.Decode (Data, Raw.Amount))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Key => Decode (Data, Raw.Key),
      Bound => W.Decode (Data, Raw.Bound),
      Origin => W.Decode (Data, Raw.Origin),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Numerator => W.Decode (Data, Raw.Numerator),
      Denominator => W.Decode (Data, Raw.Denominator),
      Amount => W.Decode (Data, Raw.Amount));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Current_Observation) return Boolean is
     (W.Well_Formed (Data, Raw.Scope)
      and then W.Well_Formed (Data, Raw.Resource_Epoch)
      and then W.Well_Formed (Data, Raw.Universe_Head)
      and then W.Well_Formed (Data, Raw.Ledger_Head)
      and then W.Well_Formed (Data, Raw.History_Head)
      and then W.Well_Formed (Data, Raw.Physical_Head)
      and then W.Well_Formed (Data, Raw.Store_Genesis)
      and then W.Well_Formed (Data, Raw.Store_Id)
      and then W.Well_Formed (Data, Raw.Root_Head)
      and then W.Well_Formed (Data, Raw.Prime)
      and then W.Well_Formed (Data, Raw.Root_Count)
      and then W.Well_Formed (Data, Raw.Cause)
      and then W.Well_Formed (Data, Raw.Requester)
      and then W.Well_Formed (Data, Raw.Receipt)
      and then W.Well_Formed (Data, Raw.Catalogue_Head)
      and then W.Well_Formed (Data, Raw.Observation_Head)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Current_Observation) return S.Current_Observation is
     (Scope => W.Decode (Data, Raw.Scope),
      Resource_Epoch => W.Decode (Data, Raw.Resource_Epoch),
      Universe_Head => W.Decode (Data, Raw.Universe_Head),
      Ledger_Head => W.Decode (Data, Raw.Ledger_Head),
      History_Head => W.Decode (Data, Raw.History_Head),
      Physical_Head => W.Decode (Data, Raw.Physical_Head),
      Store_Genesis => W.Decode (Data, Raw.Store_Genesis),
      Store_Id => W.Decode (Data, Raw.Store_Id),
      Root_Head => W.Decode (Data, Raw.Root_Head),
      Prime => W.Decode (Data, Raw.Prime),
      Root_Count => W.Decode (Data, Raw.Root_Count),
      Cause => W.Decode (Data, Raw.Cause),
      Requester => W.Decode (Data, Raw.Requester),
      Receipt => W.Decode (Data, Raw.Receipt),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Observation_Head => W.Decode (Data, Raw.Observation_Head))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Scope => W.Decode (Data, Raw.Scope),
      Resource_Epoch => W.Decode (Data, Raw.Resource_Epoch),
      Universe_Head => W.Decode (Data, Raw.Universe_Head),
      Ledger_Head => W.Decode (Data, Raw.Ledger_Head),
      History_Head => W.Decode (Data, Raw.History_Head),
      Physical_Head => W.Decode (Data, Raw.Physical_Head),
      Store_Genesis => W.Decode (Data, Raw.Store_Genesis),
      Store_Id => W.Decode (Data, Raw.Store_Id),
      Root_Head => W.Decode (Data, Raw.Root_Head),
      Prime => W.Decode (Data, Raw.Prime),
      Root_Count => W.Decode (Data, Raw.Root_Count),
      Cause => W.Decode (Data, Raw.Cause),
      Requester => W.Decode (Data, Raw.Requester),
      Receipt => W.Decode (Data, Raw.Receipt),
      Catalogue_Head => W.Decode (Data, Raw.Catalogue_Head),
      Observation_Head => W.Decode (Data, Raw.Observation_Head));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Intent) return Boolean is
     (Raw.Kind <= S.Action'Pos (S.Action'Last)
      and then W.Well_Formed (Data, Raw.Original)
      and then W.Well_Formed (Data, Raw.Expected_Epoch)
      and then W.Well_Formed (Data, Raw.Expected_Ledger_Head)
      and then W.Well_Formed (Data, Raw.Request_Id)
      and then W.Well_Formed (Data, Raw.Cause)
      and then W.Well_Formed (Data, Raw.Requester)
      and then W.Well_Formed (Data, Raw.Receipt)) with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Intent) return S.Intent is
     (Kind => S.Action'Val (Raw.Kind),
      Original => W.Decode (Data, Raw.Original),
      Expected_Epoch => W.Decode (Data, Raw.Expected_Epoch),
      Expected_Ledger_Head => W.Decode (Data, Raw.Expected_Ledger_Head),
      Request_Id => W.Decode (Data, Raw.Request_Id),
      Cause => W.Decode (Data, Raw.Cause),
      Requester => W.Decode (Data, Raw.Requester),
      Receipt => W.Decode (Data, Raw.Receipt))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result = (Kind => S.Action'Val (Raw.Kind),
      Original => W.Decode (Data, Raw.Original),
      Expected_Epoch => W.Decode (Data, Raw.Expected_Epoch),
      Expected_Ledger_Head => W.Decode (Data, Raw.Expected_Ledger_Head),
      Request_Id => W.Decode (Data, Raw.Request_Id),
      Cause => W.Decode (Data, Raw.Cause),
      Requester => W.Decode (Data, Raw.Requester),
      Receipt => W.Decode (Data, Raw.Receipt));
   function Decode_History (Data : Q.Byte_Array; Raw : Raw_History_Array) return S.History_Array
   with Global => null, Pre => (for all I in Raw'Range => Well_Formed (Data, Raw (I))),
     Post => Decode_History'Result'First = Raw'First and then Decode_History'Result'Length = Raw'Length
       and then (for all I in Raw'Range => Decode_History'Result (I) = Decode (Data, Raw (I)));
   function Decode_Bucket (Data : Q.Byte_Array; Raw : Raw_Bucket_Array) return S.Bucket_Array
   with Global => null, Pre => (for all I in Raw'Range => Well_Formed (Data, Raw (I))),
     Post => Decode_Bucket'Result'First = Raw'First and then Decode_Bucket'Result'Length = Raw'Length
       and then (for all I in Raw'Range => Decode_Bucket'Result (I) = Decode (Data, Raw (I)));
   function Decode_Projection (Data : Q.Byte_Array; Raw : Raw_Projection_Array) return S.Projection_Array
   with Global => null, Pre => (for all I in Raw'Range => Well_Formed (Data, Raw (I))),
     Post => Decode_Projection'Result'First = Raw'First and then Decode_Projection'Result'Length = Raw'Length
       and then (for all I in Raw'Range => Decode_Projection'Result (I) = Decode (Data, Raw (I)));
   function Decode_Facts (Data : Q.Byte_Array; Raw : Raw_Facts_Array) return S.Facts_Array
   with Global => null, Pre => (for all I in Raw'Range => O.Well_Formed (Data, Raw (I))),
     Post => Decode_Facts'Result'First = Raw'First and then Decode_Facts'Result'Length = Raw'Length
       and then (for all I in Raw'Range => Decode_Facts'Result (I) = O.Decode (Data, Raw (I)));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return Boolean is
     (Raw.Schema_Version = 1
      and then Well_Formed (Data, Raw.Before_State)
      and then Well_Formed (Data, Raw.Proposed_State)
      and then Well_Formed (Data, Raw.Current)
      and then Well_Formed (Data, Raw.Request)
      and then (for all I in History'Range => Well_Formed (Data, History (I)))
      and then (for all I in Proposed_History'Range => Well_Formed (Data, Proposed_History (I)))
      and then (for all I in Rows'Range => W.Well_Formed (Data, Rows (I)))
      and then (for all I in Proposed_Rows'Range => W.Well_Formed (Data, Proposed_Rows (I)))
      and then (for all I in Projection'Range => Well_Formed (Data, Projection (I)))
      and then (for all I in Proposed_Projection'Range => Well_Formed (Data, Proposed_Projection (I)))
      and then (for all I in Buckets'Range => Well_Formed (Data, Buckets (I)))
      and then (for all I in Proposed_Buckets'Range => Well_Formed (Data, Proposed_Buckets (I)))
      and then (for all I in Actual_Buckets'Range => Well_Formed (Data, Actual_Buckets (I)))
      and then (for all I in Observed'Range => W.Well_Formed (Data, Observed (I)))
      and then (for all I in Facts'Range => O.Well_Formed (Data, Facts (I)))) with Global => null;
   function Decide (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return W.Raw_Result
   with Global => null, Pre => Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts),
     Post => Decide'Result.Status = S.Status'Pos (S.Decision_Reference (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History),
        W.Decode_Rows (Data, Rows), Decode_Projection (Data, Projection), Decode_Bucket (Data, Buckets),
        Decode (Data, Raw.Proposed_State), Decode_History (Data, Proposed_History),
        W.Decode_Rows (Data, Proposed_Rows), Decode_Projection (Data, Proposed_Projection),
        Decode_Bucket (Data, Proposed_Buckets), W.Decode_Native (Data, Observed), Decode_Facts (Data, Facts),
        Decode_Bucket (Data, Actual_Buckets), Decode (Data, Raw.Current), Decode (Data, Raw.Request)));
   -- Snapshot consistency only; cannot authorize any effect.
   function Validate (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return W.Raw_Result
   with Global => null, Pre => Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts),
     Post => Validate'Result.Status = Boolean'Pos (S.Valid_Reference (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History), W.Decode_Rows (Data, Rows), Decode_Projection (Data, Projection), Decode_Bucket (Data, Buckets), Decode (Data, Raw.Current)));
   function Selected_Reference (Data : Q.Byte_Array; Raw : Raw_Packet;
      History : Raw_History_Array; Rows : W.Raw_Row_Array; Facts : Raw_Facts_Array;
      Count : Q.Byte_Count) return S.L.Liveness is
     (if Count = 0 or else Rows'Length /= Facts'Length then S.L.Unknown
      elsif not S.Shape (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History), W.Decode_Rows (Data, Rows)) then S.L.Unknown
      elsif S.L.Same (Data, W.Decode (Data, Rows (Rows'First + (Count - 1))).Bound.Reservation,
                      W.Decode (Data, Raw.Request.Original).Reservation) then
        S.Classify_Reference (Data, Decode (Data, Raw.Before_State), Decode_History (Data, History),
          W.Decode (Data, Rows (Rows'First + (Count - 1))), O.Decode (Data, Facts (Facts'First + (Count - 1))))
      else Selected_Reference (Data, Raw, History, Rows, Facts, Count - 1))
   with Ghost, Global => null,
     Pre => Count <= Rows'Length and then Count <= Facts'Length
       and then Well_Formed (Data, Raw.Before_State) and then Well_Formed (Data, Raw.Request)
       and then (for all I in History'Range => Well_Formed (Data, History (I)))
       and then (for all I in Rows'Range => W.Well_Formed (Data, Rows (I)))
       and then (for all I in Facts'Range => O.Well_Formed (Data, Facts (I))),
     Subprogram_Variant => (Decreases => Count);
   function Classify_Selected (Data : Q.Byte_Array; Raw : Raw_Packet;
      History, Proposed_History : Raw_History_Array;
      Rows, Proposed_Rows : W.Raw_Row_Array;
      Projection, Proposed_Projection : Raw_Projection_Array;
      Buckets, Proposed_Buckets, Actual_Buckets : Raw_Bucket_Array;
      Observed : W.Raw_Native_Array; Facts : Raw_Facts_Array) return W.Raw_Result
   with Global => null, Pre => Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts),
     Post => Classify_Selected'Result.Status = S.L.Liveness'Pos
       (if Rows'Length /= Facts'Length then S.L.Unknown
        else Selected_Reference (Data, Raw, History, Rows, Facts, Rows'Length));
end Resource_Scoped_Run_Ledger_Wire;
