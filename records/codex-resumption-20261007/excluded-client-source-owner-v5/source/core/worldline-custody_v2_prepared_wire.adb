with Interfaces;
package body Worldline.Custody_V2_Prepared_Wire with SPARK_Mode is
   use type Interfaces.Unsigned_8;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type W.C.Raw_Digest;
   use type W.Raw_UID;
   use type W.Raw_Rights;
   use type O.Binding;
   use type O.Operation;

   function Quantity_Valid (Data : Q.Byte_Array; V : W.Raw_Quantity) return Boolean is
     (W.Well_Formed (V) and then
       (V.Present = 0 or else Q.Span_Valid (Data, W.Decode (V).Value)));
   function Binding_Valid (Data : Q.Byte_Array; V : W.Raw_Binding) return Boolean is
     (W.Well_Formed (V) and then Quantity_Valid (Data, V.Policy_Epoch)
        and then Quantity_Valid (Data, V.Resource_Epoch));
   function Input_Valid (Data : Q.Byte_Array; V : W.Raw_Input) return Boolean is
     (W.Well_Formed (V) and then V.Mode = O.Command'Pos (O.Reserve_Use)
       and then Quantity_Valid (Data, V.Now)
       and then Binding_Valid (Data, V.Bound)
       and then Binding_Valid (Data, V.Facts.Effect_Binding)
       and then Binding_Valid (Data, V.Facts.No_Effect_Binding)
       and then Binding_Valid (Data, V.Facts.Owner_Resolution)
       and then W.Recovery_Well_Formed (Data, V.Facts));
   function Grant_Valid (Data : Q.Byte_Array; V : W.Raw_Grant) return Boolean is
     (W.Well_Formed (V) and then Quantity_Valid (Data, V.Epoch)
       and then Quantity_Valid (Data, V.Ceiling)
       and then Quantity_Valid (Data, V.Issued_At)
       and then Quantity_Valid (Data, V.Expires_At));
   function Same_Quantity (Data : Q.Byte_Array; L, R : W.Raw_Quantity)
      return Boolean is
   begin
      if not Quantity_Valid (Data, L) or else not Quantity_Valid (Data, R)
        or else L.Present /= R.Present then return False; end if;
      if L.Present = 0 then return True; end if;
      declare
         A : constant Q.Quantity := W.Decode (L).Value;
         B : constant Q.Quantity := W.Decode (R).Value;
      begin
         if A.Negative /= B.Negative or else A.Length /= B.Length then return False; end if;
         if A.Length > 0 then
            for I in Q.Byte_Count range 0 .. A.Length - 1 loop
               if Data (A.First + I) /= Data (B.First + I) then return False; end if;
            end loop;
         end if;
         return True;
      end;
   end Same_Quantity;
   function Same_Grant (Data : Q.Byte_Array; L, R : W.Raw_Grant) return Boolean is
     (L.Id = R.Id and then L.Parent = R.Parent and then L.Issuer = R.Issuer
      and then L.Instance = R.Instance and then L.Root_Set = R.Root_Set
      and then L.Policy = R.Policy and then L.Subject = R.Subject and then L.Owner = R.Owner
      and then L.Allowed = R.Allowed and then L.State = R.State
      and then Same_Quantity (Data, L.Epoch, R.Epoch)
      and then Same_Quantity (Data, L.Ceiling, R.Ceiling)
      and then Same_Quantity (Data, L.Issued_At, R.Issued_At)
      and then Same_Quantity (Data, L.Expires_At, R.Expires_At));

   procedure Try_Next
     (Data : Q.Byte_Array; Event : P.C.Event_Row; Before : M.Root_State;
      Reserve, Intent : W.Raw_Input; Reserve_Grants, Intent_Grants : Raw_Grants;
      Reserve_Uses, Intent_Uses : Raw_Uses;
      Reserve_Receipts, Reserve_Events, Intent_Receipts, Intent_Events : Raw_Rows;
      After : out M.Root_State; Disposition : out Status) is
   begin
      After := Before;
      Disposition := Malformed_Reserve;
      if not Input_Valid (Data, Reserve) then return; end if;
      Disposition := Malformed_Intent;
      if not Input_Valid (Data, Intent) then return; end if;
      Disposition := Malformed_Roster;
      if not (for all G of Reserve_Grants => Grant_Valid (Data, G)) or else
        not (for all G of Intent_Grants => Grant_Valid (Data, G)) or else
        not (for all H of Reserve_Uses => W.Well_Formed (H) and then Binding_Valid (Data, H.Bound)) or else
        not (for all H of Intent_Uses => W.Well_Formed (H) and then Binding_Valid (Data, H.Bound)) or else
        not (for all C of Reserve_Receipts => CW.Well_Formed (C)) or else
        not (for all C of Reserve_Events => CW.Well_Formed (C)) or else
        not (for all C of Intent_Receipts => CW.Well_Formed (C)) or else
        not (for all C of Intent_Events => CW.Well_Formed (C)) then return; end if;
      Disposition := Operation_Or_Grant_Changed;
      if Reserve_Grants'Length /= Intent_Grants'Length or else
        not O.Same (Data, W.Decode (Reserve.Bound), W.Decode (Intent.Bound)) then return; end if;
      for I in Reserve_Grants'Range loop
         if not Same_Grant (Data, Reserve_Grants (I),
           Intent_Grants (Intent_Grants'First + (I - Reserve_Grants'First))) then return; end if;
      end loop;
      declare
         G : O.Grants (Reserve_Grants'Range);
         RH : O.Uses (Reserve_Uses'Range);
         IH : O.Uses (Intent_Uses'Range);
         RR : O.C.Retained_Rows (Reserve_Receipts'Range);
         RE : O.C.Retained_Rows (Reserve_Events'Range);
         IR : O.C.Retained_Rows (Intent_Receipts'Range);
         IE : O.C.Retained_Rows (Intent_Events'Range);
         Joined : Boolean;
      begin
         for I in G'Range loop G (I) := W.Decode (Reserve_Grants (I)); end loop;
         for I in RH'Range loop RH (I) := W.Decode (Reserve_Uses (I)); end loop;
         for I in IH'Range loop IH (I) := W.Decode (Intent_Uses (I)); end loop;
         for I in RR'Range loop RR (I) := CW.Decode (Reserve_Receipts (I)); end loop;
         for I in RE'Range loop RE (I) := CW.Decode (Reserve_Events (I)); end loop;
         for I in IR'Range loop IR (I) := CW.Decode (Intent_Receipts (I)); end loop;
         for I in IE'Range loop IE (I) := CW.Decode (Intent_Events (I)); end loop;
         P.Try_Next (Data, Event, Before, G, RH, IH, W.Decode (Reserve.Bound),
           W.Decode (Reserve.Now).Value, W.Decode (Intent.Now).Value,
           W.Decode (Data, Reserve.Facts), W.Decode (Data, Intent.Facts), RR, RE, IR, IE,
           After, Joined);
         Disposition := (if Joined then Prepared_Value_Step_Only else Native_Prepared_Refused);
      end;
   end Try_Next;
end Worldline.Custody_V2_Prepared_Wire;
