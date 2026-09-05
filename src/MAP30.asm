* ====================================================================
* MASTER MAPPING TABLE FOR SMF TYPE 30 (JSON CONVERSION)
* Layout reference: https://www.pacsys.com/smf/smf30.htm
* Scope: common sections only (no subtype-only / repeating EXCP /
*        variable accounting / 8-byte binary / float fields)
* ====================================================================

* CONSTANTS FOR DATA TYPES
T_BIN1   EQU   0      Binary 1 Byte
T_CHR1   EQU   1      EBCDIC STRING 1 Bytes
T_CHR2   EQU   2      EBCDIC STRING 2 Bytes
T_CHR4   EQU   3      EBCDIC STRING 4 Bytes
T_CHR8   EQU   4      EBCDIC STRING 8 Bytes
T_DEC1   EQU   5      Decimal 1 Byte
T_DEC2   EQU   6      Decimal 2 Bytes
T_DEC4   EQU   7      Decimal 4 Bytes
T_DTE    EQU   8      SMF DATE (4 Bytes)
T_TME    EQU   9      SMF TIME (4 Bytes)
T_RS_STR EQU   10     RS Variable Length EBCDIC String (Tag-Len-Data)
T_CHR16  EQU   11     EBCDIC STRING 16 Bytes
T_CHR20  EQU   12     EBCDIC STRING 20 Bytes


TABLE30  SMF_START

* --------------------------------------------------------------------
* Standard header / self-defining section (no triplet)
* --------------------------------------------------------------------
         SMF_FIELD SMF30FLG-SMF30LEN,TYPE=T_DEC1,JSON=smf_sys_flag

         SMF_FIELD SMF30RTY-SMF30LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF30TME-SMF30LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF30DTE-SMF30LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF30SID-SMF30LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF30WID-SMF30LEN,TYPE=T_CHR4,JSON=work_type
* SMF30STP (subtype) intentionally omitted

* --------------------------------------------------------------------
* Subsystem section  (triplet SMF30SOF, base SMF30PSS)
* --------------------------------------------------------------------
* SMF30TYP (subtype id) intentionally omitted
         SMF_FIELD SMF30RVN-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR2,JSON=rec_version

         SMF_FIELD SMF30PNM-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF30OSL-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=os_level

         SMF_FIELD SMF30SYN-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=sys_name

         SMF_FIELD SMF30SYP-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=sysplex_name

* --------------------------------------------------------------------
* Identification section  (triplet SMF30IOF, base SMF30JBN)
* --------------------------------------------------------------------
         SMF_FIELD SMF30JBN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=job_name

         SMF_FIELD SMF30PGM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=program_name

         SMF_FIELD SMF30STM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=step_name

         SMF_FIELD SMF30UIF-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=user_id_field

         SMF_FIELD SMF30JNM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=jes_job_id

         SMF_FIELD SMF30STN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=step_number

         SMF_FIELD SMF30CLS-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR1,JSON=job_class

         SMF_FIELD SMF30PGN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=perf_group

         SMF_FIELD SMF30JPT-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=jes_priority

         SMF_FIELD SMF30AST-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_TME,JSON=alloc_start_t

         SMF_FIELD SMF30PPS-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_TME,JSON=prog_start_t

         SMF_FIELD SMF30SIT-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_TME,JSON=step_init_t

         SMF_FIELD SMF30STD-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DTE,JSON=step_init_d

         SMF_FIELD SMF30RST-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_TME,JSON=reader_start_t

         SMF_FIELD SMF30RSD-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DTE,JSON=reader_start_d

         SMF_FIELD SMF30RET-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_TME,JSON=reader_end_t

         SMF_FIELD SMF30RED-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DTE,JSON=reader_end_d

         SMF_FIELD SMF30USR-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR20,JSON=programmer_name

         SMF_FIELD SMF30GRP-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=racf_group

         SMF_FIELD SMF30RUD-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=racf_user

         SMF_FIELD SMF30TID-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=racf_term_id

         SMF_FIELD SMF30TSN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=term_sym_name

         SMF_FIELD SMF30PSN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=proc_step_name

         SMF_FIELD SMF30CL8-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=job_class_8

         SMF_FIELD SMF30SSN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=substep_num

         SMF_FIELD SMF30EXN-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR16,JSON=omvs_pgm_name

