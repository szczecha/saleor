import graphene
from graphene import relay

from ....discount import models
from ....permission.auth_filters import AuthorizationFilters
from ....permission.enums import AccountPermissions, AppPermission, DiscountPermissions
from ...account.dataloaders import UserByUserIdLoader
from ...account.types import User
from ...account.utils import check_is_owner_or_has_one_of_perms
from ...app.dataloaders import AppByIdLoader
from ...app.types import App
from ...channel.types import Channel
from ...core import ResolveInfo
from ...core.descriptions import ADDED_IN_315, PREVIEW_FEATURE
from ...core.doc_category import DOC_CATEGORY_DISCOUNTS
from ...core.fields import PermissionsField
from ...core.scalars import JSON, PositiveDecimal
from ...core.types import ModelObjectType, NonNullList
from ...meta.types import ObjectWithMetadata
from ...utils import get_user_or_app_from_context
from ..dataloaders import (
    ChannelsByPromotionRuleIdLoader,
    PromotionByIdLoader,
    PromotionEventsByPromotionIdLoader,
    PromotionRulesByPromotionIdLoader,
)
from ..enums import PromotionEventsEnum, RewardValueTypeEnum


class Promotion(ModelObjectType[models.Promotion]):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True, description="Name of the promotion.")
    description = JSON(description="Description of the promotion.")
    start_date = graphene.DateTime(
        required=True, description="Start date of the promotion."
    )
    end_date = graphene.DateTime(description="End date of the promotion.")
    created_at = graphene.DateTime(
        required=True, description="Date time of promotion creation."
    )
    updated_at = graphene.DateTime(
        required=True, description="Date time of last update of promotion."
    )
    rules = NonNullList(
        lambda: PromotionRule, description="The list of promotion rules."
    )
    events = NonNullList(
        lambda: PromotionEvent,
        description="The list of events associated with the promotion.",
    )

    class Meta:
        description = (
            "Represents the promotion that allow creating discounts based on given "
            "conditions, and is visible to all the customers."
            + ADDED_IN_315
            + PREVIEW_FEATURE
        )
        interfaces = [relay.Node, ObjectWithMetadata]
        model = models.Promotion
        doc_category = DOC_CATEGORY_DISCOUNTS

    @staticmethod
    def resolve_rules(root: models.Promotion, info: ResolveInfo):
        return PromotionRulesByPromotionIdLoader(info.context).load(root.id)

    @staticmethod
    def resolve_events(root: models.Promotion, info: ResolveInfo):
        return PromotionEventsByPromotionIdLoader(info.context).load(root.id)


class PromotionRule(ModelObjectType[models.PromotionRule]):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True, description="Name of the promotion rule.")
    description = JSON(description="Description of the promotion rule.")
    promotion = graphene.Field(
        Promotion, description="Promotion to which the rule belongs."
    )
    channels = PermissionsField(
        NonNullList(Channel),
        description="List of channels where the rule applies.",
        permissions=[
            AuthorizationFilters.AUTHENTICATED_APP,
            AuthorizationFilters.AUTHENTICATED_STAFF_USER,
        ],
    )
    reward_value_type = RewardValueTypeEnum(
        description="The type of reward value of the promotion rule."
    )
    catalogue_predicate = JSON(
        description=(
            "The catalogue predicate that must be met to apply the rule reward."
        ),
    )
    reward_value = PositiveDecimal(
        description=(
            "The reward value of the promotion rule. Defines the discount value "
            "applied when the rule conditions are met."
        )
    )

    class Meta:
        description = (
            "Represents the promotion rule that specifies the conditions that must "
            "be met to apply the promotion discount." + ADDED_IN_315 + PREVIEW_FEATURE
        )
        interfaces = [relay.Node]
        model = models.PromotionRule
        doc_category = DOC_CATEGORY_DISCOUNTS

    @staticmethod
    def resolve_promotion(root: models.PromotionRule, info: ResolveInfo):
        return PromotionByIdLoader(info.context).load(root.promotion_id)

    @staticmethod
    def resolve_channels(root: models.PromotionRule, info: ResolveInfo):
        return ChannelsByPromotionRuleIdLoader(info.context).load(root.id)


class PromotionEvent(ModelObjectType[models.PromotionEvent]):
    id = graphene.GlobalID()
    date = graphene.DateTime(description="Date when event happened.")
    type = PromotionEventsEnum(description="Promotion event type.")
    user = graphene.Field(User, description="User who performed the action.")
    app = graphene.Field(App, description="App that performed the action.")
    message = graphene.String(description="Content of the event.")
    rule_id = graphene.ID(description="ID of the rule.")

    class Meta:
        description = "History log of the promotion." + ADDED_IN_315 + PREVIEW_FEATURE
        interfaces = [relay.Node]
        model = models.PromotionEvent
        doc_category = DOC_CATEGORY_DISCOUNTS

    @staticmethod
    def resolve_user(root: models.PromotionEvent, info):
        def _resolve_user(user):
            requester = get_user_or_app_from_context(info.context)
            if not requester:
                return None
            check_is_owner_or_has_one_of_perms(
                requester,
                user,
                AccountPermissions.MANAGE_USERS,
                AccountPermissions.MANAGE_STAFF,
            )
            return user

        if root.user_id is None:
            return _resolve_user(None)

        return UserByUserIdLoader(info.context).load(root.user_id).then(_resolve_user)

    @staticmethod
    def resolve_app(root: models.PromotionEvent, info):
        def _resolve_app(app):
            requester = get_user_or_app_from_context(info.context)
            if not requester:
                return None
            check_is_owner_or_has_one_of_perms(
                requester,
                app,
                AppPermission.MANAGE_APPS,
                DiscountPermissions.MANAGE_DISCOUNTS,
            )
            return app

        if root.app_id is None:
            return _resolve_app(None)

        return AppByIdLoader(info.context).load(root.app_id).then(_resolve_app)

    @staticmethod
    def resolve_message(root: models.PromotionEvent, _info):
        return root.parameters.get("message", None)

    @staticmethod
    def resolve_rule_id(root: models.PromotionEvent, _info):
        return root.parameters.get("rule_id", None)
