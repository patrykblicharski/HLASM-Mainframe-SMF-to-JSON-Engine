* ====================================================================
* SMF TYPE 74 SUBTYPE 3 — OMVS kernel activity
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* Section fields capped: 12/section, 48 total
* ====================================================================
TABLE74_3 SMF_START

         SMF_FIELD SMF74RTY-SMF74LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF74SID-SMF74LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF74TME-SMF74LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF74DTE-SMF74LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF74SSI-SMF74LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF74STY-SMF74LEN,TYPE=T_DEC2,JSON=subtype

* --- section SMF74_SUBTYPE3_PRODUCT_SECTION via SMF74PRS ---
         SMF_FIELD SMF74PRD-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF74DAT-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DTE,JSON=interval_date

         SMF_FIELD SMF74SAM-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC4,JSON=sample_count

         SMF_FIELD SMF74MVS-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_FIELD SMF74SRL-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC1,JSON=rmf_release

         SMF_FIELD SMF74RAO-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC4,JSON=rao

         SMF_FIELD SMF74RAL-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC2,JSON=ral

         SMF_FIELD SMF74RAN-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC2,JSON=ran

         SMF_FIELD SMF74OIL-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC2,JSON=oil

         SMF_FIELD SMF74SYN-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_DEC2,JSON=syn

         SMF_FIELD SMF74XNM-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_CHR8,JSON=sysplex_name

         SMF_FIELD SMF74SNM-SMF74MFV,TRIPLET=SMF74PRS-SMF74LEN,        X
               TYPE=T_CHR8,JSON=system_name

         SMF_END
