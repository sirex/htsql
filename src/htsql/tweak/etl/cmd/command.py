#
# Copyright (c) 2006-2012, Prometheus Research, LLC
#


from ....core.util import listof, tupleof, maybe
from ....core.cmd.command import Command
from ....core.entity import TableEntity



class ETLCmd(Command):

    def __init__(self, feed, mark):
        super(ETLCmd, self).__init__(mark)
        assert isinstance(feed, Command)
        self.feed = feed


class InsertCmd(ETLCmd):
    pass


class MergeCmd(ETLCmd):
    pass


class UpdateCmd(ETLCmd):
    pass


class DeleteCmd(ETLCmd):
    pass


class TruncateCmd(Command):

    def __init__(self, table, mark):
        super(TruncateCmd, self).__init__(mark)
        assert isinstance(table, TableEntity)
        self.table = table


class DoCmd(Command):

    def __init__(self, blocks, mark):
        super(DoCmd, self).__init__(mark)
        assert isinstance(blocks, listof(tupleof(maybe(unicode), Command)))
        self.blocks = blocks

