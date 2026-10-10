with Worldline.Custody_V2_Load_Input;
package Worldline.Custody_V2_Closed_State with SPARK_Mode is
   package I renames Worldline.Custody_V2_Load_Input;
   package E renames I.E;
   use type E.Count;
   -- Complete original owner-state value relation. Source/OFD and terminal
   -- provenance are independently established by the closed-witness consumer.
   -- Physical SQLite page/WAL bytes and process-local descriptor numbers are
   -- retained observations, not logical-state equality operands.
   function Original_Equal
     (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Left.Length);
   -- Complete actual root_worker_journal_v2._event image: all SQL13 cells,
   -- unchanged original record and retained full wrapper, not event-id alone.
   function Event_Record_Matches
     (Value : I.Parsed_Input; Index : E.Count; Data : E.Bytes; Record_Image : E.Span)
      return Boolean with Global => null;
   -- Both full v2 custody load images are natively redecided. Original v1
   -- retained snapshots instead reuse the actual all-event original HMAC
   -- verifier with the independently held issuer key. In either case complete
   -- SQL, metadata, table definitions and every old event row are retained.
   -- Owner_Plan is the original raw-byte span from the independently
   -- authenticated prior TRANSFER_SENT frame.root_plan, never the proposed
   -- current capture. It binds original-v1 genesis to the actual owner plan.
   function Matches
     (Data : E.Bytes; Before, Current, Containing_Input, Owner_Key, Owner_Plan : E.Span)
      return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Containing_Input.Length, Decreases => 2);
end Worldline.Custody_V2_Closed_State;
