"""SMF type 14 — INPUT or RDBACK data set activity (non-VSAM).

Layout from IBM z/OS SMF (IFASMFR / IFGSMF14) and PACSYS smf14 tables.
Type 14 shares structure with type 15; this module maps 14 only.

Fixed contiguous sections (no header triplets):
  header + sizes, TIOT @52, JFCB @68, DCB/DEB @244.
UCB sections follow at 244 + SMF14SDC. Fields under ``_UCB`` assume the
common 28-byte DCB/DEB section (SMF14SDC == 28); set that in samples.
"""

from __future__ import annotations

from ..types import FieldSpec as F

# First UCB section when SMF14SDC == 28 (12-byte DCB/DEB + 16-byte extension).
_UCB = 244 + 28


def _h(key, ibm, ftype, off, desc, length=None):
    return F(key, ibm, ftype, off, None, length=length, description=desc)


FIELDS = [
    # Header
    _h("smf_sys_flag", "SMF14FLG", "DEC1", 4, "System indicator flags"),
    _h("smf_record_type", "SMF14RTY", "DEC1", 5, "Record type (14)"),
    _h("time", "SMF14TME", "TME", 6, "Time record moved to SMF buffer (HH:MM:SS)"),
    _h("date", "SMF14DTE", "DTE", 10, "Date record moved to SMF buffer (YYYY-MM-DD)"),
    _h("smf_system_id", "SMF14SID", "CHR4", 14, "System identification (SID)"),
    _h("job_name", "SMF14JBN", "CHR8", 18, "Job name (job log identification)"),
    _h("reader_start_t", "SMF14RST", "TME", 26, "Reader recognized JOB card — time"),
    _h("reader_start_d", "SMF14RSD", "DTE", 30, "Reader recognized JOB card — date"),
    _h("user_id_field", "SMF14UID", "CHR8", 34, "User-defined identification (common exit)"),
    _h("record_indicators", "SMF14RIN", "HEX2", 42, "Record / data set indicators (EOV, DASD, VIO, …)"),
    # Section sizes
    _h("dcb_deb_size", "SMF14SDC", "DEC1", 44, "Size of DCB/DEB section"),
    _h("ucb_section_count", "SMF14NUC", "DEC1", 45, "Number of UCB sections"),
    _h("ucb_section_size", "SMF14SUC", "DEC1", 46, "Size of each UCB section"),
    _h("isam_ext_size", "SMF14SET", "DEC1", 47, "Size of ISAM extension (0 on modern z/OS)"),
    _h("open_time", "SMF14OPE", "TME", 48, "Time data set was opened"),
    # TIOT
    _h("dd_entry_length", "SMF14TIOE1", "DEC1", 52, "TIOT DD entry length (TIOELNGH)"),
    _h("tiot_status", "SMF14TIOE2", "HEX1", 53, "TIOT status / tape label processing (TIOESSTA)"),
    _h("devices_requested", "SMF14TIOE3", "DEC1", 54, "Devices requested at allocation (TIOEWTCT)"),
    _h("ddname", "SMF14TIOE5", "CHR8", 56, "DD name (TIOEDDNM)"),
    # JFCB (key fields; absolute offsets within the 176-byte JFCB at 68)
    _h(
        "dsname",
        "SMF14_JFCBDSNM",
        "CHR",
        68,
        "Data set name (JFCBDSNM / DSNAME=)",
        length=44,
    ),
    _h("member_name", "SMF14_JFCBELNM", "CHR8", 112, "Member or relative generation (JFCBELNM)"),
    _h("jfcb_tsdm", "SMF14_JFCBTSDM", "HEX1", 120, "JFCB management interface flags (JFCBTSDM)"),
    _h("label_type", "SMF14_JFCBLTYP", "HEX1", 134, "LABEL= type (JFCBLTYP)"),
    _h("file_seq", "SMF14_JFCBFLSQ", "DEC2", 136, "LABEL= data set sequence number"),
    _h("vol_seq", "SMF14_JFCBVLSQ", "DEC2", 138, "VOLUME= volume sequence number"),
    _h("creation_date_jfcb", "SMF14_JFCBCRDT", "HEX", 148, "JFCB creation date (YYDDD packed)", length=3),
    _h("expiration_date_jfcb", "SMF14_JFCBXPDT", "HEX", 151, "JFCB expiration date (YYDDD packed)", length=3),
    _h("jfcb_ind1", "SMF14_JFCBIND1", "HEX1", 154, "JFCB indicator 1 (GDG/PDS/RLSE/…)"),
    _h("jfcb_ind2", "SMF14_JFCBIND2", "HEX1", 155, "JFCB indicator 2 (DISP= NEW/MOD/OLD/…)"),
    _h("dsorg_jfcb", "SMF14_JFCDSRG1", "HEX1", 166, "JFCB DSORG byte 1 (PS/PO/DA/…)"),
    _h("recfm_jfcb", "SMF14_JFCRECFM", "HEX1", 168, "JFCB record format (RECFM)"),
    _h("blksize", "SMF14_JFCBLKSI", "DEC2", 170, "Maximum block size (BLKSIZE)"),
    _h("lrecl", "SMF14_JFCLRECL", "DEC2", 172, "Logical record length (LRECL)"),
    _h("volser_count", "SMF14_JFCBNVOL", "DEC1", 185, "Number of volume serial numbers"),
    _h("volser_1", "SMF14_JFCBVOLS_1", "CHR", 186, "Volume serial number 1", length=6),
    # DCB/DEB (common 12 bytes @244; open date in extension @268)
    _h("dsorg_dcb", "SMF14DCBOR", "HEX2", 244, "DCB DSORG being used"),
    _h("recfm_dcb", "SMF14DCBRF", "HEX1", 246, "DCB record format"),
    _h("open_date", "SMF14OPD", "DTE", 268, "Date data set was opened"),
    # First UCB (requires SMF14SDC == 28)
    _h("device_number", "SMF14UCBDV", "HEX2", _UCB + 0, "Device number (X'7FFF' may be VIO)"),
    _h("ucb_volser", "SMF14FSRTEV", "CHR", _UCB + 2, "UCB volume serial number", length=6),
    _h("unit_type", "SMF14UCBTY", "HEX4", _UCB + 8, "Unit type (UCBTYP)"),
    _h("extent_count", "SMF14NEX", "DEC1", _UCB + 13, "Number of extents"),
    _h("excp_count", "SMF14EXCP", "DEC4", _UCB + 16, "EXCP count for entire step (cumulative)"),
    _h("tracks_allocated", "SMF14NTA", "DEC4", _UCB + 20, "Tracks allocated on device (DASD)"),
]
