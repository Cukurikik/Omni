       IDENTIFICATION DIVISION.
       PROGRAM-ID. OMNI-LEDGER.
       AUTHOR. OMNI-MOTHER.
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT LEDGER-FILE ASSIGN TO "ledger.dat"
           ORGANIZATION IS LINE SEQUENTIAL.
           
       DATA DIVISION.
       FILE SECTION.
       FD LEDGER-FILE.
       01 LEDGER-RECORD.
          05 TX-ID         PIC X(10).
          05 TX-AMOUNT     PIC 9(7)V99.
          05 TX-STATUS     PIC X(10).

       WORKING-STORAGE SECTION.
       01 EOF-FLAG         PIC X VALUE 'N'.
       01 TOTAL-AMOUNT     PIC 9(9)V99 VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
           OPEN INPUT LEDGER-FILE.
           PERFORM READ-RECORD UNTIL EOF-FLAG = 'Y'.
           DISPLAY "OMNI Total Ledger Amount: " TOTAL-AMOUNT.
           CLOSE LEDGER-FILE.
           STOP RUN.

       READ-RECORD.
           READ LEDGER-FILE INTO LEDGER-RECORD
               AT END
                   MOVE 'Y' TO EOF-FLAG
               NOT AT END
                   IF TX-STATUS = "CLEARED   "
                       ADD TX-AMOUNT TO TOTAL-AMOUNT
                   END-IF
           END-READ.
