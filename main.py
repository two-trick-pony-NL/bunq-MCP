# server.py
from bunq.sdk.context.api_context import ApiContext, ApiEnvironmentType
from bunq.sdk.context.bunq_context import BunqContext
from bunq import Pagination
from bunq.sdk.model.generated.endpoint import (
    BillingContractSubscriptionApiObject,
    CustomerLimitApiObject,
    InvoiceByUserApiObject,
    PaymentApiObject,
    RequestInquiryApiObject,
    MonetaryAccountBankApiObject,
    CardDebitApiObject,
    SchedulePaymentApiObject,
    BunqMeTabApiObject,
    BunqMeTabEntryApiObject,
    ScheduleApiObject,
    PaymentApiObject,

)
from bunq.sdk.model.generated.object_ import AmountObject, PointerObject
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Literal

# Load environment variables and initialize bunq API context
load_dotenv()
print("=== Starting MCP Server for bunq API ===")

BUNQ_API_KEY = os.getenv("BUNQ_API_KEY")
BUNQ_ENVIROMENT = os.getenv("BUNQ_ENVIROMENT")

if BUNQ_ENVIROMENT == 'PRODUCTION': 
    environment = ApiEnvironmentType.PRODUCTION
else: 
    environment = ApiEnvironmentType.SANDBOX

print("├ Setting bunq environment: ", BUNQ_ENVIROMENT)

print("├ Creating API Context")
api_context = ApiContext.create(
    environment,
    BUNQ_API_KEY,
    "bunq MCP Server"
)
print("├ Loading API Context")
BunqContext.load_api_context(api_context)
user_context = BunqContext.user_context()
print("└ Loaded User Context, this is your user ", user_context.user_person.display_name, " // id: ", user_context.user_id, "\n")

# Initialize FastMCP server
print("=== Starting MCP Server ===")
mcp = FastMCP("bunq")


@mcp.tool()
def get_user_id() -> str:
    """Returns the current bunq user ID."""
    print("<UNK> Getting User ID")
    return str(user_context.user_id)


@mcp.tool()
def get_user_display_name() -> str:
    """Returns the display name of the current bunq user."""
    print("Get display name")
    return str(user_context.user_person.display_name)



@mcp.tool()
def get_primary_monetary_account_id() -> str:
    """Returns the ID of the primary monetary account."""
    print("Get primary monetary account ID")
    primary_account = user_context.primary_monetary_account.to_json()
    return primary_account

@mcp.tool()
def get_list_monetary_accounts() -> list:
    """Returns the ID of the primary monetary account."""
    print("get list monetary accounts")
    accounts:list = MonetaryAccountBankApiObject.list().value
    return accounts


@mcp.tool()
def list_user_invoices():
    """
    Lists all invoices for the current user.

    Returns:
    - List of InvoiceByUserApiObject
    """
    print("List user invoices")
    return InvoiceByUserApiObject.list().value


@mcp.tool()
def get_subscription_contracts():
    """
    Retrieves all subscription contracts for the user.

    Returns:
    - List of BillingContractSubscriptionApiObject
    """
    print("Get subscription contracts")
    return BillingContractSubscriptionApiObject.list().value


@mcp.tool()
def send_payment(amount: str, currency: str, alias_type: str, alias_value:str, counterparty_name:str,  description: str):
    """
    Sends a payment to a counterparty.

    Parameters:
    - amount (str): The amount to send.
    - currency (str): The currency code, e.g., EUR.
    - counterparty_alias (dict): The alias object for the recipient.
    - description (str): The payment description.

    Returns:
    - PaymentApiObject: The created payment object.
    """
    print("Sending payment")
    if alias_type not in {"EMAIL", "PHONE_NUMBER", "IBAN"}:
        raise ValueError("Invalid alias type. Must be EMAIL, PHONE_NUMBER, or IBAN")
    alias = PointerObject(alias_type, alias_value, counterparty_name)
    payment_id = PaymentApiObject.create(
        amount=AmountObject(amount, currency),
        counterparty_alias=alias,
        description=description,
    ).value
    return PaymentApiObject.get(payment_id).value


