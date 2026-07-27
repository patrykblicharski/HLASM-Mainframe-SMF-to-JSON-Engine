* ====================================================================
* SMF TYPE 77 SUBTYPE 1 — Enqueue activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* ====================================================================
TABLE77_1 SMF_START

         SMF_FIELD SMF77RTY-SMF77LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF77SID-SMF77LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF77TME-SMF77LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF77DTE-SMF77LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF77SSI-SMF77LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF77STY-SMF77LEN,TYPE=T_DEC2,JSON=subtype

         SMF_FIELD SMF77PRD-SMF77MFV,TRIPLET=SMF77PRS-SMF77LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF77MVS-SMF77MFV,TRIPLET=SMF77PRS-SMF77LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_END
