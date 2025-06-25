# Register this blueprint by adding the following line of code
# to your entry point file.
# app.register_functions(blueprint)
#
# Please refer to https://aka.ms/azure-functions-python-blueprints
# pylint: disable=unused-argument
import azure.functions as func
import logging
from Postgres.postgres import (
    create_postgres_connection,
)
from Postgres.session_ending import (
    get_sessions_to_finish,
    finish_session,
)
from .insights import get_insights

blueprint = func.Blueprint()


@blueprint.timer_trigger(
    schedule="0 0 5 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def finish_sessions(
    myTimer: func.TimerRequest,
) -> None:

    logging.info("Python timer trigger function started")
    with create_postgres_connection() as conn:  # pylint: disable=E1129
        logging.info("Connected to Postgres")
        # Get the sessions that need to be finished
        sessions_to_finish = get_sessions_to_finish(conn)
        logging.info("Sessions to finish: %s", len(sessions_to_finish))
        for s in sessions_to_finish:
            analysis = get_insights(s)
            logging.info("Analysis of session %s: %s", s[0], analysis)
        
            finish_session(conn, s)
            logging.info("Session %s finished", s[0])
