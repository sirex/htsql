#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# Authors: Clark C. Evans <cce@clarkevans.com>,
#          Kirill Simonov <xi@resolvent.net>
#


"""
:mod:`htsql_mysql.tr.dump`
==========================

This module adapts the SQL serializer for MySQL.
"""


from htsql.adapter import adapts
from htsql.domain import (BooleanDomain, NumberDomain, IntegerDomain,
                          StringDomain)
from htsql.tr.dump import (FormatName, FormatLiteral,
                           DumpBoolean, DumpDecimal, DumpFloat, DumpDate,
                           DumpToDomain, DumpToInteger, DumpToFloat,
                           DumpToDecimal, DumpToString, DumpIsTotallyEqual)
from htsql.tr.fn.dump import (DumpLength, DumpSubstring, DumpTrim,
                              DumpDateIncrement, DumpDateDecrement,
                              DumpDateDifference, DumpConcatenate, DumpLike,
                              DumpMakeDate, DumpSum)


class MySQLFormatName(FormatName):

    def __call__(self):
        self.stream.write("`%s`" % self.value.replace("`", "``"))


class MySQLFormatLiteral(FormatLiteral):

    def __call__(self):
        self.stream.write("'%s'" % self.value.replace("\\", r"\\")
                                             .replace("'", r"\'")
                                             .replace("\n", r"\n")
                                             .replace("\r", r"\r"))


class MySQLDumpFloat(DumpFloat):

    def __call__(self):
        assert str(self.value) not in ['inf', '-inf', 'nan']
        value = repr(self.value)
        if 'e' not in value and 'E' not in value:
            value = value+'e0'
        self.write(value)


class MySQLDumpDecimal(DumpDecimal):

    def __call__(self):
        assert self.value.is_finite()
        value = str(self.value)
        if 'E' in value:
            value = "CAST(%s AS DECIMAL(65,30))" % value
        elif '.' not in value:
            value = "CAST(%s AS DECIMAL(65))" % value
        self.write(value)


class MySQLDumpDate(DumpDate):

    def __call__(self):
        self.format("DATE({value:literal})", value=str(self.value))


class MySQLDumpToInteger(DumpToInteger):

    def __call__(self):
        self.format("CAST({base} AS SIGNED INTEGER)", base=self.base)


class MySQLDumpToFloat(DumpToFloat):

    def __call__(self):
        if isinstance(self.base.domain, NumberDomain):
            self.format("(1E0 * {base})", base=self.base)
        else:
            self.format("(1E0 * CAST({base} AS DECIMAL(65,30)))",
                        base=self.base)


class MySQLDumpToDecimal(DumpToDecimal):

    def __call__(self):
        self.format("CAST({base} AS DECIMAL(65,30))", base=self.base)


class MySQLDumpToString(DumpToString):

    def __call__(self):
        self.format("CAST({base} AS CHAR)", base=self.base)


class MySQLDumpBooleanToString(DumpToDomain):

    adapts(BooleanDomain, StringDomain)

    def __call__(self):
        if self.base.is_nullable:
            self.format("(CASE WHEN {base} THEN 'true'"
                        " WHEN NOT {base} THEN 'false' END)",
                        base=self.base)
        else:
            self.format("(CASE WHEN {base} THEN 'true' ELSE 'false' END)",
                        base=self.base)


class MySQLDumpIsTotallyEqual(DumpIsTotallyEqual):

    def __call__(self):
        if self.signature.polarity == +1:
            self.format("({lop} <=> {rop})", self.arguments)
        if self.signature.polarity == -1:
            self.format("(NOT ({lop} <=> {rop}))", self.arguments)


class MySQLDumpDateIncrement(DumpDateIncrement):

    template = "ADDDATE({lop}, {rop})"


class MySQLDumpDateDecrement(DumpDateDecrement):

    template = "SUBDATE({lop}, {rop})"


class MySQLDumpDateDifference(DumpDateDifference):

    template = "DATEDIFF({lop}, {rop})"


class MySQLDumpConcatenate(DumpConcatenate):

    template = "CONCAT({lop}, {rop})"


class MySQLDumpLike(DumpLike):

    def __call__(self):
        self.format("({lop} {polarity:not}LIKE {rop})",
                    self.arguments, self.signature)


class MySQLDumpMakeDate(DumpMakeDate):

    template = ("ADDDATE(ADDDATE(ADDDATE(DATE('2001-01-01'),"
                " INTERVAL ({year} - 2001) YEAR),"
                " INTERVAL ({month} - 1) MONTH),"
                " INTERVAL ({day} - 1) DAY)")


class MySQLDumpSum(DumpSum):

    def __call__(self):
        if isinstance(self.phrase.domain, IntegerDomain):
            self.format("CAST(SUM({op}) AS SIGNED INTEGER)", self.arguments)
        else:
            self.format("SUM({op})", self.arguments)

