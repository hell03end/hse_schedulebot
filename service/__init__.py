def register(dispatcher: object) -> None:
    from service.common_handlers import register as common_handlers_reg
    from service.mailing import register as mailing_reg

    common_handlers_reg(dispatcher)
    mailing_reg(dispatcher)
