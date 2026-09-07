-- Auto-generated SMF ClickHouse schema for smf2json maps.
-- Regenerate: python infra/scripts/gen_init_sql.py
-- All mapped columns are String (smf2json CSV values are always strings).
-- Retention: 10 days via TTL on event_date.

CREATE DATABASE IF NOT EXISTS smf;


-- Tables: 81

-- smf_14 (44 columns)
CREATE TABLE IF NOT EXISTS smf.smf_14
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `record_indicators` String,
    `dcb_deb_size` String,
    `ucb_section_count` String,
    `ucb_section_size` String,
    `isam_ext_size` String,
    `open_time` String,
    `dd_entry_length` String,
    `tiot_status` String,
    `devices_requested` String,
    `ddname` LowCardinality(String),
    `dsname` String,
    `member_name` String,
    `jfcb_tsdm` String,
    `label_type` String,
    `file_seq` String,
    `vol_seq` String,
    `creation_date_jfcb` String,
    `expiration_date_jfcb` String,
    `jfcb_ind1` String,
    `jfcb_ind2` String,
    `dsorg_jfcb` String,
    `recfm_jfcb` String,
    `blksize` String,
    `lrecl` String,
    `volser_count` String,
    `volser_1` String,
    `dsorg_dcb` String,
    `recfm_dcb` String,
    `open_date` String,
    `device_number` String,
    `ucb_volser` String,
    `unit_type` String,
    `extent_count` String,
    `excp_count` String,
    `tracks_allocated` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_15 (34 columns)
CREATE TABLE IF NOT EXISTS smf.smf_15
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `record_ds_ind` String,
    `dcb_deb_size` String,
    `ucb_section_count` String,
    `ucb_section_size` String,
    `isam_ext_size` String,
    `open_time` String,
    `ddname` LowCardinality(String),
    `dsname` String,
    `member_name` String,
    `jfcb_ind2` String,
    `dsorg` String,
    `recfm` String,
    `blksize` String,
    `lrecl` String,
    `vol_count_jfcb` String,
    `volser_1` String,
    `dcb_dsorg` String,
    `dcb_recfm` String,
    `open_date` String,
    `device_number` String,
    `ucb_volser` String,
    `unit_type` String,
    `extent_count` String,
    `excp_count` String,
    `tracks_allocated` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_17 (12 columns)
