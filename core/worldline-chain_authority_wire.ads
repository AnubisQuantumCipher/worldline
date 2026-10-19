with Interfaces;
with Worldline.Chain_Authority;

package Worldline.Chain_Authority_Wire with SPARK_Mode is
   package A renames Worldline.Chain_Authority;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Integer_64;
   use type A.Optional_Digest;
   use type A.Chain_Row;
   use type Hash;
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
   type Raw_Row is record
      Previous, Actual_Payload_Root, Stored_Payload_Root, Stored_Head : Raw_Digest;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Row use record
      Previous at 0 range 0 .. 263;
      Actual_Payload_Root at 33 range 0 .. 263;
      Stored_Payload_Root at 66 range 0 .. 263;
      Stored_Head at 99 range 0 .. 263;
   end record;
   for Raw_Row'Size use 1056;
   for Raw_Row'Object_Size use 1056;
   for Raw_Row'Alignment use 1;
   type Raw_Anchors is record
      Kind : Interfaces.Unsigned_8;
      Observed_Genesis, Witnessed_Genesis, Witnessed_Head : Raw_Digest;
   end record with Convention => C;
   type Raw_Result is record
      Disposition : Interfaces.Unsigned_8;
      Head : Raw_Hash;
      Accepted_Count : Interfaces.Integer_64;
   end record with Convention => C;
   function Well_Formed (Raw : Raw_Digest) return Boolean is
     (Raw.Present <= 1 and then
       (Raw.Present = 1 or else Raw.Value = Raw_Hash'(others => 0)))
     with Global => null;
   function Well_Formed (Raw : Raw_Row) return Boolean is
     (Well_Formed (Raw.Previous) and then Well_Formed (Raw.Actual_Payload_Root)
      and then Well_Formed (Raw.Stored_Payload_Root) and then Well_Formed (Raw.Stored_Head))
     with Global => null;
   function Well_Formed (Raw : Raw_Anchors) return Boolean is
     (Raw.Kind <= A.Chain_Kind'Pos (A.Chain_Kind'Last)
      and then Well_Formed (Raw.Observed_Genesis)
      and then Well_Formed (Raw.Witnessed_Genesis)
      and then Well_Formed (Raw.Witnessed_Head))
     with Global => null;
   function Decode (Raw : Raw_Digest) return A.Optional_Digest is
     (Present => Raw.Present = 1, Value => Hash (Raw.Value))
     with Global => null, Pre => Well_Formed (Raw),
       Post => Decode'Result =
         (Present => Raw.Present = 1, Value => Hash (Raw.Value));
   function Decode (Raw : Raw_Row) return A.Chain_Row is
     (Previous => Decode (Raw.Previous),
      Actual_Payload_Root => Decode (Raw.Actual_Payload_Root),
      Stored_Payload_Root => Decode (Raw.Stored_Payload_Root),
      Stored_Head => Decode (Raw.Stored_Head))
     with Global => null, Pre => Well_Formed (Raw),
       Post => Decode'Result =
         (Previous => Decode (Raw.Previous),
          Actual_Payload_Root => Decode (Raw.Actual_Payload_Root),
          Stored_Payload_Root => Decode (Raw.Stored_Payload_Root),
          Stored_Head => Decode (Raw.Stored_Head));
   function Decide (Rows : A.Retained_Rows; Raw : Raw_Anchors) return Raw_Result
     with Global => null, Pre => Well_Formed (Raw),
       Post => Decide'Result.Disposition = A.Reason'Pos
         (A.Replay_Reference (A.Chain_Kind'Val (Raw.Kind), Rows,
           Decode (Raw.Observed_Genesis), Decode (Raw.Witnessed_Genesis),
           Decode (Raw.Witnessed_Head)).Disposition)
         and then Hash (Decide'Result.Head) =
           A.Replay_Reference (A.Chain_Kind'Val (Raw.Kind), Rows,
             Decode (Raw.Observed_Genesis), Decode (Raw.Witnessed_Genesis),
             Decode (Raw.Witnessed_Head)).Head
         and then Decide'Result.Accepted_Count = Interfaces.Integer_64
           (A.Replay_Reference (A.Chain_Kind'Val (Raw.Kind), Rows,
             Decode (Raw.Observed_Genesis), Decode (Raw.Witnessed_Genesis),
             Decode (Raw.Witnessed_Head)).Accepted_Count);
end Worldline.Chain_Authority_Wire;
