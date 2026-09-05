* ====================================================================
* SMF TYPE 71 SUBTYPE 1 — Paging activity
* ====================================================================
TABLE71_1 SMF_START

         SMF_FIELD SMF71RTY-SMF71LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF71SID-SMF71LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF71TME-SMF71LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF71DTE-SMF71LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF71SSI-SMF71LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF71STY-SMF71LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF71PIN-SMF71PIN,TRIPLET=SMF71PDS-SMF71LEN,        X
               TYPE=T_DEC4,JSON=page_ins

         SMF_FIELD SMF71POT-SMF71PIN,TRIPLET=SMF71PDS-SMF71LEN,        X
               TYPE=T_DEC4,JSON=page_outs

         SMF_FIELD SMF71SIN-SMF71PIN,TRIPLET=SMF71PDS-SMF71LEN,        X
               TYPE=T_DEC4,JSON=swap_ins

         SMF_FIELD SMF71SOT-SMF71PIN,TRIPLET=SMF71PDS-SMF71LEN,        X
               TYPE=T_DEC4,JSON=swap_outs

         SMF_FIELD SMF71AVF-SMF71PIN,TRIPLET=SMF71PDS-SMF71LEN,        X
               TYPE=T_DEC4,JSON=avg_frames

         SMF_END
