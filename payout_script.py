from orderbook_api import get_solver_competition_data
import sys
from time import sleep
from constants import UPPER_PERFORMANCE_REWARD_CAP, LOWER_PERFORMANCE_REWARD_CAP, BUDGET

results_per_auction = []


def compute_auction_rewards(auction_id, environment):
    """
    This function computes the rewards associated
    with an auction
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

    is_revert = data["transactionHash"] is None
    winning_solution = data["solutions"][-1]
    winning_score = int(winning_solution["score"])
    winning_solver = environment + "-" + winning_solution["solver"]
    reference_score = 0
    participating_non_winning_solvers = []
    num_solutions = len(data["solutions"])
    for i in range(num_solutions - 1, -1, -1):
        s = data["solutions"][i]
        name = s["solver"]
        if name not in participating_non_winning_solvers:
            participating_non_winning_solvers.append(name)
    if num_solutions > 1:
        reference_score = int(data["solutions"][-2]["score"])
    if is_revert:
        performance_reward = -reference_score
    else:
        performance_reward = winning_score - reference_score
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
            "participation": participating_non_winning_solvers,
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
        participation = res["participation"]
        if solver not in perfomance_rewards:
            perfomance_rewards[solver] = reward
        else:
            perfomance_rewards[solver] += reward
        for l in participation:
            if l not in consistency_rewards:
                consistency_rewards[l] = 1
            else:
                consistency_rewards[l] += 1

    total_performance_rewards = 0
    for s in perfomance_rewards:
        total_performance_rewards += perfomance_rewards[s]
    consistency_budget = 0
    if total_performance_rewards < BUDGET:
        consistency_budget = BUDGET - total_performance_rewards
        total_participation = 0
        for s in consistency_rewards:
            total_participation += consistency_rewards[s]
        for s in consistency_rewards:
            consistency_rewards[s] = (
                consistency_rewards[s] * consistency_budget / total_participation
            )

    total_rewards = {}
    for s in perfomance_rewards:
        total_rewards[s] = perfomance_rewards[s]
    if consistency_budget > 0:
        for s in consistency_rewards:
            if s in total_rewards:
                total_rewards[s] += consistency_rewards[s]
            else:
                total_rewards[s] = consistency_rewards[s]
    return total_rewards


def main() -> None:
    results = compute_payouts(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
    print(results)


if __name__ == "__main__":
    main()
