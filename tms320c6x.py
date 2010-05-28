from map import Map, ParsingError, LineStripper, Function, Memory
import datetime
import re

#TODO : Seperate out this parsing stuff from the main class to make loading the class file faster
HEADER_1 = "******************************************************************************"
HEADER_2 = "               TMS320C6x Linker PC v6.1.11                     "
HEADER_3 = "******************************************************************************"
#Matches: >> Linked Fri May 28 11:04:31 2010
TIMESTAMP = re.compile( "^>> Linked (.*)$" )
TIMESTAMP_FORMAT = "%a %B %d %H:%M:%S %Y"
#Matches: OUTPUT FILE NAME:   <bootloader.out>
OUTPUT_FILE = re.compile( "^OUTPUT FILE NAME: *<(.*)>$" )
#Matches: ENTRY POINT SYMBOL: "_c_int00"  address: c0715f00
ENTRY_POINT = re.compile( "^ENTRY POINT SYMBOL: \"(.+)\" +address: ([0-9a-f]{8})$" )
MEMORIES_START = "----------------------  --------  ---------  --------  --------  ----  --------"
#Matches:   IRAM                  11820000   00020000  00010a4c  0000f5b4  RWIX
MEMORIES = re.compile( "^ *(\S*) +([0-9a-f]{8}) +([0-9a-f]{8}) +([0-9a-f]{8}) +([0-9a-f]{8}) +([RWIX]{4})$" )
SECTIONS_START = "--------  ----  ----------  ----------   ----------------"
#Matches: .vers      0    00000000    00000044     COPY SECTION
SECTION_DEF = re.compile( "^(\S*) +([0-9a-f]) +([0-9a-f]{8}) +([0-9a-f]{8}) *(.*)$" )
#Matches:                   00000000    00000044     BootloaderHWcfg.obj (.vers)
OBJECT_DEF = re.compile( "^ *([0-9a-f]{8}) +([0-9a-f]{8}) +(\S+) \((.*)\)$" )
#Matches:                  11830254    00000004     basicHubFunctionality.lib : syscfg.obj (.pinit)
OBJECT_IN_LIBRARY_DEF = re.compile( "^ *([0-9a-f]{8}) +([0-9a-f]{8}) +(\S+) : (\S+) \((.*)\)$" )

class tms3206cx( Map ):
    def __init__(self, lines ):
        Map.__init__( self )
        self.parse( lines )

    def parse(self, lines ):
        self.checkHeader( lines )
        self.getTimestamp( lines )
        self.getOutputFileName( lines )
        self.getEntryPoint( lines )
        lines.eatLines( 2 )
        self.getMemories( lines )

    def getMemories( self, lines ):
        if lines.next() != MEMORIES_START:
            raise ParsingError( "Header of memories table not found" )

        while True:
            m = MEMORIES.match( lines.next() )
            if m == None:
                return
            mem = Memory( m.group(1),
                          int(m.group(2), 16),
                          int(m.group(3), 16),
                          int(m.group(4), 16),
                          int(m.group(5), 16),
                          m.group(6) )
            self.addMemory( mem )

    def getEntryPoint( self, lines ):
        m = ENTRY_POINT.match( lines.next() )
        if m == None:
            raise ParsingError( "Entry point not found" )
        #TODO : Can't really add the symbol until the sections are loaded
        return
        self.entry_point = Function( m.group(1), int( m.group(2), 16 ) )
        self.addSymbol( self.entry_point )

    def getOutputFileName( self, lines ):
        m = OUTPUT_FILE.match( lines.next() )
        if m == None:
            raise ParsingError( "Output filename not found" )
        self.output_file = m.group(1)
    
    def getTimestamp(self, lines):
        m = TIMESTAMP.match( lines.next() )
        if m == None:
            raise ParsingError( "Timestamp not found" )
        timestring = m.group(1)
        timestamp = datetime.datetime.strptime( timestring, TIMESTAMP_FORMAT )
        self.timestamp = timestamp

    def checkHeader(self, lines):
        if lines.next().startswith( HEADER_1 ) and \
           lines.next().startswith( HEADER_2 ) and \
           lines.next().startswith( HEADER_3 ):
            return

        raise ParsingError( "Header not found" )
        
if __name__ == "__main__":
    import sys
    t = tms3206cx( LineStripper( open(sys.argv[1], "rt") ) )
    print t
