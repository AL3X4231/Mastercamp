import random

# Board size
board_dim = 8

# Individual representation for genetic algorithm
class Individual:
    def __init__(self, val=None):
        if val is None:
            self.val = random.sample(range(board_dim), board_dim)
        else:
            self.val = val

    def __str__(self):
        result_str = ""
        for v in self.val:
            result_str += str(v)
        return result_str

    @staticmethod
    def conflict(p1, p2):
        # Line or column conflict
        if p1[0]==p2[0] or p1[1] ==p2[1]:
            return True
        
        # Diagonal conflict
        if abs(p1[0]-p2[0])==abs(p1[1]-p2[1]):
            return True
            
        return False

    def fitness(self):
        self.nbconflict = 0
        for i in range(board_dim):
            for j in range(i + 1, board_dim):
                if Individual.conflict([self.val[i],i], [self.val[j],j]):
                    self.nbconflict = self.nbconflict + 1
        return self.nbconflict

# --- Genetic Operators & Helpers ---

def get_fitness(ind):
    return ind.fitness()

def create_rand_pop(count):
    population = []
    for _ in range(count):
        population.append(Individual())
    return population

def evaluate(pop):
    pop_sorted = sorted(pop, key=get_fitness)
    return pop_sorted

def selection(pop, hcount, lcount):
    selected = []
    # Add the best individuals
    for i in range(hcount):
        selected.append(pop[i])
    # Add the worst individuals
    for i in range(len(pop) - lcount, len(pop)):
        selected.append(pop[i])
    return selected

def crossover(ind1, ind2):
    mid = board_dim // 2
    
    val1 = []
    for i in range(mid):
        val1.append(ind1.val[i])
    for i in range(mid, board_dim):
        val1.append(ind2.val[i])
        
    val2 = []
    for i in range(mid):
        val2.append(ind2.val[i])
    for i in range(mid, board_dim):
        val2.append(ind1.val[i])
        
    child1 = Individual(val1)
    child2 = Individual(val2)
    return [child1, child2]

def mutation(ind):
    new_value = []
    for x in ind.val:
        new_value.append(x)
        
    random_index = random.randint(0, board_dim - 1)
    new_value[random_index] = random.randint(0, board_dim - 1)
    
    mutant_ind = Individual(new_value)
    return mutant_ind

#Main loop 

def algo_loop_simple():
    pop = create_rand_pop(25)
    solution_found = False
    iteration_count = 0
    
    while not solution_found:
        print("iteration number: ", iteration_count)
        iteration_count += 1
        
        evaluation = evaluate(pop)
        
        if evaluation[0].fitness() == 0:
            solution_found = True
            print("Solution found: ", evaluation[0])
        else:
            select = selection(evaluation, 10, 4)
            
            crossed = []
            for i in range(0, len(select), 2):
                crossed += crossover(select[i], select[i+1])
                
            mutated = []
            for i in select:
                mutated.append(mutation(i))
                
            new_random = create_rand_pop(5)
            
            pop = select + crossed + mutated + new_random 
            
    print("Final state: ", evaluation[0])

# Main entry point
if __name__ == "__main__":
    algo_loop_simple()