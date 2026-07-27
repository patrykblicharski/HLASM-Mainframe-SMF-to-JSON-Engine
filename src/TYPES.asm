* ====================================================================
* SHARED DATA TYPE CONSTANTS FOR SMF_FIELD / SMF2ZIIP BTAB
* ====================================================================
T_BIN1   EQU   0      * Reserved / skip (not a converter)
T_CHR1   EQU   1      * EBCDIC string 1 byte
T_CHR2   EQU   2      * EBCDIC string 2 bytes
T_CHR4   EQU   3      * EBCDIC string 4 bytes
T_CHR8   EQU   4      * EBCDIC string 8 bytes
T_DEC1   EQU   5      * Unsigned/signed binary 1 byte -> decimal digits
T_DEC2   EQU   6      * Binary 2 bytes -> decimal digits
T_DEC4   EQU   7      * Binary 4 bytes -> decimal digits
T_DTE    EQU   8      * SMF packed date -> YYYY-MM-DD
T_TME    EQU   9      * SMF time (1/100s) -> HH:MM:SS
T_RS_STR EQU   10     * Relocate section Tag-Length-Data string
T_CHR20  EQU   11     * EBCDIC string 20 bytes
T_HEX2   EQU   12     * Binary 2 bytes -> 4-char hex string
