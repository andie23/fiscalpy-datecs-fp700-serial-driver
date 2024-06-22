FP_PREAMBLE = 0x1
FP_POSTAMBLE = 0x5
FP_TERMINATOR = 0x3
MARKER_SPACE = 0x20

class FpProtocol:
    """
    Author: Andrew Mfune

    Driver supports sending Fiscal printer commands via Serial Cable to Datecs
    Printers.
    """

    def __init__(self):
        self.sequence_number = 0

    def uint_16_to_4_bytes(self, word):
        """
        Honestly this is some weird shit, let's be glad it makes things work
        """
        return [
            ((word >> 12 & 0x0f) + 0x30),
            ((word >> 8 & 0x0f) + 0x30),
            ((word >> 4 & 0x0f) + 0x30),
            ((word >> 0 & 0x0f) + 0x30)
        ]

    def calculate_bcc(self, framents):
        """
        Sums bytes of <LEN> + <SEQ> + <CMD> + <DATA> + <05> for some checksum value.
        this value has to be 4bytes long
        """
        return self.uint_16_to_4_bytes(sum(framents))

    def wrap_message(self, cmd, data=''):
        """
        Composition of message sent to the printer:
            <01> Marks the start of the message represented as hex 0x01 or 1
            <len> Declare length by summing <01> (1) + <SEQ> (1) + <CMD> (1) + <data> (upto 210bytes)
            <seq> Some sort of unique index to identify a wrapped messages if you have plenty of them to send.
            <cmd> The Command to ask the printer
            <data> The supporting data of a command
            <05> Preamble
            <bcc> Checksum value
            <03> Terminates the message
        """
        byte_data = bytes(data, "utf-8")
        # 4 represents the bytes of the sum of <SEQ> + <LEN> + <CMD> + <05>. Each is 1 byte which adds up to 4
        # According to the protocol, After determing the length of <SEQ> + <LEN> + <CMD> + <05> + <DATA>, you
        # need to sum the result with 0x20
        wlen = MARKER_SPACE + 4 + len(byte_data)
        seq = MARKER_SPACE + self.sequence_number
        msg = [
            FP_PREAMBLE,
            wlen,
            seq,
            cmd
        ]
        self.sequence_number += 1 if self.sequence_number <= 9 else 0
        # Data is optional depending on the command, check if the bytes are null before appending
        if len(byte_data) > 0:
            msg.extend(byte_data)
        msg.append(FP_POSTAMBLE)
        msg.extend(self.calculate_bcc(msg[1:len(msg)])) # Exclude Preamble when calculating BCC
        msg.append(FP_TERMINATOR)
        return msg


