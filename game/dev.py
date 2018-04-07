import random
from game.models import *
# Create your models here.


same_rank_ex = [Card('Clubs', 2), Card('Diamonds', 2), Card('Hearts', 2)]
diff_rank_ex = [Card('Clubs', 2), Card('Diamonds', 2), Card('Hearts', 3)]

run_ex = [Card('Hearts', 4), Card('Hearts', 2), Card('Hearts', 3), Card('Hearts', 5)]


if __name__ == '__main__':
    assert (validate_same_rank(same_rank_ex))
    # assert (validate_same_rank(diff_rank_ex))
    assert (validate_run(run_ex))
    # assert (validate_run(diff_rank_ex))