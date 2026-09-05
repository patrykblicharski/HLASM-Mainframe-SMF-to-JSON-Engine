* ====================================================================
* SMF TYPE 14 — INPUT or RDBACK data set activity
* Header + common job identity (IFASMFR). Expand sections from SA38-0667.
* ====================================================================
TABLE14  SMF_START

         SMF_FIELD SMF14RTY-SMF14LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF14SID-SMF14LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF14TME-SMF14LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF14DTE-SMF14LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF14JBN-SMF14LEN,TYPE=T_CHR8,JSON=job_name

         SMF_FIELD SMF14RST-SMF14LEN,TYPE=T_TME,JSON=reader_start_t

         SMF_FIELD SMF14RSD-SMF14LEN,TYPE=T_DTE,JSON=reader_start_d

         SMF_FIELD SMF14UIF-SMF14LEN,TYPE=T_CHR8,JSON=user_id

         SMF_FIELD SMF14NDS-SMF14LEN,TYPE=T_DEC1,JSON=dataset_count

         SMF_END
