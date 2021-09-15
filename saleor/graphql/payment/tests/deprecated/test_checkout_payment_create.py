from uuid import uuid4

import graphene
import pytest

from .....checkout import calculations
from .....checkout.fetch import fetch_checkout_info, fetch_checkout_lines
from .....payment.error_codes import PaymentErrorCode
from .....payment.models import ChargeStatus, Payment
from .....plugins.manager import get_plugins_manager
from ....tests.utils import get_graphql_content

DUMMY_GATEWAY = "mirumee.payments.dummy"

CREATE_PAYMENT_MUTATION = """
    mutation CheckoutPaymentCreate(
        $checkoutId: ID, $token: UUID, $input: PaymentInput!
    ) {
        checkoutPaymentCreate(checkoutId: $checkoutId, token: $token, input: $input) {
            payment {
                transactions {
                    kind,
                    token
                }
                chargeStatus
            }
            errors {
                code
                field
            }
        }
    }
    """


def test_checkout_add_payment_by_checkout_id(
    user_api_client, checkout_without_shipping_required, address
):
    checkout = checkout_without_shipping_required
    checkout.billing_address = address
    checkout.save()

    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    manager = get_plugins_manager()
    lines = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    total = calculations.checkout_total(
        manager=manager, checkout_info=checkout_info, lines=lines, address=address
    )
    variables = {
        "checkoutId": checkout_id,
        "input": {
            "gateway": DUMMY_GATEWAY,
            "token": "sample-token",
            "amount": total.gross.amount,
        },
    }
    response = user_api_client.post_graphql(CREATE_PAYMENT_MUTATION, variables)
    content = get_graphql_content(response)
    data = content["data"]["checkoutPaymentCreate"]
    assert not data["errors"]
    transactions = data["payment"]["transactions"]
    assert not transactions
    payment = Payment.objects.get()
    assert payment.checkout == checkout
    assert payment.is_active
    assert payment.token == "sample-token"
    assert payment.total == total.gross.amount
    assert payment.currency == total.gross.currency
    assert payment.charge_status == ChargeStatus.NOT_CHARGED
    assert payment.billing_address_1 == checkout.billing_address.street_address_1
    assert payment.billing_first_name == checkout.billing_address.first_name
    assert payment.billing_last_name == checkout.billing_address.last_name


def test_checkout_add_payment_neither_token_and_id_given(
    user_api_client, checkout_without_shipping_required, address
):
    checkout = checkout_without_shipping_required
    checkout.billing_address = address
    checkout.save()

    manager = get_plugins_manager()
    lines = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    total = calculations.checkout_total(
        manager=manager, checkout_info=checkout_info, lines=lines, address=address
    )
    variables = {
        "input": {
            "gateway": DUMMY_GATEWAY,
            "token": "sample-token",
            "amount": total.gross.amount,
        },
    }
    response = user_api_client.post_graphql(CREATE_PAYMENT_MUTATION, variables)
    content = get_graphql_content(response)
    data = content["data"]["checkoutPaymentCreate"]
    assert len(data["errors"]) == 1
    assert not data["payment"]
    assert data["errors"][0]["code"] == PaymentErrorCode.GRAPHQL_ERROR.name


def test_checkout_add_payment_both_token_and_id_given(
    user_api_client, checkout_without_shipping_required, address
):
    checkout = checkout_without_shipping_required
    checkout.billing_address = address
    checkout.save()

    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    manager = get_plugins_manager()
    lines = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    total = calculations.checkout_total(
        manager=manager, checkout_info=checkout_info, lines=lines, address=address
    )
    variables = {
        "checkoutId": checkout_id,
        "token": checkout.token,
        "input": {
            "gateway": DUMMY_GATEWAY,
            "token": "sample-token",
            "amount": total.gross.amount,
        },
    }
    response = user_api_client.post_graphql(CREATE_PAYMENT_MUTATION, variables)
    content = get_graphql_content(response)
    data = content["data"]["checkoutPaymentCreate"]
    assert len(data["errors"]) == 1
    assert not data["payment"]
    assert data["errors"][0]["code"] == PaymentErrorCode.GRAPHQL_ERROR.name


def test_create_partial_payments(
    user_api_client, checkout_without_shipping_required, address
):
    # given
    checkout = checkout_without_shipping_required
    checkout.billing_address = address
    checkout.save()

    manager = get_plugins_manager()
    lines = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    total = calculations.checkout_total(
        manager=manager, checkout_info=checkout_info, lines=lines, address=address
    )

    def _variables():
        return {
            "token": checkout.token,
            "input": {
                "gateway": DUMMY_GATEWAY,
                "token": uuid4().hex,
                "amount": total.gross.amount,
                "partial": True,
            },
        }

    # when
    response_1 = user_api_client.post_graphql(CREATE_PAYMENT_MUTATION, _variables())
    response_2 = user_api_client.post_graphql(CREATE_PAYMENT_MUTATION, _variables())
    content_1 = get_graphql_content(response_1)
    content_2 = get_graphql_content(response_2)
    data_1 = content_1["data"]["checkoutPaymentCreate"]
    data_2 = content_2["data"]["checkoutPaymentCreate"]

    # then
    assert data_1["payment"]
    assert data_2["payment"]
    assert checkout.payments.filter(is_active=True, partial=True).count() == 2


@pytest.mark.parametrize("first_payment_is_partial", [True, False])
def test_create_subsequent_full_payment(
    user_api_client,
    checkout_without_shipping_required,
    address,
    first_payment_is_partial,
):
    # given
    checkout = checkout_without_shipping_required
    checkout.billing_address = address
    checkout.save()

    manager = get_plugins_manager()
    lines = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    total = calculations.checkout_total(
        manager=manager, checkout_info=checkout_info, lines=lines, address=address
    )

    def _variables(partial):
        return {
            "token": checkout.token,
            "input": {
                "gateway": DUMMY_GATEWAY,
                "token": uuid4().hex,
                "amount": total.gross.amount,
                "partial": partial,
            },
        }

    # when
    response_1 = user_api_client.post_graphql(
        CREATE_PAYMENT_MUTATION, _variables(first_payment_is_partial)
    )
    response_2 = user_api_client.post_graphql(
        CREATE_PAYMENT_MUTATION, _variables(False)
    )
    content_1 = get_graphql_content(response_1)
    content_2 = get_graphql_content(response_2)
    data_1 = content_1["data"]["checkoutPaymentCreate"]
    data_2 = content_2["data"]["checkoutPaymentCreate"]

    # then
    assert data_1["payment"]
    assert data_2["payment"]
    assert checkout.payments.filter(is_active=True).count() == 1
