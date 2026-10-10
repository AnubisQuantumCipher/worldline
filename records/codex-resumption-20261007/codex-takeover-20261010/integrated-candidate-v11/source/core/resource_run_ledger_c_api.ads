--  Typed observer entry points retain the original complete snapshot/decoder bodies.
--  The unchanged C exports are enrolled in the existing sole Off Worldline.C_API.
--  C_API maps constrained views only after numeric transport validation; the
--  original loops below take the single snapshot before any foreign output write.
with Resource_Quantities;
with Resource_Run_Ledger_Wire;
with Interfaces;
with Interfaces.C;
package Resource_Run_Ledger_C_API with SPARK_Mode => On is
   function Version return Interfaces.Unsigned_32;
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long;
   function Check
     (Input : not null access constant Resource_Run_Ledger_Wire.Raw_Packet;
      Arena : not null access constant Resource_Quantities.Byte_Array;
      Before_Rows, Proposed_Rows : not null access constant Resource_Run_Ledger_Wire.Raw_Row_Array;
      Native : not null access constant Resource_Run_Ledger_Wire.Raw_Native_Array;
      Output : out Resource_Run_Ledger_Wire.Raw_Result) return Interfaces.C.int
     with Side_Effects;
end Resource_Run_Ledger_C_API;
