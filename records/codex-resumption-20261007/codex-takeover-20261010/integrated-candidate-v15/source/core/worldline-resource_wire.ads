with Worldline.Resources;

package Worldline.Resource_Wire with SPARK_Mode is
   --  Signed availability is explicit; missing observations are refused by
   --  the admission boundary before this total arithmetic rule is called.
   function Can_Reserve
     (Available_Negative : Boolean;
      Available, Withheld, Floor, Requested : Resources.Byte_Array)
      return Boolean
     with Global => null,
          Post => Can_Reserve'Result =
            (not Available_Negative and then Resources.Fits_By_Addition
              (Available, Withheld, Floor, Requested))
            and then Can_Reserve'Result =
              (not Available_Negative and then Resources.Fits_Mathematically
                (Available, Withheld, Floor, Requested));
end Worldline.Resource_Wire;
