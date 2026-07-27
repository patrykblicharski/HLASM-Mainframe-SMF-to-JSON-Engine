* ====================================================================
* SMF TYPE 79 SUBTYPE 9 — Device activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE79_9 SMF_START

         SMF_FIELD SMF79RTY-SMF79LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF79SID-SMF79LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF79TME-SMF79LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF79DTE-SMF79LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF79SSI-SMF79LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF79STY-SMF79LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF79PRD-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF79MVS-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
