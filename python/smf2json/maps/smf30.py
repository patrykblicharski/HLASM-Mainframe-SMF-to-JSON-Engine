"""SMF type 30 — Common address space work (subtypes 1–6 via SMF30STP).

Layouts from IBM z/OS SMF (IFASMFR) / PACSYS smf30 tables and MAP30.asm.
Header + subsystem + identification are shared; resource sections vary by subtype.
Register via ``MAPS_BY_SUBTYPE[(30, sty)]`` — do not use a flat type-30 map.

Section presence (IBM / PACSYS):
  1 Job initiation — no resource sections (identifies the work unit only)
  2 Interval — I/O, processor, storage, performance (no completion)
  3 Last interval before step end — same as 2
  4 Step total — I/O, completion, processor, storage, performance, operator
  5 Job termination — same as 4
  6 System address space — I/O, processor, storage, performance (partial fields)
"""

from __future__ import annotations

from ..types import FieldSpec as F

# Header triplet absolute offsets (from SMF30LEN / record start including RDW)
SOF, IOF, UOF, TOF, COF, ROF, POF, OOF = 24, 32, 40, 48, 56, 72, 80, 88
# AOF (accounting @64) and EXCP / APPC / USS / … triplets exist but are unmapped here.


def _h(key, ibm, ftype, off, desc):
    return F(key, ibm, ftype, off, None, description=desc)


def _s(key, ibm, ftype, off, trip, desc):
    return F(key, ibm, ftype, off, trip, description=desc)


HEADER = [
    _h("smf_sys_flag", "SMF30FLG", "DEC1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF30RTY", "DEC1", 5, "Record type (30)"),
    _h("time", "SMF30TME", "TME", 6, "Time record moved to SMF buffer (HH:MM:SS)"),
    _h("date", "SMF30DTE", "DTE", 10, "Date record moved to SMF buffer (YYYY-MM-DD)"),
    _h("smf_system_id", "SMF30SID", "CHR4", 14, "System identification (SID)"),
    _h("work_type", "SMF30WID", "CHR4", 18, "Work type indicator (JOB/STC/TSO/...)"),
    _h("smf_subtype", "SMF30STP", "DEC2", 22, "Record subtype (SMF30STP)"),
]

SUBSYSTEM = [
    _s("rec_version", "SMF30RVN", "CHR2", 4, SOF, "Record version number"),
    _s("product_name", "SMF30PNM", "CHR8", 6, SOF, "Subsystem / product name (e.g. SMF)"),
    _s("os_level", "SMF30OSL", "CHR8", 14, SOF, "MVS software level"),
    _s("sys_name", "SMF30SYN", "CHR8", 22, SOF, "System name (SYSNAME)"),
    _s("sysplex_name", "SMF30SYP", "CHR8", 30, SOF, "Sysplex name"),
]

