with Interfaces;
with Resource_Quantities;
with Resource_Run_Ledger;
package Resource_Run_Ledger_Wire with SPARK_Mode is
   package Q renames Resource_Quantities;
   package L renames Resource_Run_Ledger;
   subtype U8 is Interfaces.Unsigned_8;
   subtype U32 is Interfaces.Unsigned_32;
   subtype I64 is Interfaces.Integer_64;
   use type U8;
   use type U32;
   use type I64;
   use type Q.Byte_Count;
   use type Q.Quantity;
   type Raw_Id is record
      Present : U8;
      First : I64;
      Length : I64;
   end record with Convention => C;
   --  Preserve the compiler-observed C ABI as explicit proof-visible layout.
   for Raw_Id use record
      Present at 0 range 0 .. 7;
      First at 8 range 0 .. 63;
      Length at 16 range 0 .. 63;
   end record;
   for Raw_Id'Size use 192;
   for Raw_Id'Alignment use 8;
   type Raw_Quantity is record
      Negative : U8;
      First : I64;
      Length : I64;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Quantity use record
      Negative at 0 range 0 .. 7;
      First at 8 range 0 .. 63;
      Length at 16 range 0 .. 63;
   end record;
   for Raw_Quantity'Size use 192;
   for Raw_Quantity'Object_Size use 192;
   for Raw_Quantity'Alignment use 8;
   type Raw_Epoch is record
      Present : U8;
      Value : Raw_Quantity;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Epoch use record
      Present at 0 range 0 .. 7;
      Value at 8 range 0 .. 191;
   end record;
   for Raw_Epoch'Size use 256;
   for Raw_Epoch'Object_Size use 256;
   for Raw_Epoch'Alignment use 8;
   type Raw_Context is record
      Universe : Raw_Id;
      Policy : Raw_Id;
      Resource : Raw_Id;
      Unit : Raw_Id;
      Instance : Raw_Id;
      Host : Raw_Id;
      Boot : Raw_Id;
      Authority : Raw_Id;
      Policy_Epoch : Raw_Epoch;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Context use record
      Universe at 0 range 0 .. 191;
      Policy at 24 range 0 .. 191;
      Resource at 48 range 0 .. 191;
      Unit at 72 range 0 .. 191;
      Instance at 96 range 0 .. 191;
      Host at 120 range 0 .. 191;
      Boot at 144 range 0 .. 191;
      Authority at 168 range 0 .. 191;
      Policy_Epoch at 192 range 0 .. 255;
   end record;
   for Raw_Context'Size use 1792;
   for Raw_Context'Object_Size use 1792;
   for Raw_Context'Alignment use 8;
   type Raw_Binding is record
      Reservation : Raw_Id;
      Operation : Raw_Id;
      Owner : Raw_Id;
      Workload : Raw_Id;
      Universe_Head : Raw_Id;
      Capability : Raw_Id;
      Grant_Use : Raw_Id;
      Payload : Raw_Id;
      Provenance : Raw_Id;
      Resource_Epoch : Raw_Epoch;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Binding use record
      Reservation at 0 range 0 .. 191;
      Operation at 24 range 0 .. 191;
      Owner at 48 range 0 .. 191;
      Workload at 72 range 0 .. 191;
      Universe_Head at 96 range 0 .. 191;
      Capability at 120 range 0 .. 191;
      Grant_Use at 144 range 0 .. 191;
      Payload at 168 range 0 .. 191;
      Provenance at 192 range 0 .. 191;
      Resource_Epoch at 216 range 0 .. 255;
   end record;
   for Raw_Binding'Size use 1984;
   for Raw_Binding'Object_Size use 1984;
   for Raw_Binding'Alignment use 8;
   type Raw_Row is record
      Scope : Raw_Context;
      Bound : Raw_Binding;
      Parent : Raw_Id;
      Kind : U8;
      State : U8;
      Amount : Raw_Quantity;
      Observed_Usage : Raw_Epoch;
      Planned_Unit : Raw_Id;
      Actual_Unit : Raw_Id;
      Cgroup : Raw_Id;
      Invocation : Raw_Id;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Row use record
      Scope at 0 range 0 .. 1791;
      Bound at 224 range 0 .. 1983;
      Parent at 472 range 0 .. 191;
      Kind at 496 range 0 .. 7;
      State at 497 range 0 .. 7;
      Amount at 504 range 0 .. 191;
      Observed_Usage at 528 range 0 .. 255;
      Planned_Unit at 560 range 0 .. 191;
      Actual_Unit at 584 range 0 .. 191;
      Cgroup at 608 range 0 .. 191;
      Invocation at 632 range 0 .. 191;
   end record;
   for Raw_Row'Size use 5248;
   for Raw_Row'Object_Size use 5248;
   for Raw_Row'Alignment use 8;
   type Raw_State is record
      Scope : Raw_Context;
      Resource_Epoch : Raw_Epoch;
      Universe_Head : Raw_Id;
      Ledger_Head : Raw_Id;
      Capacity : Raw_Quantity;
      Held_Total : Raw_Quantity;
      Charged_Total : Raw_Quantity;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_State use record
      Scope at 0 range 0 .. 1791;
      Resource_Epoch at 224 range 0 .. 255;
      Universe_Head at 256 range 0 .. 191;
      Ledger_Head at 280 range 0 .. 191;
      Capacity at 304 range 0 .. 191;
      Held_Total at 328 range 0 .. 191;
      Charged_Total at 352 range 0 .. 191;
   end record;
   for Raw_State'Size use 3008;
   for Raw_State'Object_Size use 3008;
   for Raw_State'Alignment use 8;
   type Raw_Native is record
      Scope : Raw_Context;
      Resource_Epoch : Raw_Epoch;
      Bound : Raw_Binding;
      Actual_Unit : Raw_Id;
      Cgroup : Raw_Id;
      Invocation : Raw_Id;
      Observation_Head : Raw_Id;
      Observed : U8;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Native use record
      Scope at 0 range 0 .. 1791;
      Resource_Epoch at 224 range 0 .. 255;
      Bound at 256 range 0 .. 1983;
      Actual_Unit at 504 range 0 .. 191;
      Cgroup at 528 range 0 .. 191;
      Invocation at 552 range 0 .. 191;
      Observation_Head at 576 range 0 .. 191;
      Observed at 600 range 0 .. 7;
   end record;
   for Raw_Native'Size use 4808;
   for Raw_Native'Object_Size use 4864;
   for Raw_Native'Alignment use 8;
   type Raw_Request is record
      Kind : U8;
      Scope : Raw_Context;
      Expected_Epoch : Raw_Epoch;
      Expected_Ledger_Head : Raw_Id;
      Request_Id : Raw_Id;
      Reservation : Raw_Id;
      Operation_Id : Raw_Id;
      Requester : Raw_Id;
      Bound : Raw_Binding;
      New_Row : Raw_Row;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Request use record
      Kind at 0 range 0 .. 7;
      Scope at 8 range 0 .. 1791;
      Expected_Epoch at 232 range 0 .. 255;
      Expected_Ledger_Head at 264 range 0 .. 191;
      Request_Id at 288 range 0 .. 191;
      Reservation at 312 range 0 .. 191;
      Operation_Id at 336 range 0 .. 191;
      Requester at 360 range 0 .. 191;
      Bound at 384 range 0 .. 1983;
      New_Row at 632 range 0 .. 5247;
   end record;
   for Raw_Request'Size use 10304;
   for Raw_Request'Object_Size use 10304;
   for Raw_Request'Alignment use 8;
   type Raw_Packet is record
      Schema_Version : U32;
      Before_State : Raw_State;
      Proposed_State : Raw_State;
      Intent : Raw_Request;
   end record with Convention => C;
   type Raw_Result is record
      Status : U32;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Result use record
      Status at 0 range 0 .. 31;
   end record;
   for Raw_Result'Size use 32;
   for Raw_Result'Object_Size use 32;
   for Raw_Result'Alignment use 4;
   type Raw_Row_Array is array (Q.Byte_Index range <>) of Raw_Row;
   type Raw_Native_Array is array (Q.Byte_Index range <>) of Raw_Native;
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Id) return Boolean is
     (Raw.Present <= 1 and then Raw.First >= 1 and then Raw.Length >= 0
      and then Raw.First <= I64 (Q.Byte_Index'Last) and then Raw.Length <= I64 (Q.Byte_Count'Last)
      and then (if Raw.Present = 0 then Raw.First = 1 and then Raw.Length = 0
        else Raw.Length = 0 or else
          (Q.Byte_Index (Raw.First) in Data'Range and then
           Q.Byte_Count (Raw.Length) - 1 <= Data'Last - Q.Byte_Index (Raw.First))))
   with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Id) return L.Identity is
     (if Raw.Present = 0 then (Present => False)
      else (Present => True, Value => (First => Q.Byte_Index (Raw.First), Length => Q.Byte_Count (Raw.Length))))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result.Present = (Raw.Present = 1)
       and then (if Decode'Result.Present then
         Decode'Result.Value.First = Q.Byte_Index (Raw.First)
         and then Decode'Result.Value.Length = Q.Byte_Count (Raw.Length));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Quantity) return Boolean is
     (Raw.Negative <= 1 and then Raw.First >= 1 and then Raw.Length >= 0
      and then Raw.First <= I64 (Q.Byte_Index'Last) and then Raw.Length <= I64 (Q.Byte_Count'Last)
      and then (Raw.Length = 0 or else
        (Q.Byte_Index (Raw.First) in Data'Range and then
         Q.Byte_Count (Raw.Length) - 1 <= Data'Last - Q.Byte_Index (Raw.First))))
   with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Quantity) return Q.Quantity is
     (Negative => Raw.Negative = 1, First => Q.Byte_Index (Raw.First), Length => Q.Byte_Count (Raw.Length))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result.Negative = (Raw.Negative = 1)
       and then Decode'Result.First = Q.Byte_Index (Raw.First)
       and then Decode'Result.Length = Q.Byte_Count (Raw.Length);
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Epoch) return Boolean is
     (Raw.Present <= 1 and then Well_Formed (Data, Raw.Value)
      and then (if Raw.Present = 0 then
        Raw.Value.Negative = 0 and then Raw.Value.First = 1 and then Raw.Value.Length = 0))
   with Global => null;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Epoch) return Q.Optional_Quantity is
     (if Raw.Present = 0 then (Present => False)
      else (Present => True, Value => Decode (Data, Raw.Value)))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result.Present = (Raw.Present = 1)
       and then (if Decode'Result.Present then Decode'Result.Value = Decode (Data, Raw.Value));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Context) return Boolean is
     (Well_Formed (Data, Raw.Universe)
      and then Well_Formed (Data, Raw.Policy)
      and then Well_Formed (Data, Raw.Resource)
      and then Well_Formed (Data, Raw.Unit)
      and then Well_Formed (Data, Raw.Instance)
      and then Well_Formed (Data, Raw.Host)
      and then Well_Formed (Data, Raw.Boot)
      and then Well_Formed (Data, Raw.Authority)
      and then Well_Formed (Data, Raw.Policy_Epoch)) with Global => null;
   use type L.Context;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Context) return L.Context is
     (Universe => Decode (Data, Raw.Universe),
      Policy => Decode (Data, Raw.Policy),
      Resource => Decode (Data, Raw.Resource),
      Unit => Decode (Data, Raw.Unit),
      Instance => Decode (Data, Raw.Instance),
      Host => Decode (Data, Raw.Host),
      Boot => Decode (Data, Raw.Boot),
      Authority => Decode (Data, Raw.Authority),
      Policy_Epoch => Decode (Data, Raw.Policy_Epoch))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result =
     (Universe => Decode (Data, Raw.Universe),
      Policy => Decode (Data, Raw.Policy),
      Resource => Decode (Data, Raw.Resource),
      Unit => Decode (Data, Raw.Unit),
      Instance => Decode (Data, Raw.Instance),
      Host => Decode (Data, Raw.Host),
      Boot => Decode (Data, Raw.Boot),
      Authority => Decode (Data, Raw.Authority),
      Policy_Epoch => Decode (Data, Raw.Policy_Epoch));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Binding) return Boolean is
     (Well_Formed (Data, Raw.Reservation)
      and then Well_Formed (Data, Raw.Operation)
      and then Well_Formed (Data, Raw.Owner)
      and then Well_Formed (Data, Raw.Workload)
      and then Well_Formed (Data, Raw.Universe_Head)
      and then Well_Formed (Data, Raw.Capability)
      and then Well_Formed (Data, Raw.Grant_Use)
      and then Well_Formed (Data, Raw.Payload)
      and then Well_Formed (Data, Raw.Provenance)
      and then Well_Formed (Data, Raw.Resource_Epoch)) with Global => null;
   use type L.Binding;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Binding) return L.Binding is
     (Reservation => Decode (Data, Raw.Reservation),
      Operation => Decode (Data, Raw.Operation),
      Owner => Decode (Data, Raw.Owner),
      Workload => Decode (Data, Raw.Workload),
      Universe_Head => Decode (Data, Raw.Universe_Head),
      Capability => Decode (Data, Raw.Capability),
      Grant_Use => Decode (Data, Raw.Grant_Use),
      Payload => Decode (Data, Raw.Payload),
      Provenance => Decode (Data, Raw.Provenance),
      Resource_Epoch => Decode (Data, Raw.Resource_Epoch))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result =
     (Reservation => Decode (Data, Raw.Reservation),
      Operation => Decode (Data, Raw.Operation),
      Owner => Decode (Data, Raw.Owner),
      Workload => Decode (Data, Raw.Workload),
      Universe_Head => Decode (Data, Raw.Universe_Head),
      Capability => Decode (Data, Raw.Capability),
      Grant_Use => Decode (Data, Raw.Grant_Use),
      Payload => Decode (Data, Raw.Payload),
      Provenance => Decode (Data, Raw.Provenance),
      Resource_Epoch => Decode (Data, Raw.Resource_Epoch));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Row) return Boolean is
     (Well_Formed (Data, Raw.Scope)
      and then Well_Formed (Data, Raw.Bound)
      and then Well_Formed (Data, Raw.Parent)
      and then Raw.Kind <= L.Charge_Kind'Pos (L.Charge_Kind'Last)
      and then Raw.State <= L.Phase'Pos (L.Phase'Last)
      and then Well_Formed (Data, Raw.Amount)
      and then Well_Formed (Data, Raw.Observed_Usage)
      and then Well_Formed (Data, Raw.Planned_Unit)
      and then Well_Formed (Data, Raw.Actual_Unit)
      and then Well_Formed (Data, Raw.Cgroup)
      and then Well_Formed (Data, Raw.Invocation)) with Global => null;
   use type L.Row;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Row) return L.Row is
     (Scope => Decode (Data, Raw.Scope),
      Bound => Decode (Data, Raw.Bound),
      Parent => Decode (Data, Raw.Parent),
      Kind => L.Charge_Kind'Val (Raw.Kind),
      State => L.Phase'Val (Raw.State),
      Amount => Decode (Data, Raw.Amount),
      Observed_Usage => Decode (Data, Raw.Observed_Usage),
      Planned_Unit => Decode (Data, Raw.Planned_Unit),
      Actual_Unit => Decode (Data, Raw.Actual_Unit),
      Cgroup => Decode (Data, Raw.Cgroup),
      Invocation => Decode (Data, Raw.Invocation))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result =
     (Scope => Decode (Data, Raw.Scope),
      Bound => Decode (Data, Raw.Bound),
      Parent => Decode (Data, Raw.Parent),
      Kind => L.Charge_Kind'Val (Raw.Kind),
      State => L.Phase'Val (Raw.State),
      Amount => Decode (Data, Raw.Amount),
      Observed_Usage => Decode (Data, Raw.Observed_Usage),
      Planned_Unit => Decode (Data, Raw.Planned_Unit),
      Actual_Unit => Decode (Data, Raw.Actual_Unit),
      Cgroup => Decode (Data, Raw.Cgroup),
      Invocation => Decode (Data, Raw.Invocation));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_State) return Boolean is
     (Well_Formed (Data, Raw.Scope)
      and then Well_Formed (Data, Raw.Resource_Epoch)
      and then Well_Formed (Data, Raw.Universe_Head)
      and then Well_Formed (Data, Raw.Ledger_Head)
      and then Well_Formed (Data, Raw.Capacity)
      and then Well_Formed (Data, Raw.Held_Total)
      and then Well_Formed (Data, Raw.Charged_Total)) with Global => null;
   use type L.Ledger_State;
   function Decode (Data : Q.Byte_Array; Raw : Raw_State) return L.Ledger_State is
     (Scope => Decode (Data, Raw.Scope),
      Resource_Epoch => Decode (Data, Raw.Resource_Epoch),
      Universe_Head => Decode (Data, Raw.Universe_Head),
      Ledger_Head => Decode (Data, Raw.Ledger_Head),
      Capacity => Decode (Data, Raw.Capacity),
      Held_Total => Decode (Data, Raw.Held_Total),
      Charged_Total => Decode (Data, Raw.Charged_Total))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result =
     (Scope => Decode (Data, Raw.Scope),
      Resource_Epoch => Decode (Data, Raw.Resource_Epoch),
      Universe_Head => Decode (Data, Raw.Universe_Head),
      Ledger_Head => Decode (Data, Raw.Ledger_Head),
      Capacity => Decode (Data, Raw.Capacity),
      Held_Total => Decode (Data, Raw.Held_Total),
      Charged_Total => Decode (Data, Raw.Charged_Total));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Native) return Boolean is
     (Well_Formed (Data, Raw.Scope)
      and then Well_Formed (Data, Raw.Resource_Epoch)
      and then Well_Formed (Data, Raw.Bound)
      and then Well_Formed (Data, Raw.Actual_Unit)
      and then Well_Formed (Data, Raw.Cgroup)
      and then Well_Formed (Data, Raw.Invocation)
      and then Well_Formed (Data, Raw.Observation_Head)
      and then Raw.Observed <= L.Liveness'Pos (L.Liveness'Last)) with Global => null;
   use type L.Native_Row;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Native) return L.Native_Row is
     (Scope => Decode (Data, Raw.Scope),
      Resource_Epoch => Decode (Data, Raw.Resource_Epoch),
      Bound => Decode (Data, Raw.Bound),
      Actual_Unit => Decode (Data, Raw.Actual_Unit),
      Cgroup => Decode (Data, Raw.Cgroup),
      Invocation => Decode (Data, Raw.Invocation),
      Observation_Head => Decode (Data, Raw.Observation_Head),
      Observed => L.Liveness'Val (Raw.Observed))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result =
     (Scope => Decode (Data, Raw.Scope),
      Resource_Epoch => Decode (Data, Raw.Resource_Epoch),
      Bound => Decode (Data, Raw.Bound),
      Actual_Unit => Decode (Data, Raw.Actual_Unit),
      Cgroup => Decode (Data, Raw.Cgroup),
      Invocation => Decode (Data, Raw.Invocation),
      Observation_Head => Decode (Data, Raw.Observation_Head),
      Observed => L.Liveness'Val (Raw.Observed));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Request) return Boolean is
     (Raw.Kind <= L.Operation'Pos (L.Operation'Last)
      and then Well_Formed (Data, Raw.Scope)
      and then Well_Formed (Data, Raw.Expected_Epoch)
      and then Well_Formed (Data, Raw.Expected_Ledger_Head)
      and then Well_Formed (Data, Raw.Request_Id)
      and then Well_Formed (Data, Raw.Reservation)
      and then Well_Formed (Data, Raw.Operation_Id)
      and then Well_Formed (Data, Raw.Requester)
      and then Well_Formed (Data, Raw.Bound)
      and then Well_Formed (Data, Raw.New_Row)) with Global => null;
   use type L.Request;
   function Decode (Data : Q.Byte_Array; Raw : Raw_Request) return L.Request is
     (Kind => L.Operation'Val (Raw.Kind),
      Scope => Decode (Data, Raw.Scope),
      Expected_Epoch => Decode (Data, Raw.Expected_Epoch),
      Expected_Ledger_Head => Decode (Data, Raw.Expected_Ledger_Head),
      Request_Id => Decode (Data, Raw.Request_Id),
      Reservation => Decode (Data, Raw.Reservation),
      Operation_Id => Decode (Data, Raw.Operation_Id),
      Requester => Decode (Data, Raw.Requester),
      Bound => Decode (Data, Raw.Bound),
      New_Row => Decode (Data, Raw.New_Row))
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decode'Result =
     (Kind => L.Operation'Val (Raw.Kind),
      Scope => Decode (Data, Raw.Scope),
      Expected_Epoch => Decode (Data, Raw.Expected_Epoch),
      Expected_Ledger_Head => Decode (Data, Raw.Expected_Ledger_Head),
      Request_Id => Decode (Data, Raw.Request_Id),
      Reservation => Decode (Data, Raw.Reservation),
      Operation_Id => Decode (Data, Raw.Operation_Id),
      Requester => Decode (Data, Raw.Requester),
      Bound => Decode (Data, Raw.Bound),
      New_Row => Decode (Data, Raw.New_Row));
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Packet;
                         Before_Rows, Proposed_Rows : Raw_Row_Array;
                         Native : Raw_Native_Array) return Boolean is
     (Raw.Schema_Version = 1 and then Well_Formed (Data, Raw.Before_State)
      and then Well_Formed (Data, Raw.Proposed_State) and then Well_Formed (Data, Raw.Intent)
      and then (for all I in Before_Rows'Range => Well_Formed (Data, Before_Rows (I)))
      and then (for all I in Proposed_Rows'Range => Well_Formed (Data, Proposed_Rows (I)))
      and then (for all I in Native'Range => Well_Formed (Data, Native (I))))
   with Global => null;
   function Decode_Rows (Data : Q.Byte_Array; Raw : Raw_Row_Array) return L.Row_Array
   with Global => null, Pre => (for all I in Raw'Range => Well_Formed (Data, Raw (I))),
     Post => Decode_Rows'Result'First = Raw'First and then Decode_Rows'Result'Length = Raw'Length
       and then (for all I in Raw'Range => Decode_Rows'Result (I) = Decode (Data, Raw (I)));
   function Decode_Native (Data : Q.Byte_Array; Raw : Raw_Native_Array) return L.Native_Array
   with Global => null, Pre => (for all I in Raw'Range => Well_Formed (Data, Raw (I))),
     Post => Decode_Native'Result'First = Raw'First and then Decode_Native'Result'Length = Raw'Length
       and then (for all I in Raw'Range => Decode_Native'Result (I) = Decode (Data, Raw (I)));
   function Decide (Data : Q.Byte_Array; Raw : Raw_Packet;
                    Before_Rows, Proposed_Rows : Raw_Row_Array;
                    Native : Raw_Native_Array) return Raw_Result
   with Global => null, Pre => Well_Formed (Data, Raw, Before_Rows, Proposed_Rows, Native),
     Post => Decide'Result.Status = L.Status'Pos (L.Decision_Reference
       (Data, Decode (Data, Raw.Before_State), Decode_Rows (Data, Before_Rows),
        Decode (Data, Raw.Proposed_State), Decode_Rows (Data, Proposed_Rows),
        Decode_Native (Data, Native), Decode (Data, Raw.Intent)));
end Resource_Run_Ledger_Wire;
