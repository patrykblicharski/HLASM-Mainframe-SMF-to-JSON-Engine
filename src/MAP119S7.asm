* ====================================================================
* SMF TYPE 119 SUBTYPE 7 — TCP/IP Statistics
* Generated from temp/smf119-app pacsys layouts. Labels: CommServer/IFASMFR.
* ====================================================================
TABLE119_7 SMF_START

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
         SMF_FIELD SMF119SP_TCRName-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=sptcrname

         SMF_FIELD SMF119SP_TCPort-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sptcport

         SMF_FIELD SMF119SP_TCConn-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sptcconn

         SMF_FIELD SMF119SP_TCBinds-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sptcbinds

         SMF_FIELD SMF119SP_TCBusySrv-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sptcbusysrv

         SMF_FIELD SMF119SP_TCSynAttack-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sptcsynattack

         SMF_FIELD SMF119SP_TCHighwater-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sptchighwater

         SMF_FIELD SMF119SP_TCNumConns-SMF119SP_TCRName,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sptcnumconns

* --- section via SMF119S2Off ---
         SMF_FIELD SMF119SP_UDRName-SMF119SP_UDRName,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=spudrname

         SMF_FIELD SMF119SP_UDPort-SMF119SP_UDRName,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=spudport

         SMF_END