IDENTIFICATION = [
    _s("job_name", "SMF30JBN", "CHR8", 0, IOF, "Job or session name"),
    _s("program_name", "SMF30PGM", "CHR8", 8, IOF, "Program name (PGM=)"),
    _s("step_name", "SMF30STM", "CHR8", 16, IOF, "Step name"),
    _s("user_id_field", "SMF30UIF", "CHR8", 24, IOF, "User-defined identification field"),
    _s("jes_job_id", "SMF30JNM", "CHR8", 32, IOF, "JES job identifier"),
    _s("step_number", "SMF30STN", "DEC2", 40, IOF, "Step number"),
    _s("job_class", "SMF30CLS", "CHR1", 42, IOF, "Job class"),
    _s("perf_group", "SMF30PGN", "DEC2", 44, IOF, "Performance group number (legacy)"),
    _s("jes_priority", "SMF30JPT", "DEC2", 46, IOF, "JES input priority"),
    _s("alloc_start_t", "SMF30AST", "TME", 48, IOF, "Device allocation start time"),
    _s("prog_start_t", "SMF30PPS", "TME", 52, IOF, "Problem program start time"),
    _s("step_init_t", "SMF30SIT", "TME", 56, IOF, "Step initiation time"),
    _s("step_init_d", "SMF30STD", "DTE", 60, IOF, "Step initiation date"),
    _s("reader_start_t", "SMF30RST", "TME", 64, IOF, "Reader start time"),
    _s("reader_start_d", "SMF30RSD", "DTE", 68, IOF, "Reader start date"),
    _s("reader_end_t", "SMF30RET", "TME", 72, IOF, "Reader end time"),
    _s("reader_end_d", "SMF30RED", "DTE", 76, IOF, "Reader end date"),
    _s("programmer_name", "SMF30USR", "CHR20", 80, IOF, "Programmer name"),
    _s("racf_group", "SMF30GRP", "CHR8", 100, IOF, "RACF group ID"),
    _s("racf_user", "SMF30RUD", "CHR8", 108, IOF, "RACF user ID"),
    _s("racf_term_id", "SMF30TID", "CHR8", 116, IOF, "RACF terminal ID"),
    _s("term_sym_name", "SMF30TSN", "CHR8", 124, IOF, "Terminal symbolic name"),
    _s("proc_step_name", "SMF30PSN", "CHR8", 132, IOF, "Procedure step name"),
    _s("job_class_8", "SMF30CL8", "CHR8", 140, IOF, "8-character job class"),
    _s("substep_num", "SMF30SSN", "DEC4", 164, IOF, "Substep number (OpenMVS)"),
    _s("omvs_pgm_name", "SMF30EXN", "CHR16", 168, IOF, "OpenMVS / program name"),
]

IO_ACTIVITY = [
    _s("card_images", "SMF30INP", "DEC4", 0, UOF, "Card-image records read"),
    _s("total_blocks", "SMF30TEP", "DEC4", 4, UOF, "Total blocks transferred (EXCP)"),
    _s("tput_count", "SMF30TPT", "DEC4", 8, UOF, "TPUT count (TSO)"),
    _s("tget_count", "SMF30TGT", "DEC4", 12, UOF, "TGET count (TSO)"),
    _s("reader_dev_cls", "SMF30RDR", "DEC1", 16, UOF, "Reader device class"),
    _s("reader_dev_typ", "SMF30RDT", "DEC1", 17, UOF, "Reader device type"),
    _s("tot_dev_conn", "SMF30TCN", "DEC4", 18, UOF, "Total device connect time"),
    _s("io_flag_word", "SMF30DCF", "DEC4", 22, UOF, "I/O activity flags"),
    _s("reread_count", "SMF30TRR", "DEC4", 28, UOF, "Address space re-read count"),
    _s("dasd_conn_t", "SMF30AIC", "DEC4", 32, UOF, "DASD connect time (AS+dep)"),
    _s("dasd_disc_t", "SMF30AID", "DEC4", 36, UOF, "DASD disconnect time"),
    _s("dasd_pend_t", "SMF30AIW", "DEC4", 40, UOF, "DASD pending time"),
    _s("dasd_ssch_ct", "SMF30AIS", "DEC4", 44, UOF, "DASD SSCH count"),
    _s("ie_conn_t", "SMF30EIC", "DEC4", 48, UOF, "Indep. enclave DASD connect"),
    _s("ie_disc_t", "SMF30EID", "DEC4", 52, UOF, "Indep. enclave DASD disconnect"),
    _s("ie_pend_t", "SMF30EIW", "DEC4", 56, UOF, "Indep. enclave DASD pending"),
    _s("ie_ssch_ct", "SMF30EIS", "DEC4", 60, UOF, "Indep. enclave SSCH count"),
]

COMPLETION = [
    _s("step_comp_code", "SMF30SCC", "DEC2", 0, TOF, "Step / job completion code"),
    _s("term_indicator", "SMF30STI", "DEC2", 2, TOF, "Termination indicator flags"),
    _s("abend_reason", "SMF30ARC", "DEC4", 4, TOF, "Abend reason code"),
]

