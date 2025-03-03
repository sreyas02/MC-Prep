from abc import ABC, abstractmethod
from typing import Dict
from typing import List
from threading import Lock


class User:
    def __init__(self, user_id: str, name: str, email: str):
        self.id = user_id
        self.name = name
        self.email = email
        self.balances: Dict[str, float] = {}

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_email(self) -> str:
        return self.email

    def get_balances(self) -> Dict[str, float]:
        return self.balances

class Split(ABC):
    def __init__(self, user: User):
        self.user = user
        self.amount = 0.0

    @abstractmethod
    def get_amount(self) -> float:
        pass

    def set_amount(self, amount: float):
        self.amount = amount

    def get_user(self) -> User:
        return self.user
    

class EqualSplit(Split):
    def __init__(self, user: User):
        super().__init__(user)

    def get_amount(self) -> float:
        return self.amount
    

class ExactSplit(Split):
    def __init__(self, user: User, amount: float):
        super().__init__(user)
        self.amount = amount

    def get_amount(self) -> float:
        return self.amount


class PercentSplit(Split):
    def __init__(self, user: User, percent: float):
        super().__init__(user)
        self.percent = percent

    def get_amount(self) -> float:
        return self.amount

    def get_percent(self) -> float:
        return self.percent
    

class Expense:
    def __init__(self, expense_id: str, amount: float, description: str, paid_by: User):
        self.id = expense_id
        self.amount = amount
        self.description = description
        self.paid_by = paid_by
        self.splits: List[Split] = []

    def add_split(self, split: Split):
        self.splits.append(split)

    def get_id(self) -> str:
        return self.id

    def get_amount(self) -> float:
        return self.amount

    def get_description(self) -> str:
        return self.description

    def get_paid_by(self) -> User:
        return self.paid_by

    def get_splits(self) -> List[Split]:
        return self.splits
    

class Group:
    def __init__(self, group_id: str, name: str):
        self.id = group_id
        self.name = name
        self.members: List[User] = []
        self.expenses: List[Expense] = []

    def add_member(self, user: User):
        self.members.append(user)

    def add_expense(self, expense: Expense):
        self.expenses.append(expense)

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_members(self) -> List[User]:
        return self.members

    def get_expenses(self) -> List[Expense]:
        return self.expenses
    

class SplitwiseService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.users: Dict[str, User] = {}
                cls._instance.groups: Dict[str, Group] = {}
                cls._instance._operation_lock = Lock()
            return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_user(self, user: User):
        with self._operation_lock:
            self.users[user.get_id()] = user

    def add_group(self, group: Group):
        with self._operation_lock:
            self.groups[group.get_id()] = group

    def add_expense(self, group_id: str, expense: Expense):
        with self._operation_lock:
            group = self.groups.get(group_id)
            if group:
                group.add_expense(expense)
                self._split_expense(expense)
                self._update_balances(expense)

    def _split_expense(self, expense: Expense):
        total_amount = expense.get_amount()
        splits = expense.get_splits()
        total_splits = len(splits)

        split_amount = total_amount / total_splits
        for split in splits:
            if isinstance(split, EqualSplit):
                split.set_amount(split_amount)
            elif isinstance(split, PercentSplit):
                split.set_amount(total_amount * split.get_percent() / 100.0)

    def _update_balances(self, expense: Expense):
        for split in expense.get_splits():
            paid_by = expense.get_paid_by()
            user = split.get_user()
            amount = split.get_amount()

            if paid_by != user:
                self._update_balance(paid_by, user, amount)
                self._update_balance(user, paid_by, -amount)

    def _update_balance(self, user1: User, user2: User, amount: float):
        key = self._get_balance_key(user1, user2)
        user1.get_balances()[key] = user1.get_balances().get(key, 0.0) + amount

    def _get_balance_key(self, user1: User, user2: User) -> str:
        return f"{user1.get_id()}:{user2.get_id()}"

    def settle_balance(self, user_id1: str, user_id2: str):
        with self._operation_lock:
            user1 = self.users.get(user_id1)
            user2 = self.users.get(user_id2)

            if user1 and user2:
                key = self._get_balance_key(user1, user2)
                balance = user1.get_balances().get(key, 0.0)

                if balance > 0:
                    user1.get_balances()[key] = 0.0
                    user2.get_balances()[self._get_balance_key(user2, user1)] = 0.0
                elif balance < 0:
                    user1.get_balances()[key] = 0.0
                    user2.get_balances()[self._get_balance_key(user2, user1)] = 0.0


class SplitwiseDemo:
    @staticmethod
    def run():
        splitwise_service = SplitwiseService.get_instance()

        # Create users
        user1 = User("1", "Alice", "alice@example.com")
        user2 = User("2", "Bob", "bob@example.com")
        user3 = User("3", "Charlie", "charlie@example.com")

        splitwise_service.add_user(user1)
        splitwise_service.add_user(user2)
        splitwise_service.add_user(user3)

        # Create a group
        group = Group("1", "Apartment")
        group.add_member(user1)
        group.add_member(user2)
        group.add_member(user3)

        splitwise_service.add_group(group)

        # Add an expense
        expense = Expense("1", 300.0, "Rent", user1)
        equal_split1 = EqualSplit(user1)
        equal_split2 = EqualSplit(user2)
        percent_split = PercentSplit(user3, 20.0)

        expense.add_split(equal_split1)
        expense.add_split(equal_split2)
        expense.add_split(percent_split)

        splitwise_service.add_expense(group.get_id(), expense)

        # Settle balances
        splitwise_service.settle_balance(user1.get_id(), user2.get_id())
        splitwise_service.settle_balance(user1.get_id(), user3.get_id())

        # Print user balances
        for user in [user1, user2, user3]:
            print(f"User: {user.get_name()}")
            for key, value in user.get_balances().items():
                print(f"  Balance with {key}: {value}")


if __name__ == "__main__":
    SplitwiseDemo.run()

    