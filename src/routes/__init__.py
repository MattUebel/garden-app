from ..models import PlantStatus

# Define valid status transitions
VALID_STATUS_TRANSITIONS = {
    PlantStatus.PLANTED: {PlantStatus.SPROUTED},
    PlantStatus.SPROUTED: {PlantStatus.FLOWERING},
    PlantStatus.FLOWERING: {PlantStatus.HARVESTING},
    PlantStatus.HARVESTING: {PlantStatus.FINISHED},
    PlantStatus.FINISHED: set()  # No transitions from FINISHED
}