from enum import Enum


class PaymentError(Exception):
    def __init__(self, message, code=None):
        super(PaymentError, self).__init__(message, code)
        self.message = message
        self.code = code

    def __str__(self):
        return self.message


class GatewayError(IOError):
    pass


class CustomPaymentChoices:
    MANUAL = "manual"

    CHOICES = [(MANUAL, "Manual")]


class OperationType(Enum):
    PROCESS_PAYMENT = "process_payment"
    AUTH = "authorize"
    CAPTURE = "capture"
    VOID = "void"
    REFUND = "refund"
    CONFIRM = "confirm"


class TransactionError(Enum):
    """Represents a transaction error."""

    INCORRECT_NUMBER = "incorrect_number"
    INVALID_NUMBER = "invalid_number"
    INCORRECT_CVV = "incorrect_cvv"
    INVALID_CVV = "invalid_cvv"
    INCORRECT_ZIP = "incorrect_zip"
    INCORRECT_ADDRESS = "incorrect_address"
    INVALID_EXPIRY_DATE = "invalid_expiry_date"
    EXPIRED = "expired"
    PROCESSING_ERROR = "processing_error"
    DECLINED = "declined"


class TransactionKind:
    """Represents the type of a transaction.

    The following transactions types are possible:
    - AUTH - an amount reserved against the customer's funding source. Money
    does not change hands until the authorization is captured.
    - VOID - a cancellation of a pending authorization or capture.
    - CAPTURE - a transfer of the money that was reserved during the
    authorization stage.
    - REFUND - full or partial return of captured funds to the customer.
    """

    EXTERNAL = "external"
    AUTH = "auth"
    CAPTURE = "capture"
    CAPTURE_FAILED = "capture_failed"
    ACTION_TO_CONFIRM = "action_to_confirm"
    VOID = "void"
    PENDING = "pending"
    REFUND = "refund"
    REFUND_ONGOING = "refund_ongoing"
    REFUND_FAILED = "refund_failed"
    REFUND_REVERSED = "refund_reversed"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    # FIXME we could use another status like WAITING_FOR_AUTH for transactions
    # Which were authorized, but needs to be confirmed manually by staff
    # eg. Braintree with "submit_for_settlement" enabled
    CHOICES = [
        (EXTERNAL, "External reference"),
        (AUTH, "Authorization"),
        (PENDING, "Pending"),
        (ACTION_TO_CONFIRM, "Action to confirm"),
        (REFUND, "Refund"),
        (REFUND_ONGOING, "Refund in progress"),
        (CAPTURE, "Capture"),
        (VOID, "Void"),
        (CONFIRM, "Confirm"),
        (CANCEL, "Cancel"),
    ]


class ChargeStatus:
    """Represents possible statuses of a payment.

    The following statuses are possible:
    - NOT_CHARGED - no funds were take off the customer founding source yet.
    - PARTIALLY_CHARGED - funds were taken off the customer's funding source,
    partly covering the payment amount.
    - FULLY_CHARGED - funds were taken off the customer founding source,
    partly or completely covering the payment amount.
    - PARTIALLY_REFUNDED - part of charged funds were returned to the customer.
    - FULLY_REFUNDED - all charged funds were returned to the customer.
    """

    NOT_CHARGED = "not-charged"
    PENDING = "pending"
    PARTIALLY_CHARGED = "partially-charged"
    FULLY_CHARGED = "fully-charged"
    PARTIALLY_REFUNDED = "partially-refunded"
    FULLY_REFUNDED = "fully-refunded"
    REFUSED = "refused"
    CANCELLED = "cancelled"

    CHOICES = [
        (NOT_CHARGED, "Not charged"),
        (PENDING, "Pending"),
        (PARTIALLY_CHARGED, "Partially charged"),
        (FULLY_CHARGED, "Fully charged"),
        (PARTIALLY_REFUNDED, "Partially refunded"),
        (FULLY_REFUNDED, "Fully refunded"),
        (REFUSED, "Refused"),
        (CANCELLED, "Cancelled"),
    ]


class StorePaymentMethod:
    """Represents if and how a payment should be stored in a payment gateway.

    The following store types are possible:
    - ON_SESSION - the payment is stored only to be reused when
    the customer is present in the checkout flow
    - OFF_SESSION - the payment is stored to be reused even if
    the customer is absent
    - NONE - the payment is not stored.
    """

    ON_SESSION = "on_session"
    OFF_SESSION = "off_session"
    NONE = "none"

    CHOICES = [
        (ON_SESSION, "On session"),
        (OFF_SESSION, "Off session"),
        (NONE, "None"),
    ]


class TransactionAction:
    """Represents possible actions on payment transaction.

    The following actions are possible:
    CHARGE - Represents the charge action.
    REFUND - Represents a refund action.
    VOID - Represents a void action. DEPRECATED: this enum value will be removed
    in Saleor 3.9 (Feature Preview). Use `CANCEL` instead.
    CANCEL - Represents a cancel action.
    """

    CHARGE = "charge"
    REFUND = "refund"
    VOID = "void"
    CANCEL = "cancel"

    CHOICES = [
        (CHARGE, "Charge payment"),
        (REFUND, "Refund payment"),
        (VOID, "Void payment"),
        (CANCEL, "Cancel payment"),
    ]


class TransactionEventActionType:
    """Represents possible event actions.

    The following actions are possible:
    AUTHORIZE - Represents a authorize event.
    CHARGE - Represents a charge event.
    REFUND - Represents a refund event.
    CANCEL - Represents a cancel event.
    """

    AUTHORIZE = "authorize"
    CHARGE = "charge"
    REFUND = "refund"
    CANCEL = "cancel"

    CHOICES = [
        (AUTHORIZE, "Authorize event"),
        (CHARGE, "Charge event"),
        (REFUND, "Refund event"),
        (CANCEL, "Cancel event"),
    ]


class TransactionEventStatus:
    """Represents a status of payment transaction.

    The following statuses are possible:
    SUCCESS - Represents a sucess action.
    FAILURE - Represents a failure action.
    PENDING - Represents a pending action. DEPRECATED: this enum value will be removed
    in Saleor 3.9 (Feature Preview). Saleor automatically marks transaction as pending.
    REQUEST - Represents a request that was send for the payment transaction.
    """

    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    REQUEST = "request"

    CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILURE, "Failure"),
        (REQUEST, "Request"),
    ]


class TransactionEventReportResult:
    """Represents a status of transaction result.

    The following statuses are possible:
    SUCCESS - Represents a sucess success.
    FAILURE - Represents a failure result.
    """

    SUCCESS = "success"
    FAILURE = "failure"

    CHOICES = [
        (SUCCESS, "Success"),
        (FAILURE, "Failure"),
    ]
