-- Linux AArch64 LP64 process-filter successor: original guard policy plus
-- the actual setns/unshare denials, with the original thread-clone domain.
package Worldline.Confinement_Filter with SPARK_Mode is
   function Establishes (Encoded_Program : String) return Boolean
      with Global => null;
end Worldline.Confinement_Filter;
