from typing import Union
from pydantic import BaseModel, Field
from typing import Optional, Any


# Pydantic
class FinalResponse(BaseModel):
    """For the final response to the user answer the user's query.
    Only explanation and able_to_answer are required.
    """

    answer: Optional[float] = Field(
        ...,
        description="The final answer/score to the user's query in floating point form",
        examples=[3.0, 24.7, None],
    )

    explanation: str = Field(
        ...,
        description="A step-by-step explanation of how you arrived at the answer.",
        examples=[
            "The an example score is calculated by assigning points to each response: "
            "\n - Feeling nervous, anxious, or on edge: Not at all (0 points)"
            "\n - Not being able to stop or control worrying: Nearly every day (3 points)"
            "\n - Worrying too much about different things: Several days (1 point)"
            "\n The total score is 0+3+1 = 4."
        ],
    )

    able_to_answer: bool = Field(
        ...,
        description="Whether or not you were able to answer the user's query; True if you were able to answer, False otherwise.",
        examples=[True, False],
    )


class StringResponse(BaseModel):
    """Respond in a conversational manner. Be kind and helpful."""

    response: str = Field(
        description="Any string response to the user or scratchpad (if you have one)"
    )


class StructuredResponse(BaseModel):
    # output: Union[StringResponse, FinalResponse]
    output: Union[FinalResponse]
