"""Registro centralizado de modelos SQLAlchemy de AURA."""
from app.models.adaptive_profile_db import AdaptiveProfileDB
from app.models.conversation_context_db import ConversationContextDB
from app.models.conversation_message_db import ConversationMessageDB
from app.models.daily_plan_db import DailyPlanDB
from app.models.human_state_db import HumanStateDB
from app.models.notification_db import NotificationDB
from app.models.proactive_follow_up_db import ProactiveFollowUpDB
from app.models.recommendation_history_db import RecommendationHistoryDB
from app.models.recurring_availability_db import RecurringAvailabilityDB
from app.models.routine_db import RoutineDB
from app.models.task_db import TaskDB
from app.models.task_execution_db import TaskExecutionDB
from app.models.user_db import UserDB
from app.models.user_profile_db import UserProfileDB