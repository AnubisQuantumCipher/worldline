with Ada.Characters.Latin_1;

package Input_Buffers is
   --  Library-level caller storage. Never mutated; Open requires access String.
   D01 : aliased String :=
     "From a" & Ada.Characters.Latin_1.LF &
     "Subject: A" & Ada.Characters.Latin_1.LF &
     Ada.Characters.Latin_1.LF & "one" & Ada.Characters.Latin_1.LF &
     Ada.Characters.Latin_1.LF & "From b" & Ada.Characters.Latin_1.LF &
     "Subject: B" & Ada.Characters.Latin_1.LF &
     Ada.Characters.Latin_1.LF & "two" & Ada.Characters.Latin_1.LF;
   D02 : aliased String :=
     "From a" & Ada.Characters.Latin_1.LF &
     "Subject: A" & Ada.Characters.Latin_1.LF &
     Ada.Characters.Latin_1.LF & "one" & Ada.Characters.Latin_1.LF;
end Input_Buffers;
