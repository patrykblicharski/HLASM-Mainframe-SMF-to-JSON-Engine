* ====================================================================
* SMF TYPE 70 SUBTYPE 1 — CPU, PR/SM, and ICF activity
* ====================================================================
TABLE70_1 SMF_START

         SMF_FIELD SMF70RTY-SMF70LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF70SID-SMF70LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF70TME-SMF70LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF70DTE-SMF70LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF70SSI-SMF70LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF70STY-SMF70LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF70PRD-SMF70MFV,TRIPLET=SMF70PRS-SMF70LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF70MVS-SMF70MFV,TRIPLET=SMF70PRS-SMF70LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_FIELD SMF70LPM-SMF70LPM,TRIPLET=SMF70BCS-SMF70LEN,        X
               TYPE=T_CHR8,JSON=lpar_name

         SMF_END
