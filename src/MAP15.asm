* ====================================================================
* SMF TYPE 15 — OUTPUT/UPDAT/INOUT/OUTIN data set activity
* Header + common job identity (IFASMFR). Expand sections from SA38-0667.
* ====================================================================
TABLE15  SMF_START

         SMF_FIELD SMF15RTY-SMF15LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF15SID-SMF15LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF15TME-SMF15LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF15DTE-SMF15LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF15JBN-SMF15LEN,TYPE=T_CHR8,JSON=job_name

         SMF_FIELD SMF15RST-SMF15LEN,TYPE=T_TME,JSON=reader_start_t

         SMF_FIELD SMF15RSD-SMF15LEN,TYPE=T_DTE,JSON=reader_start_d

         SMF_FIELD SMF15UIF-SMF15LEN,TYPE=T_CHR8,JSON=user_id

         SMF_FIELD SMF15NDS-SMF15LEN,TYPE=T_DEC1,JSON=dataset_count

         SMF_END
