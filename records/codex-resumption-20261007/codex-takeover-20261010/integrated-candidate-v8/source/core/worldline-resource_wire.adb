package body Worldline.Resource_Wire with SPARK_Mode is
   function Can_Reserve
     (Available_Negative : Boolean;
      Available, Withheld, Floor, Requested : Resources.Byte_Array)
      return Boolean
   is
   begin
      return not Available_Negative and then Resources.Can_Reserve
        (Available, Withheld, Floor, Requested);
   end Can_Reserve;
end Worldline.Resource_Wire;
