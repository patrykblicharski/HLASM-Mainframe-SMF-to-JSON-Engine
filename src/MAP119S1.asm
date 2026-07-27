* ====================================================================
* SMF TYPE 119 SUBTYPE 1 — TCP/IP Statistics
* Generated from temp/smf119-app pacsys layouts. Labels: CommServer/IFASMFR.
* ====================================================================
TABLE119_1 SMF_START

* --- header ---
         SMF_FIELD SMF119RTY-SMF119LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF119TME-SMF119LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF119DTE-SMF119LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF119SID-SMF119LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF119SSI-SMF119LEN,TYPE=T_CHR4,JSON=ssi

         SMF_FIELD SMF119STY-SMF119LEN,TYPE=T_DEC2,JSON=subtype

* --- section via SMF119IDOff ---
         SMF_FIELD SMF119TI_SYSName-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=system_name

         SMF_FIELD SMF119TI_SysplexName-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=sysplex_name

         SMF_FIELD SMF119TI_Stack-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=stack_name

         SMF_FIELD SMF119TI_ReleaseID-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tireleaseid

         SMF_FIELD SMF119TI_Comp-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=ticomp

         SMF_FIELD SMF119TI_ASName-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=as_name

         SMF_FIELD SMF119TI_UserID-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=user_id

         SMF_FIELD SMF119TI_ASID-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_DEC2,JSON=tiasid

         SMF_FIELD SMF119TI_Reason-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tireason

* --- section via SMF119S1Off ---
         SMF_FIELD SMF119AP_TIRName-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=aptirname

         SMF_FIELD SMF119AP_TIConnID-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=apticonnid

         SMF_FIELD SMF119AP_TIRsv1-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=aptirsv1

         SMF_FIELD SMF119AP_TISubTask-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=aptisubtask

         SMF_FIELD SMF119AP_TIRPort-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=aptirport

         SMF_FIELD SMF119AP_TILPort-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=aptilport

         SMF_FIELD SMF119AP_TITime-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=aptitime

         SMF_FIELD SMF119AP_TIDate-SMF119AP_TIRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DTE,JSON=aptidate

         SMF_END
