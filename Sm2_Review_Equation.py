from pydantic import BaseModel, Field
from datetime import date, timedelta

class Evaluation_Input(BaseModel):
    quality: int = Field(default=3, ge=1, le=5)
    efficiency: float = Field(default=2.5)
    interval: int = Field(default=1)
    repetition: int = Field(default=0)
    next_practice_date: date = Field(default_factory=date.today)

class Sm2_Review_Equation:
    def sm2_review(self, input: Evaluation_Input) -> Evaluation_Input:
        output = Evaluation_Input(**input.dict())  # Copy input values

        if input.quality < 3:
            output.interval = 1
            output.efficiency = 1.3
            output.repetition = 0
        else:
            if input.repetition == 0:
                output.interval = 1
            elif input.repetition == 1:
                output.interval = 6
            else:
                output.interval = round(input.interval * input.efficiency)

            # Update Efficiency
            output.efficiency = input.efficiency + (0.1 - (5 - input.quality) * (0.08 + (5 - input.quality) * 0.02))
            output.efficiency = max(1.3, output.efficiency)
            output.repetition = input.repetition + 1

        output.next_practice_date = input.next_practice_date + timedelta(days=output.interval)
        return output