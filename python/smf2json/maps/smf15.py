"""SMF type 15 field map — OUTPUT / UPDAT / INOUT / OUTIN data set activity (non-VSAM).

Layout matches type 14 (IBM IFASMFR / PACSYS). Fixed sections; UCB fields assume
the common DCB/DEB size SMF15SDC=28 so the first UCB starts at absolute offset 272.
"""

from __future__ import annotations

from ..types import FieldSpec as F

# First UCB section when SMF15SDC == 28 (12-byte DCB/DEB + 16-byte DASD/tape extension)
UCB0 = 272

FIELDS = [
    # Standard header + job log id
    F("smf_sys_flag", "SMF15FLG", "DEC1", 4, description="System indicator flags"),
    F("smf_record_type", "SMF15RTY", "DEC1", 5, description="Record type (15)"),
    F("time", "SMF15TME", "TME", 6, description="Time record moved to SMF buffer"),
    F("date", "SMF15DTE", "DTE", 10, description="Date record moved to SMF buffer"),
    F("smf_system_id", "SMF15SID", "CHR4", 14, description="System identification (SID)"),
    F("job_name", "SMF15JBN", "CHR8", 18, description="Job name"),
    F("reader_start_t", "SMF15RST", "TME", 26, description="Reader start time (JOB card)"),
    F("reader_start_d", "SMF15RSD", "DTE", 30, description="Reader start date (JOB card)"),
    F("user_id_field", "SMF15UID", "CHR8", 34, description="User-defined identification field"),
    F("record_ds_ind", "SMF15RIN", "HEX2", 42, description="Record and data set indicator flags"),
    # Section sizes + open time
    F("dcb_deb_size", "SMF15SDC", "DEC1", 44, description="Size of DCB/DEB section"),
    F("ucb_section_count", "SMF15NUC", "DEC1", 45, description="Number of UCB sections"),
    F("ucb_section_size", "SMF15SUC", "DEC1", 46, description="Size of each UCB section"),
    F("isam_ext_size", "SMF15SET", "DEC1", 47, description="Size of ISAM extension section"),
    F("open_time", "SMF15OPE", "TME", 48, description="Time when the data set was opened"),
    # TIOT
    F("ddname", "SMF15TIOE5", "CHR8", 56, description="Data definition name (DDNAME)"),
    # JFCB (key fields)
    F(
        "dsname",
        "SMF15_JFCBDSNM",
        "CHR",
        68,
        length=44,
        description="Data set name (DSNAME=)",
    ),
    F("member_name", "SMF15_JFCBELNM", "CHR8", 112, description="Member / relative generation name"),
    F("jfcb_ind2", "SMF15_JFCBIND2", "HEX1", 155, description="JFCB indicator byte 2 (DISP= NEW/MOD/OLD)"),
    F("dsorg", "SMF15_JFCDSRG1", "HEX1", 166, description="Data set organization (JFCDSORG byte 1)"),
    F("recfm", "SMF15_JFCRECFM", "HEX1", 168, description="Record format (DCB=RECFM=)"),
    F("blksize", "SMF15_JFCBLKSI", "DEC2", 170, description="Maximum block size (DCB=BLKSIZE=)"),
    F("lrecl", "SMF15_JFCLRECL", "DEC2", 172, description="Logical record length (DCB=LRECL=)"),
    F("vol_count_jfcb", "SMF15_JFCBNVOL", "DEC1", 185, description="Number of volume serial numbers"),
    F(
        "volser_1",
        "SMF15_JFCBVOLS_1",
        "CHR",
        186,
        length=6,
        description="Volume serial number 1",
    ),
    # DCB/DEB (absolute from record start; DASD open date in the 16-byte extension)
    F("dcb_dsorg", "SMF15DCBOR", "HEX2", 244, description="Data set organization being used (DCBDSORG)"),
    F("dcb_recfm", "SMF15DCBRF", "HEX1", 246, description="Record format (DCBRECFM)"),
    F("open_date", "SMF15OPD_DASD", "DTE", 268, description="Date when the data set was opened (DASD)"),
    # First UCB (SMF15SDC=28 → offset 272)
    F("device_number", "SMF15UCBDV", "HEX2", UCB0 + 0, description="Device number (UCB)"),
    F(
        "ucb_volser",
        "SMF15FSRTEV",
        "CHR",
        UCB0 + 2,
        length=6,
        description="Volume serial number (UCB)",
    ),
    F("unit_type", "SMF15UCBTY", "HEX4", UCB0 + 8, description="Unit type (UCBTYP)"),
    F("extent_count", "SMF15NEX", "DEC1", UCB0 + 13, description="Number of extents"),
    F("excp_count", "SMF15EXCP", "DEC4", UCB0 + 16, description="EXCP count for entire step"),
    F("tracks_allocated", "SMF15NTA", "DEC4", UCB0 + 20, description="Number of tracks allocated (DASD)"),
]
