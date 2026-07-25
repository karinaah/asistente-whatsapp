from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreBreakdown:
    fragmentation: float
    preferred_time: float
    deadline: float
    earliest_start: float

    @property
    def total(self) -> float:
        return (
            self.fragmentation
            + self.preferred_time
            + self.deadline
            + self.earliest_start
        )