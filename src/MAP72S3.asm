* ====================================================================
* SMF TYPE 72 SUBTYPE 3 — Workload activity (WLM)
* ====================================================================
TABLE72_3 SMF_START

         SMF_FIELD SMF72RTY-SMF72LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF72SID-SMF72LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF72TME-SMF72LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF72DTE-SMF72LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF72SSI-SMF72LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF72STY-SMF72LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD R723MCNM-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=class_name

         SMF_FIELD R723MCPG-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_DEC2,JSON=period_count

         SMF_FIELD R723CPER-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC1,JSON=period_number

         SMF_FIELD R723CCDE-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=cpu_delay

         SMF_END
