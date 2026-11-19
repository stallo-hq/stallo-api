"""Import every module's models so Alembic sees them."""

from app.db.base import Base  # noqa: E402, F401
from app.modules.conversations import models as conversations_models  # noqa: F401
from app.modules.delivery import models as delivery_models  # noqa: F401
from app.modules.exceptions import models as exceptions_models  # noqa: F401
from app.modules.ingestion import models as ingestion_models  # noqa: F401
from app.modules.inventory import models as inventory_models  # noqa: F401
from app.modules.notifications import models as notifications_models  # noqa: F401
from app.modules.orchestrator import models as orchestrator_models  # noqa: F401
from app.modules.orders import models as orders_models  # noqa: F401
from app.modules.payments import models as payments_models  # noqa: F401
from app.modules.sellers import models as sellers_models  # noqa: F401
