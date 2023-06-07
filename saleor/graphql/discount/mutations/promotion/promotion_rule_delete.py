import graphene

from .....discount import events, models
from .....graphql.core.mutations import ModelDeleteMutation
from .....permission.enums import DiscountPermissions
from ....app.dataloaders import get_app_promise
from ....core.descriptions import ADDED_IN_315, PREVIEW_FEATURE
from ....core.doc_category import DOC_CATEGORY_DISCOUNTS
from ....core.types import Error
from ...enums import PromotionRuleDeleteErrorCode
from ...types import PromotionRule


class PromotionRuleDeleteError(Error):
    code = PromotionRuleDeleteErrorCode(description="The error code.", required=True)


class PromotionRuleDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(
            required=True, description="The ID of the promotion to remove."
        )

    class Meta:
        description = "Deletes a promotion rule." + ADDED_IN_315 + PREVIEW_FEATURE
        model = models.PromotionRule
        object_type = PromotionRule
        permissions = (DiscountPermissions.MANAGE_DISCOUNTS,)
        error_type_class = PromotionRuleDeleteError
        doc_category = DOC_CATEGORY_DISCOUNTS

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        app = get_app_promise(info.context).get()
        events.rule_deleted_event(
            instance.promotion, info.context.user, app, [instance]
        )
