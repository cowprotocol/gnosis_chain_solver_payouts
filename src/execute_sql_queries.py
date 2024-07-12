import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from src.constants import (
    UPPER_PERFORMANCE_REWARD_CAP,
    LOWER_PERFORMANCE_REWARD_CAP,
)


def create_db_connections():
    """Helper function that creates the connections to the prod and barn db."""

    load_dotenv()
    barn_db_url = os.environ["BARN_DB_URL"]
    prod_db_url = os.environ["PROD_DB_URL"]
    barn_connection = create_engine(f"postgresql+psycopg2://{barn_db_url}")
    prod_connection = create_engine(f"postgresql+psycopg2://{prod_db_url}")

    return prod_connection, barn_connection


def get_auction_range(start_block_str, end_block_str):
    """
    Executes a query that returns the auction range between
    a start and an end block for prod and barn.
    """

    prod_connection, barn_connection = create_db_connections()

    query_file = (
        open("src/queries/auction_range.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
    )

    res = pd.read_sql(query_file, prod_connection)
    prod_start_auction_str = str(res["start_auction"].iloc[0])
    prod_end_auction_str = str(res["end_auction"].iloc[0])
    res = pd.read_sql(query_file, barn_connection)
    barn_start_auction_str = str(res["start_auction"].iloc[0])
    barn_end_auction_str = str(res["end_auction"].iloc[0])

    return (
        prod_start_auction_str,
        prod_end_auction_str,
        barn_start_auction_str,
        barn_end_auction_str,
    )


def compute_quote_rewards(start_block_str, end_block_str):
    """
    Executes a query that computes the number of quotes that should
    be rewarded, for each solver.
    """

    prod_connection, barn_connection = create_db_connections()

    query_file = (
        open("src/queries/quote_rewards.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
    )
    results = []

    results.append(pd.read_sql(query_file, prod_connection))
    results.append(pd.read_sql(query_file, barn_connection))

    return pd.concat(results)


def compute_solver_rewards(start_block_str, end_block_str):
    """Executes the main solver rewards query."""

    prod_connection, barn_connection = create_db_connections()

    query_file = (
        open("src/queries/solver_rewards.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
        .replace("{{EPSILON_LOWER}}", str(LOWER_PERFORMANCE_REWARD_CAP))
        .replace("{{EPSILON_UPPER}}", str(UPPER_PERFORMANCE_REWARD_CAP))
    )
    results = []

    results.append(pd.read_sql(query_file, prod_connection))
    results.append(pd.read_sql(query_file, barn_connection))

    return pd.concat(results)


def execute_participation_rewards_helper(start_block_str, end_block_str):
    """
    Executes a helper query that recovers competition data, in order to be able
    to find the ranking and give weighted participation rewards.
    """

    prod_connection, barn_connection = create_db_connections()

    query_file = (
        open("src/queries/successful_auction_ids.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
    )
    prod_res = pd.read_sql(query_file, prod_connection)
    barn_res = pd.read_sql(query_file, barn_connection)

    prod_auction_list = []
    barn_auction_list = []
    for index, row in prod_res.iterrows():
        prod_auction_list.append(str(row["auction_id"]))
    for index, row in barn_res.iterrows():
        barn_auction_list.append(str(row["auction_id"]))

    prod_auction_list_str = str(prod_auction_list).replace("[", "(").replace("]", ")")
    barn_auction_list_str = str(barn_auction_list).replace("[", "(").replace("]", ")")
    prod_query_file = (
        open("src/queries/participation_rewards_aux.sql", "r")
        .read()
        .replace("{{auction_list}}", prod_auction_list_str)
    )
    barn_query_file = (
        open("src/queries/participation_rewards_aux.sql", "r")
        .read()
        .replace("{{auction_list}}", barn_auction_list_str)
    )
    results = []
    if len(prod_auction_list) > 0:
        results.append(pd.read_sql(prod_query_file, prod_connection))
    if len(barn_auction_list) > 0:
        results.append(pd.read_sql(barn_query_file, barn_connection))

    return pd.concat(results)
