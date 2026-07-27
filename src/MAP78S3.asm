* ====================================================================
* SMF TYPE 78 SUBTYPE 3 — I/O queuing activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE78_3 SMF_START

         SMF_FIELD SMF78RTY-SMF78LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF78SID-SMF78LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF78TME-SMF78LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF78DTE-SMF78LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF78SSI-SMF78LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF78STY-SMF78LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF78PRD-SMF78MFV,TRIPLET=SMF78PRS-SMF78LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF78MVS-SMF78MFV,TRIPLET=SMF78PRS-SMF78LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
