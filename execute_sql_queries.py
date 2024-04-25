import os
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from constants import (
    UPPER_PERFORMANCE_REWARD_CAP,
    LOWER_PERFORMANCE_REWARD_CAP,
)
from dotenv import load_dotenv

def get_auction_range(start_block_str, end_block_str):

    load_dotenv()
    BARN_DB_URL = os.environ["BARN_DB_URL"]
    PROD_DB_URL = os.environ["PROD_DB_URL"]
    prod_connection = create_engine(f"postgresql+psycopg2://{PROD_DB_URL}")
    barn_connection = create_engine(f"postgresql+psycopg2://{BARN_DB_URL}")

    quote_file = (
        open("auction_range.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
    )

    # Here, we use the convention that we run the prod query for the first connection
    # and the barn query to all other connections
    res = pd.read_sql(quote_file, prod_connection)
    prod_start_auction_str = str(res["start_auction"].iloc[0])
    prod_end_auction_str = str(res["end_auction"].iloc[0])
    res = pd.read_sql(quote_file, barn_connection)
    barn_start_auction_str = str(res["start_auction"].iloc[0])
    barn_end_auction_str = str(res["end_auction"].iloc[0])
    return (
        prod_start_auction_str,
        prod_end_auction_str,
        barn_start_auction_str,
        barn_end_auction_str,
    )


def compute_quote_rewards(start_block_str, end_block_str):
    
    load_dotenv()
    BARN_DB_URL = os.environ["BARN_DB_URL"]
    PROD_DB_URL = os.environ["PROD_DB_URL"]
    prod_connection = create_engine(f"postgresql+psycopg2://{PROD_DB_URL}")
    barn_connection = create_engine(f"postgresql+psycopg2://{BARN_DB_URL}")

    quote_file = (
        open("quote_rewards.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
    )
    results = []

    # Here, we use the convention that we run the prod query for the first connection
    # and the barn query to all other connections
    results.append(pd.read_sql(quote_file, prod_connection))
    results.append(pd.read_sql(quote_file, barn_connection))
    return pd.concat(results)


def compute_solver_rewards(start_block_str, end_block_str):

    load_dotenv()
    BARN_DB_URL = os.environ["BARN_DB_URL"]
    PROD_DB_URL = os.environ["PROD_DB_URL"]
    prod_connection = create_engine(f"postgresql+psycopg2://{PROD_DB_URL}")
    barn_connection = create_engine(f"postgresql+psycopg2://{BARN_DB_URL}")

    query_file = (
        open("solver_rewards.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
        .replace("{{EPSILON_LOWER}}", str(LOWER_PERFORMANCE_REWARD_CAP))
        .replace("{{EPSILON_UPPER}}", str(UPPER_PERFORMANCE_REWARD_CAP))
    )
    results = []

    # Here, we use the convention that we run the prod query for the first connection
    # and the barn query to all other connections
    results.append(pd.read_sql(query_file, prod_connection))
    results.append(pd.read_sql(query_file, barn_connection))
    return pd.concat(results)



def execute_participation_rewards_helper(start_block_str, end_block_str):

    load_dotenv()
    BARN_DB_URL = os.environ["BARN_DB_URL"]
    PROD_DB_URL = os.environ["PROD_DB_URL"]
    prod_connection = create_engine(f"postgresql+psycopg2://{PROD_DB_URL}")
    barn_connection = create_engine(f"postgresql+psycopg2://{BARN_DB_URL}")
    query_file = (
        open("successful_auction_ids.sql", "r")
        .read()
        .replace("{{start_block}}", start_block_str)
        .replace("{{end_block}}", end_block_str)
    )
    prod_res = pd.read_sql(query_file, prod_connection)
    barn_res = pd.read_sql(query_file, barn_connection)
    prod_auction_list =[]
    barn_auction_list = []
    for index, row in prod_res.iterrows():
        prod_auction_list.append(str(row["auction_id"]))
    for index, row in barn_res.iterrows():
        barn_auction_list.append(str(row["auction_id"]))

    prod_auction_list_str = str(prod_auction_list).replace("[","(").replace("]", ")")
    barn_auction_list_str = str(barn_auction_list).replace("[","(").replace("]", ")")
    prod_query_file = (
        open("participation_rewards_aux.sql", "r")
        .read()
        .replace("{{auction_list}}", prod_auction_list_str)
    )
    barn_query_file = (
        open("participation_rewards_aux.sql", "r")
        .read()
        .replace("{{auction_list}}", barn_auction_list_str)
    )
    prod_res = pd.read_sql(prod_query_file, prod_connection)
    barn_res = pd.read_sql(barn_query_file, barn_connection)
    results = [prod_res, barn_res]
    return pd.concat(results)



