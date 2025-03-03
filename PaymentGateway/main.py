# user.py
class User:
    def __init__(self, user_id, name, email, phone):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.account = Account(user_id)


# account.py
class Account:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transaction_history = []  # List of transactions
        self.preferred_payment_method = None  # Store user's preferred payment method
        self.balance = 0  # Initialize balance

    def set_preferred_payment_method(self, payment_method):
        self.preferred_payment_method = payment_method

    def get_preferred_payment_method(self):
        return self.preferred_payment_method

    def get_transaction_history(self):
        return self.transaction_history

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)

    def refund_transaction(self, transaction_id):
        print(self.transaction_history)
        # Logic to refund a transaction
        for transaction in self.transaction_history:
            if transaction['id'] == transaction_id:
                transaction['refunded'] = True
                return f"Transaction {transaction_id} refunded."
        return "Transaction not found."

    def set_balance(self, amount):
        self.balance = amount

    def has_sufficient_balance(self, amount):
        return self.balance >= amount


# payment_strategy.py
from abc import ABC, abstractmethod

# Payment Strategy Interface
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount, currency):
        pass

# Concrete Payment Strategies
class CreditCardPayment(PaymentStrategy):
    def __init__(self):
        self.payment_name="CreditCard"

    def get_name(self):
        return self.payment_name
    
    def process_payment(self, amount, currency):
        print(f"Processing credit card payment of {amount} {currency}")

class UpiPayment(PaymentStrategy):
    def __init__(self):
        self.payment_name="Upi"

    def get_name(self):
        return self.payment_name
    
    def process_payment(self, amount, currency):
        print(f"Processing UPI payment of {amount} {currency}")

class WalletPayment(PaymentStrategy):
    def __init__(self):
        self.payment_name="Wallet"

    def get_name(self):
        return self.payment_name
    
    def process_payment(self, amount, currency):
        print(f"Processing wallet payment of {amount} {currency}")


# notification_strategy.py
# Notification Strategy Interface
class NotificationStrategy(ABC):
    @abstractmethod
    def send_notification(self, contact_info, message):
        pass

# Concrete Notification Strategies
class SmsNotification(NotificationStrategy):
    def send_notification(self, contact_info, message):
        print(f"Sending SMS to {contact_info}: {message}")

class EmailNotification(NotificationStrategy):
    def send_notification(self, contact_info, message):
        print(f"Sending Email to {contact_info}: {message}")


# payment_gateway.py
import threading  # Import threading for locks

class PaymentGateway:
    _instance = None
    _lock = threading.Lock()  # Lock for thread-safe singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Ensure only one thread can create an instance at a time
            if not cls._instance:
                cls._instance = super(PaymentGateway, cls).__new__(cls)
        return cls._instance

    def __init__(self, notification_strategy: NotificationStrategy = None):
        if not hasattr(self, 'initialized'):  # Prevent re-initialization
            self.notification_strategy = notification_strategy
            self.payment_methods = {}
            self.initialized = True

    def add_payment_method(self, payment_method: PaymentStrategy):
        with self._lock:  # Lock to ensure thread-safe modification
            self.payment_methods[payment_method.get_name()] = payment_method
            print(f"Payment method {payment_method.get_name()} added.")

    def get_available_payment_methods(self):
        print("Available payment methods:")
        for payment_method in self.payment_methods:
            print(payment_method)

    def set_preferred_payment_method(self, user: User, payment_method):
        with self._lock:  # Lock to ensure thread-safe modification
            if payment_method.get_name() in self.payment_methods:
                user.account.set_preferred_payment_method(self.payment_methods[payment_method.get_name()])
                print(f"Preferred payment method {payment_method.get_name()} set for user {user.name}.")
            else:
                print(f"Payment method not available.")

    def execute_payment(self, user: User, amount, currency, selected_payment_method=None):
        try:
            with self._lock:  # Lock to ensure thread-safe access
                if not user.account.has_sufficient_balance(amount):
                    print("Insufficient balance for the payment.")
                    return  # Fail the payment process

                if selected_payment_method:
                    if selected_payment_method.get_name() in self.payment_methods:
                        selected_payment_method.process_payment(amount, currency)
                        transaction_id = self._log_transaction(user, amount, currency, selected_payment_method.get_name())
                        print(f"Payment processed using {selected_payment_method.get_name()}")
                    else:
                        print("Selected payment method is not available.")
                        return
                else:
                    preferred_payment_method = user.account.get_preferred_payment_method()
                    if preferred_payment_method:
                        preferred_payment_method.process_payment(amount, currency)
                        transaction_id = self._log_transaction(user, amount, currency, preferred_payment_method.get_name())
                    else:
                        print("No preferred payment method set for the user.")
                        return

                message = f"Dear {user.name}, your payment of {amount} {currency} has been processed."
                self.notification_strategy.send_notification(user.phone, message)

        except Exception as e:
            print(f"Error processing payment: {e}")

    def _log_transaction(self, user: User, amount, currency, payment_method_name):
        transaction = {
            'id': len(user.account.get_transaction_history()) + 1,  # Simple ID generation
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method_name,
            'refunded': False
        }
        user.account.add_transaction(transaction)
        return transaction['id']

    def refund_payment(self, user: User, transaction_id):
        result = user.account.refund_transaction(transaction_id)
        print(result)

    def get_transaction_history(self, user: User):
        return user.account.get_transaction_history()


# PaymentGatewayDemo class for testing
class PaymentGatewayDemo:
    @staticmethod
    def run_demo():
        # Create a PaymentGateway with SMS notification
        notification_method = SmsNotification()
        payment_gateway = PaymentGateway(notification_method)

        payment_gateway.add_payment_method(CreditCardPayment())
        payment_gateway.add_payment_method(UpiPayment())
        payment_gateway.add_payment_method(WalletPayment())

        # Create a user
        user = User(user_id=1, name="John Doe", email="john@example.com", phone="1234567890")

        user.account.set_balance(100.00)  # Set balance to $100.00

        payment_gateway.get_available_payment_methods()

        # Set preferred payment method through PaymentGateway
        payment_gateway.set_preferred_payment_method(user, UpiPayment())  # UpiPayment

        # Execute a payment with a selected payment method
        print("Executing Payment with selected payment method (Credit Card):")
        payment_gateway.execute_payment(user, 100, 'USD', selected_payment_method=CreditCardPayment())

        print("\n---\n")

        # Execute a payment without selecting a payment method (should use preferred)
        print("Executing Payment without selecting a payment method (should use preferred):")
        payment_gateway.execute_payment(user, 200, 'INR')

        # Retrieve transaction history
        print("\nTransaction History:")
        print(payment_gateway.get_transaction_history(user))

        # Refund a transaction
        print("\nRefunding Transaction ID 1:")
        payment_gateway.refund_payment(user, 1)

        # Check transaction history after refund
        print("\nTransaction History after refund:")
        print(payment_gateway.get_transaction_history(user))


# Example usage
if __name__ == "__main__":
    PaymentGatewayDemo.run_demo()

