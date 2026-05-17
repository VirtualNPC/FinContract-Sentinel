class AuditError(Exception):
    pass


class ParseError(AuditError):
    pass


class RuleError(AuditError):
    pass


class ToolError(AuditError):
    pass
