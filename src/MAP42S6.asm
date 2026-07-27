* ====================================================================
* SMF TYPE 42 SUBTYPE 6 — Data set level I/O statistics
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_6 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- Job header section (data set statistics) via SMF42JHO ---
         SMF_FIELD S42JDJNM-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=job_name

         SMF_FIELD S42JDRST-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=jdrst

         SMF_FIELD S42JDRSD-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DTE,JSON=jdrsd

         SMF_FIELD S42JDUID-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=user_id

         SMF_FIELD S42JDCOD-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=jdcod

         SMF_FIELD S42JDVER-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=jdver

         SMF_FIELD S42JDPGN-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=jdpgn

         SMF_FIELD S42JDST1-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=jdst1

         SMF_FIELD S42JDGMO-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=jdgmo

         SMF_FIELD S42JDWSC-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=service_class

         SMF_FIELD S42JDWLD-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=workload_name

         SMF_FIELD S42JDTMP-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_CHR4,JSON=jdtmp

         SMF_FIELD S42JDSTN-S42JDJNM,TRIPLET=SMF42JHO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=step_name

         SMF_END
