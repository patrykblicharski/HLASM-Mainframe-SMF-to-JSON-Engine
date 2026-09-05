* ====================================================================
* SMF TYPE 42 SUBTYPE 27 — VTOC DSCB audit record
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_27 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- VTOC update header section via SMF4227R1 ---
         SMF_FIELD SMF42RJOB-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_CHR8,JSON=rjob

         SMF_FIELD SMF42RJNO-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_CHR8,JSON=rjno

         SMF_FIELD SMF42RSTN-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_CHR8,JSON=rstn

         SMF_FIELD SMF42RPRN-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_CHR8,JSON=rprn

         SMF_FIELD SMF42RDEV-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_DEC2,JSON=rdev

         SMF_FIELD SMF42RACT-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_CHR4,JSON=ract

         SMF_FIELD SMF42RACT-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_CHR4,JSON=ract2

         SMF_FIELD SMF42RIND-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_DEC1,JSON=rind

         SMF_FIELD SMF42RDS1-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_DEC1,JSON=rds1

         SMF_FIELD SMF42RSEEK-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_DEC4,JSON=rseek

         SMF_FIELD SMF42RUPSW-SMF42RJOB,TRIPLET=SMF4227R1-SMF42RCL,        X
               TYPE=T_DEC4,JSON=rupsw

         SMF_END
