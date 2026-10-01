with Interfaces;

package Worldline.Recovery with SPARK_Mode is
   --  Transaction markers are text identities, not content hashes. Preserve
   --  their complete encoded values, including present empty identities.
   type Byte_Count is range 0 .. Long_Long_Integer'Last;
   subtype Byte_Index is Byte_Count range 1 .. Byte_Count'Last;
   type Identity_Bytes is array (Byte_Index range <>) of Interfaces.Unsigned_8;
   type Optional_Marker
     (Present : Boolean := False; Length : Byte_Count := 0)
   is record
      case Present is
         when False => null;
         when True => Value : Identity_Bytes (1 .. Length);
      end case;
   end record;

   function Matches
     (Expected : Identity_Bytes; Marker : Optional_Marker) return Boolean
   with Global => null,
     Post => Matches'Result =
       (Marker.Present and then Marker.Value = Expected);

   type Recovery_Action is (Finish_Committed, Abort_Prepared, Ambiguous);

   --  Exact original marker relation. The kernel decides only the action;
   --  observation provenance, effect custody and durable completion remain
   --  required integrated recovery obligations.
   function Select_Action
     (Expected : Identity_Bytes; Live, Prepared : Optional_Marker)
      return Recovery_Action
   with Global => null,
     Post => Select_Action'Result =
       (if Matches (Expected, Live) and then not Matches (Expected, Prepared)
        then Finish_Committed
        elsif Matches (Expected, Prepared) and then not Matches (Expected, Live)
        then Abort_Prepared
        else Ambiguous);
end Worldline.Recovery;
