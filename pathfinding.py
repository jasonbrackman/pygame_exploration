from __future__ import annotations
from typing import Deque, Dict, List, Callable, Generic, Optional, TypeVar, Set
from collections import deque
from heapq import heappush, heappop

T = TypeVar("T")


class Stack(Generic[T]):
    """
    LIFO Structure:
    - always append items to the end of the list and
    - always pop the last item off first.
    """

    def __init__(self):
        self._container: List[T] = []

    @property
    def empty(self) -> bool:
        return len(self._container) == 0

    def push(self, item):
        self._container.append(item)

    def pop(self):
        return self._container.pop()

    def __repr__(self):
        return repr(self._container)


class Queue(Generic[T]):
    """
    FIFO Structure:
    - always append to the right
    - always pop from the left
    """

    def __init__(self) -> None:
        # While the book uses Deque -- it isn't recognized by PyCharm.  The idea is
        # that the Deque is an 'analog' for the collections.deque()... probably helps
        # when defining internal types of the container.
        self._container: Deque[T] = deque()

    @property
    def empty(self) -> bool:
        return not self._container  # not is true for empty container

    def push(self, item: T) -> None:
        self._container.append(item)

    def pop(self) -> T:
        return self._container.popleft()  # FIFO

    def __repr__(self) -> str:
        return repr(self._container)


class PriorityQueue(Generic[T]):
    def __init__(self) -> None:
        self._container: List[T] = []

    @property
    def empty(self) -> bool:
        return not self._container  # not is true for empty container

    def push(self, item: T) -> None:
        heappush(self._container, item)  # in by priority

    def pop(self) -> T:
        return heappop(self._container)  # out by priority

    def __repr__(self) -> str:
        return repr(self._container)


class Node(Generic[T]):
    def __init__(
            self,
            state: T,
            parent: Optional[Node],
            cost: float = 0.0,
            heuristic: float = 0.0,
    ) -> None:
        """

        :param state: The Node identity to be compared to another Node.
        :param parent:
        :param cost:
        :param heuristic:
        """
        self.state = state
        self.parent: Optional[Node] = parent
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


# def _dfs(initial, goal_test, successors):
#     frontier = list()
#     frontier.append(Node(initial, parent=None))
#
#     explored = {initial}
#
#     while frontier:
#         current_node = frontier.pop()
#         current_state = current_node.state
#         if goal_test(current_state):
#             return current_node
#         for child in successors(current_state):
#             if child in explored:
#                 continue
#             explored.add(child)
#             frontier.append(Node(child, current_node))
#
#     return None


def dfs(
        initial: T, goal_test: Callable[[T], bool], successors: Callable[[T], List[T]]
) -> Optional[Node[T]]:
    # frontier is where we've yet to go
    frontier: Stack[Node[T]] = Stack()
    frontier.push(Node(initial, parent=None))

    # explored is where we've been
    explored: Set[T] = {initial}

    # keep going while there is more to explore
    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state

        # if we found the goal, we're done
        if goal_test(current_state):
            return current_node

        # check where we can go next and haven't explored
        for child in successors(current_state):
            if child in explored:
                # skip children we already explored
                continue
            explored.add(child)
            frontier.push(Node(child, current_node))

    return None  # went through everything and never found goal


def bfs(
        initial: T, goal_test: Callable[[T], bool], successors: Callable[[T], List[T]]
) -> Optional[Node[T]]:
    # frontier is where we've yet to go
    frontier: Queue[Node[T]] = Queue()
    frontier.push(Node(initial, None))  # explored is where we've been

    explored: Set[T] = {initial}

    # keep going while there is more to explore
    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state  # if we found the goal, we're done
        if goal_test(current_state):
            return current_node
        # check where we can go next and haven't explored
        for child in successors(current_state):
            if child in explored:  # skip children we already explored
                continue
            explored.add(child)
            frontier.push(Node(child, current_node))

    return None


def astar(
        initial: T,
        goal_test: Callable[[T], bool],
        successors: Callable[[T], List[T]],
        heuristic: Callable[[T], float],
) -> Optional[Node[T]]:
    # frontier is where we've yet to go
    frontier: PriorityQueue[Node[T]] = PriorityQueue()
    frontier.push(
        Node(initial, None, 0.0, heuristic(initial))
    )  # explored is where we've been
    explored: Dict[T, float] = {initial: 0.0}
    # keep going while there is more to explore
    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state  # if we found the goal, we're done
        if goal_test(current_state):
            return current_node
        # check where we can go next and haven't explored
        for child in successors(current_state):
            new_cost: float = current_node.cost + 1  # assumes a grid, need a cost function for more sophisticated apps
            if child not in explored or explored[child] > new_cost:
                explored[child] = new_cost
                frontier.push(Node(child, current_node, new_cost, heuristic(child)))
    return None  # went through everything and never found goal


def node_to_path(node: Node[T]) -> List[T]:
    path: List[T] = [node.state]
    # work backwards from end to front
    while node.parent is not None:
        node = node.parent
        path.append(node.state)

    path.reverse()

    return path
