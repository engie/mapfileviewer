class ParsingError( Exception ):
    pass

class LineStripper:
    def __init__(self, iter):
        self.iter = iter
    
    def __iter__(self):
        return self

    def next(self):
        while True:
            a = self.iter.next().rstrip( "\r\n" )
            if a != "":
                return a

    def eatLines(self, n):
        for i in range(n):
            self.next()

class Function:
    def __init__(self, name, location):
        self.name = name
        self.location = location

    def __str__(self):
        return "%s @ %s" % (self.name, hex(self.location))

class Memory:
    def __init__(self, name, origin, length, used, unused, attr):
        self.name = name
        self.origin = origin
        self.length = length
        self.used = used
        
        if used + unused != length:
            raise ParsingError( "Size of memories doesn't add up!" )

        self.attr = attr

    def __str__(self):
        return "%s @ %s to %s, using %s - %s" % (self.name,
                                                 hex(self.origin),
                                                 hex(self.origin + self.length),
                                                 hex(self.used),
                                                 self.attr)

class Map:
    def __init__(self):
        self.output_file = None
        self.timestamp = None
        self.entry_point = None
        self.memories = []
        self.sections = []
        self.symbols = {}

    def __str__(self):
        s  = "Output File: " + str( self.output_file ) + "\n"
        s += "Timestamp: " + str( self.timestamp ) + "\n"
        s += "Entry point: " + str( self.entry_point ) + "\n"
        s += "Memories:\n" + "\n".join( [str( m ) for m in self.memories ] ) + "\n"
        s += "Sections:\n" + "\n".join( [str( m ) for m in self.sections ] ) + "\n"
        s += "Symbols:\n" + "\n".join( [str( v ) for v in self.symbols.itervalues() ] ) + "\n"
        return s

    def addMemory(self, memory):
        self.memories.append( memory )

    def addSection(self, section):
        """
        Store the section and register it with the appropriate memory
        """
        self.sections.append( section )
        #TODO : Find the appropriate memory and add it to that

    def addSymbol(self, symbol):
        """
        Store a symbol and register it with the appropriate section
        """
        if not symbol.name in self.symbols:
            self.symbols[symbol.name] = symbol
        #TODO : Register with the appropriate section
