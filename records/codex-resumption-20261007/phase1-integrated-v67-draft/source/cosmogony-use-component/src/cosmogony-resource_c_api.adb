with Cosmogony.Hierarchy;

package body Cosmogony.Resource_C_API with SPARK_Mode => Off is
   use type Interfaces.C.int;

   function To_Resources (R : C_Resources)
      return Cosmogony.Hierarchy.Resources is
     (Worlds => R.Worlds,
      Evaluations => R.Evaluations,
      Memory_MiB => R.Memory_MiB,
      Threads => R.Threads);

   function Can_Add_C
     (Used, Extra, Limit : access constant C_Resources)
      return Interfaces.C.int is
   begin
      if Used = null or else Extra = null or else Limit = null then
         return -1;
      end if;
      return
        (if Cosmogony.Hierarchy.Can_Add
           (To_Resources (Used.all), To_Resources (Extra.all),
            To_Resources (Limit.all))
         then 1 else 0);
   end Can_Add_C;

   function ABI_Version return Interfaces.C.int is (1);
end Cosmogony.Resource_C_API;
