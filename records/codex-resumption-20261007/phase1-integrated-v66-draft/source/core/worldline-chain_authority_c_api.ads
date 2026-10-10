with Worldline.Chain_Authority_Wire;
with Resource_Quantities;
with Interfaces;
with Interfaces.C;
with System;
package Worldline.Chain_Authority_C_API with SPARK_Mode => On is
   function Version return Interfaces.Unsigned_32
     with Export, Convention => C, External_Name => "wl_chain_authority_version_v1";
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long
     with Export, Convention => C, External_Name => "wl_chain_authority_layout_v1";
   --  Four original digests, each one presence byte plus the complete hash.
   Row_Bits : constant :=
     4 * (1 + Worldline.Chain_Authority_Wire.Raw_Hash'Length)
       * Interfaces.Unsigned_8'Object_Size;
   type Raw_Rows is array (Resource_Quantities.Byte_Index range <>) of
     Worldline.Chain_Authority_Wire.Raw_Row
     with Component_Size => Row_Bits;
   pragma Compile_Time_Error
     (Raw_Rows'Component_Size /= Worldline.Chain_Authority_Wire.Raw_Row'Object_Size,
      "chain row stride differs from its C element layout");

   function Transport_Valid
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Boolean;

   function Replay
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t;
      Anchors_View : access constant Worldline.Chain_Authority_Wire.Raw_Anchors;
      Rows_View : access constant Raw_Rows;
      Output_View : access Worldline.Chain_Authority_Wire.Raw_Result)
      return Interfaces.C.int
     with Side_Effects;
end Worldline.Chain_Authority_C_API;