PROCESSOR = [
    _s("timer_flags", "SMF30TFL", "DEC2", 2, COF, "Invalid timer flags"),
    _s("cpu_step_time", "SMF30CPT", "DEC4", 4, COF, "Step TCB CPU time (0.01s)"),
    _s("srb_time", "SMF30CPS", "DEC4", 8, COF, "Step SRB CPU time (0.01s)"),
    _s("init_tcb_time", "SMF30ICU", "DEC4", 12, COF, "Initiator TCB CPU time"),
    _s("init_srb_time", "SMF30ISB", "DEC4", 16, COF, "Initiator SRB CPU time"),
    _s("step_vect_cpu", "SMF30JVU", "DEC4", 20, COF, "Step vector CPU time"),
    _s("init_vect_cpu", "SMF30IVU", "DEC4", 24, COF, "Initiator vector CPU time"),
    _s("step_vect_aff", "SMF30JVA", "DEC4", 28, COF, "Step vector affinity time"),
    _s("init_vect_aff", "SMF30IVA", "DEC4", 32, COF, "Initiator vector affinity time"),
    _s("interval_start", "SMF30IST", "TME", 36, COF, "Interval start time"),
    _s("interval_date", "SMF30IDT", "DTE", 40, COF, "Interval start date"),
    _s("io_int_cpu", "SMF30IIP", "DEC4", 44, COF, "I/O interrupt CPU time"),
    _s("rct_cpu_time", "SMF30RCT", "DEC4", 48, COF, "RCT CPU time"),
    _s("hiperspace_cpu", "SMF30HPT", "DEC4", 52, COF, "Hiperspace CPU time"),
    _s("icsf_svc_count", "SMF30CSC", "DEC4", 56, COF, "ICSF service count"),
    _s("admf_write_pgs", "SMF30DMI", "DEC4", 60, COF, "ADMF write pages"),
    _s("admf_read_pgs", "SMF30DMO", "DEC4", 64, COF, "ADMF read pages"),
    _s("preempt_srb_t", "SMF30ASR", "DEC4", 68, COF, "Preemptable / client SRB time"),
    _s("ind_enclave_t", "SMF30ENC", "DEC4", 72, COF, "Independent enclave CPU time"),
    _s("dep_enclave_t", "SMF30DET", "DEC4", 76, COF, "Dependent enclave CPU time"),
    _s("enqueue_cpu_t", "SMF30CEP", "DEC4", 80, COF, "Enqueue-promoted CPU time"),
    _s("timer_flags2", "SMF30TF2", "DEC2", 82, COF, "Additional timer flags"),
]