CREATE TABLE IF NOT EXISTS smf.smf_17
(
    `smf_record_type` LowCardinality(String),
    `smf_system_id` LowCardinality(String),
    `time` String,
    `date` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `record_indicator` String,
    `dsname` String,
    `volume_count` String,
    `volume_serial` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_61 (22 columns)
CREATE TABLE IF NOT EXISTS smf.smf_61
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `catalog_action` String,
    `product_offset` String,
    `product_length` String,
    `product_number` String,
    `data_offset` String,
    `data_length` String,
    `data_number` String,
    `record_version` String,
    `product_name` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `function_indicator` String,
    `catalog_name` String,
    `entry_type` String,
    `entry_name` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_65 (22 columns)
CREATE TABLE IF NOT EXISTS smf.smf_65
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `catalog_action` String,
    `product_offset` String,
    `product_length` String,
    `product_number` String,
    `data_offset` String,
    `data_length` String,
    `data_number` String,
    `record_version` String,
    `product_name` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `function_indicator` String,
    `catalog_name` String,
    `entry_type` String,
    `entry_name` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_66 (23 columns)
CREATE TABLE IF NOT EXISTS smf.smf_66
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `catalog_action` String,
    `product_offset` String,
    `product_length` String,
    `product_number` String,
    `data_offset` String,
    `data_length` String,
    `data_number` String,
    `record_version` String,
    `product_name` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `function_indicator` String,
    `catalog_name` String,
    `entry_type` String,
    `entry_name` String,
    `new_entry_name` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_80 (42 columns)
CREATE TABLE IF NOT EXISTS smf.smf_80
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `descriptor_flags` String,
    `event_code` String,
    `event_qualifier` String,
    `user_id` LowCardinality(String),
    `group_name` String,
    `relocate_offset` String,
    `relocate_count` String,
    `authorities_used` String,
    `logging_reason` String,
    `terminal_level` String,
    `command_error` String,
    `terminal_id` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_identification` String,
    `version_indicator` String,
    `logging_reason_2` String,
    `racf_fmid` String,
    `security_label` String,
    `ext_relocate_offset` String,
    `ext_relocate_count` String,
    `authorities_used_2` String,
    `old_resource` String,
    `new_dataset_name` String,
    `access_requested` String,
    `access_allowed` String,
    `command_data` String,
    `user_name` String,
    `command_resource` String,
    `from_resource` String,
    `volser` String,
    `old_volser` String,
    `class_name` String,
    `application_name` String,
    `mfa_factor_name` String,
    `mfa_policy_name` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_89 (4 columns)
CREATE TABLE IF NOT EXISTS smf.smf_89
(
    `smf_record_type` LowCardinality(String),
    `smf_system_id` LowCardinality(String),
    `time` String,
    `date` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_30_1 (38 columns)
CREATE TABLE IF NOT EXISTS smf.smf_30_1
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `work_type` String,
    `smf_subtype` LowCardinality(String),
    `rec_version` String,
    `product_name` String,
    `os_level` String,
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `job_name` LowCardinality(String),
    `program_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `user_id_field` String,
    `jes_job_id` String,
    `step_number` String,
    `job_class` String,
    `perf_group` String,
    `jes_priority` String,
    `alloc_start_t` String,
    `prog_start_t` String,
    `step_init_t` String,
    `step_init_d` String,
    `reader_start_t` String,
    `reader_start_d` String,
    `reader_end_t` String,
    `reader_end_d` String,
    `programmer_name` String,
    `racf_group` String,
    `racf_user` LowCardinality(String),
    `racf_term_id` String,
    `term_sym_name` String,
    `proc_step_name` String,
    `job_class_8` String,
    `substep_num` String,
    `omvs_pgm_name` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_30_2 (140 columns)
CREATE TABLE IF NOT EXISTS smf.smf_30_2
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `work_type` String,
    `smf_subtype` LowCardinality(String),
    `rec_version` String,
    `product_name` String,
    `os_level` String,
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `job_name` LowCardinality(String),
    `program_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `user_id_field` String,
    `jes_job_id` String,
    `step_number` String,
    `job_class` String,
    `perf_group` String,
    `jes_priority` String,
    `alloc_start_t` String,
    `prog_start_t` String,
    `step_init_t` String,
    `step_init_d` String,
    `reader_start_t` String,
    `reader_start_d` String,
    `reader_end_t` String,
    `reader_end_d` String,
    `programmer_name` String,
    `racf_group` String,
    `racf_user` LowCardinality(String),
    `racf_term_id` String,
    `term_sym_name` String,
    `proc_step_name` String,
    `job_class_8` String,
    `substep_num` String,
    `omvs_pgm_name` String,
    `card_images` String,
    `total_blocks` String,
    `tput_count` String,
    `tget_count` String,
    `reader_dev_cls` String,
    `reader_dev_typ` String,
    `tot_dev_conn` String,
    `io_flag_word` String,
    `reread_count` String,
    `dasd_conn_t` String,
    `dasd_disc_t` String,
    `dasd_pend_t` String,
    `dasd_ssch_ct` String,
    `ie_conn_t` String,
    `ie_disc_t` String,
    `ie_pend_t` String,
    `ie_ssch_ct` String,
    `timer_flags` String,
    `cpu_step_time` String,
    `srb_time` String,
    `init_tcb_time` String,
    `init_srb_time` String,
    `step_vect_cpu` String,
    `init_vect_cpu` String,
    `step_vect_aff` String,
    `init_vect_aff` String,
    `interval_start` String,
    `interval_date` String,
    `io_int_cpu` String,
    `rct_cpu_time` String,
    `hiperspace_cpu` String,
    `icsf_svc_count` String,
    `admf_write_pgs` String,
    `admf_read_pgs` String,
    `preempt_srb_t` String,
    `ind_enclave_t` String,
    `dep_enclave_t` String,
    `enqueue_cpu_t` String,
    `timer_flags2` String,
    `storage_flags` String,
    `storage_key` String,
    `priv_below_k` String,
    `sys_above_k` String,
    `pages_in` String,
    `pages_out` String,
    `eso_misses` String,
    `swap_seqs` String,
    `pages_swap_in` String,
    `pages_swap_out` String,
    `vio_pages_in` String,
    `vio_pages_out` String,
    `vio_reclaims` String,
    `common_pg_in` String,
    `hsp_pages_in` String,
    `lpa_pages_in` String,
    `hsp_pages_out` String,
    `pages_stolen` String,
    `priv_below_b` String,
    `priv_above_b` String,
    `lsqa_below_b` String,
    `lsqa_above_b` String,
    `user_below_b` String,
    `user_above_b` String,
    `region_k` String,
    `dataspace_mb` String,
    `unblk_exp_in` String,
    `unblk_exp_out` String,
    `blk_aux_in` String,
    `blk_aux_out` String,
    `blk_exp_in` String,
    `blk_exp_out` String,
    `blocks_aux_in` String,
    `blocks_aux_out` String,
    `blocks_exp_in` String,
    `blocks_exp_out` String,
    `shared_pg_aux` String,
    `shared_pg_exp` String,
    `memlimit_src` String,
    `total_service` String,
    `cpu_service` String,
    `srb_service` String,
    `io_service` String,
    `mso_service` String,
    `trans_act_t` String,
    `cpu_adj_factor` String,
    `trans_res_t` String,
    `trans_count` String,
    `workload_name` String,
    `service_class` String,
    `resource_group` String,
    `report_class` String,
    `ind_enc_act_t` String,
    `ind_enc_cpu_su` String,
    `ind_enc_trans` String,
    `sched_env_name` String,
    `job_prep_t` String,
    `inq_elig_t` String,
    `hold_queue_t` String,
    `eligible_t` String,
    `perf_flag1` String,
    `perf_flag2` String,
    `subsys_coll` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_30_3 (140 columns)
CREATE TABLE IF NOT EXISTS smf.smf_30_3
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `work_type` String,
    `smf_subtype` LowCardinality(String),
    `rec_version` String,
    `product_name` String,
    `os_level` String,
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `job_name` LowCardinality(String),
    `program_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `user_id_field` String,
    `jes_job_id` String,
    `step_number` String,
    `job_class` String,
    `perf_group` String,
    `jes_priority` String,
    `alloc_start_t` String,
    `prog_start_t` String,
    `step_init_t` String,
    `step_init_d` String,
    `reader_start_t` String,
    `reader_start_d` String,
    `reader_end_t` String,
    `reader_end_d` String,
    `programmer_name` String,
    `racf_group` String,
    `racf_user` LowCardinality(String),
    `racf_term_id` String,
    `term_sym_name` String,
    `proc_step_name` String,
    `job_class_8` String,
    `substep_num` String,
    `omvs_pgm_name` String,
    `card_images` String,
    `total_blocks` String,
    `tput_count` String,
    `tget_count` String,
    `reader_dev_cls` String,
    `reader_dev_typ` String,
    `tot_dev_conn` String,
    `io_flag_word` String,
    `reread_count` String,
    `dasd_conn_t` String,
    `dasd_disc_t` String,
    `dasd_pend_t` String,
    `dasd_ssch_ct` String,
    `ie_conn_t` String,
    `ie_disc_t` String,
    `ie_pend_t` String,
    `ie_ssch_ct` String,
    `timer_flags` String,
    `cpu_step_time` String,
    `srb_time` String,
    `init_tcb_time` String,
    `init_srb_time` String,
    `step_vect_cpu` String,
    `init_vect_cpu` String,
    `step_vect_aff` String,
    `init_vect_aff` String,
    `interval_start` String,
    `interval_date` String,
    `io_int_cpu` String,
    `rct_cpu_time` String,
    `hiperspace_cpu` String,
    `icsf_svc_count` String,
    `admf_write_pgs` String,
    `admf_read_pgs` String,
    `preempt_srb_t` String,
    `ind_enclave_t` String,
    `dep_enclave_t` String,
    `enqueue_cpu_t` String,
    `timer_flags2` String,
    `storage_flags` String,
    `storage_key` String,
    `priv_below_k` String,
    `sys_above_k` String,
    `pages_in` String,
    `pages_out` String,
    `eso_misses` String,
    `swap_seqs` String,
    `pages_swap_in` String,
    `pages_swap_out` String,
    `vio_pages_in` String,
    `vio_pages_out` String,
    `vio_reclaims` String,
    `common_pg_in` String,
    `hsp_pages_in` String,
    `lpa_pages_in` String,
    `hsp_pages_out` String,
    `pages_stolen` String,
    `priv_below_b` String,
    `priv_above_b` String,
    `lsqa_below_b` String,
    `lsqa_above_b` String,
    `user_below_b` String,
    `user_above_b` String,
    `region_k` String,
    `dataspace_mb` String,
    `unblk_exp_in` String,
    `unblk_exp_out` String,
    `blk_aux_in` String,
    `blk_aux_out` String,
    `blk_exp_in` String,
    `blk_exp_out` String,
    `blocks_aux_in` String,
    `blocks_aux_out` String,
    `blocks_exp_in` String,
    `blocks_exp_out` String,
    `shared_pg_aux` String,
    `shared_pg_exp` String,
    `memlimit_src` String,
    `total_service` String,
    `cpu_service` String,
    `srb_service` String,
    `io_service` String,
    `mso_service` String,
    `trans_act_t` String,
    `cpu_adj_factor` String,
    `trans_res_t` String,
    `trans_count` String,
    `workload_name` String,
    `service_class` String,
    `resource_group` String,
    `report_class` String,
    `ind_enc_act_t` String,
    `ind_enc_cpu_su` String,
    `ind_enc_trans` String,
    `sched_env_name` String,
    `job_prep_t` String,
    `inq_elig_t` String,
    `hold_queue_t` String,
    `eligible_t` String,
    `perf_flag1` String,
    `perf_flag2` String,
    `subsys_coll` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_30_4 (147 columns)
CREATE TABLE IF NOT EXISTS smf.smf_30_4
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `work_type` String,
    `smf_subtype` LowCardinality(String),
    `rec_version` String,
    `product_name` String,
    `os_level` String,
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `job_name` LowCardinality(String),
    `program_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `user_id_field` String,
    `jes_job_id` String,
    `step_number` String,
    `job_class` String,
    `perf_group` String,
    `jes_priority` String,
    `alloc_start_t` String,
    `prog_start_t` String,
    `step_init_t` String,
    `step_init_d` String,
    `reader_start_t` String,
    `reader_start_d` String,
    `reader_end_t` String,
    `reader_end_d` String,
    `programmer_name` String,
    `racf_group` String,
    `racf_user` LowCardinality(String),
    `racf_term_id` String,
    `term_sym_name` String,
    `proc_step_name` String,
    `job_class_8` String,
    `substep_num` String,
    `omvs_pgm_name` String,
    `card_images` String,
    `total_blocks` String,
    `tput_count` String,
    `tget_count` String,
    `reader_dev_cls` String,
    `reader_dev_typ` String,
    `tot_dev_conn` String,
    `io_flag_word` String,
    `reread_count` String,
    `dasd_conn_t` String,
    `dasd_disc_t` String,
    `dasd_pend_t` String,
    `dasd_ssch_ct` String,
    `ie_conn_t` String,
    `ie_disc_t` String,
    `ie_pend_t` String,
    `ie_ssch_ct` String,
    `step_comp_code` String,
    `term_indicator` String,
    `abend_reason` String,
    `timer_flags` String,
    `cpu_step_time` String,
    `srb_time` String,
    `init_tcb_time` String,
    `init_srb_time` String,
    `step_vect_cpu` String,
    `init_vect_cpu` String,
    `step_vect_aff` String,
    `init_vect_aff` String,
    `interval_start` String,
    `interval_date` String,
    `io_int_cpu` String,
    `rct_cpu_time` String,
    `hiperspace_cpu` String,
    `icsf_svc_count` String,
    `admf_write_pgs` String,
    `admf_read_pgs` String,
    `preempt_srb_t` String,
    `ind_enclave_t` String,
    `dep_enclave_t` String,
    `enqueue_cpu_t` String,
    `timer_flags2` String,
    `storage_flags` String,
    `storage_key` String,
    `priv_below_k` String,
    `sys_above_k` String,
    `pages_in` String,
    `pages_out` String,
    `eso_misses` String,
    `swap_seqs` String,
    `pages_swap_in` String,
    `pages_swap_out` String,
    `vio_pages_in` String,
    `vio_pages_out` String,
    `vio_reclaims` String,
    `common_pg_in` String,
    `hsp_pages_in` String,
    `lpa_pages_in` String,
    `hsp_pages_out` String,
    `pages_stolen` String,
    `priv_below_b` String,
    `priv_above_b` String,
    `lsqa_below_b` String,
    `lsqa_above_b` String,
    `user_below_b` String,
    `user_above_b` String,
    `region_k` String,
    `dataspace_mb` String,
    `unblk_exp_in` String,
    `unblk_exp_out` String,
    `blk_aux_in` String,
    `blk_aux_out` String,
    `blk_exp_in` String,
    `blk_exp_out` String,
    `blocks_aux_in` String,
    `blocks_aux_out` String,
    `blocks_exp_in` String,
    `blocks_exp_out` String,
    `shared_pg_aux` String,
    `shared_pg_exp` String,
    `memlimit_src` String,
    `total_service` String,
    `cpu_service` String,
    `srb_service` String,
    `io_service` String,
    `mso_service` String,
    `trans_act_t` String,
    `cpu_adj_factor` String,
    `trans_res_t` String,
    `trans_count` String,
    `workload_name` String,
    `service_class` String,
    `resource_group` String,
    `report_class` String,
    `ind_enc_act_t` String,
    `ind_enc_cpu_su` String,
    `ind_enc_trans` String,
    `sched_env_name` String,
    `job_prep_t` String,
    `inq_elig_t` String,
    `hold_queue_t` String,
    `eligible_t` String,
    `perf_flag1` String,
    `perf_flag2` String,
    `subsys_coll` String,
    `nonspec_dasd` String,
    `spec_dasd_mnt` String,
    `nonspec_tape` String,
    `spec_tape_mnt` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_30_5 (147 columns)
CREATE TABLE IF NOT EXISTS smf.smf_30_5
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `work_type` String,
    `smf_subtype` LowCardinality(String),
    `rec_version` String,
    `product_name` String,
    `os_level` String,
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `job_name` LowCardinality(String),
    `program_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `user_id_field` String,
    `jes_job_id` String,
    `step_number` String,
    `job_class` String,
    `perf_group` String,
    `jes_priority` String,
    `alloc_start_t` String,
    `prog_start_t` String,
    `step_init_t` String,
    `step_init_d` String,
    `reader_start_t` String,
    `reader_start_d` String,
    `reader_end_t` String,
    `reader_end_d` String,
    `programmer_name` String,
    `racf_group` String,
    `racf_user` LowCardinality(String),
    `racf_term_id` String,
    `term_sym_name` String,
    `proc_step_name` String,
    `job_class_8` String,
    `substep_num` String,
    `omvs_pgm_name` String,
    `card_images` String,
    `total_blocks` String,
    `tput_count` String,
    `tget_count` String,
    `reader_dev_cls` String,
    `reader_dev_typ` String,
    `tot_dev_conn` String,
    `io_flag_word` String,
    `reread_count` String,
    `dasd_conn_t` String,
    `dasd_disc_t` String,
    `dasd_pend_t` String,
    `dasd_ssch_ct` String,
    `ie_conn_t` String,
    `ie_disc_t` String,
    `ie_pend_t` String,
    `ie_ssch_ct` String,
    `step_comp_code` String,
    `term_indicator` String,
    `abend_reason` String,
    `timer_flags` String,
    `cpu_step_time` String,
    `srb_time` String,
    `init_tcb_time` String,
    `init_srb_time` String,
    `step_vect_cpu` String,
    `init_vect_cpu` String,
    `step_vect_aff` String,
    `init_vect_aff` String,
    `interval_start` String,
    `interval_date` String,
    `io_int_cpu` String,
    `rct_cpu_time` String,
    `hiperspace_cpu` String,
    `icsf_svc_count` String,
    `admf_write_pgs` String,
    `admf_read_pgs` String,
    `preempt_srb_t` String,
    `ind_enclave_t` String,
    `dep_enclave_t` String,
    `enqueue_cpu_t` String,
    `timer_flags2` String,
    `storage_flags` String,
    `storage_key` String,
    `priv_below_k` String,
    `sys_above_k` String,
    `pages_in` String,
    `pages_out` String,
    `eso_misses` String,
    `swap_seqs` String,
    `pages_swap_in` String,
    `pages_swap_out` String,
    `vio_pages_in` String,
    `vio_pages_out` String,
    `vio_reclaims` String,
    `common_pg_in` String,
    `hsp_pages_in` String,
    `lpa_pages_in` String,
    `hsp_pages_out` String,
    `pages_stolen` String,
    `priv_below_b` String,
    `priv_above_b` String,
    `lsqa_below_b` String,
    `lsqa_above_b` String,
    `user_below_b` String,
    `user_above_b` String,
    `region_k` String,
    `dataspace_mb` String,
    `unblk_exp_in` String,
    `unblk_exp_out` String,
    `blk_aux_in` String,
    `blk_aux_out` String,
    `blk_exp_in` String,
    `blk_exp_out` String,
    `blocks_aux_in` String,
    `blocks_aux_out` String,
    `blocks_exp_in` String,
    `blocks_exp_out` String,
    `shared_pg_aux` String,
    `shared_pg_exp` String,
    `memlimit_src` String,
    `total_service` String,
    `cpu_service` String,
    `srb_service` String,
    `io_service` String,
    `mso_service` String,
    `trans_act_t` String,
    `cpu_adj_factor` String,
    `trans_res_t` String,
    `trans_count` String,
    `workload_name` String,
    `service_class` String,
    `resource_group` String,
    `report_class` String,
    `ind_enc_act_t` String,
    `ind_enc_cpu_su` String,
    `ind_enc_trans` String,
    `sched_env_name` String,
    `job_prep_t` String,
    `inq_elig_t` String,
    `hold_queue_t` String,
    `eligible_t` String,
    `perf_flag1` String,
    `perf_flag2` String,
    `subsys_coll` String,
    `nonspec_dasd` String,
    `spec_dasd_mnt` String,
    `nonspec_tape` String,
    `spec_tape_mnt` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_30_6 (140 columns)
CREATE TABLE IF NOT EXISTS smf.smf_30_6
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `work_type` String,
    `smf_subtype` LowCardinality(String),
    `rec_version` String,
    `product_name` String,
    `os_level` String,
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `job_name` LowCardinality(String),
    `program_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `user_id_field` String,
    `jes_job_id` String,
    `step_number` String,
    `job_class` String,
    `perf_group` String,
    `jes_priority` String,
    `alloc_start_t` String,
    `prog_start_t` String,
    `step_init_t` String,
    `step_init_d` String,
    `reader_start_t` String,
    `reader_start_d` String,
    `reader_end_t` String,
    `reader_end_d` String,
    `programmer_name` String,
    `racf_group` String,
    `racf_user` LowCardinality(String),
    `racf_term_id` String,
    `term_sym_name` String,
    `proc_step_name` String,
    `job_class_8` String,
    `substep_num` String,
    `omvs_pgm_name` String,
    `card_images` String,
    `total_blocks` String,
    `tput_count` String,
    `tget_count` String,
    `reader_dev_cls` String,
    `reader_dev_typ` String,
    `tot_dev_conn` String,
    `io_flag_word` String,
    `reread_count` String,
    `dasd_conn_t` String,
    `dasd_disc_t` String,
    `dasd_pend_t` String,
    `dasd_ssch_ct` String,
    `ie_conn_t` String,
    `ie_disc_t` String,
    `ie_pend_t` String,
    `ie_ssch_ct` String,
    `timer_flags` String,
    `cpu_step_time` String,
    `srb_time` String,
    `init_tcb_time` String,
    `init_srb_time` String,
    `step_vect_cpu` String,
    `init_vect_cpu` String,
    `step_vect_aff` String,
    `init_vect_aff` String,
    `interval_start` String,
    `interval_date` String,
    `io_int_cpu` String,
    `rct_cpu_time` String,
    `hiperspace_cpu` String,
    `icsf_svc_count` String,
    `admf_write_pgs` String,
    `admf_read_pgs` String,
    `preempt_srb_t` String,
    `ind_enclave_t` String,
    `dep_enclave_t` String,
    `enqueue_cpu_t` String,
    `timer_flags2` String,
    `storage_flags` String,
    `storage_key` String,
    `priv_below_k` String,
    `sys_above_k` String,
    `pages_in` String,
    `pages_out` String,
    `eso_misses` String,
    `swap_seqs` String,
    `pages_swap_in` String,
    `pages_swap_out` String,
    `vio_pages_in` String,
    `vio_pages_out` String,
    `vio_reclaims` String,
    `common_pg_in` String,
    `hsp_pages_in` String,
    `lpa_pages_in` String,
    `hsp_pages_out` String,
    `pages_stolen` String,
    `priv_below_b` String,
    `priv_above_b` String,
    `lsqa_below_b` String,
    `lsqa_above_b` String,
    `user_below_b` String,
    `user_above_b` String,
    `region_k` String,
    `dataspace_mb` String,
    `unblk_exp_in` String,
    `unblk_exp_out` String,
    `blk_aux_in` String,
    `blk_aux_out` String,
    `blk_exp_in` String,
    `blk_exp_out` String,
    `blocks_aux_in` String,
    `blocks_aux_out` String,
    `blocks_exp_in` String,
    `blocks_exp_out` String,
    `shared_pg_aux` String,
    `shared_pg_exp` String,
    `memlimit_src` String,
    `total_service` String,
    `cpu_service` String,
    `srb_service` String,
    `io_service` String,
    `mso_service` String,
    `trans_act_t` String,
    `cpu_adj_factor` String,
    `trans_res_t` String,
    `trans_count` String,
    `workload_name` String,
    `service_class` String,
    `resource_group` String,
    `report_class` String,
    `ind_enc_act_t` String,
    `ind_enc_cpu_su` String,
    `ind_enc_trans` String,
    `sched_env_name` String,
    `job_prep_t` String,
    `inq_elig_t` String,
    `hold_queue_t` String,
    `eligible_t` String,
    `perf_flag1` String,
    `perf_flag2` String,
    `subsys_coll` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_42_20 (16 columns)
CREATE TABLE IF NOT EXISTS smf.smf_42_20
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `product_level` String,
    `product_name` String,
    `subtype_version` String,
    `job_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `proc_name` String,
    `dsname` String,
    `volser` String,
    `user_token` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_42_21 (20 columns)
CREATE TABLE IF NOT EXISTS smf.smf_42_21
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `product_level` String,
    `product_name` String,
    `subtype_version` String,
    `job_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `proc_name` String,
    `dsname` String,
    `volser` String,
    `member_name_len` String,
    `member_flags` String,
    `member_name` String,
    `alias_count` String,
    `user_token` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_42_22 (17 columns)
CREATE TABLE IF NOT EXISTS smf.smf_42_22
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `product_level` String,
    `product_name` String,
    `subtype_version` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `racf_user` LowCardinality(String),
    `activity_type` String,
    `audit_flags` String,
    `journal_record_number` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_42_23 (24 columns)
CREATE TABLE IF NOT EXISTS smf.smf_42_23
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `product_level` String,
    `product_name` String,
    `subtype_version` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `user_id_field` String,
    `racf_user` LowCardinality(String),
    `racf_group` String,
    `record_version` String,
    `activity_type` String,
    `security_type` String,
    `dsname` String,
    `volser` String,
    `device_type` String,
    `dataset_seq` String,
    `volume_seq` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_42_24 (20 columns)
CREATE TABLE IF NOT EXISTS smf.smf_42_24
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `product_level` String,
    `product_name` String,
    `subtype_version` String,
    `job_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `proc_name` String,
    `dsname` String,
    `volser` String,
    `member_name_len` String,
    `member_flags` String,
    `member_name` String,
    `alias_count` String,
    `user_token` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_42_25 (20 columns)
CREATE TABLE IF NOT EXISTS smf.smf_42_25
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `product_level` String,
    `product_name` String,
    `subtype_version` String,
    `job_name` LowCardinality(String),
    `step_name` LowCardinality(String),
    `proc_name` String,
    `dsname` String,
    `volser` String,
    `member_name_len` String,
    `member_name` String,
    `old_member_name_len` String,
    `old_member_name` String,
    `user_token` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_1 (38 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_1
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `event_stck` String,
    `path_offset` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_device` String,
    `ddname` LowCardinality(String),
    `fs_type_name` String,
    `fs_name` String,
    `fs_blocksize` String,
    `fs_space_total` String,
    `fs_space_used` String,
    `mount_flags` String,
    `mount_flags_2` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_2 (33 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_2
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `event_stck` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_device` String,
    `ddname` LowCardinality(String),
    `fs_type_name` String,
    `fs_name` String,
    `quiesce_flags` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_4 (34 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_4
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `suspend_stck` String,
    `resume_stck` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_device` String,
    `ddname` LowCardinality(String),
    `fs_type_name` String,
    `fs_name` String,
    `resume_flags` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_5 (45 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_5
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `mount_stck` String,
    `unmount_stck` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_device` String,
    `ddname` LowCardinality(String),
    `fs_type_name` String,
    `fs_name` String,
    `fs_blocksize` String,
    `fs_space_total` String,
    `fs_space_used` String,
    `read_calls` String,
    `write_calls` String,
    `dir_io_blocks` String,
    `io_blocks_read` String,
    `io_blocks_written` String,
    `bytes_read` String,
    `bytes_written` String,
    `unmount_flags` String,
    `unmount_flags_2` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_6 (45 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_6
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `mount_stck` String,
    `unmount_stck` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_device` String,
    `ddname` LowCardinality(String),
    `fs_type_name` String,
    `fs_name` String,
    `fs_blocksize` String,
    `fs_space_total` String,
    `fs_space_used` String,
    `read_calls` String,
    `write_calls` String,
    `dir_io_blocks` String,
    `io_blocks_read` String,
    `io_blocks_written` String,
    `bytes_read` String,
    `bytes_written` String,
    `unmount_flags` String,
    `unmount_flags_2` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_7 (46 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_7
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `move_stck` String,
    `mount_stck` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_device` String,
    `ddname` LowCardinality(String),
    `fs_type_name` String,
    `fs_name` String,
    `fs_blocksize` String,
    `fs_space_total` String,
    `fs_space_used` String,
    `read_calls` String,
    `write_calls` String,
    `dir_io_blocks` String,
    `io_blocks_read` String,
    `io_blocks_written` String,
    `bytes_read` String,
    `bytes_written` String,
    `move_reason_flags` String,
    `old_status_flags` String,
    `new_status_flags` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_10 (31 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_10
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `open_stck` String,
    `file_type` String,
    `open_flags` String,
    `file_token` String,
    `file_inode` String,
    `fs_device` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_11 (40 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_11
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `open_stck` String,
    `close_stck` String,
    `file_type` String,
    `close_flags` String,
    `file_token` String,
    `file_inode` String,
    `fs_device` String,
    `read_calls` String,
    `write_calls` String,
    `dir_io_blocks` String,
    `io_blocks_read` String,
    `io_blocks_written` String,
    `bytes_read` String,
    `bytes_written` String,
    `pathname` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_12 (30 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_12
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `mmap_stck` String,
    `mmap_bytes` String,
    `file_token` String,
    `file_inode` String,
    `fs_device` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_13 (33 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_13
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `mmap_stck` String,
    `munmap_stck` String,
    `mmap_bytes` String,
    `file_token` String,
    `file_inode` String,
    `fs_device` String,
    `io_blocks_read` String,
    `io_blocks_written` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_14 (36 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_14
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `event_stck` String,
    `file_type` String,
    `delete_flags` String,
    `file_inode` String,
    `parent_inode` String,
    `fs_device` String,
    `fs_name` String,
    `file_name_len` String,
    `file_name` String,
    `new_name_len` String,
    `new_file_name` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_15 (42 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_15
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `change_stck` String,
    `file_type` String,
    `attr_flags` String,
    `file_inode` String,
    `fs_device` String,
    `fs_name` String,
    `old_gen_value` String,
    `old_sec_attrs` String,
    `new_gen_value` String,
    `new_sec_attrs` String,
    `owner_uid` String,
    `owner_gid` String,
    `security_label` String,
    `audit_file_id` String,
    `getcwd_rc` String,
    `getcwd_rsn` String,
    `path_name_len` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_16 (26 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_16
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `reserved` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_92_17 (31 columns)
CREATE TABLE IF NOT EXISTS smf.smf_92_17
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `subtype_id` String,
    `record_version` String,
    `product_name` String,
    `os_level` String,
    `job_name` LowCardinality(String),
    `reader_start_t` String,
    `reader_start_d` String,
    `step_name` LowCardinality(String),
    `saf_group` String,
    `saf_user` String,
    `omvs_uid` String,
    `omvs_gid` String,
    `omvs_pid` String,
    `omvs_pgid` String,
    `omvs_sid` String,
    `omvs_anchor_pid` String,
    `omvs_anchor_pgid` String,
    `omvs_anchor_sid` String,
    `interval_stck` String,
    `access_flags` String,
    `file_inode` String,
    `fs_device` String,
    `access_count` String,
    `pathname` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, job_name)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_1 (26 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_1
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `resource_name` String,
    `connection_id` String,
    `subtask_tcb` String,
    `remote_ip` String,
    `local_ip` String,
    `remote_port` String,
    `local_port` String,
    `conn_time` String,
    `conn_date` String,
    `conn_stck` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_2 (58 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_2
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `resource_name` String,
    `connection_id` String,
    `ttttlscs` String,
    `ttttlsps` String,
    `term_code` String,
    `subtask_tcb` String,
    `conn_time` String,
    `conn_date` String,
    `conn_end_time` String,
    `conn_end_date` String,
    `remote_ip` String,
    `local_ip` String,
    `remote_port` String,
    `local_port` String,
    `in_bytes` String,
    `out_bytes` String,
    `ttsws` String,
    `ttmsws` String,
    `ttcws` String,
    `ttsms` String,
    `ttrtt` String,
    `ttrva` String,
    `socket_status` String,
    `tttos` String,
    `ttxrt` String,
    `tt_prof` String,
    `tt_pol` String,
    `in_segments` String,
    `out_segments` String,
    `ttsstck_d` String,
    `ttestck_d` String,
    `tt_dup_acks_rcvd` String,
    `tt_tel_lu_name` String,
    `tt_tel_appl` String,
    `tt_tel_logmode` String,
    `tt_tel_status` String,
    `tt_tel_term_code` String,
    `ttttlssp` String,
    `ttttlsnc` String,
    `ttttlsst` String,
    `ttttlsuid` String,
    `ttappldata` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_3 (58 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_3
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ftp_cmd` String,
    `fcf_type` String,
    `fcdrip` String,
    `fcdlip` String,
    `fcdr_port` String,
    `fcdl_port` String,
    `fccrip` String,
    `fcclip` String,
    `fccr_port` String,
    `fccl_port` String,
    `remote_user` String,
    `local_user` String,
    `fc_type` String,
    `fc_mode` String,
    `fc_struct` String,
    `fcds_type` String,
    `fcs_time` String,
    `fcs_date` String,
    `fce_time` String,
    `fce_date` String,
    `fc_dur` String,
    `bytes_transferred` String,
    `fcl_reply` String,
    `fcm1` String,
    `fc_hostname` String,
    `fcrs` String,
    `fc_bytes_float` String,
    `fcc_conn_id` String,
    `fcd_conn_id` String,
    `file_name` String,
    `fccip` String,
    `fcc_port` String,
    `fcc_prot` String,
    `fc_mechanism` String,
    `fcc_protect` String,
    `fcd_protect` String,
    `fc_login_mech` String,
    `fc_proto_level` String,
    `fc_cipher_spec` String,
    `fc_prot_buff_size` String,
    `fc_cipher` String,
    `fc_user_id` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_4 (130 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_4
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `pico_eye` String,
    `pico_start_time` String,
    `pico_start_date` String,
    `pico_change_time` String,
    `pico_change_date` String,
    `change_rsn` String,
    `pico_flags` String,
    `pico_dep_stmts` String,
    `pico_dep_changed` String,
    `sections_changed` String,
    `console` String,
    `sysplex_grp` String,
    `pids_eye` String,
    `pids_flag` String,
    `profile_dsn` String,
    `alpr_eye` String,
    `autolog_proc` String,
    `autolog_job` String,
    `alpr_options` String,
    `alpr_parm_str` String,
    `alpr_wait_time` String,
    `v4_cf_eye` String,
    `v4_cf_flags` String,
    `v4_cf_arp_timeout` String,
    `v4_cf_dev_retry` String,
    `tcp_src_vipa` String,
    `dynxcf_v4` String,
    `v4_cf_dyn_xcf_cost_metric` String,
    `v4_cf_dyn_xcf_mask` String,
    `v4_cf_dyn_xcf_sec_class` String,
    `v4_cfqdio_priority` String,
    `v4_cf_ign_redirect_rsn` String,
    `v4_cf_reasm_timeout` String,
    `v4_cfttl` String,
    `primary_intf` String,
    `v4_cf_dyn_xcf_src_vipa_intf_name` String,
    `v6_cf_eye` String,
    `v6_cf_flags` String,
    `v6_cf_dyn_xcf_intf_id` String,
    `v6_cf_dyn_xcf_addr` String,
    `v6_cf_dyn_xcf_src_vipa_intf_name` String,
    `v6_cf_tcp_src_vipa_intf_name` String,
    `v6_cf_dyn_xcf_pfx_rte_len` String,
    `v6_cf_dyn_xcf_sec_class` String,
    `v6_cf_hop_limit` String,
    `v6_cf_icmp_err_limit` String,
    `v6_cf_ign_redirect_rsn` String,
    `v6_cfosm_sec_class` String,
    `v6_cf_temp_addrs_pref_life_time` String,
    `v6_cf_temp_addrs_valid_life_time` String,
    `tccf_eye` String,
    `tccf_flags` String,
    `tccf_fin_wait2_time` String,
    `tccf_interval` String,
    `somaxconn` String,
    `tccf_max_rcv_buf_size` String,
    `tcp_rcvbuf` String,
    `tcp_sndbuf` String,
    `tcp_ephem_beg` String,
    `tcp_ephem_end` String,
    `tccf_time_wait_interval` String,
    `tccf_retran_attempts` String,
    `tccf_connect_time_out` String,
    `tccf_connect_interval` String,
    `tccf_keep_alive_probes` String,
    `tccfka_probe_interval` String,
    `tccf_queued_rtt` String,
    `tccffrr_threshold` String,
    `tccf_max_snd_buf_size` String,
    `tccf_max_retransmit` String,
    `udcf_eye` String,
    `udcf_flags` String,
    `udp_rcvbuf` String,
    `udp_sndbuf` String,
    `udcf_ephem_port_beg_num` String,
    `udcf_ephem_port_end_num` String,
    `gbcf_eye` String,
    `gbl_flags` String,
    `gbcf_sys_mon_options` String,
    `gbcf_iqd_vlan_id` String,
    `gbcf_sys_wlm_poll` String,
    `gbcf_ziip_options` String,
    `gbcf_sys_mon_timer_secs` String,
    `gbcf_xcf_group_id` String,
    `gbcf_exp_bind_port_range_beg_num` String,
    `gbcf_exp_bind_port_range_end_num` String,
    `gbcf_max_recs` String,
    `gbcf_ecsa_limit` String,
    `gbcf_pool_limit` String,
    `gbcfwpqcv0_pri` String,
    `gbcfwpqcv1_pri` String,
    `gbcfwpqcv2_pri` String,
    `gbcfwpqcv3_pri` String,
    `gbcfwpqcv4_pri` String,
    `gbcfwpqcv5_pri` String,
    `gbcfwpqcv6_pri` String,
    `gbcfwpq_fwd_pri` String,
    `gbcfautoiqdx` String,
    `gbcfp_fid_cnt` String,
    `gbcfsmcg_flags` String,
    `gbcf_adj_dvmss` String,
    `gbcf_fixed_memory` String,
    `gbcf_tcp_keep_min_int` String,
    `gbcf_zert_parms` String,
    `gbcfautoiqdc` String,
    `gbcf_policy_req` String,
    `gbcf_iked_req` String,
    `gbcf_fixed_memory_d` String,
    `gbcf_tcp_keep_min_int_d` String,
    `gbc_fz_ag_gtim_intval` String,
    `gbc_fz_ag_gtim_syncval_hh` String,
    `gbc_fz_ag_gtim_syncval_mm` String,
    `gbcfsmceid_count` String,
    `gbcfsystemeidstr` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_5 (166 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_5
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tsip_duration` String,
    `tsip_rec_data` String,
    `tsip_att_fwd_data` String,
    `tsip_dlv_data` String,
    `tsipx_data` String,
    `tsipx_dsc_oth` String,
    `tsipx_dsc_route` String,
    `tsip_timeouts` String,
    `tsip_rec_d_rsbm` String,
    `tsip_rsmb` String,
    `tsip_fail_rsmb` String,
    `tsip_rec_fgmt` String,
    `tsip_dsc_d_fgmt` String,
    `tsipx_fgmt` String,
    `tsip_route_disc` String,
    `tsip_max_rsmb` String,
    `tsip_cur_rsmb` String,
    `tsip_rsmb_flags` String,
    `tsip_in_calls` String,
    `tsip_in_uerrs` String,
    `tsipid_mem` String,
    `tsipod_sync` String,
    `tsipod_asyn` String,
    `tsipod_mem` String,
    `tstc_duration` String,
    `tstc_alg` String,
    `tstc_min_ret` String,
    `tstc_mx_ret` String,
    `tstc_mx_con` String,
    `tstc_open_conn` String,
    `tstc_pass_conn` String,
    `tstco_fails` String,
    `tstc_con_reset` String,
    `tstc_estab` String,
    `tstc_in_segs` String,
    `tstco_segs` String,
    `tstc_rx_segs` String,
    `tstc_in_errs` String,
    `tstc_reset` String,
    `tstc_con_cls` String,
    `tstc_con_att_d` String,
    `tstctw_ref` String,
    `tstchok_ack` String,
    `tstchok_dat` String,
    `tstci_dup_ack` String,
    `tstc_dsc_checksum` String,
    `tstc_dsc_len` String,
    `tstc_dsc_ins_data` String,
    `tstc_dsc_old_time` String,
    `tstci_cmp_dup_seg` String,
    `tstci_part_dup_seg` String,
    `tstci_cmp_segs_win` String,
    `tstci_part_segs_win` String,
    `tstcio_order` String,
    `tstci_seg_cls` String,
    `tstci_win_pr` String,
    `tstci_win_up` String,
    `tstco_win_pr` String,
    `tstco_win_up` String,
    `tstco_dl_ack` String,
    `tstcok_apr` String,
    `tstc_rx_tim` String,
    `tstc_rx_mtu` String,
    `tstc_path_m` String,
    `tstc_drop_pr` String,
    `tstc_drop_ka` String,
    `tstc_drop_f2` String,
    `tstc_drop_rx` String,
    `tsud_duration` String,
    `tsud_rec_data` String,
    `tsud_rec_no_port` String,
    `tsud_no_rec` String,
    `tsud_xmt_data` String,
    `tsic_duration` String,
    `tsic_in_msg` String,
    `tsic_in_error` String,
    `tsic_in_dst_unreach` String,
    `tsic_in_time_excd` String,
    `tsic_in_parm_prob` String,
    `tsic_in_src_quench` String,
    `tsic_in_redirect` String,
    `tsic_in_echo` String,
    `tsic_in_echo_rep` String,
    `tsic_in_tstamp` String,
    `tsic_in_tstamp_rep` String,
    `tsic_in_addr_mask` String,
    `tsic_in_addr_m_rep` String,
    `tsic_out_msg` String,
    `tsic_out_error` String,
    `tsic_out_dst_unreach` String,
    `tsic_out_time_excd` String,
    `tsic_out_parm_prob` String,
    `tsic_out_src_quench` String,
    `tsic_out_redirect` String,
    `tsic_out_echo` String,
    `tsic_out_echo_rep` String,
    `tsic_out_tstamp` String,
    `tsic_out_tstamp_rep` String,
    `tsic_out_addr_mask` String,
    `tsic_out_addr_m_rep` String,
    `tsp6_duration` String,
    `tsp6_rec_data` String,
    `tsp6_att_fwd_data` String,
    `tsp6_dlv_data` String,
    `tsp6_x_data` String,
    `tsp6_x_dsc_oth` String,
    `tsp6_x_dsc_route` String,
    `tsp6_timeouts` String,
    `tsp6_rec_d_rsmb` String,
    `tsp6_rsmb` String,
    `tsp6_fail_rsmb` String,
    `tsp6_rec_fgmt` String,
    `tsp6_dsc_d_fgmt` String,
    `tsp6_x_fgmt` String,
    `tsp6_route_disc` String,
    `tsc6_duration` String,
    `tsc6_in_msg` String,
    `tsc6_in_error` String,
    `tsc6_in_dst_unreach` String,
    `tsc6_in_time_excd` String,
    `tsc6_in_parm_prob` String,
    `tsc6_in_adm_prohib` String,
    `tsc6_in_pkt_too_big` String,
    `tsc6_in_echo` String,
    `tsc6_in_echo_rep` String,
    `tsc6_in_rt_solicit` String,
    `tsc6_in_rt_adv` String,
    `tsc6_in_nb_solicit` String,
    `tsc6_in_nb_adv` String,
    `tsc6_in_redirect` String,
    `tsc6_in_grp_mem_qry` String,
    `tsc6_in_grp_mem_rsp` String,
    `tsc6_in_grp_mem_red` String,
    `tsc6_out_msg` String,
    `tsc6_out_error` String,
    `tsc6_out_dst_unrch` String,
    `tsc6_out_time_excd` String,
    `tsc6_out_parm_prob` String,
    `tsc6_out_adm_prohib` String,
    `tsc6_out_pkt_too_big` String,
    `tsc6_out_echo` String,
    `tsc6_out_echo_rep` String,
    `tsc6_out_rt_solicit` String,
    `tsc6_out_rt_adv` String,
    `tsc6_out_nb_solicit` String,
    `tsc6_out_nb_adv` String,
    `tsc6_out_redirect` String,
    `tsc6_out_grp_mem_qry` String,
    `tsc6_out_grp_mem_rsp` String,
    `tsc6_out_grp_mem_red` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_6 (46 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_6
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `if_duration` String,
    `if_lnk_home` String,
    `if_name` String,
    `if_dev_name` String,
    `if_desc` String,
    `if_actual_mtu` String,
    `ifs_peed` String,
    `ifh_speed` String,
    `if_in_bytes` String,
    `if_in_uni_c` String,
    `if_in_broad_c` String,
    `if_in_multi_c` String,
    `if_in_disc` String,
    `if_in_error` String,
    `if_in_u_prot` String,
    `if_out_bytes` String,
    `if_out_uni_c` String,
    `if_out_broad_c` String,
    `if_out_multi_c` String,
    `if_out_disc` String,
    `if_out_error` String,
    `ifoql` String,
    `ifiqdx_name` String,
    `if_in_iqdx_bytes` String,
    `if_in_iqdx_uni_c` String,
    `if_out_iqdx_bytes` String,
    `if_out_iqdx_uni_c` String,
    `ifp_net_id` String,
    `if_add_intf_name` String,
    `if_add_intf_home` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_7 (34 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_7
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tc_duration` String,
    `tcr_name` String,
    `tc_bind_ip` String,
    `tc_port` String,
    `tc_conn` String,
    `tc_binds` String,
    `tc_busy_srv` String,
    `tc_syn_attack` String,
    `tc_highwater` String,
    `tc_num_conns` String,
    `ud_duration` String,
    `udr_name` String,
    `ud_bind_ip` String,
    `ud_port` String,
    `udi_dgrams` String,
    `udo_dgrams` String,
    `udi_bytes` String,
    `udo_bytes` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_8 (20 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_8
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `st_type` String,
    `st_flags` String,
    `st_time` String,
    `st_date` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_10 (33 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_10
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `resource_name` String,
    `connection_id` String,
    `subtask_tcb` String,
    `conn_time` String,
    `conn_date` String,
    `conn_end_time` String,
    `conn_end_date` String,
    `remote_ip` String,
    `local_ip` String,
    `remote_port` String,
    `local_port` String,
    `uc_type` String,
    `uc_reason` String,
    `in_datagrams` String,
    `out_datagrams` String,
    `in_bytes` String,
    `out_bytes` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_11 (163 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_11
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `sa_event_type` String,
    `sa_sec_protos` String,
    `sa_flags` String,
    `sa_sec_flags` String,
    `saip_proto` String,
    `sa_jobname` String,
    `sa_job_id` String,
    `sa_user_id` String,
    `sas_time` String,
    `sas_date` String,
    `sae_time` String,
    `sae_date` String,
    `sarip` String,
    `salip` String,
    `sar_port` String,
    `sal_port` String,
    `sa_conn_id` String,
    `sa_in_bytes` String,
    `sa_out_bytes` String,
    `sa_in_seg_dg` String,
    `sa_out_seg_dg` String,
    `ip_flt_out_act` String,
    `ip_flt_inb_act` String,
    `ip_flt_out_rule_name` String,
    `ip_flt_out_rule_ext` String,
    `ip_flt_in_rule_name` String,
    `ip_flt_in_rule_ext` String,
    `tls_prot_ver` String,
    `tls_source` String,
    `tls_handshake_type` String,
    `tls_handshake_role` String,
    `tls_session_id_len` String,
    `tls_session_id` String,
    `tls_protocol_provider` String,
    `tls_neg_cipher` String,
    `tls_cs_enc_alg` String,
    `tls_cs_msg_auth` String,
    `tls_cs_kex_alg` String,
    `tls_fips_mode` String,
    `tls_crypto_flags` String,
    `tls_rsvd2` String,
    `tls_s_cert_signature_method` String,
    `tls_s_cert_enc_method` String,
    `tls_s_cert_digest_alg` String,
    `tls_s_cert_serial_len` String,
    `tls_s_cert_serial` String,
    `tls_s_cert_time_type` String,
    `tls_s_cert_time` String,
    `tls_s_cert_key_type` String,
    `tls_s_cert_key_len` String,
    `tls_c_cert_signature_method` String,
    `tls_c_cert_enc_method` String,
    `tls_c_cert_digest_alg` String,
    `tls_c_cert_serial_len` String,
    `tls_c_cert_serial` String,
    `tls_c_cert_time_type` String,
    `tls_c_cert_time` String,
    `tls_c_cert_key_type` String,
    `tls_c_cert_key_len` String,
    `ssh_prot_ver` String,
    `ssh_source` String,
    `ssh_fips_mode` String,
    `ssh_crypto_flags` String,
    `ssh_comp` String,
    `ssh_protocol_provider` String,
    `ssh_auth_method` String,
    `ssh_auth_method2` String,
    `ssh_in_enc_alg` String,
    `ssh_in_msg_auth` String,
    `ssh_kex_method` String,
    `ssh_out_enc_alg` String,
    `ssh_out_msg_auth` String,
    `ssh_s_key_type` String,
    `ssh_s_key_len` String,
    `ssh_c_key_type` String,
    `ssh_c_key_len` String,
    `ssh_s_key_fp_len` String,
    `ssh_c_key_fp_len` String,
    `ssh_s_key_fp` String,
    `ssh_c_key_fp` String,
    `ssh_s_cert_signature_method` String,
    `ssh_s_cert_enc_method` String,
    `ssh_s_cert_digest_alg` String,
    `ssh_s_cert_serial_len` String,
    `ssh_s_cert_serial` String,
    `ssh_s_cert_time_type` String,
    `ssh_s_cert_time` String,
    `ssh_s_cert_key_type` String,
    `ssh_s_cert_key_len` String,
    `ssh_c_cert_signature_method` String,
    `ssh_c_cert_enc_method` String,
    `ssh_c_cert_digest_alg` String,
    `ssh_c_cert_serial_len` String,
    `ssh_c_cert_serial` String,
    `ssh_c_cert_time_type` String,
    `ssh_c_cert_time` String,
    `ssh_c_cert_key_type` String,
    `ssh_c_cert_key_len` String,
    `ip_sec_ike_tun_id` String,
    `ip_sec_ike_maj_ver` String,
    `ip_sec_ike_min_ver` String,
    `ip_sec_ike_tun_key_exch_rule` String,
    `ip_sec_ike_tun_lcl_endpt` String,
    `ip_sec_ike_tun_rmt_endpt` String,
    `ip_sec_ike_tun_lcl_auth_meth` String,
    `ip_sec_ike_tun_rmt_auth_meth` String,
    `ip_sec_ike_tun_auth_alg` String,
    `ip_sec_ike_tun_enc_alg` String,
    `ip_sec_ike_tun_dh_group` String,
    `ip_sec_ike_tun_pseudo_rand_func` String,
    `ip_sec_ike_tun_lifesize` String,
    `ip_sec_ike_tun_lifetime` String,
    `ip_sec_ike_tun_reauth_intvl` String,
    `ip_sec_lcl_cert_sign_meth` String,
    `ip_sec_lcl_cert_enc_meth` String,
    `ip_sec_lcl_cert_digest_alg` String,
    `i_psec_rsvd2` String,
    `ip_sec_lcl_cert_serial_len` String,
    `ip_sec_lcl_cert_serial` String,
    `ip_sec_lcl_cert_time_type` String,
    `ip_sec_lcl_cert_time` String,
    `ip_sec_lcl_cert_key_type` String,
    `ip_sec_lcl_cert_key_len` String,
    `ip_sec_rmt_cert_sign_meth` String,
    `ip_sec_rmt_cert_enc_meth` String,
    `ip_sec_rmt_cert_digest_alg` String,
    `ip_sec_rmt_cert_serial_len` String,
    `ip_sec_rmt_cert_serial` String,
    `ip_sec_rmt_cert_time_type` String,
    `ip_sec_rmt_cert_time` String,
    `ip_sec_rmt_cert_key_type` String,
    `ip_sec_rmt_cert_key_len` String,
    `ip_sec_tun_id` String,
    `ip_sec_tun_flags` String,
    `ip_sec_tun_type` String,
    `ip_sec_tun_state` String,
    `ip_sec_encap_mode` String,
    `ip_sec_auth_proto` String,
    `ip_sec_auth_alg` String,
    `ip_sec_enc_alg` String,
    `ip_sec_pfs_group` String,
    `ip_sec_lifesize` String,
    `ip_sec_lifetime` String,
    `ip_sec_vpn_life_expire` String,
    `dn_len` String,
    `dn_type` String,
    `dn` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_12 (113 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_12
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `sa_interval_duration` String,
    `sa_event_type` String,
    `sa_flags` String,
    `sa_sec_protos` String,
    `sa_jobname` String,
    `sa_user_id` String,
    `saip_proto` String,
    `sa_srv_ip` String,
    `sa_clt_ip` String,
    `sa_srv_port_start` String,
    `sa_srv_port_end` String,
    `sa_session_id` String,
    `sa_init_life_conn_cnt` String,
    `sa_init_life_partial_conn_cnt` String,
    `sa_init_life_short_conn_cnt` String,
    `sa_init_active_conn_cnt` String,
    `sa_init_life_in_bytes` String,
    `sa_init_life_out_bytes` String,
    `sa_init_life_in_seg_dg` String,
    `sa_init_life_out_seg_dg` String,
    `sa_end_life_conn_cnt` String,
    `sa_end_life_partial_conn_cnt` String,
    `sa_end_life_short_conn_cnt` String,
    `sa_end_active_conn_cnt` String,
    `sa_end_life_in_bytes` String,
    `sa_end_life_out_bytes` String,
    `sa_end_life_in_seg_dg` String,
    `sa_end_life_out_seg_dg` String,
    `tls_source` String,
    `tls_crypto_flags` String,
    `tls_prot_ver` String,
    `tls_neg_cipher` String,
    `tls_cs_enc_alg` String,
    `tls_cs_msg_auth` String,
    `tls_cs_kex_alg` String,
    `tls_s_cert_signature_method` String,
    `tls_s_cert_enc_method` String,
    `tls_s_cert_digest_alg` String,
    `tls_s_cert_key_type` String,
    `tls_s_cert_key_len` String,
    `tls_c_cert_signature_method` String,
    `tls_c_cert_enc_method` String,
    `tls_c_cert_digest_alg` String,
    `tls_c_cert_key_type` String,
    `tls_c_cert_key_len` String,
    `ssh_source` String,
    `ssh_prot_ver` String,
    `ssh_crypto_flags` String,
    `ssh_auth_method` String,
    `ssh_auth_method2` String,
    `ssh_in_enc_alg` String,
    `ssh_in_msg_auth` String,
    `ssh_kex_method` String,
    `ssh_out_enc_alg` String,
    `ssh_out_msg_auth` String,
    `ssh_s_key_type` String,
    `ssh_s_key_len` String,
    `ssh_c_key_type` String,
    `ssh_c_key_len` String,
    `ssh_s_cert_signature_method` String,
    `ssh_s_cert_enc_method` String,
    `ssh_s_cert_digest_alg` String,
    `ssh_s_cert_key_type` String,
    `ssh_s_cert_key_len` String,
    `ssh_c_cert_signature_method` String,
    `ssh_c_cert_enc_method` String,
    `ssh_c_cert_digest_alg` String,
    `ssh_c_cert_key_type` String,
    `ssh_c_cert_key_len` String,
    `ip_sec_ike_maj_ver` String,
    `ip_sec_ike_min_ver` String,
    `ip_sec_ike_tun_lcl_endpt` String,
    `ip_sec_ike_tun_rmt_endpt` String,
    `ip_sec_ike_tun_lcl_auth_meth` String,
    `ip_sec_ike_tun_rmt_auth_meth` String,
    `ip_sec_ike_tun_auth_alg` String,
    `ip_sec_ike_tun_enc_alg` String,
    `ip_sec_ike_tun_dh_group` String,
    `ip_sec_ike_tun_pseudo_rand_func` String,
    `ip_sec_lcl_cert_sign_meth` String,
    `ip_sec_lcl_cert_enc_meth` String,
    `ip_sec_lcl_cert_digest_alg` String,
    `ip_sec_lcl_cert_key_type` String,
    `ip_sec_lcl_cert_key_len` String,
    `ip_sec_rmt_cert_sign_meth` String,
    `ip_sec_rmt_cert_enc_meth` String,
    `ip_sec_rmt_cert_digest_alg` String,
    `ip_sec_rmt_cert_key_type` String,
    `ip_sec_rmt_cert_key_len` String,
    `ip_sec_pfs_group` String,
    `ip_sec_encap_mode` String,
    `ip_sec_auth_proto` String,
    `ip_sec_auth_alg` String,
    `ip_sec_enc_alg` String,
    `dn_len` String,
    `dn_type` String,
    `dn` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_20 (25 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_20
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `nilu` String,
    `ni_appl` String,
    `ni_ldev` String,
    `nirip` String,
    `nilip` String,
    `nir_port` String,
    `nil_port` String,
    `ni_time` String,
    `ni_date` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_21 (58 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_21
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ntlu` String,
    `nt_appl` String,
    `nt_ldev` String,
    `ntrip` String,
    `ntlip` String,
    `ntr_port` String,
    `ntl_port` String,
    `nt_host_nm` String,
    `nt_in_byte` String,
    `nt_out_byte` String,
    `n_ti_time` String,
    `n_ti_date` String,
    `n_tt_time` String,
    `n_tt_date` String,
    `nt_dur` String,
    `nts_type` String,
    `ntlu_sel` String,
    `ntssl` String,
    `nt_copt` String,
    `nt32opt` String,
    `ntr_code` String,
    `ntl_mode` String,
    `nt_devt` String,
    `nt_hostname` String,
    `ntr_rts` String,
    `ntrip_rts` String,
    `ntr_count_trans` String,
    `ntr_count_ip` String,
    `ntr_elaps_rnd_trp_sq` String,
    `ntr_elaps_ip_rt_sq` String,
    `ntr_elaps_sna_rt_sq` String,
    `ntr_grp_index` String,
    `ntrdr` String,
    `nt_bucket_bndry1` String,
    `nt_bucket_bndry2` String,
    `nt_bucket_bndry3` String,
    `nt_bucket_bndry4` String,
    `nt_bucket1_rts` String,
    `nt_bucket2_rts` String,
    `nt_bucket3_rts` String,
    `nt_bucket4_rts` String,
    `nt_bucket5_rts` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_22 (22 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_22
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `cirip` String,
    `cilip` String,
    `cir_port` String,
    `cil_port` String,
    `ci_time` String,
    `ci_date` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_23 (30 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_23
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ctrip` String,
    `ctlip` String,
    `ctr_port` String,
    `ctl_port` String,
    `ctnje_node` String,
    `ct_in_bytes` String,
    `ct_out_bytes` String,
    `c_ti_time` String,
    `c_ti_date` String,
    `c_tt_time` String,
    `c_tt_date` String,
    `ct_dur` String,
    `ctc_opt` String,
    `ct_devt` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_24 (50 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_24
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `pi_eye` String,
    `pi_flags` String,
    `pi_event` String,
    `pi_job` String,
    `pi_stack` String,
    `pi_prof_id` String,
    `pi_port` String,
    `ds_eye` String,
    `ds_flags` String,
    `ds_addr` String,
    `ds_pfx_len` String,
    `ds_group` String,
    `ds_ds_name` String,
    `tg_eye` String,
    `tg_flag1` String,
    `tg_flag2` String,
    `tg_flag3` String,
    `tg_flag4` String,
    `tgtcp_name` String,
    `tgsa_cache_time` String,
    `tgxcf_subplex` String,
    `tgxcf_mon` String,
    `tgxcf_conn_to` String,
    `tgxcf_rcvy_to` String,
    `tglu_port` String,
    `tglu_ip_addr` String,
    `lu_eye` String,
    `lu_flags` String,
    `lu_name` String,
    `lu_appl` String,
    `lu_logmode` String,
    `lu_group` String,
    `lu_client_ip` String,
    `lu_user` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_32 (23 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_32
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `sc_flags` String,
    `sc_type` String,
    `sc_rank` String,
    `sc_pfx_len` String,
    `sc_addr` String,
    `sc_intf` String,
    `sc_saf` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_33 (23 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_33
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `rm_flags` String,
    `rm_type` String,
    `rm_rank` String,
    `rm_pfx_len` String,
    `rm_addr` String,
    `rm_intf` String,
    `rm_saf` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_34 (23 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_34
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ta_flags` String,
    `ta_dvipa` String,
    `ta_target` String,
    `ta_port` String,
    `ta_port_end` String,
    `ta_prot` String,
    `ta_job` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_35 (23 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_35
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tr_flags` String,
    `tr_dvipa` String,
    `tr_target` String,
    `tr_port` String,
    `tr_port_end` String,
    `tr_prot` String,
    `tr_job` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_36 (24 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_36
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tss_flags` String,
    `tss_dvipa` String,
    `tss_target` String,
    `tss_port` String,
    `tss_port_end` String,
    `tss_prot` String,
    `tss_job` String,
    `tss_conn_id` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_37 (24 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_37
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tse_flags` String,
    `tse_dvipa` String,
    `tse_target` String,
    `tse_port` String,
    `tse_port_end` String,
    `tse_prot` String,
    `tse_job` String,
    `tse_conn_id` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_38 (30 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_38
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ls_lcl_name` String,
    `ls_rmt_name` String,
    `ls_flags` String,
    `lssmc_version` String,
    `ls_in_bytes` String,
    `ls_out_bytes` String,
    `ls_in_pkts` String,
    `ls_out_pkts` String,
    `ls_in_rmb` String,
    `ls_out_rmb` String,
    `ls_conn_cnt` String,
    `ls_eid` String,
    `ls_rmt_host_name` String,
    `ls_rmt_os_type` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_39 (26 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_39
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `li_lcl_name` String,
    `li_rmt_name` String,
    `li_flags` String,
    `lismc_version` String,
    `li_eid` String,
    `lis_time` String,
    `lisstck` String,
    `li_rmt_host_name` String,
    `li_rmt_os_type` String,
    `li_ism_dev` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_40 (28 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_40
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `lt_lcl_name` String,
    `lt_rmt_name` String,
    `lt_flags` String,
    `ltsmc_version` String,
    `lt_term_code` String,
    `lt_eid` String,
    `lte_time` String,
    `ltestck` String,
    `lt_in_bytes` String,
    `lt_out_bytes` String,
    `lt_rmt_host_name` String,
    `lt_rmt_os_type` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_41 (37 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_41
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `gs_lcl_gid` String,
    `gs_rmt_gid` String,
    `gs_flags` String,
    `gs_version` String,
    `gs_link_cnt` String,
    `gs_in_bytes` String,
    `gs_out_bytes` String,
    `gs_in_pkts` String,
    `gs_out_pkts` String,
    `gs_conn_cnt` String,
    `ls_lcl_lnk_id` String,
    `ls_rmt_lnk_id` String,
    `ls_lcl_mac` String,
    `ls_rmt_mac` String,
    `ls_vlan_id` String,
    `ls_flags` String,
    `ls_in_bytes` String,
    `ls_out_bytes` String,
    `ls_in_pkts` String,
    `ls_out_pkts` String,
    `lsqp` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_42 (29 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_42
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `li_lcl_gid` String,
    `li_rmt_gid` String,
    `li_lcl_mac` String,
    `li_rmt_mac` String,
    `li_vlan_id` String,
    `li_flags` String,
    `li_lcl_lnk_id` String,
    `li_rmt_lnk_id` String,
    `li_lcl_qp` String,
    `li_rmt_qp` String,
    `li_lnk_grp_id` String,
    `lis_time` String,
    `lisstck` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_43 (28 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_43
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `lt_lcl_gid` String,
    `lt_rmt_gid` String,
    `lt_lcl_mac` String,
    `lt_rmt_mac` String,
    `lt_vlan_id` String,
    `lt_term_code` String,
    `lt_lcl_lnk_id` String,
    `lt_rmt_lnk_id` String,
    `lt_in_bytes` String,
    `lt_out_bytes` String,
    `lte_time` String,
    `ltestck` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_44 (28 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_44
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `rs_name` String,
    `rsmac` String,
    `rs_flags` String,
    `rspci` String,
    `rs_in_bytes` String,
    `rs_out_bytes` String,
    `rs_in_pkts` String,
    `rs_out_pkts` String,
    `rs_in_err` String,
    `rs_out_err` String,
    `rsqp_cnt` String,
    `rs_link_cnt` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_45 (27 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_45
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `is_name` String,
    `is_flags` String,
    `isfid` String,
    `is_in_bytes` String,
    `is_out_bytes` String,
    `is_in_pkts` String,
    `is_out_pkts` String,
    `is_in_err` String,
    `is_out_err` String,
    `is_dmb_cnt` String,
    `is_link_cnt` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_48 (31 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_48
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ci_job` String,
    `ci_entry` String,
    `ci_e_date` String,
    `ci_useid` String,
    `ci_extwrt` String,
    `ci_jes` String,
    `cf_flags` String,
    `cf_flag2` String,
    `cf_flag3` String,
    `cf_host` String,
    `cf_port` String,
    `cf_job` String,
    `cf_retry` String,
    `cf_max_conn` String,
    `cf_charset` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_49 (36 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_49
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ci_job` String,
    `ci_entry` String,
    `ci_e_date` String,
    `ci_useid` String,
    `ci_extwrt` String,
    `ci_jes` String,
    `cnrip` String,
    `cnlip` String,
    `cnr_port` String,
    `cnl_port` String,
    `cn_conn_id` String,
    `cn_event` String,
    `cn_host` String,
    `cs_status` String,
    `cs_secure` String,
    `css_time` String,
    `css_date` String,
    `cs_bytes` String,
    `cs_reply` String,
    `cs_reason` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_50 (33 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_50
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `si` String,
    `si_job` String,
    `si_entry` String,
    `si_e_date` String,
    `si_useid` String,
    `si_job_id` String,
    `si_sys` String,
    `si_xeq` String,
    `si_crer` String,
    `si_tkid` String,
    `si_jnum` String,
    `si_dsky` String,
    `si_dsnm` String,
    `mi` String,
    `mh_len` String,
    `mh_key` String,
    `mh_data` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_51 (42 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_51
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ci_job` String,
    `ci_entry` String,
    `ci_e_date` String,
    `ci_useid` String,
    `ci_extwrt` String,
    `ci_jes` String,
    `si_job` String,
    `si_entry` String,
    `si_e_date` String,
    `si_useid` String,
    `si_job_id` String,
    `si_sys` String,
    `si_xeq` String,
    `si_crer` String,
    `si_tkid` String,
    `si_jnum` String,
    `si_dsky` String,
    `si_dsnm` String,
    `sj_event` String,
    `sj_job` String,
    `sj_job_id` String,
    `sj_class` String,
    `sj_recs` String,
    `sj_bytes` String,
    `sj_dest` String,
    `sj_writer` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_52 (33 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_52
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ci_job` String,
    `ci_entry` String,
    `ci_e_date` String,
    `ci_useid` String,
    `ci_extwrt` String,
    `ci_jes` String,
    `sts_time` String,
    `sts_date` String,
    `ste_time` String,
    `ste_date` String,
    `st_mail_sent` String,
    `st_mail_fail` String,
    `st_bytes_out` String,
    `st_conn_ok` String,
    `st_conn_fail` String,
    `st_spool_read` String,
    `st_retry` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_70 (57 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_70
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `fs_oper` String,
    `ftp_cmd` String,
    `fsf_type` String,
    `fsdrip` String,
    `fsdlip` String,
    `fsdr_port` String,
    `fsdl_port` String,
    `fscrip` String,
    `fsclip` String,
    `fscr_port` String,
    `fscl_port` String,
    `server_user` String,
    `fs_type` String,
    `fs_mode` String,
    `fs_struct` String,
    `fs_ds_type` String,
    `fss_time` String,
    `fss_date` String,
    `fse_time` String,
    `fse_date` String,
    `fs_dur` String,
    `bytes_transferred` String,
    `fsl_reply` String,
    `fsm1` String,
    `fsrs` String,
    `fsm2` String,
    `fs_bytes_float` String,
    `fsc_conn_id` String,
    `fsd_conn_id` String,
    `fs_session_id` String,
    `hostname` String,
    `file_name` String,
    `fs_file_name2` String,
    `fs_mechanism` String,
    `fsc_protect` String,
    `fsd_protect` String,
    `fs_login_mech` String,
    `fs_proto_level` String,
    `fs_cipher_spec` String,
    `fs_proto_buf_size` String,
    `fs_cipher` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_71 (29 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_71
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `id_eye` String,
    `id_flags` String,
    `id_job` String,
    `id_stack` String,
    `idasid` String,
    `id_user` String,
    `cf_eye` String,
    `cf_flags` String,
    `cf_event` String,
    `cf_port` String,
    `cf_items` String,
    `cf_ds_name` String,
    `ci_text` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_72 (32 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_72
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ffrip` String,
    `fflip` String,
    `ffr_port` String,
    `ffl_port` String,
    `ff_user_id` String,
    `ff_reason` String,
    `ffc_conn_id` String,
    `ff_session_id` String,
    `ff_mechanism` String,
    `ffc_protect` String,
    `ffd_protect` String,
    `ff_login_mech` String,
    `ff_proto_level` String,
    `ff_cipher_spec` String,
    `ff_prot_buff_size` String,
    `ff_cipher` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_73 (30 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_73
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_version` String,
    `tn_auth` String,
    `tn_life_sec` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_vpn` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_dh_grp` String,
    `tns_time` String,
    `tns_date` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_74 (38 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_74
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_version` String,
    `tn_auth` String,
    `tn_life_sec` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_vpn` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_dh_grp` String,
    `tns_time` String,
    `tns_date` String,
    `ts_in_bytes` String,
    `ts_out_bytes` String,
    `ts_in_pkts` String,
    `ts_out_pkts` String,
    `ts_child_sa` String,
    `ts_rekey` String,
    `tse_time` String,
    `tse_date` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_75 (39 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_75
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_type` String,
    `tn_mode` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_proto` String,
    `tn_spi_in` String,
    `tn_spi_out` String,
    `tns_time` String,
    `tns_date` String,
    `dt_flags` String,
    `dt_tun_id` String,
    `dt_ike_id` String,
    `dt_lcl_ip` String,
    `dt_rmt_ip` String,
    `dt_lcl_port` String,
    `dt_rmt_port` String,
    `dt_prot` String,
    `dt_spi` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_76 (39 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_76
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_type` String,
    `tn_mode` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_proto` String,
    `tn_spi_in` String,
    `tn_spi_out` String,
    `tns_time` String,
    `tns_date` String,
    `dt_flags` String,
    `dt_tun_id` String,
    `dt_ike_id` String,
    `dt_lcl_ip` String,
    `dt_rmt_ip` String,
    `dt_lcl_port` String,
    `dt_rmt_port` String,
    `dt_prot` String,
    `dt_spi` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_77 (39 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_77
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_type` String,
    `tn_mode` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_proto` String,
    `tn_spi_in` String,
    `tn_spi_out` String,
    `tns_time` String,
    `tns_date` String,
    `dt_flags` String,
    `dt_tun_id` String,
    `dt_ike_id` String,
    `dt_lcl_ip` String,
    `dt_rmt_ip` String,
    `dt_lcl_port` String,
    `dt_rmt_port` String,
    `dt_prot` String,
    `dt_spi` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_78 (39 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_78
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_type` String,
    `tn_mode` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_proto` String,
    `tn_spi_in` String,
    `tn_spi_out` String,
    `tns_time` String,
    `tns_date` String,
    `dt_flags` String,
    `dt_tun_id` String,
    `dt_ike_id` String,
    `dt_lcl_ip` String,
    `dt_rmt_ip` String,
    `dt_lcl_port` String,
    `dt_rmt_port` String,
    `dt_prot` String,
    `dt_spi` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_79 (40 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_79
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_type` String,
    `tn_mode` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_proto` String,
    `tn_spi_in` String,
    `tn_spi_out` String,
    `tns_time` String,
    `tns_date` String,
    `mt_flags` String,
    `mt_tun_id` String,
    `mt_lcl_ip` String,
    `mt_rmt_ip` String,
    `mt_spi_in` String,
    `mt_spi_out` String,
    `mt_enc_alg` String,
    `mt_int_alg` String,
    `mts_time` String,
    `mts_date` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_80 (40 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_80
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `tn_flags` String,
    `tn_type` String,
    `tn_mode` String,
    `tn_lcl_ip` String,
    `tn_rmt_ip` String,
    `tn_tun_id` String,
    `tn_enc_alg` String,
    `tn_int_alg` String,
    `tn_proto` String,
    `tn_spi_in` String,
    `tn_spi_out` String,
    `tns_time` String,
    `tns_date` String,
    `mt_flags` String,
    `mt_tun_id` String,
    `mt_lcl_ip` String,
    `mt_rmt_ip` String,
    `mt_spi_in` String,
    `mt_spi_out` String,
    `mt_enc_alg` String,
    `mt_int_alg` String,
    `mts_time` String,
    `mts_date` String,
    `id_str` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;

-- smf_119_81 (37 columns)
CREATE TABLE IF NOT EXISTS smf.smf_119_81
(
    `smf_sys_flag` String,
    `smf_record_type` LowCardinality(String),
    `time` String,
    `date` String,
    `smf_system_id` LowCardinality(String),
    `smf_subsystem_id` LowCardinality(String),
    `smf_subtype` LowCardinality(String),
    `sys_name` LowCardinality(String),
    `sysplex_name` LowCardinality(String),
    `tcp_stack` LowCardinality(String),
    `tcp_release` String,
    `tcp_component` String,
    `as_name` String,
    `user_id` LowCardinality(String),
    `asid` String,
    `record_reason` String,
    `ist119_ds_time` String,
    `ist119_ds_plu_name` String,
    `ist119_ds_slu_name` String,
    `ist119_ds_sid` String,
    `ist119_ds_inc_tk` String,
    `ist119_ds_e_code` String,
    `ist119_ds_dscount` String,
    `ist119_ds_action` String,
    `ist119_ds_ripv6` String,
    `ist119_ds_r_port` String,
    `ist119_ds_row` String,
    `ist119_ds_column` String,
    `ist119_ds_offset` String,
    `ist119_ds_o_buf_o` String,
    `ist119_ds_i_buf_o` String,
    `ist119_ds_o_buf_l` String,
    `ist119_ds_i_buf_l` String,
    `ist119_ds_oseq` String,
    `ist119_ds_iseq` String,
    `ist119_ds_doru` String,
    `ist119_ds_diru` String,
    ingested_at DateTime DEFAULT now(),
    event_date Date MATERIALIZED toDateOrZero(`date`)
)
ENGINE = MergeTree
PARTITION BY event_date
ORDER BY (event_date, smf_system_id, `time`)
TTL event_date + INTERVAL 10 DAY
SETTINGS index_granularity = 8192;


-- ---------------------------------------------------------------------------
-- Lightweight rollup tables for Grafana (filled by scripts/refresh_stats.sh)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS smf.stats_records_daily
(
    event_date Date,
    table_name LowCardinality(String),
    smf_system_id LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, table_name, smf_system_id)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_tcp_hourly
(
    hour DateTime,
    smf_system_id LowCardinality(String),
    tcp_stack LowCardinality(String),
    conn_count UInt64,
    in_bytes UInt64,
    out_bytes UInt64
)
ENGINE = SummingMergeTree((conn_count, in_bytes, out_bytes))
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, smf_system_id, tcp_stack)
TTL toDate(hour) + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_dataset_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    direction LowCardinality(String),
    job_name LowCardinality(String),
    dsname String,
    row_count UInt64,
    excp_sum UInt64
)
ENGINE = SummingMergeTree((row_count, excp_sum))
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, direction, job_name, dsname)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_racf_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    event_code String,
    user_id LowCardinality(String),
    job_name LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, event_code, user_id, job_name)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_ftp_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    direction LowCardinality(String),
    local_user LowCardinality(String),
    bytes_sum UInt64,
    xfer_count UInt64
)
ENGINE = SummingMergeTree((bytes_sum, xfer_count))
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, direction, local_user)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_jobs_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    smf_subtype String,
    job_name LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, smf_subtype, job_name)
TTL event_date + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_uss_hourly
(
    hour DateTime,
    smf_system_id LowCardinality(String),
    action LowCardinality(String),
    row_count UInt64
)
ENGINE = SummingMergeTree(row_count)
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, smf_system_id, action)
TTL toDate(hour) + INTERVAL 10 DAY;

CREATE TABLE IF NOT EXISTS smf.stats_uss_path_daily
(
    event_date Date,
    smf_system_id LowCardinality(String),
    pathname String,
    job_name LowCardinality(String),
    close_count UInt64,
    bytes_read UInt64,
    bytes_written UInt64
)
ENGINE = SummingMergeTree((close_count, bytes_read, bytes_written))
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, smf_system_id, pathname, job_name)
TTL event_date + INTERVAL 10 DAY;
