class MemberRefused(Exception):
    """A hook of an extension refuses the member it is given, which breaks one of that extension's invariants. The unit of
    work is rolled back and the command answers a parameter value range error."""
