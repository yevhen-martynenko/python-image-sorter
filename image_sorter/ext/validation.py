from image_sorter.ext.loggers import Logger


def validate_args(args):
    logger = Logger()

    if args.help or args.version:
        return

    if not args.input_dir:
        message: str = '"input_dir" is required'
    elif not args.output_dirs:
        message: str = '"output_dirs" is required'
    elif not isinstance(args.copy_mode, bool):
        message: str = '"copy_mode" must be a boolean'
    elif not isinstance(args.safe_delete, bool):
        message: str = '"safe_delete" must be a boolean'
    elif not isinstance(args.tree, bool):
        message: str = '"tree" must be a boolean'
    elif not isinstance(args.auto_rename, int):
        message: str = '"auto_rename" must be an integer or None'
    elif not isinstance(args.theme, str):
        message: str = '"theme" must be a string'
    else:
        return

    logger.log_message(message=f"ValidationError: {message}", level="error")
    raise ValidationError(message)


class ValidationError(ValueError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"ValidationError: {self.message}"
