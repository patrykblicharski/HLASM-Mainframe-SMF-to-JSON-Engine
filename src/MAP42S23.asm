* ====================================================================
* SMF TYPE 42 SUBTYPE 23 — DFSMSrmm security records
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_23 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- DFSMSrmm security records section via SMF42SEC ---
         SMF_FIELD SMF42NJBN-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR8,JSON=njbn

         SMF_FIELD SMF42NRST-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_TME,JSON=nrst

         SMF_FIELD SMF42NRSD-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_DTE,JSON=nrsd

         SMF_FIELD SMF42NUIF-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR8,JSON=nuif

         SMF_FIELD SMF42NUID-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR8,JSON=nuid

         SMF_FIELD SMF42NCGP-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR8,JSON=ncgp

         SMF_FIELD SMF42NVER-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR1,JSON=nver

         SMF_FIELD SMF42NACT-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR1,JSON=nact

         SMF_FIELD SMF42NSTP-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_DEC1,JSON=nstp

         SMF_FIELD SMF42NUNT-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR8,JSON=nunt

         SMF_FIELD SMF42NLDTO-SMF42NJBN,TRIPLET=SMF42SEC-SMF42RCL,        X
               TYPE=T_CHR8,JSON=nldto

         SMF_END
