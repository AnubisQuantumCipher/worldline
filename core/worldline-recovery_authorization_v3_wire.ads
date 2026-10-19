with Interfaces;
with Resource_Quantities;
with Resource_Reservation_Transition;
with SPARK.Big_Integers;
with Worldline.Recovery_Authorization_V3;

package Worldline.Recovery_Authorization_V3_Wire with SPARK_Mode is
   package R renames Worldline.Recovery_Authorization_V3;
   package Q renames Resource_Quantities;
   package T renames Resource_Reservation_Transition;
   use type SPARK.Big_Integers.Valid_Big_Integer;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Integer_64;
   use type Interfaces.Unsigned_32;
   use type Q.Byte_Count;
   use type R.Binding;
   use type R.Optional_Digest;
   use type R.Native_Observation;
   use type R.Recovery_Action;
   type Raw_Hash is array (Hash'Range) of Interfaces.Unsigned_8
     with Convention => C;
   --  Preserve compiler-observed C array layout.
   for Raw_Hash'Component_Size use 8;
   for Raw_Hash'Size use 256;
   for Raw_Hash'Object_Size use 256;
   for Raw_Hash'Alignment use 1;
   type Raw_Digest is record
      Present : Interfaces.Unsigned_8;
      Value : Raw_Hash;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Digest use record
      Present at 0 range 0 .. 7;
      Value at 1 range 0 .. 255;
   end record;
   for Raw_Digest'Size use 264;
   for Raw_Digest'Object_Size use 264;
   for Raw_Digest'Alignment use 1;
   type Raw_Epoch is record
      Present, Negative : Interfaces.Unsigned_8;
      First, Length : Interfaces.Integer_64;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Epoch use record
      Present at 0 range 0 .. 7;
      Negative at 1 range 0 .. 7;
      First at 8 range 0 .. 63;
      Length at 16 range 0 .. 63;
   end record;
   for Raw_Epoch'Size use 192;
   for Raw_Epoch'Object_Size use 192;
   for Raw_Epoch'Alignment use 8;
   type Raw_Binding is record
      Mode : Interfaces.Unsigned_8;
      Operation : Raw_Digest;
      Transaction : Raw_Digest;
      Capability : Raw_Digest;
      Universe_Head : Raw_Digest;
      Instance : Raw_Digest;
      Subject : Raw_Digest;
      Staged_Root : Raw_Digest;
      Current_Requirement : Raw_Digest;
      Resulting_Requirement : Raw_Digest;
      Requester : Raw_Digest;
      Grant_Use : Raw_Digest;
      Policy_Identity : Raw_Digest;
      Selected_Evaluation : Raw_Digest;
      History_Head : Raw_Digest;
      Reservation : Raw_Digest;
      Host : Raw_Digest;
      Before_Prime : Raw_Digest;
      Before_Root : Raw_Digest;
      Before_Mapping : Raw_Digest;
      Staged_Mapping : Raw_Digest;
      Input_Snapshot : Raw_Digest;
      Kernel_Build : Raw_Digest;
      Kernel_Library : Raw_Digest;
      Kernel_Mapping : Raw_Digest;
      Issuer_Head : Raw_Digest;
      Receipt_Head : Raw_Digest;
      Causal_Head : Raw_Digest;
      Policy_Epoch, Resource_Epoch : Raw_Epoch;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Binding use record
      Mode at 0 range 0 .. 7;
      Operation at 1 range 0 .. 263;
      Transaction at 34 range 0 .. 263;
      Capability at 67 range 0 .. 263;
      Universe_Head at 100 range 0 .. 263;
      Instance at 133 range 0 .. 263;
      Subject at 166 range 0 .. 263;
      Staged_Root at 199 range 0 .. 263;
      Current_Requirement at 232 range 0 .. 263;
      Resulting_Requirement at 265 range 0 .. 263;
      Requester at 298 range 0 .. 263;
      Grant_Use at 331 range 0 .. 263;
      Policy_Identity at 364 range 0 .. 263;
      Selected_Evaluation at 397 range 0 .. 263;
      History_Head at 430 range 0 .. 263;
      Reservation at 463 range 0 .. 263;
      Host at 496 range 0 .. 263;
      Before_Prime at 529 range 0 .. 263;
      Before_Root at 562 range 0 .. 263;
      Before_Mapping at 595 range 0 .. 263;
      Staged_Mapping at 628 range 0 .. 263;
      Input_Snapshot at 661 range 0 .. 263;
      Kernel_Build at 694 range 0 .. 263;
      Kernel_Library at 727 range 0 .. 263;
      Kernel_Mapping at 760 range 0 .. 263;
      Issuer_Head at 793 range 0 .. 263;
      Receipt_Head at 826 range 0 .. 263;
      Causal_Head at 859 range 0 .. 263;
      Policy_Epoch at 896 range 0 .. 191;
      Resource_Epoch at 920 range 0 .. 191;
   end record;
   for Raw_Binding'Size use 7552;
   for Raw_Binding'Object_Size use 7552;
   for Raw_Binding'Alignment use 8;
   type Raw_Native is record
      Live_Mapping, Live_Root : Raw_Digest;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Native use record
      Live_Mapping at 0 range 0 .. 263;
      Live_Root at 33 range 0 .. 263;
   end record;
   for Raw_Native'Size use 528;
   for Raw_Native'Object_Size use 528;
   for Raw_Native'Alignment use 1;
   type Raw_Request is record
      Schema_Version : Interfaces.Unsigned_32;
      State, Fresh, Historical, Grant_Eligible : Interfaces.Unsigned_8;
      Issued_Binding, Recovered_Binding : Raw_Binding;
      Native : Raw_Native;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Request use record
      Schema_Version at 0 range 0 .. 31;
      State at 4 range 0 .. 7;
      Fresh at 5 range 0 .. 7;
      Historical at 6 range 0 .. 7;
      Grant_Eligible at 7 range 0 .. 7;
      Issued_Binding at 8 range 0 .. 7551;
      Recovered_Binding at 952 range 0 .. 7551;
      Native at 1896 range 0 .. 527;
   end record;
   for Raw_Request'Size use 15696;
   for Raw_Request'Object_Size use 15744;
   for Raw_Request'Alignment use 8;
   type Raw_Result is record
      Action, State : Interfaces.Unsigned_8;
   end record with Convention => C;

   function Well_Formed (Raw : Raw_Digest) return Boolean is
     (Raw.Present <= 1
      and then (Raw.Present = 1 or else Raw.Value = Raw_Hash'(others => 0)))
     with Global => null;
   --  Canonical raw epoch: absent and present zero have distinct presence.
   --  Numeric values are spans; a fixed index width is a storage extent only.
   function Decode (Raw : Raw_Epoch) return R.Optional_Epoch is
     (if Raw.Present = 1 then
        (Present => True, Value =>
          (Negative => False, First => Q.Byte_Index (Raw.First),
           Length => Q.Byte_Count (Raw.Length)))
      else (Present => False))
     with Global => null,
       Pre => Raw.Present <= 1 and then Raw.Negative = 0
         and then Raw.First >= 1
         and then Raw.First <= Interfaces.Integer_64 (Q.Byte_Index'Last)
         and then Raw.Length >= 0
         and then Raw.Length <= Interfaces.Integer_64 (Q.Byte_Count'Last),
       Post => Decode'Result.Present = (Raw.Present = 1)
         and then (if Decode'Result.Present then
           not Decode'Result.Value.Negative
           and then Decode'Result.Value.First = Q.Byte_Index (Raw.First)
           and then Decode'Result.Value.Length = Q.Byte_Count (Raw.Length));

   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Epoch)
      return Boolean is
     (Raw.Present <= 1 and then Raw.Negative = 0
      and then Raw.First >= 1
      and then Raw.First <= Interfaces.Integer_64 (Q.Byte_Index'Last)
      and then Raw.Length >= 0
      and then Raw.Length <= Interfaces.Integer_64 (Q.Byte_Count'Last)
      and then
        (if Raw.Present = 0 then Raw.First = 1 and then Raw.Length = 0
         elsif Raw.Length = 0 then Raw.First = 1
         else Q.Span_Valid (Data, Decode (Raw).Value)
           and then Data (Q.Byte_Index (Raw.First) +
                           (Q.Byte_Count (Raw.Length) - 1)) /= 0))
     with Global => null;
   --  Total bridge from the unchanged original Optional_Quantity domain.
   --  Valid padding and signed zero are canonicalized without changing value;
   --  malformed/negative required facts retain an explicit invalid marker.
   function Encode_Original (Data : Q.Byte_Array; Epoch : R.Optional_Epoch)
      return Raw_Epoch
   with Global => null,
     Post =>
       (if not Epoch.Present then
          Encode_Original'Result =
            (Present => 0, Negative => 0, First => 1, Length => 0)
        elsif T.Epoch_Valid (Data, Epoch) then
          Well_Formed (Data, Encode_Original'Result)
          and then Decode (Encode_Original'Result).Present
          and then R.Same_Epoch_Reference
            (Data, Epoch, Decode (Encode_Original'Result))
        else not Well_Formed (Data, Encode_Original'Result));

   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Binding) return Boolean is
     (Raw.Mode <= R.Promotion_Mode'Pos (R.Promotion_Mode'Last)
      and then Well_Formed (Raw.Operation)
      and then Well_Formed (Raw.Transaction)
      and then Well_Formed (Raw.Capability)
      and then Well_Formed (Raw.Universe_Head)
      and then Well_Formed (Raw.Instance)
      and then Well_Formed (Raw.Subject)
      and then Well_Formed (Raw.Staged_Root)
      and then Well_Formed (Raw.Current_Requirement)
      and then Well_Formed (Raw.Resulting_Requirement)
      and then Well_Formed (Raw.Requester)
      and then Well_Formed (Raw.Grant_Use)
      and then Well_Formed (Raw.Policy_Identity)
      and then Well_Formed (Raw.Selected_Evaluation)
      and then Well_Formed (Raw.History_Head)
      and then Well_Formed (Raw.Reservation)
      and then Well_Formed (Raw.Host)
      and then Well_Formed (Raw.Before_Prime)
      and then Well_Formed (Raw.Before_Root)
      and then Well_Formed (Raw.Before_Mapping)
      and then Well_Formed (Raw.Staged_Mapping)
      and then Well_Formed (Raw.Input_Snapshot)
      and then Well_Formed (Raw.Kernel_Build)
      and then Well_Formed (Raw.Kernel_Library)
      and then Well_Formed (Raw.Kernel_Mapping)
      and then Well_Formed (Raw.Issuer_Head)
      and then Well_Formed (Raw.Receipt_Head)
      and then Well_Formed (Raw.Causal_Head)
      and then Well_Formed (Data, Raw.Policy_Epoch)
      and then Well_Formed (Data, Raw.Resource_Epoch))
     with Global => null;
   function Well_Formed (Raw : Raw_Native) return Boolean is
     (Well_Formed (Raw.Live_Mapping) and then Well_Formed (Raw.Live_Root))
     with Global => null;
   function Well_Formed (Data : Q.Byte_Array; Raw : Raw_Request) return Boolean is
     (Raw.Schema_Version = 3
      and then Raw.State <= R.Use_State'Pos (R.Use_State'Last)
      and then Raw.Fresh <= R.Fresh_Verdict'Pos (R.Fresh_Verdict'Last)
      and then Raw.Historical <= R.Historical_Verdict'Pos (R.Historical_Verdict'Last)
      and then Raw.Grant_Eligible <= 1
      and then Well_Formed (Data, Raw.Issued_Binding)
      and then Well_Formed (Data, Raw.Recovered_Binding)
      and then Well_Formed (Raw.Native))
     with Global => null;

   function Decode (Raw : Raw_Digest) return R.Optional_Digest is
     (Present => Raw.Present = 1, Value => Hash (Raw.Value))
     with Global => null, Pre => Well_Formed (Raw),
       Post => Decode'Result =
         (Present => Raw.Present = 1, Value => Hash (Raw.Value));
   function Decode (Data : Q.Byte_Array; Raw : Raw_Binding) return R.Binding is
     (Mode => R.Promotion_Mode'Val (Raw.Mode),
      Operation => Decode (Raw.Operation),
      Transaction => Decode (Raw.Transaction),
      Capability => Decode (Raw.Capability),
      Universe_Head => Decode (Raw.Universe_Head),
      Instance => Decode (Raw.Instance),
      Subject => Decode (Raw.Subject),
      Staged_Root => Decode (Raw.Staged_Root),
      Current_Requirement => Decode (Raw.Current_Requirement),
      Resulting_Requirement => Decode (Raw.Resulting_Requirement),
      Requester => Decode (Raw.Requester),
      Grant_Use => Decode (Raw.Grant_Use),
      Policy_Identity => Decode (Raw.Policy_Identity),
      Selected_Evaluation => Decode (Raw.Selected_Evaluation),
      History_Head => Decode (Raw.History_Head),
      Reservation => Decode (Raw.Reservation),
      Host => Decode (Raw.Host),
      Before_Prime => Decode (Raw.Before_Prime),
      Before_Root => Decode (Raw.Before_Root),
      Before_Mapping => Decode (Raw.Before_Mapping),
      Staged_Mapping => Decode (Raw.Staged_Mapping),
      Input_Snapshot => Decode (Raw.Input_Snapshot),
      Kernel_Build => Decode (Raw.Kernel_Build),
      Kernel_Library => Decode (Raw.Kernel_Library),
      Kernel_Mapping => Decode (Raw.Kernel_Mapping),
      Issuer_Head => Decode (Raw.Issuer_Head),
      Receipt_Head => Decode (Raw.Receipt_Head),
      Causal_Head => Decode (Raw.Causal_Head),
      Policy_Epoch => Decode (Raw.Policy_Epoch),
      Resource_Epoch => Decode (Raw.Resource_Epoch))
     with Global => null, Pre => Well_Formed (Data, Raw),
       Post => Decode'Result =
     (Mode => R.Promotion_Mode'Val (Raw.Mode),
      Operation => Decode (Raw.Operation),
      Transaction => Decode (Raw.Transaction),
      Capability => Decode (Raw.Capability),
      Universe_Head => Decode (Raw.Universe_Head),
      Instance => Decode (Raw.Instance),
      Subject => Decode (Raw.Subject),
      Staged_Root => Decode (Raw.Staged_Root),
      Current_Requirement => Decode (Raw.Current_Requirement),
      Resulting_Requirement => Decode (Raw.Resulting_Requirement),
      Requester => Decode (Raw.Requester),
      Grant_Use => Decode (Raw.Grant_Use),
      Policy_Identity => Decode (Raw.Policy_Identity),
      Selected_Evaluation => Decode (Raw.Selected_Evaluation),
      History_Head => Decode (Raw.History_Head),
      Reservation => Decode (Raw.Reservation),
      Host => Decode (Raw.Host),
      Before_Prime => Decode (Raw.Before_Prime),
      Before_Root => Decode (Raw.Before_Root),
      Before_Mapping => Decode (Raw.Before_Mapping),
      Staged_Mapping => Decode (Raw.Staged_Mapping),
      Input_Snapshot => Decode (Raw.Input_Snapshot),
      Kernel_Build => Decode (Raw.Kernel_Build),
      Kernel_Library => Decode (Raw.Kernel_Library),
      Kernel_Mapping => Decode (Raw.Kernel_Mapping),
      Issuer_Head => Decode (Raw.Issuer_Head),
      Receipt_Head => Decode (Raw.Receipt_Head),
      Causal_Head => Decode (Raw.Causal_Head),
      Policy_Epoch => Decode (Raw.Policy_Epoch),
      Resource_Epoch => Decode (Raw.Resource_Epoch));
   function Decode (Raw : Raw_Native) return R.Native_Observation is
     (Live_Mapping => Decode (Raw.Live_Mapping),
      Live_Root => Decode (Raw.Live_Root))
     with Global => null, Pre => Well_Formed (Raw),
       Post => Decode'Result =
         (Live_Mapping => Decode (Raw.Live_Mapping),
          Live_Root => Decode (Raw.Live_Root));

   function Selected_Action (Data : Q.Byte_Array; Raw : Raw_Request) return R.Recovery_Action is
     (R.Select_Action
        (Data, R.Use_State'Val (Raw.State), Decode (Data, Raw.Issued_Binding),
         Decode (Data, Raw.Recovered_Binding), R.Fresh_Verdict'Val (Raw.Fresh),
         R.Historical_Verdict'Val (Raw.Historical), Raw.Grant_Eligible = 1,
         Decode (Raw.Native)))
     with Global => null, Pre => Well_Formed (Data, Raw),
       Post => Selected_Action'Result = R.Action_Reference
         (Data, R.Use_State'Val (Raw.State), Decode (Data, Raw.Issued_Binding),
          Decode (Data, Raw.Recovered_Binding), R.Fresh_Verdict'Val (Raw.Fresh),
          R.Historical_Verdict'Val (Raw.Historical), Raw.Grant_Eligible = 1,
          Decode (Raw.Native));

   function Decide (Data : Q.Byte_Array; Raw : Raw_Request) return Raw_Result
   with Global => null, Pre => Well_Formed (Data, Raw),
     Post => Decide'Result =
       (Action => R.Recovery_Action'Pos (Selected_Action (Data, Raw)),
        State => R.Use_State'Pos
          (R.Next_State (R.Use_State'Val (Raw.State), Selected_Action (Data, Raw))));
end Worldline.Recovery_Authorization_V3_Wire;
