with Worldline.Canonical_Exchange;
-- Historical completion consumes an actual retained K4 intent, never grants an
-- exchange or accepts a copied native verdict. The producer must authenticate
-- complete original histories and resource terminal custody independently.
package Worldline.Canonical_Owner_Completion with SPARK_Mode is
   package X renames Worldline.Canonical_Exchange;
   package A renames X.A;
   package R renames A.R;
   use type A.Q.Byte_Count; use type A.Q.Ordering;
   use type A.Rights; use type A.Grant_State; use type A.Use_State; use type A.Operation;
   use type X.Decision; use type A.Decision;
   type Decision is (Refused, Resolve_Effect, Resolve_No_Effect,
      Effect_Already, No_Effect_Already);
   function Grant_Lineage(Data : A.Q.Byte_Array; Original, Current : A.Grant)
      return Boolean is
     (A.Grant_Valid(Data,Original) and then A.Grant_Valid(Data,Current)
      and then R.Same(Original.Id,Current.Id)
      and then Original.Parent.Present=Current.Parent.Present
      and then (if Original.Parent.Present then R.Same(Original.Parent,Current.Parent))
      and then R.Same(Original.Issuer,Current.Issuer)
      and then R.Same(Original.Instance,Current.Instance)
      and then R.Same(Original.Root_Set,Current.Root_Set)
      and then R.Same(Original.Policy,Current.Policy)
      and then A.Same(Original.Subject,Current.Subject)
      and then A.Same(Original.Owner,Current.Owner)
      and then Original.Allowed=Current.Allowed
      and then R.Same(Data,Original.Epoch,Current.Epoch)
      and then A.Q.Compare(Data,Original.Ceiling,Current.Ceiling)=A.Q.Equal
      and then A.Q.Compare(Data,Original.Issued_At,Current.Issued_At)=A.Q.Equal
      and then A.Q.Compare(Data,Original.Expires_At,Current.Expires_At)=A.Q.Equal
      and then (if Original.State=A.Revoked then Current.State=A.Revoked))
     with Global=>null;
   function History_Extends(Data : A.Q.Byte_Array; HG,G : A.Grants;
      HH,H : A.Uses; B : A.Binding) return Boolean is
     (A.Roster_Valid(Data,HG,B.Id(A.Issuer),B.Owner)
      and then A.Roster_Valid(Data,G,B.Id(A.Issuer),B.Owner)
      and then G'Length>=HG'Length and then H'Length>=HH'Length
      and then (for all I in HG'Range =>
        Grant_Lineage(Data,HG(I),G(G'First+(I-HG'First))))
      and then (for all I in HH'Range =>
        A.Same(Data,HH(I).Bound,H(H'First+(I-HH'First)).Bound)
        and then (case HH(I).State is
          when A.Settled => H(H'First+(I-HH'First)).State=A.Settled,
          when A.Released => H(H'First+(I-HH'First)).State=A.Released,
          when A.Effect_Observed => H(H'First+(I-HH'First)).State in
             A.Effect_Observed | A.Settled | A.Quarantined,
          when A.Reserved | A.Quarantined => True))
      and then (for all I in H'Range => A.Valid(Data,H(I).Bound)
        and then (for some J in G'Range => R.Same(G(J).Id,H(I).Bound.Id(A.Grant_Id)))
        and then (for all J in H'Range =>
          (if J/=I then not R.Same(H(J).Bound.Id(A.Operation_Id),H(I).Bound.Id(A.Operation_Id))))))
     with Global=>null;
   function Reference(Data : A.Q.Byte_Array; HG : A.Grants; HH : A.Uses;
      HB : A.Binding; HNow : A.Q.Quantity; HE : A.Evidence;
      HS : X.L.Ledger_State; HR : X.L.Row_Array; HN : X.L.Native_Array;
      HBound : X.L.Binding; HRequester : X.L.Identity; HPeer : A.Optional_UID;
      HCollapse : X.K.C.Raw_Request; HM : X.Material;
      HWR, HWE, HER, HEE : A.C.Retained_Rows;
      G : A.Grants; H : A.Uses; B : A.Binding; E : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Decision with Global=>null;
   function Decide(Data : A.Q.Byte_Array; HG : A.Grants; HH : A.Uses;
      HB : A.Binding; HNow : A.Q.Quantity; HE : A.Evidence;
      HS : X.L.Ledger_State; HR : X.L.Row_Array; HN : X.L.Native_Array;
      HBound : X.L.Binding; HRequester : X.L.Identity; HPeer : A.Optional_UID;
      HCollapse : X.K.C.Raw_Request; HM : X.Material;
      HWR, HWE, HER, HEE : A.C.Retained_Rows;
      G : A.Grants; H : A.Uses; B : A.Binding; E : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Decision with Global=>null,
      Post=>Decide'Result=Reference(Data,HG,HH,HB,HNow,HE,HS,HR,HN,HBound,HRequester,HPeer,HCollapse,HM,HWR,HWE,HER,HEE,G,H,B,E,Receipts,Events);
end Worldline.Canonical_Owner_Completion;
