package body Worldline.Canonical_Owner_Completion with SPARK_Mode is
   function Reference(Data : A.Q.Byte_Array; HG : A.Grants; HH : A.Uses;
      HB : A.Binding; HNow : A.Q.Quantity; HE : A.Evidence;
      HS : X.L.Ledger_State; HR : X.L.Row_Array; HN : X.L.Native_Array;
      HBound : X.L.Binding; HRequester : X.L.Identity; HPeer : A.Optional_UID;
      HCollapse : X.K.C.Raw_Request; HM : X.Material;
      HWR, HWE, HER, HEE : A.C.Retained_Rows;
      G : A.Grants; H : A.Uses; B : A.Binding; E : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Decision is
      Selected : constant X.Decision:=X.Decide(Data,HG,HH,HB,HNow,HE,
         HS,HR,HN,HBound,HRequester,HPeer,HCollapse,HM,X.Quarantined,
         X.Resolve_Owner,HWR,HWE,HER,HEE);
   begin
      -- Re-evaluate complete original owner/grant/use/native dual captures at
      -- their authentic original intent boundary. Fresh expiry/revocation now
      -- cannot undo a committed terminal or issue an additional exchange/use.
      if Selected not in X.Owner_Record_Abort | X.Owner_Record_Effect
        or else not A.Same(Data,HB,B)
        or else not History_Extends(Data,HG,G,HH,H,B)
        or else not A.Same(Data,HE.Owner_Resolution,E.Owner_Resolution)
        or else not R.Same(E.Quarantine_Head,HM.Quarantine_Head)
        or else not (for some I in H'Range =>
          A.Same(Data,H(I).Bound,HE.Owner_Resolution)
          and then H(I).State in A.Reserved | A.Quarantined |
            A.Effect_Observed | A.Settled)
      then return Refused; end if;
      for I in H'Range loop
         if A.Same(Data,H(I).Bound,B) then
            if Selected=X.Owner_Record_Abort
              and then A.Same(Data,B,E.No_Effect_Binding) then
               if H(I).State=A.Quarantined then return Resolve_No_Effect;
               elsif H(I).State=A.Released then return No_Effect_Already;
               else return Refused; end if;
            elsif Selected=X.Owner_Record_Effect
              and then A.Chain_Effect(Data,B,E,Receipts,Events) then
               if H(I).State=A.Quarantined then return Resolve_Effect;
               elsif H(I).State in A.Effect_Observed | A.Settled then
                  return Effect_Already;
               else return Refused; end if;
            else return Refused; end if;
         end if;
      end loop;
      return Refused;
   end Reference;
   function Decide(Data : A.Q.Byte_Array; HG : A.Grants; HH : A.Uses;
      HB : A.Binding; HNow : A.Q.Quantity; HE : A.Evidence;
      HS : X.L.Ledger_State; HR : X.L.Row_Array; HN : X.L.Native_Array;
      HBound : X.L.Binding; HRequester : X.L.Identity; HPeer : A.Optional_UID;
      HCollapse : X.K.C.Raw_Request; HM : X.Material;
      HWR, HWE, HER, HEE : A.C.Retained_Rows;
      G : A.Grants; H : A.Uses; B : A.Binding; E : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Decision is
   begin return Reference(Data,HG,HH,HB,HNow,HE,HS,HR,HN,HBound,HRequester,HPeer,HCollapse,HM,HWR,HWE,HER,HEE,G,H,B,E,Receipts,Events); end Decide;
end Worldline.Canonical_Owner_Completion;