* --------------------------------------------------------------------
* I/O activity section  (triplet SMF30UOF, base SMF30INP)
* --------------------------------------------------------------------
         SMF_FIELD SMF30INP-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=card_images

         SMF_FIELD SMF30TEP-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=total_blocks

         SMF_FIELD SMF30TPT-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=tput_count

         SMF_FIELD SMF30TGT-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=tget_count

         SMF_FIELD SMF30RDR-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=reader_dev_cls

         SMF_FIELD SMF30RDT-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=reader_dev_typ

         SMF_FIELD SMF30TCN-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=tot_dev_conn

         SMF_FIELD SMF30DCF-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=io_flag_word

         SMF_FIELD SMF30TRR-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=reread_count

         SMF_FIELD SMF30AIC-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=dasd_conn_t

         SMF_FIELD SMF30AID-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=dasd_disc_t

         SMF_FIELD SMF30AIW-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=dasd_pend_t

         SMF_FIELD SMF30AIS-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=dasd_ssch_ct

         SMF_FIELD SMF30EIC-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ie_conn_t

         SMF_FIELD SMF30EID-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ie_disc_t

         SMF_FIELD SMF30EIW-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ie_pend_t

         SMF_FIELD SMF30EIS-SMF30INP,TRIPLET=SMF30UOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ie_ssch_ct

* --------------------------------------------------------------------
* Completion section  (triplet SMF30TOF, base SMF30SCC)
* --------------------------------------------------------------------
         SMF_FIELD SMF30SCC-SMF30SCC,TRIPLET=SMF30TOF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=step_comp_code

         SMF_FIELD SMF30STI-SMF30SCC,TRIPLET=SMF30TOF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=term_indicator

         SMF_FIELD SMF30ARC-SMF30SCC,TRIPLET=SMF30TOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=abend_reason

* --------------------------------------------------------------------
* Processor accounting section  (triplet SMF30COF, base SMF30PTY)
* --------------------------------------------------------------------
         SMF_FIELD SMF30TFL-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=timer_flags

         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=cpu_step_time

         SMF_FIELD SMF30CPS-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=srb_time

         SMF_FIELD SMF30ICU-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=init_tcb_time

         SMF_FIELD SMF30ISB-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=init_srb_time

         SMF_FIELD SMF30JVU-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=step_vect_cpu

         SMF_FIELD SMF30IVU-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=init_vect_cpu

         SMF_FIELD SMF30JVA-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=step_vect_aff

         SMF_FIELD SMF30IVA-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=init_vect_aff

         SMF_FIELD SMF30IST-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_TME,JSON=interval_start

         SMF_FIELD SMF30IDT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DTE,JSON=interval_date

         SMF_FIELD SMF30IIP-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=io_int_cpu

         SMF_FIELD SMF30RCT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=rct_cpu_time

         SMF_FIELD SMF30HPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=hiperspace_cpu

         SMF_FIELD SMF30CSC-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=icsf_svc_count

         SMF_FIELD SMF30DMI-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=admf_write_pgs

         SMF_FIELD SMF30DMO-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=admf_read_pgs

         SMF_FIELD SMF30ASR-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=preempt_srb_t

         SMF_FIELD SMF30ENC-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ind_enclave_t

         SMF_FIELD SMF30DET-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=dep_enclave_t

         SMF_FIELD SMF30CEP-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=enqueue_cpu_t

         SMF_FIELD SMF30TF2-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=timer_flags2

