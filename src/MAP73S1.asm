* ====================================================================
* SMF TYPE 73 SUBTYPE 1 — Channel path activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE73_1 SMF_START

         SMF_FIELD SMF73RTY-SMF73LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF73SID-SMF73LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF73TME-SMF73LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF73DTE-SMF73LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF73SSI-SMF73LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF73STY-SMF73LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF73PRD-SMF73MFV,TRIPLET=SMF73PRS-SMF73LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF73MVS-SMF73MFV,TRIPLET=SMF73PRS-SMF73LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