STORAGE = [
    _s("storage_flags", "SMF30SFL", "DEC1", 2, ROF, "Storage flags"),
    _s("storage_key", "SMF30SPK", "DEC1", 3, ROF, "Storage protect key"),
    _s("priv_below_k", "SMF30PRV", "DEC2", 4, ROF, "Private below 16M (K)"),
    _s("sys_above_k", "SMF30SYS", "DEC2", 6, ROF, "System area from top (K)"),
    _s("pages_in", "SMF30PGI", "DEC4", 8, ROF, "Pages paged in"),
    _s("pages_out", "SMF30PGO", "DEC4", 12, ROF, "Pages paged out"),
    _s("eso_misses", "SMF30CPM", "DEC4", 16, ROF, "ESO hiperspace misses"),
    _s("swap_seqs", "SMF30NSW", "DEC4", 20, ROF, "Swap sequences"),
    _s("pages_swap_in", "SMF30PSI", "DEC4", 24, ROF, "Pages swapped in"),
    _s("pages_swap_out", "SMF30PSO", "DEC4", 28, ROF, "Pages swapped out"),
    _s("vio_pages_in", "SMF30VPI", "DEC4", 32, ROF, "VIO pages in"),
    _s("vio_pages_out", "SMF30VPO", "DEC4", 36, ROF, "VIO pages out"),
    _s("vio_reclaims", "SMF30VPR", "DEC4", 40, ROF, "VIO reclaims"),
    _s("common_pg_in", "SMF30CPI", "DEC4", 44, ROF, "Common area page-ins"),
    _s("hsp_pages_in", "SMF30HPI", "DEC4", 48, ROF, "Hiperspace page-ins"),
    _s("lpa_pages_in", "SMF30LPI", "DEC4", 52, ROF, "LPA page-ins"),
    _s("hsp_pages_out", "SMF30HPO", "DEC4", 56, ROF, "Hiperspace page-outs"),
    _s("pages_stolen", "SMF30PST", "DEC4", 60, ROF, "Pages stolen"),
    _s("priv_below_b", "SMF30RGB", "DEC4", 72, ROF, "Private area <16M (bytes)"),
    _s("priv_above_b", "SMF30ERG", "DEC4", 76, ROF, "Private area >16M (bytes)"),
    _s("lsqa_below_b", "SMF30ARB", "DEC4", 80, ROF, "LSQA/SWA <16M (bytes)"),
    _s("lsqa_above_b", "SMF30EAR", "DEC4", 84, ROF, "LSQA/SWA >16M (bytes)"),
    _s("user_below_b", "SMF30URB", "DEC4", 88, ROF, "User subpools <16M (bytes)"),
    _s("user_above_b", "SMF30EUR", "DEC4", 92, ROF, "User subpools >16M (bytes)"),
    _s("region_k", "SMF30RGN", "DEC4", 96, ROF, "Region size (K)"),
    _s("dataspace_mb", "SMF30DSV", "DEC4", 100, ROF, "Data space / hiperspace HWM (MB)"),
    _s("unblk_exp_in", "SMF30PIE", "DEC4", 104, ROF, "Unblocked pages in from expanded"),
    _s("unblk_exp_out", "SMF30POE", "DEC4", 108, ROF, "Unblocked pages out to expanded"),
    _s("blk_aux_in", "SMF30BIA", "DEC4", 112, ROF, "Blocked pages in from aux"),
    _s("blk_aux_out", "SMF30BOA", "DEC4", 116, ROF, "Blocked pages out to aux"),
    _s("blk_exp_in", "SMF30BIE", "DEC4", 120, ROF, "Blocked pages in from expanded"),
    _s("blk_exp_out", "SMF30BOE", "DEC4", 124, ROF, "Blocked pages out to expanded"),
    _s("blocks_aux_in", "SMF30KIA", "DEC4", 128, ROF, "Blocks in from aux"),
    _s("blocks_aux_out", "SMF30KOA", "DEC4", 132, ROF, "Blocks out to aux"),
    _s("blocks_exp_in", "SMF30KIE", "DEC4", 136, ROF, "Blocks in from expanded"),
    _s("blocks_exp_out", "SMF30KOE", "DEC4", 140, ROF, "Blocks out to expanded"),
    _s("shared_pg_aux", "SMF30PAI", "DEC4", 152, ROF, "Shared pages in from aux"),
    _s("shared_pg_exp", "SMF30PEI", "DEC4", 156, ROF, "Shared pages in from expanded"),
    _s("memlimit_src", "SMF30MLS", "DEC1", 176, ROF, "MEMLIMIT source"),
]

