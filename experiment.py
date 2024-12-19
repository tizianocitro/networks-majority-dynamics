from network import *
from utils import *
from heapq import *


def run_experiment(exp_name="experiment"):
    # set for logging file
    os.environ["LOG_FILE_DIR"] = "logs"
    os.environ["LOG_FILE_PATH"] = exp_name

    log(text=f"\n{BLUE}### STARTING EXPERIMENT {exp_name} ###{RESET}\n")

    run_simulation()

    # save_results(results)

    log(text=f"\n{BLUE}### ENDING EXPERIMENT {exp_name} ###{RESET}\n")


def run_simulation():
    graph_name = "karate_club_graph"

    graph = graphs_by_name[graph_name]
    max_degree = get_max_degree(graph)
    log(text=f"Using graph {graph_name} with max degree {max_degree}\n")
    # print_graph(graph, with_nodes=True, with_edges=False)

    nodes_threshold = generate_nodes_threshold_with_node_degrees(graph, graph.nodes)
    nodes_cost = generate_nodes_cost(graph.nodes)

    n = 20
    cost = 50
    log(text=f"Generating {n} seed sets from the graph partition given a cost of {cost}\n")
    seed_sets = seed_sets_from_graph_permutation_given_cost(graph, nodes_cost_dict=nodes_cost, cost=cost, n=n)

    # the max heap will store the seed set cost and the seed set index
    # so, if we want the top 5 seed sets, we can pop 5 times from the heap
    max_heap = []
    for i, s in enumerate(seed_sets):
        log(text="\n---------------------------------------------\n")
        log(text=f"{RED}### START Seed set {i}: {s} START ###{RESET}\n")
        s_cost = seed_set_cost(s.seed_set, nodes_cost)
        s_score = seed_set_score(s.seed_set)

        log(text=f"{YELLOW}Influencing nodes in the seed set {i} with initial cost {s_cost} and score {s_score}")
        print_seed_set(s)
        # start with a clean graph (without any influenced nodes)
        nodes_influenced = generate_nodes_influenced(graph.nodes)
        # influence the node in the seed set i
        nodes_influenced = influence_nodes(s.seed_set, nodes_influenced)
        log(text=f"{RESET}Nodes influenced {i} at the start: {nodes_influenced}\n")

        # influence the nodes in the graph starting from the seed set i
        s_influenced, t = threshold_influence_diffusion(graph, s.seed_set, nodes_influenced, nodes_threshold)
        s.seed_set = s_influenced

        log(text=f"{YELLOW}Influenced seed set {i} in {t} steps:")
        print_seed_set(s_influenced)
        log(text=f"{RESET}Nodes influenced {i} at the end: {nodes_influenced}\n")

        s_influenced_cost = seed_set_cost(s_influenced, nodes_cost) - s_cost
        s_influenced_score = seed_set_score(s_influenced)
        log(text=f"{GREEN}Cost of influenced seed set {i}: {s_influenced_cost}{RESET}")
        log(text=f"{GREEN}Score of influenced seed set {i}: {s_influenced_score}\n{RESET}")

        heappush(max_heap, (-s_influenced_score, i))

        log(text=f"{RED}### ENDING Seed set {i} ENDING ###{RESET}")
        log(text="\n---------------------------------------------\n")
        log()

    log(text="\n---------------------------------------------\n")
    log(text=f"{RED}### Creating new population ###{RESET}\n")

    log(text=f"{RED}### Creating top 50% sets ###{RESET}\n")
    top_50_len = len(max_heap) // 2
    top_50_sets = set()
    log(text=f"{GREEN}Top 50% ({top_50_len} sets) influencing seed sets:{RESET}")
    for _ in range(top_50_len):
        score, i = heappop(max_heap)
        log(text=f"- Seed set {i} with score {-score} -> current: {seed_sets[i].seed_set} | initial: {seed_sets[i].initial_seed_set}")
        top_50_sets.add(seed_sets[i])

    log(text=f"\n{RED}### Creating random sets ###{RESET}")
    random_len = (n - top_50_len) // 2
    random_sets = set()
    while len(random_sets) < random_len:
        random_set = seed_set_from_graph_permutation_given_cost(graph, nodes_cost_dict=nodes_cost, cost=cost)
        if random_set in random_sets or random_set in top_50_sets:
            continue
        random_sets.add(random_set)

    log(text=f"\n{GREEN}Random ({random_len} sets) influencing seed sets:{RESET}")
    for i, s in enumerate(random_sets):
        log(text=f"- Seed set {i} -> {s.seed_set}")

    log(text="\n---------------------------------------------\n")

