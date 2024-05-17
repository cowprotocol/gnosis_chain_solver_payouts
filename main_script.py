import sys
import csv
from constants import (
    PERFORMANCE_REWARDS_BUDGET,
    CONSISTENCY_REWARDS_BUDGET,
    QUOTE_REWARDS_BUDGET,
    SOLVER_ADDRESSES,
    GNOSIS_SAFE,
)
from gnosis_scan_api import get_block_range
from execute_sql_queries import (
    get_auction_range,
    compute_solver_rewards,
    compute_quote_rewards,
    execute_participation_rewards_helper,
)


def main() -> None:
    # parsing command-line arguments
    if len(sys.argv) < 4:
        print("Wrong usage. Need at least three entries: YEAR MONTH DAY")
        exit()
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    ignore_gnosis_transfers = False
    if len(sys.argv) == 5:
        if sys.argv[4] == "ignore_gnosis_transfers":
            ignore_gnosis_transfers = True
            print("Gnosis Solvers transfers will be removed from the final .csv.")

    # preprocessing
    start_block, end_block = get_block_range(year, month, day)
    print(
        "\nAccounting period from block "
        + str(start_block)
        + " to block "
        + str(end_block)
        + "."
    )

    # compute prod and barn auction range
    (
        prod_start_auction_str,
        prod_end_auction_str,
        barn_start_auction_str,
        barn_end_auction_str,
    ) = get_auction_range(str(start_block), str(end_block))

    print(
        "Production auctions from "
        + prod_start_auction_str
        + " until "
        + prod_end_auction_str
        + ".\n"
        + "Barn auctions from "
        + barn_start_auction_str
        + " until "
        + barn_end_auction_str
        + ".\n"
    )

    final_consistency_rewards_budget = CONSISTENCY_REWARDS_BUDGET
    # computing solver performance rewards
    performance_rewards_per_solver = {}
    performance_spend = 0
    performance_rewards = compute_solver_rewards(str(start_block), str(end_block))
    for index, row in performance_rewards.iterrows():
        amount = int(row["primary_reward_xdai"])
        if amount > 0:
            performance_spend += amount
        performance_rewards_per_solver[row["solver"]] = amount

    for solver in performance_rewards_per_solver:
        if performance_rewards_per_solver[solver] > 0:
            performance_rewards_per_solver[solver] = (
                performance_rewards_per_solver[solver]
                * PERFORMANCE_REWARDS_BUDGET
                / performance_spend
            )
        else:
            final_consistency_rewards_budget += (-1) * performance_rewards_per_solver[
                solver
            ]

    # computing quote rewards
    quote_rewards_per_solver = {}
    total_quotes = 0
    quote_rewards = compute_quote_rewards(str(start_block), str(end_block))
    for index, row in quote_rewards.iterrows():
        number = int(row["num_quotes"])
        total_quotes += number
        quote_rewards_per_solver[row["solver"]] = number

    for solver in quote_rewards_per_solver:
        quote_rewards_per_solver[solver] = (
            quote_rewards_per_solver[solver] * QUOTE_REWARDS_BUDGET / total_quotes
        )

    # computing consistency rewards
    participation_data = execute_participation_rewards_helper(
        str(start_block), str(end_block)
    )
    participation_per_solver = {}
    total_participation_tokens = 0
    for index, row in participation_data.iterrows():
        ll = list(row["competition_info"])
        num_solutions = len(ll)
        for i in range(num_solutions):
            if i >= num_solutions - 3:
                token_delta = 1.2
            else:
                token_delta = 1.0
            solver = ll[i]["solverAddress"]
            if solver in participation_per_solver:
                participation_per_solver[solver] += token_delta
            else:
                participation_per_solver[solver] = token_delta
            total_participation_tokens += token_delta

    for solver in participation_per_solver:
        participation_per_solver[solver] = (
            participation_per_solver[solver]
            * final_consistency_rewards_budget
            / total_participation_tokens
        )

    # putting everything together
    ovedrafts = {}
    final_rewards_per_solver = {
        solver: [0, 0, 0, 0]
        for solver in performance_rewards_per_solver
        | quote_rewards_per_solver
        | participation_per_solver
    }
    for solver in performance_rewards_per_solver:
        final_rewards_per_solver[solver][0] = performance_rewards_per_solver[solver]
        final_rewards_per_solver[solver][3] += performance_rewards_per_solver[solver]
    for solver in quote_rewards_per_solver:
        final_rewards_per_solver[solver][1] = quote_rewards_per_solver[solver]
        final_rewards_per_solver[solver][3] += quote_rewards_per_solver[solver]
    for solver in participation_per_solver:
        final_rewards_per_solver[solver][2] = participation_per_solver[solver]
        final_rewards_per_solver[solver][3] += participation_per_solver[solver]

    for solver in final_rewards_per_solver:
        if final_rewards_per_solver[solver][3] < 0:
            ovedrafts[solver] = round(final_rewards_per_solver[solver][3] / 10**18, 3)

    print("Summary of results (performance, quoting, consistency, total):\n")

    total_xdai_needed = 0
    processed_solver_addresses = {}
    for s in SOLVER_ADDRESSES:
        solver = s.lower()
        processed_solver_addresses[solver] = SOLVER_ADDRESSES[s]
        processed_solver_addresses[solver][1] = processed_solver_addresses[solver][
            1
        ].lower()
    for solver in final_rewards_per_solver:
        name = processed_solver_addresses[solver][0]
        reward = final_rewards_per_solver[solver][3] / 10**18
        total_xdai_needed += reward
        print(
            name
            + ":\t["
            + str(round(final_rewards_per_solver[solver][0] / 10**18, 3))
            + ", "
            + str(round(final_rewards_per_solver[solver][1] / 10**18, 3))
            + ", "
            + str(round(final_rewards_per_solver[solver][2] / 10**18, 3))
            + ", "
            + str(round(final_rewards_per_solver[solver][3] / 10**18, 3))
            + "]."
        )
    print("\nTotal xDAI needed for the payouts: " + str(total_xdai_needed))

    # generate csv with transfers
    with open(
        f"./out/transfers-start-{year}-{month}-{day}.csv", "w", newline=""
    ) as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",")
        csvwriter.writerow(["token_type", "token_address", "receiver", "amount"])
        for solver in final_rewards_per_solver:
            if solver in ovedrafts:
                continue
            target = processed_solver_addresses[solver][1]
            if target == GNOSIS_SAFE.lower() and ignore_gnosis_transfers:
                continue
            reward = final_rewards_per_solver[solver][3] / 10**18
            csvwriter.writerow(["native", "", target, reward])

    if ovedrafts:
        print()
        print("Ovedrafts summary.")
        for solver in ovedrafts:
            print(
                "Overdraft for "
                + processed_solver_addresses[solver][0]
                + ":\t"
                + str(ovedrafts[solver])
            )


if __name__ == "__main__":
    main()
