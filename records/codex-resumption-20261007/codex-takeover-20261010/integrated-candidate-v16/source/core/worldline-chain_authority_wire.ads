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
   type Raw_Digest is record
      Present : Interfaces.Unsigned_8;
      Value : Raw_Hash;
   end record with Convention => C;
   type Raw_Row is record
      Previous, Actual_Payload_Root, Stored_Payload_Root, Stored_Head : Raw_Digest;
   end record with Convention => C;
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
