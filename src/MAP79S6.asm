* ====================================================================
* SMF TYPE 79 SUBTYPE 6 — Reserve data
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* All supported T_* section fields (no per-section caps)
* ====================================================================
TABLE79_6 SMF_START

         SMF_FIELD SMF79RTY-SMF79LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF79SID-SMF79LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF79TME-SMF79LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF79DTE-SMF79LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF79SSI-SMF79LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF79STY-SMF79LEN,TYPE=T_DEC2,JSON=subtype

* --- section SMF79_SUBTYPE6_PRODUCT_SECTION via SMF79PRS ---
         SMF_FIELD SMF79PRD-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF79DAT-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DTE,JSON=interval_date

         SMF_FIELD SMF79SAM-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC4,JSON=sample_count

         SMF_FIELD SMF79MVS-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_FIELD SMF79SRL-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC1,JSON=rmf_release

         SMF_FIELD SMF79RAO-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC4,JSON=rao

         SMF_FIELD SMF79RAL-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=ral

         SMF_FIELD SMF79RAN-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=ran

         SMF_FIELD SMF79OIL-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=oil

         SMF_FIELD SMF79SYN-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=syn

         SMF_FIELD SMF79XNM-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=sysplex_name

         SMF_FIELD SMF79SNM-SMF79MFV,TRIPLET=SMF79PRS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=system_name

* --- section SMF79_SUBTYPE6_MONITOR_2_CONTROL_SECTION via SMF79MCS ---
         SMF_FIELD R79SES-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_CHR2,JSON=ses

         SMF_FIELD R79USER-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=user

         SMF_FIELD R79RID-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_CHR8,JSON=rid

         SMF_FIELD R79CTXTL-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=ctxtl

         SMF_FIELD R79DTXTL-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=dtxtl

         SMF_FIELD R79TSR-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_DEC2,JSON=tsr

         SMF_FIELD R79TOT-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_DEC4,JSON=tot

         SMF_FIELD R79NXT-R79GTOD,TRIPLET=SMF79MCS-SMF79LEN,        X
               TYPE=T_DEC4,JSON=nxt

         SMF_END
