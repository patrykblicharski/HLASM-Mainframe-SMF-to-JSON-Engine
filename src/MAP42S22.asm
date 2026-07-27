* ====================================================================
* SMF TYPE 42 SUBTYPE 22 — DFSMSrmm audit records
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_22 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- DFSMSrmm audit records section via SMF42AUD ---
         SMF_FIELD SMF42MJBN-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR8,JSON=mjbn

         SMF_FIELD SMF42MRST-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_TME,JSON=mrst

         SMF_FIELD SMF42MRSD-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_DTE,JSON=mrsd

         SMF_FIELD SMF42MUID-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR8,JSON=muid

         SMF_FIELD SMF42MACT-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR1,JSON=mact

         SMF_FIELD SMF42MFG1-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_DEC1,JSON=mfg1

         SMF_FIELD SMF42MLDTO-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR8,JSON=mldto

         SMF_FIELD SMF42MCVRLCTK-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR8,JSON=mcvrlctk

         SMF_FIELD SMF42MCSYNCTS-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR8,JSON=mcsyncts

         SMF_FIELD SMF42MCSYNCDT-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR4,JSON=mcsyncdt

         SMF_FIELD SMF42MCSYNCTM-SMF42MJBN,TRIPLET=SMF42AUD-SMF42RCL,        X
               TYPE=T_CHR4,JSON=mcsynctm

         SMF_END
