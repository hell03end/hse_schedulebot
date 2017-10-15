def register(dispatcher: object) -> None:
    from .week_schedule import register as week_schedule_reg
    from .eve_schedule import register as eve_schedule_reg

    week_schedule_reg(dispatcher)
    eve_schedule_reg(dispatcher)
