* ====================================================================
* SMF TYPE 72 SUBTYPE 5 — Serialization delay
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE72_5 SMF_START

         SMF_FIELD SMF72RTY-SMF72LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF72SID-SMF72LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF72TME-SMF72LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF72DTE-SMF72LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF72SSI-SMF72LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF72STY-SMF72LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF72PRD-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF72MVS-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
