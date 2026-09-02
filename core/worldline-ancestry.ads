package Worldline.Ancestry with SPARK_Mode is
   use type Hash;


   type Parent_Guard is private;

   function New_Parent_Guard (Expected_Parent : Hash) return Parent_Guard
     with Post => Accepted (New_Parent_Guard'Result)
       and then Expected (New_Parent_Guard'Result) = Expected_Parent;

   function Accepted (Guard : Parent_Guard) return Boolean;
   function Expected (Guard : Parent_Guard) return Hash;

   procedure Claim
     (Guard           : in out Parent_Guard;
      Supplied_Parent : Hash;
      Claimed_Parent  : Hash)
     with Post =>
       Expected (Guard) = Expected (Guard'Old)
       and then
         (if not Accepted (Guard'Old) then not Accepted (Guard)
          else Accepted (Guard) =
            (Supplied_Parent = Expected (Guard'Old)
             and Claimed_Parent = Supplied_Parent));

   type Owner_Guard is private;

   function New_Owner_Guard (Owner : Hash) return Owner_Guard
     with Post => Owner_Accepted (New_Owner_Guard'Result)
       and then Expected_Owner (New_Owner_Guard'Result) = Owner;
   function Owner_Accepted (Guard : Owner_Guard) return Boolean;
   function Expected_Owner (Guard : Owner_Guard) return Hash;

   procedure Check_Owner
     (Guard          : in out Owner_Guard;
      Supplied_Owner : Hash)
     with Post =>
       Expected_Owner (Guard) = Expected_Owner (Guard'Old)
       and then
         (if not Owner_Accepted (Guard'Old) then
             not Owner_Accepted (Guard)
          else
             Owner_Accepted (Guard) =
               (Supplied_Owner = Expected_Owner (Guard'Old)));

private

   type Parent_Guard is record
      Parent : Hash;
      Valid  : Boolean;
   end record;

   function Accepted (Guard : Parent_Guard) return Boolean is (Guard.Valid);
   function Expected (Guard : Parent_Guard) return Hash is (Guard.Parent);

   type Owner_Guard is record
      Owner : Hash;
      Valid : Boolean;
   end record;

   function Owner_Accepted (Guard : Owner_Guard) return Boolean is
     (Guard.Valid);
   function Expected_Owner (Guard : Owner_Guard) return Hash is
     (Guard.Owner);

end Worldline.Ancestry;
