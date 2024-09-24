from prefect import flow, task, get_run_logger
from datetime import datetime, timedelta

from slack_messages.send_message import SlackClient
from src.main_script import main

#@task
def calculate_solver_payouts():
    #logger = get_run_logger()

    one_week_ago = datetime.now() - timedelta(weeks=1)
    year = one_week_ago.year
    month = one_week_ago.month
    day = one_week_ago.day
    #logger.info(f"Running pipeline with args {year} {month} {day}")
    payouts_file, message = main(year, month, day, ignore_gnosis_transfers=True)
    #logger.info(f"Calculated payouts:\n{message}:")
    return payouts_file, message



@task
def send_results_to_slack(payouts_file, message):
    #logger = get_run_logger()
    Slack = SlackClient()
    #logger.info("Sending summary of results to slack")
    Slack.send_message(message)
    #logger.info("Sending results to slack as .csv file")
    Slack.send_csv(payouts_file)



@flow(retries=3, retry_delay_seconds=60)
def solver_payouts():
    payouts_file, message = calculate_solver_payouts()
    send_results_to_slack(payouts_file, message)


if __name__ == "__main__":
    payouts_file, message = calculate_solver_payouts()
    print("*******")
    print(message)
    print("*******")
    """
    solver_payouts.serve(
        name="gnosis-chain-solver-payouts",
        cron="0 16 * * 4", # Every thursday at 4 pm
        tags=["solver", "slack"],
        description="Compute solver rewards of the solver competition of CoW Protocol on Gnosis Chain and send the results on slack.",
        version="0.0.1",
        )
    """
