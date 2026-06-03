class CrisisLensError(Exception):
    pass


class IngestionError(CrisisLensError):
    pass


class ClassificationError(CrisisLensError):
    pass


class ExtractionError(CrisisLensError):
    pass


class ReasoningError(CrisisLensError):
    pass


class StorageError(CrisisLensError):
    pass