PERFORMANCE = [
    _s("total_service", "SMF30SRV", "DEC4", 0, POF, "Total service units"),
    _s("cpu_service", "SMF30CSU", "DEC4", 4, POF, "CPU service units"),
    _s("srb_service", "SMF30SRB", "DEC4", 8, POF, "SRB service units"),
    _s("io_service", "SMF30IO", "DEC4", 12, POF, "I/O service units"),
    _s("mso_service", "SMF30MSO", "DEC4", 16, POF, "MSO service units"),
    _s("trans_act_t", "SMF30TAT", "DEC4", 20, POF, "Transaction active time"),
    _s("cpu_adj_factor", "SMF30SUS", "DEC4", 24, POF, "CPU service adjustment factor"),
    _s("trans_res_t", "SMF30RES", "DEC4", 28, POF, "Transaction residency time"),
    _s("trans_count", "SMF30TRS", "DEC4", 32, POF, "Transaction count"),
    _s("workload_name", "SMF30WLM", "CHR8", 36, POF, "WLM workload name"),
    _s("service_class", "SMF30SCN", "CHR8", 44, POF, "Service class name"),
    _s("resource_group", "SMF30GRN", "CHR8", 52, POF, "Resource group name"),
    _s("report_class", "SMF30RCN", "CHR8", 60, POF, "Report class name"),
    _s("ind_enc_act_t", "SMF30ETA", "DEC4", 68, POF, "Indep. enclave active time"),
    _s("ind_enc_cpu_su", "SMF30ESU", "DEC4", 72, POF, "Indep. enclave CPU service"),
    _s("ind_enc_trans", "SMF30ETC", "DEC4", 76, POF, "Indep. enclave transaction count"),
    _s("sched_env_name", "SMF30PFL", "CHR16", 80, POF, "Scheduling environment name"),
    _s("job_prep_t", "SMF30JQT", "DEC4", 96, POF, "Job preparation time"),
    _s("inq_elig_t", "SMF30RQT", "DEC4", 100, POF, "Ineligible queue time"),
    _s("hold_queue_t", "SMF30HQT", "DEC4", 104, POF, "Hold queue time"),
    _s("eligible_t", "SMF30SQT", "DEC4", 108, POF, "Eligible wait time"),
    _s("perf_flag1", "SMF30PF1", "DEC1", 112, POF, "Performance flag byte 1"),
    _s("perf_flag2", "SMF30PF2", "DEC1", 113, POF, "Performance flag byte 2"),
    _s("subsys_coll", "SMF30JPN", "CHR8", 116, POF, "Subsystem collection name"),
]

OPERATOR = [
    _s("nonspec_dasd", "SMF30PDM", "DEC4", 0, OOF, "Non-specific DASD mounts"),
    _s("spec_dasd_mnt", "SMF30PRD", "DEC4", 4, OOF, "Specific DASD mounts"),
    _s("nonspec_tape", "SMF30PTM", "DEC4", 8, OOF, "Non-specific tape mounts"),
    _s("spec_tape_mnt", "SMF30TPR", "DEC4", 12, OOF, "Specific tape mounts"),
]

COMMON = HEADER + SUBSYSTEM + IDENTIFICATION

# Resource sections typically present (absent triplets decode as empty fields).
_INTERVAL = IO_ACTIVITY + PROCESSOR + STORAGE + PERFORMANCE
_STEP_OR_JOB = IO_ACTIVITY + COMPLETION + PROCESSOR + STORAGE + PERFORMANCE + OPERATOR
_SYSTEM_AS = IO_ACTIVITY + PROCESSOR + STORAGE + PERFORMANCE

SUBTYPE_TITLES = {
    1: "Job initiation",
    2: "Interval",
    3: "Step or interval termination",
    4: "Step total",
    5: "Job termination",
    6: "System address space",
}

SECTION_FIELDS: dict[int, list[F]] = {
    1: [],  # initiation: header + subsystem + identification only
    2: list(_INTERVAL),
    3: list(_INTERVAL),
    4: list(_STEP_OR_JOB),
    5: list(_STEP_OR_JOB),
    6: list(_SYSTEM_AS),
}

FIELDS_BY_SUBTYPE: dict[int, list[F]] = {
    sty: COMMON + list(sections) for sty, sections in SECTION_FIELDS.items()
}

# Back-compat alias (subtype 4 step total — historical flat map shape).
FIELDS = FIELDS_BY_SUBTYPE[4]

__all__ = [
    "COMMON",
    "COMPLETION",
    "FIELDS",
    "FIELDS_BY_SUBTYPE",
    "HEADER",
    "IDENTIFICATION",
    "IO_ACTIVITY",
    "OPERATOR",
    "PERFORMANCE",
    "PROCESSOR",
    "SECTION_FIELDS",
    "STORAGE",
    "SUBSYSTEM",
    "SUBTYPE_TITLES",
]
