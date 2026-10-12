with Worldline.Operation_Archive;
with Worldline.Custody_V2_Owner_Canonical;
with Worldline.Custody_V2_K4_Resource_Ack;
with Worldline.Custody_V2_Fold_Engine;
package body Worldline.Journal_Witness with SPARK_Mode is
   package OA renames Worldline.Operation_Archive;
   package F renames Worldline.Custody_V2_Fold_Engine;
   package O renames Worldline.Custody_V2_Owner_Canonical;
   package K renames Worldline.Custody_V2_K4_Resource_Ack;
   use type F.Fold_Status;
   use type L.Decode_Status;
   use type E.Count;
   function Decide (Kind : Witness_Kind; Current, Input : E.Bytes)
      return Decision is
      Extents : constant L.Sizes := L.Counts (Current);
      Whole : constant E.Span := (Input'First, Input'Length);
   begin
      if Extents.Status /= L.Parsed or else not OA.Valid (Input, Whole) then
         return Input_Invalid;
      end if;
      declare
         Value : L.Parsed_Input (Extents.Arena, Extents.Events, Extents.Heads,
            Extents.Roots, Extents.Subjects, Extents.Alternatives, Extents.Blobs);
      begin
         L.Decode (Current, Value);
         if Value.Status /= L.Parsed then return Input_Invalid; end if;
         declare
            Facts : constant E.Bytes :=
              O.Extract_Replay_Capsules (Value.Arena, Value.Owner_Roster);
            -- Both observers are established on the original stack owner's
            -- arena and bound to its exact extent and digest. No copied arena
            -- or allocation.
            Owner_Context : O.Prepared_History;
            Resource_Context : K.Prepared_History;
         begin
            O.Establish_History (Owner_Context, Value.Arena, Facts, Value.Owner_Roster);
            K.Establish_History (Resource_Context, Value.Arena, Value.Owner_Roster);
            -- Full custody replay shares these native-verified observers;
            -- neither a copied roster bit nor a cached producer verdict
            -- replaces the complete fold. Legitimate retained/unknown
            -- history remains admissible without requiring Front_Startup.
            if F.Load_Decide
                 (Value, Owner_Context, Resource_Context).State /=
               F.History_Folded
            then
               return Refused;
            end if;
            case Kind is
               when Owner_Canonical =>
                  if O.Authenticated (Owner_Context, Value.Arena, Input, Whole) then
                     return Ready;
                  end if;
               when Resource_ACK =>
                  if K.Direct_Authenticated
                       (Resource_Context, Value.Arena, Input, OA.Field (Input, Whole, "capture"),
                        OA.Field (Input, Whole, "ack"))
                  then
                     return Ready;
                  end if;
            end case;
            return Refused;
         end;
      end;
   end Decide;
end Worldline.Journal_Witness;