@mcp.tool()
def request_money(amount: str, currency: str, alias_type: str, alias_value:str, counterparty_name:str,  description: str):
    """
    Creates a payment request (request inquiry).

    Parameters:
    - amount (str): Requested amount.
    - currency (str): Currency code.
    - counterparty_alias (dict): The alias object for the requester.
    - description (str): Description of the request.

    Returns:
    - RequestInquiryApiObject: The created request object.
    """
    print("Requesting payment")
    if alias_type not in {"EMAIL", "PHONE_NUMBER", "IBAN"}:
        raise ValueError("Invalid alias type. Must be EMAIL, PHONE_NUMBER, or IBAN")
    alias = PointerObject(alias_type, alias_value, counterparty_name)
    request_id = RequestInquiryApiObject.create(
        amount_inquired=AmountObject(amount, currency),
        counterparty_alias=alias,
        description=description,
        allow_bunqme=True
    ).value
    return RequestInquiryApiObject.get(request_id).value

@mcp.tool()
def create_card(second_line, type, product_type):
    """
    Creates a new debit card.

    Parameters:
    - second_line (str): Second line text on the card.
    - type (str): Type of card (e.g., MAESTRO, MASTERCARD).
    - product_type (str): Product type (e.g., DIGICARD).

    Returns:
    - CardDebitApiObject: The created card object.
    """
    print("Create new debit card")
    return CardDebitApiObject.create(
        second_line=second_line,
        name_on_card=user_context.user_person.display_name,
        type_=type,
        product_type=product_type,
    ).value


@mcp.tool()
def fetch_last_payments(count: int = 10):
    """
    Fetches the most recent payments.

    Args:
        count: The maximum number of payments to retrieve (default: 10)

    Returns:
        List of recent Payment objects, sorted by date (newest first)
    """
    print("Fetch last payments")
    pagination = Pagination()
    pagination.count = count

    payments = PaymentApiObject.list(params=pagination.url_params_count_only).value
    return [
        {
            "id": payment.id_,
            "created": payment.created,
            "amount": {
                "value": payment.amount.value,
                "currency": payment.amount.currency,
            },
            "description": payment.description,
            "counterparty": {
                "name": getattr(payment.counterparty_alias.pointer, "name", None),
                "type": getattr(payment.counterparty_alias.pointer, "type", None),
                "value": getattr(payment.counterparty_alias.pointer, "value", None),
            },
        }
        for payment in payments
    ]


@mcp.tool()
def schedule_payment(payment: dict, schedule: dict, description: str):
    """
    Schedule a recurring payment to a recipient with the necessary amount, recipient, description, and schedule details.

    Args:
        payment: Dictionary containing:
            - amount: Object with 'value' and 'currency'
            - counterparty_alias: Object with 'type', 'value', and 'name'
        schedule: Dictionary containing:
            - time_start: ISO 8601 formatted start time
            - recurrence_unit: Recurrence frequency (ONCE, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY)
            - recurrence_size: Interval between recurrences
        description: A description of the scheduled payment purpose

    Returns:
        The created scheduled payment object
    """
    scheduled_payment_id = SchedulePaymentApiObject.create(
        payment=payment,
        schedule=schedule,
        monetary_account_id=get_primary_monetary_account_id(),
        purpose=description
    ).value

    return ScheduleApiObject.get(scheduled_payment_id).value


@mcp.tool()
def generate_bunq_me_link(amount, currency, description, redirect_url=None):
    """
    Generates a bunq.me payment link.

    Parameters:
    - amount (str): The amount requested.
    - currency (str): Currency code.
    - description (str): Purpose of the request.
    - redirect_url (str, optional): URL to redirect after payment.

    Returns:
    - str: Shareable bunq.me link or error message.
    """
    try:
        amount_inquired = AmountObject(amount, currency)
        bunq_me_tab_entry = BunqMeTabEntryApiObject(
            amount_inquired=amount_inquired,
            description=description,
            redirect_url=redirect_url
        )

        bunq_me_tab = BunqMeTabApiObject.create(bunq_me_tab_entry).value
        bunq_me_tab = BunqMeTabApiObject.get(bunq_me_tab).value

        share_url = getattr(bunq_me_tab, "bunqme_tab_share_url", None)
        if share_url:
            return share_url

        if hasattr(bunq_me_tab, "bunqme_tab_entry"):
            entry = bunq_me_tab.bunqme_tab_entry
            share_url = getattr(entry, "share_url", None)
            if share_url:
                return share_url

        return "URL generation failed: Could not find share URL in the response"
    except Exception as e:
        return f"URL generation failed: {str(e)}"


if __name__ == "__main__":
    mcp.run()