* --------------------------------------------------------------------
* Storage and paging section  (triplet SMF30ROF, base SMF30RSV)
* --------------------------------------------------------------------
         SMF_FIELD SMF30SFL-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=storage_flags

         SMF_FIELD SMF30SPK-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=storage_key

         SMF_FIELD SMF30PRV-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=priv_below_k

         SMF_FIELD SMF30SYS-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC2,JSON=sys_above_k

         SMF_FIELD SMF30PGI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=pages_in

         SMF_FIELD SMF30PGO-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=pages_out

         SMF_FIELD SMF30CPM-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=eso_misses

         SMF_FIELD SMF30NSW-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=swap_seqs

         SMF_FIELD SMF30PSI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=pages_swap_in

         SMF_FIELD SMF30PSO-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=pages_swap_out

         SMF_FIELD SMF30VPI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=vio_pages_in

         SMF_FIELD SMF30VPO-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=vio_pages_out

         SMF_FIELD SMF30VPR-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=vio_reclaims

         SMF_FIELD SMF30CPI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=common_pg_in

         SMF_FIELD SMF30HPI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=hsp_pages_in

         SMF_FIELD SMF30LPI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=lpa_pages_in

         SMF_FIELD SMF30HPO-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=hsp_pages_out

         SMF_FIELD SMF30PST-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=pages_stolen

         SMF_FIELD SMF30RGB-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=priv_below_b

         SMF_FIELD SMF30ERG-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=priv_above_b

         SMF_FIELD SMF30ARB-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=lsqa_below_b

         SMF_FIELD SMF30EAR-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=lsqa_above_b

         SMF_FIELD SMF30URB-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=user_below_b

         SMF_FIELD SMF30EUR-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=user_above_b

         SMF_FIELD SMF30RGN-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=region_k

         SMF_FIELD SMF30DSV-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=dataspace_mb

         SMF_FIELD SMF30PIE-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=unblk_exp_in

         SMF_FIELD SMF30POE-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=unblk_exp_out

         SMF_FIELD SMF30BIA-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blk_aux_in

         SMF_FIELD SMF30BOA-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blk_aux_out

         SMF_FIELD SMF30BIE-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blk_exp_in

         SMF_FIELD SMF30BOE-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blk_exp_out

         SMF_FIELD SMF30KIA-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blocks_aux_in

         SMF_FIELD SMF30KOA-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blocks_aux_out

         SMF_FIELD SMF30KIE-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blocks_exp_in

         SMF_FIELD SMF30KOE-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=blocks_exp_out

         SMF_FIELD SMF30PAI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=shared_pg_aux

         SMF_FIELD SMF30PEI-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=shared_pg_exp

         SMF_FIELD SMF30MLS-SMF30RSV,TRIPLET=SMF30ROF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=memlimit_src

* --------------------------------------------------------------------
* Performance section  (triplet SMF30POF, base SMF30SRV)
* --------------------------------------------------------------------
         SMF_FIELD SMF30SRV-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=total_service

         SMF_FIELD SMF30CSU-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=cpu_service

         SMF_FIELD SMF30SRB-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=srb_service

         SMF_FIELD SMF30IO-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,         X
               TYPE=T_DEC4,JSON=io_service

         SMF_FIELD SMF30MSO-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=mso_service

         SMF_FIELD SMF30TAT-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=trans_act_t

         SMF_FIELD SMF30SUS-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=cpu_adj_factor

         SMF_FIELD SMF30RES-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=trans_res_t

         SMF_FIELD SMF30TRS-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=trans_count

         SMF_FIELD SMF30WLM-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=workload_name

         SMF_FIELD SMF30SCN-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=service_class

         SMF_FIELD SMF30GRN-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=resource_group

         SMF_FIELD SMF30RCN-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=report_class

         SMF_FIELD SMF30ETA-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ind_enc_act_t

         SMF_FIELD SMF30ESU-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ind_enc_cpu_su

         SMF_FIELD SMF30ETC-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=ind_enc_trans

         SMF_FIELD SMF30PFL-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_CHR16,JSON=sched_env_name

         SMF_FIELD SMF30JQT-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=job_prep_t

         SMF_FIELD SMF30RQT-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=inq_elig_t

         SMF_FIELD SMF30HQT-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=hold_queue_t

         SMF_FIELD SMF30SQT-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=eligible_t

         SMF_FIELD SMF30PF1-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=perf_flag1

         SMF_FIELD SMF30PF2-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_DEC1,JSON=perf_flag2

         SMF_FIELD SMF30JPN-SMF30SRV,TRIPLET=SMF30POF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=subsys_coll

* --------------------------------------------------------------------
* Operator section  (triplet SMF30OOF, base SMF30PDM)
* --------------------------------------------------------------------
         SMF_FIELD SMF30PDM-SMF30PDM,TRIPLET=SMF30OOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=nonspec_dasd

         SMF_FIELD SMF30PRD-SMF30PDM,TRIPLET=SMF30OOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=spec_dasd_mnt

         SMF_FIELD SMF30PTM-SMF30PDM,TRIPLET=SMF30OOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=nonspec_tape

         SMF_FIELD SMF30TPR-SMF30PDM,TRIPLET=SMF30OOF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=spec_tape_mnt

         SMF_END
