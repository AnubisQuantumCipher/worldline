with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Hierarchy;
with Cosmogony.Universes;

package Cosmogony.Host_Profiles with SPARK_Mode => On is
   use type Interfaces.Unsigned_32;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.Genesis.Digest;
   use type Cosmogony.Universes.Lifecycle_State;

   subtype Digest is Cosmogony.Genesis.Digest;
   Zero_Digest : Digest renames Cosmogony.Genesis.Zero_Digest;

   --  A monitor supplies these sampled values. Memory figures are MiB
   --  rounded conservatively by the boundary; tasks are OS cgroup pids.
   type Host_Observation is record
      Host_Id : Digest;
      Boot_Id : Digest;
      Cgroup_Id : Digest;
      Universe_Id : Digest;
      Policy_Epoch : Interfaces.Unsigned_64;
      Sequence : Interfaces.Unsigned_64;
      Observed_Tick : Interfaces.Unsigned_64;
      Expires_Tick : Interfaces.Unsigned_64;
      Memory_Capacity_MiB : Interfaces.Unsigned_64;
      Memory_Resident_MiB : Interfaces.Unsigned_64;
      Memory_Host_Reserve_MiB : Interfaces.Unsigned_64;
      Memory_Pending_MiB : Interfaces.Unsigned_64;
      Tasks_Capacity : Interfaces.Unsigned_32;
      Tasks_Resident : Interfaces.Unsigned_32;
      Tasks_Host_Reserve : Interfaces.Unsigned_32;
      Tasks_Pending : Interfaces.Unsigned_32;
      Memory_Limit_Enforced : Boolean;
      Tasks_Limit_Enforced : Boolean;
      Dormant_Universe_Count : Interfaces.Unsigned_32;
   end record;

   type Admission_Kind is (Refused, Eligible_Reservation);

   function Memory_Fits
     (S : Host_Observation; Need_MiB : Interfaces.Unsigned_32)
      return Boolean is
     (S.Memory_Resident_MiB <= S.Memory_Capacity_MiB
      and then S.Memory_Host_Reserve_MiB <=
        S.Memory_Capacity_MiB - S.Memory_Resident_MiB
      and then S.Memory_Pending_MiB <=
        S.Memory_Capacity_MiB - S.Memory_Resident_MiB -
        S.Memory_Host_Reserve_MiB
      and then Interfaces.Unsigned_64 (Need_MiB) <=
        S.Memory_Capacity_MiB - S.Memory_Resident_MiB -
        S.Memory_Host_Reserve_MiB - S.Memory_Pending_MiB);

   function Tasks_Fit
     (S : Host_Observation; Need : Interfaces.Unsigned_32)
      return Boolean is
     (S.Tasks_Resident <= S.Tasks_Capacity
      and then S.Tasks_Host_Reserve <=
        S.Tasks_Capacity - S.Tasks_Resident
      and then S.Tasks_Pending <=
        S.Tasks_Capacity - S.Tasks_Resident - S.Tasks_Host_Reserve
      and then Need <= S.Tasks_Capacity - S.Tasks_Resident -
        S.Tasks_Host_Reserve - S.Tasks_Pending);

   function Can_Admit
     (H : Cosmogony.Hierarchy.Hierarchy_State;
      S : Host_Observation;
      Request : Cosmogony.Hierarchy.Resources;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Cosmogony.Hierarchy.Valid (H)
      and then H.Universe.Life = Cosmogony.Universes.Active
      and then S.Host_Id /= Zero_Digest
      and then S.Boot_Id /= Zero_Digest
      and then S.Cgroup_Id /= Zero_Digest
      and then S.Universe_Id = H.Universe.Universe_Id
      and then S.Policy_Epoch = H.Universe.Policy_Epoch
      and then S.Sequence /= 0
      and then S.Observed_Tick <= Now_Tick
      and then Now_Tick < S.Expires_Tick
      and then S.Memory_Limit_Enforced
      and then S.Tasks_Limit_Enforced
      and then Request.Memory_MiB > 0
      and then Request.Threads > 0
      and then Cosmogony.Hierarchy.Can_Add
        (H.Child_Allocated, H.Local_Reserved, H.Limit)
      and then Cosmogony.Hierarchy.Can_Add
        (Cosmogony.Hierarchy.Plus
           (H.Child_Allocated, H.Local_Reserved, H.Limit),
         Request, H.Limit)
      and then Memory_Fits (S, Request.Memory_MiB)
      and then Tasks_Fit (S, Request.Threads));

   function Admit
     (H : Cosmogony.Hierarchy.Hierarchy_State;
      S : Host_Observation;
      Request : Cosmogony.Hierarchy.Resources;
      Now_Tick : Interfaces.Unsigned_64) return Admission_Kind
   with Post =>
     ((Admit'Result = Eligible_Reservation) =
        Can_Admit (H, S, Request, Now_Tick));
end Cosmogony.Host_Profiles;
