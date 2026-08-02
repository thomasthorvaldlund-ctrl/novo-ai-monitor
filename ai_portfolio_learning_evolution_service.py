from ai_portfolio_learning_history_service import get_learning_history


def get_learning_evolution():

    history = get_learning_history()


    if len(history) == 0:
        return {
            "status": "Ingen historik",
            "message": "Ingen AI læringsdata endnu."
        }


    latest = history[-1]


    previous = None

    if len(history) > 1:
        previous = history[-2]


    change = "Stabil"

    observation = (
        "AI's historiske læring er uændret."
    )


    if previous:

        if latest.get("score") > previous.get("score"):
            change = "Forbedret"

            observation = (
                "AI's historiske signalstyrke er forbedret."
            )


        elif latest.get("score") < previous.get("score"):
            change = "Svagere"

            observation = (
                "AI's historiske signalstyrke er faldet."
            )


        elif latest.get("strongest_signal") != previous.get("strongest_signal"):

            change = "Ændret"

            observation = (
                "AI's stærkeste historiske signal har ændret sig."
            )


    return {

        "latest_signal":
            latest.get("strongest_signal"),

        "latest_score":
            latest.get("score"),

        "confidence":
            latest.get("confidence"),

        "change":
            change,

        "observation":
            observation,

        "history_points":
            len(history)
    }
