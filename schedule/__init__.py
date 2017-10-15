def register(dispatcher: object) -> None:
    from schedule.week_schedule import register as week_schedule_reg
    from schedule.eve_schedule import register as eve_schedule_reg

    week_schedule_reg(dispatcher)
    eve_schedule_reg(dispatcher)
