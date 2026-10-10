package body Worldline.Ancestry with SPARK_Mode is

   function New_Parent_Guard (Expected_Parent : Hash) return Parent_Guard is
     (Parent => Expected_Parent, Valid => True);

   procedure Claim
     (Guard           : in out Parent_Guard;
      Supplied_Parent : Hash;
      Claimed_Parent  : Hash)
   is
   begin
      if Guard.Valid then
         Guard.Valid :=
           Supplied_Parent = Guard.Parent
           and then Claimed_Parent = Supplied_Parent;
      end if;
   end Claim;

   function New_Owner_Guard (Owner : Hash) return Owner_Guard is
     (Owner => Owner, Valid => True);

   procedure Check_Owner
     (Guard          : in out Owner_Guard;
      Supplied_Owner : Hash)
   is
   begin
      if Guard.Valid then
         Guard.Valid := Supplied_Owner = Guard.Owner;
      end if;
   end Check_Owner;

end Worldline.Ancestry;
