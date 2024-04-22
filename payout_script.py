from orderbook_api import get_solver_competition_data
import sys
from time import sleep
from constants import (
    UPPER_PERFORMANCE_REWARD_CAP,
    LOWER_PERFORMANCE_REWARD_CAP,
    PERFORMANCE_REWARDS_BUDGET,
    CONSISTENCY_REWARDS_BUDGET,
)

results_per_auction = []


def compute_auction_rewards(auction_id, environment):
    """
    This function computes the performance reward associated
    with an auction, and also collects all necessary data for
    computing participation rewards
    """
    global result
    data = get_solver_competition_data(auction_id, environment)

    if data is None:
        results_per_auction.append(
            {
                "auction_id": auction_id,
                "environment": environment,
                "tx_hash": None,
                "status": False,
                "performance_reward": 0,
                "winner": None,
                "participation": None,
            }
        )
        # case where auction was trivial or non existent
        return

    failed = data["transactionHash"] is None
    winning_solution = data["solutions"][-1]
    winning_score = int(winning_solution["score"])
    winning_solver = winning_solution["solverAddress"]
    reference_score = 0
    participating_solvers = []
    num_solutions = len(data["solutions"])
    if num_solutions > 1:
        reference_score = int(data["solutions"][-2]["score"])
    if failed:
        performance_reward = -reference_score
    else:
        performance_reward = winning_score - reference_score
        # participation rewards are only considered for auctions that led to settlements onchain
        # the participation_solvers list contains solutions in decreasing order of ranking
        for i in range(num_solutions - 1, -1, -1):
            s = data["solutions"][i]
            solver = s["solverAddress"]
            participating_solvers.append(solver)

    if performance_reward > UPPER_PERFORMANCE_REWARD_CAP:
        performance_reward = UPPER_PERFORMANCE_REWARD_CAP
    elif performance_reward < LOWER_PERFORMANCE_REWARD_CAP:
        performance_reward = LOWER_PERFORMANCE_REWARD_CAP
    results_per_auction.append(
        {
            "auction_id": auction_id,
            "environment": environment,
            "tx_hash": data["transactionHash"],
            "status": True,
            "performance_reward": performance_reward,
            "winner": winning_solver,
            "participation": participating_solvers,
        }
    )


def compute_payouts(
    prod_start_auction, prod_end_auction, barn_start_auction, barn_end_auction
) -> any:
    """
    This is the main function that computes solver rewards.
    Note that that this payout ignores all network fee reimursemenets,
    and it also ignores all quote rewards.
    These should be handled in a separate script, if needed.
    """

    perfomance_rewards = {}
    consistency_rewards = {}
    global results_per_auction
    results_per_auction = []

    # in the following while loop we go over all auctions and compute associated rewards,
    # which we store in the results list.
    # We have one loop for prod and one loop for barn.

    # prod looop
    auction_id = prod_start_auction
    end_auction = prod_end_auction
    while auction_id <= end_auction:
        compute_auction_rewards(auction_id, "prod")
        auction_id += 1

    # barn loop
    auction_id = barn_start_auction
    end_auction = barn_end_auction
    while auction_id <= end_auction:
        compute_auction_rewards(auction_id, "barn")
        auction_id += 1

    # at this point, we have all relevant data collected in the results_per_auction list
    for res in results_per_auction:
        if not res["status"]:
            continue

        solver = res["winner"]
        reward = res["performance_reward"]
        if solver not in perfomance_rewards:
            perfomance_rewards[solver] = reward
        else:
            perfomance_rewards[solver] += reward

        participation = res["participation"]
        num_participants = len(participation)
        for i in range(0, min(3, num_participants)):
            solver = participation[i]
            if solver not in consistency_rewards:
                consistency_rewards[solver] = 1.2
            else:
                consistency_rewards[solver] += 1.2
        for i in range(3, num_participants):
            solver = participation[i]
            if solver not in consistency_rewards:
                consistency_rewards[solver] = 1
            else:
                consistency_rewards[solver] += 1

    total_performance_rewards = 0
    for s in perfomance_rewards:
        total_performance_rewards += perfomance_rewards[s]
    # we now scale the performance rewards to fit the budget
    for s in perfomance_rewards:
        perfomance_rewards[s] = (
            perfomance_rewards[s] * PERFORMANCE_REWARDS_BUDGET / total_performance_rewards
        )

    total_participation = 0
    for s in consistency_rewards:
        total_participation += consistency_rewards[s]
    for s in consistency_rewards:
        consistency_rewards[s] = (
            consistency_rewards[s] * CONSISTENCY_REWARDS_BUDGET / total_participation
        )

    total_rewards = {}
    for s in perfomance_rewards:
        total_rewards[s] = perfomance_rewards[s] / 10**18
    for s in consistency_rewards:
        if s in total_rewards:
            total_rewards[s] += consistency_rewards[s] / 10**18
        else:
            total_rewards[s] = consistency_rewards[s] / 10**18
    return total_rewards


def main() -> None:
    results = compute_payouts(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
    print(results)



if __name__ == "__main__":
    main()
