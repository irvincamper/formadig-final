"""Blueprint de Psicología. La lógica compartida vive fuera del frontend estático."""
from clinical.api import make_blueprint

psicologia_bp = make_blueprint('psicologia')
