with Worldline.Recovery_Protocol;
procedure Test_Protocol with SPARK_Mode is
   package P renames Worldline.Recovery_Protocol;
   use type P.State;
begin
   for Before in P.State loop
      for Cause in P.Event loop
         pragma Assert (P.Advance (Before, Cause) = P.Reference (Before, Cause));
         pragma Assert (P.Changed_Only_By_Resolution (Before, Cause));
      end loop;
   end loop;
   pragma Assert (P.Advance (P.Issued, P.Fresh_Claim) = P.Effect_Intent);
   pragma Assert (P.Advance (P.Effect_Intent, P.Historical_Effect) = P.Effect_Observed);
   pragma Assert (P.Advance (P.Effect_Observed, P.Settlement_Complete) = P.Settled);
   pragma Assert (P.Advance (P.Settled, P.Replay) = P.Settled);
   pragma Assert (P.Advance (P.Effect_Intent, P.No_Effect_Released) = P.Aborted);
   pragma Assert (P.Advance (P.Quarantined, P.Fresh_Claim) = P.Quarantined);
end Test_Protocol;
