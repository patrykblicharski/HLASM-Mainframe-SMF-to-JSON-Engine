* ====================================================================
* SMF TYPE 79 SUBTYPE 15 — IRLM long lock detection
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* All supported T_* section fields (no per-section caps)
* ====================================================================
TABLE79_15 SMF_START

         SMF_FIELD SMF79RTY-SMF79LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF79SID-SMF79LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF79TME-SMF79LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF79DTE-SMF79LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF79SSI-SMF79LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF79STY-SMF79LEN,TYPE=T_DEC2,JSON=subtype

* --- section SMF79_SUBTYPE15_LONG_LOCK_DATA_SECTION via SMF79FPO ---
         SMF_FIELD R79FDLKC-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_DEC4,JSON=fdlkc

         SMF_FIELD R79FETYP-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_CHR1,JSON=fetyp

         SMF_FIELD R79FIMSI-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_CHR8,JSON=fimsi

         SMF_FIELD R79FPSTN-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_DEC2,JSON=fpstn

         SMF_FIELD R79FPSBN-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_CHR8,JSON=fpsbn

         SMF_FIELD R79FLHCN-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_DEC4,JSON=flhcn

         SMF_FIELD R79FTRNM-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_CHR8,JSON=ftrnm

         SMF_FIELD R79FRSNA-R79FISTN,TRIPLET=SMF79FPO-SMF79LEN,        X
               TYPE=T_CHR8,JSON=frsna

         SMF_END
