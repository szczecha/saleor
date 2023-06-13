from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Set, Union

if TYPE_CHECKING:
    from .models import Sale, SaleChannelListing


class DiscountValueType:
    FIXED = "fixed"
    PERCENTAGE = "percentage"

    CHOICES = [
        (FIXED, "fixed"),
        (PERCENTAGE, "%"),
    ]


class DiscountType:
    SALE = "sale"
    VOUCHER = "voucher"
    MANUAL = "manual"
    CHOICES = [(SALE, "Sale"), (VOUCHER, "Voucher"), (MANUAL, "Manual")]


class VoucherType:
    SHIPPING = "shipping"
    ENTIRE_ORDER = "entire_order"
    SPECIFIC_PRODUCT = "specific_product"

    CHOICES = [
        (ENTIRE_ORDER, "Entire order"),
        (SHIPPING, "Shipping"),
        (SPECIFIC_PRODUCT, "Specific products, collections and categories"),
    ]


class RewardValueType:
    FIXED = "fixed"
    PERCENTAGE = "percentage"

    CHOICES = [
        (FIXED, "fixed"),
        (PERCENTAGE, "%"),
    ]


class PromotionEvents:
    PROMOTION_CREATED = "promotion_created"
    PROMOTION_UPDATED = "promotion_updated"

    RULE_CREATED = "rule_created"
    RULE_UPDATED = "rule_updated"
    RULE_DELETED = "rule_deleted"

    PROMOTION_STARTED = "promotion_start"
    PROMOTION_ENDED = "promotion_ended"

    CHOICES = [
        (PROMOTION_CREATED, "Promotion created"),
        (PROMOTION_UPDATED, "Promotion updated"),
        (RULE_CREATED, "Rule created"),
        (RULE_UPDATED, "Rule updated"),
        (RULE_DELETED, "Rule deleted"),
        (PROMOTION_STARTED, "Promotion started"),
        (PROMOTION_ENDED, "Promotion ended"),
    ]


@dataclass
class DiscountInfo:
    sale: "Sale"
    channel_listings: Dict[str, "SaleChannelListing"]
    product_ids: Union[List[int], Set[int]]
    category_ids: Union[List[int], Set[int]]
    collection_ids: Union[List[int], Set[int]]
    variants_ids: Union[List[int], Set[int]]
