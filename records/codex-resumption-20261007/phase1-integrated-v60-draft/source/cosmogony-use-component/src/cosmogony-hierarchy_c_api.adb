with Cosmogony.Hierarchy;
with Cosmogony.Capabilities;
with Cosmogony.Genesis;

package body Cosmogony.Hierarchy_C_API with SPARK_Mode => Off is
   use type Interfaces.C.int;

   function To_Digest
     (D : Cosmogony.C_API.C_Digest) return Cosmogony.Genesis.Digest is
     (1 => D (0), 2 => D (1), 3 => D (2), 4 => D (3));

   function From_Digest
     (D : Cosmogony.Genesis.Digest) return Cosmogony.C_API.C_Digest is
     (0 => D (1), 1 => D (2), 2 => D (3), 3 => D (4));

   function To_Resources (R : C_Resources)
      return Cosmogony.Hierarchy.Resources is
     (Worlds => R.Worlds, Evaluations => R.Evaluations,
      Memory_MiB => R.Memory_MiB, Threads => R.Threads);

   function From_Resources (R : Cosmogony.Hierarchy.Resources)
      return C_Resources is
     (Worlds => R.Worlds, Evaluations => R.Evaluations,
      Memory_MiB => R.Memory_MiB, Threads => R.Threads);

   function Canonical_H (H : C_Hierarchy) return Boolean is
     (H.Count in 0 .. 8
      and then Cosmogony.Universe_C_API.Canonical_C (H.Universe));

   function To_Hierarchy (H : C_Hierarchy)
      return Cosmogony.Hierarchy.Hierarchy_State
   is
      Result : Cosmogony.Hierarchy.Hierarchy_State;
   begin
      Result.Universe := Cosmogony.Universe_C_API.To_Record (H.Universe);
      Result.Limit := To_Resources (H.Limit);
      Result.Local_Reserved := To_Resources (H.Local_Reserved);
      Result.Child_Allocated := To_Resources (H.Child_Allocated);
      Result.Count := Cosmogony.Hierarchy.Child_Count (H.Count);
      for I in Result.Allocations'Range loop
         Result.Allocations (I) :=
           (Child_Id =>
              To_Digest (H.Allocations (Interfaces.C.int (I) - 1).Child_Id),
            Grant =>
              To_Resources (H.Allocations (Interfaces.C.int (I) - 1).Grant));
      end loop;
      return Result;
   end To_Hierarchy;

   function From_Hierarchy (H : Cosmogony.Hierarchy.Hierarchy_State)
      return C_Hierarchy
   is
      Result : C_Hierarchy;
   begin
      Result.Universe := Cosmogony.Universe_C_API.From_Record (H.Universe);
      Result.Limit := From_Resources (H.Limit);
      Result.Local_Reserved := From_Resources (H.Local_Reserved);
      Result.Child_Allocated := From_Resources (H.Child_Allocated);
      Result.Count := Interfaces.C.int (H.Count);
      for I in H.Allocations'Range loop
         Result.Allocations (Interfaces.C.int (I) - 1) :=
           (Child_Id => From_Digest (H.Allocations (I).Child_Id),
            Grant => From_Resources (H.Allocations (I).Grant));
      end loop;
      return Result;
   end From_Hierarchy;

   function ABI_Version return Interfaces.C.int is (1);

   function Valid_C
     (H : access constant C_Hierarchy) return Interfaces.C.int is
   begin
      if H = null or else not Canonical_H (H.all) then
         return -1;
      end if;
      return
        (if Cosmogony.Hierarchy.Valid (To_Hierarchy (H.all))
         then 1 else 0);
   end Valid_C;

   function Parent_Ready_C
     (Parent : access constant Cosmogony.Universe_C_API.C_Record)
      return Interfaces.C.int is
   begin
      if Parent = null or else not Cosmogony.Universe_C_API.Canonical_C
        (Parent.all)
      then
         return -1;
      end if;
      return
        (if Cosmogony.Hierarchy.Parent_Ready
          (Cosmogony.Universe_C_API.To_Record (Parent.all))
         then 1 else 0);
   end Parent_Ready_C;

   function Create_C
     (Input : access constant C_Create_Input;
      Output : access C_Create_Output) return Interfaces.C.int
   is
      Result : Cosmogony.Hierarchy.Create_Result;
   begin
      if Output = null then
         return -1;
      end if;
      Output.Created := 0;
      if Input = null then
         return -1;
      end if;
      if not Canonical_H (Input.Parent_State)
        or else not Cosmogony.Universe_C_API.Canonical_C
          (Input.Child_Universe)
        or else not Cosmogony.C_API.Canonical_U (Input.Parent_Genesis)
        or else not Cosmogony.C_API.Canonical_U (Input.Child_Genesis)
        or else not Cosmogony.Capability_C_API.Canonical_C
          (Input.Parent_Capability)
        or else not Cosmogony.Capability_C_API.Canonical_C
          (Input.Child_Capability)
      then
         return -1;
      end if;
      Result := Cosmogony.Hierarchy.Create_Child
        (To_Hierarchy (Input.Parent_State),
         Cosmogony.C_API.To_State (Input.Parent_Genesis),
         Cosmogony.Universe_C_API.To_Record (Input.Child_Universe),
         Cosmogony.C_API.To_State (Input.Child_Genesis),
         Cosmogony.Capability_C_API.To_Capability
           (Input.Parent_Capability),
         Cosmogony.Capability_C_API.To_Capability
           (Input.Child_Capability),
         To_Resources (Input.Grant), To_Digest (Input.Caller_Id),
         Input.Now_Tick);
      Output.all :=
        (Created => (if Result.Created then 1 else 0),
         Parent_State => From_Hierarchy (Result.Parent_State),
         Child_State => From_Hierarchy (Result.Child_State),
         Child_Capability => Cosmogony.Capability_C_API.From_Capability
           (Result.Child_Capability));
      return 0;
   end Create_C;
end Cosmogony.Hierarchy_C_API;
