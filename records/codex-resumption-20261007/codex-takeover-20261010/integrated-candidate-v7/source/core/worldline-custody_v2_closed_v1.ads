with Worldline.Retained_Custody_Chain;
package Worldline.Custody_V2_Closed_V1 with SPARK_Mode is
   package R renames Worldline.Retained_Custody_Chain;
   package E renames R.E;
   -- Complete original owner-state and logical SQLite observation. Database
   -- retains rowid and all original genesis/events/head cells; authenticated
   -- DTOs are correspondences to those rows, never independent authority.
   -- Owner_Key is the caller's held issuer-key span, not an evidence field.
   -- Owner_Plan is unchanged original BYTES from the independently authenticated
   -- prior TRANSFER_SENT.frame.root_plan.raw, not a proposed current context.
   -- Its actual original genesis/journal paths select the complete state rows.
   -- Both sides of an append relation are checked independently by the caller;
   -- schema/metadata equality and full SQL row prefixes remain its obligations.
   -- All fourteen original v1 kinds remain accepted by genuine R.Verify.
   -- This relation is neither v2 Ready nor startup/effect permission.
   function Matches
     (Data : E.Bytes; Owner_Key : E.Span; State, Database, Owner_Plan : E.Span)
      return Boolean with Global => null;
end Worldline.Custody_V2_Closed_V1;
