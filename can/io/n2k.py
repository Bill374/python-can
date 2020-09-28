#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 19:12:52 2020

@author: bill

Logging NMEA2000 frames
"""

CAN_MSG_EXT = 0x80000000
CAN_ID_MASK = 0x1FFFFFFF
BASE_HEX = 16
BASE_DEC = 10

logger = logging.getLogger("can.io.asc")

class N2KWriter(BaseIOHandler, Listener):
    """Logs NMEA 2000 frames to a log file (.n2k).
    Writes a comma separated text file with a line for each NMEA 2000 frame. 
    Includes a header line.
    NMEA 2000 messages often extend across multiple frames using Fast-packet
    transmission for sending up to 256 bytes of data.  This writter does not 
    assemble the separate frames into a complete message.

    The columns are as follows:

    ================ ======================= =========================
    name of column   format description      example
    ================ ======================= =========================
    timestamp        decimal float           1483389946.197
    PGN              integer                 127251
    dlc              integer                 8
    data             hex                     FF FF E0 6F 43 FF FF 00
    """
    
    def __init__(self, file, append=False):
        """
        :param file: a path-like object or a file-like object to write to.
                     If this is a file-like object, is has to open in text
                     write mode, not binary write mode.
        :param bool append: if set to `True` messages are appended to
                            the file and no header line is written, else
                            the file is truncated and starts with a newly
                            written header line
        """
        mode = "a" if append else "w"
        super().__init__(file, mode=mode)

        # Write a header row
        if not append:
            self.file.write("timestamp,PGN,dlc,data\n")

    def on_message_received(self, msg):
        if not(msg.is_extended_id):
            # This should never happen with NMEA 2000
            print('Unexpected standard message ID')
            return
        if msg.is_remote_frame:
            # We don't want to log remote requests
            # maybe offer this as an option later
            print('Ignoring remote request')
            return
        if msg.is_error_frame:
            # Ignore error frames
            print('Ignoring error frame')
        row = ",".join(
            [
                repr(msg.timestamp),  # cannot use str() here because that is rounding
                str(msg.arbitration_id),
                str(msg.dlc),
                hex(msg.data),
            ]
        )
        self.file.write(row)
        self.file.write("\n")

