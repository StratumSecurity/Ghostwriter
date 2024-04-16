from bs4 import BeautifulSoup
from matplotlib import pyplot as plt

from .enums import Severity

TOTAL_LABEL = "total"
WEIGHT_LABEL = "weight"
SEVERITY_LABEL = "severity"


def format_chart_data(findings):
    # Returns the findings to a specific format to return to custom_serializer to put in the JSON
    # to properly build the bar chart from reportwriter
    counts = {}
    severity_weights = {
        Severity.CRIT.value.lower(): 5,
        Severity.HIGH.value.lower(): 4,
        Severity.MED.value.lower(): 3,
        Severity.LOW.value.lower(): 2,
        Severity.INFO.value.lower(): 1,
    }

    for finding in findings:
        soup = BeautifulSoup(finding["replication_steps"], "html.parser")
        category = soup.get_text()

        # Totals and weights set for each category to properly sort the chart
        severity = finding[SEVERITY_LABEL].lower()
        weight = severity_weights.get(severity, 0)

        counts[category] = counts.get(
            category,
            {
                TOTAL_LABEL: 0,
                WEIGHT_LABEL: 0,
                SEVERITY_LABEL: {k: 0 for k in severity_weights},
            },
        )
        counts[category][TOTAL_LABEL] += 1
        counts[category][WEIGHT_LABEL] += weight
        counts[category][SEVERITY_LABEL][severity] += 1
    return counts


def build_bar_chart(findings):
    # findings format is in the report JSON as {"Injection": 3, "Security Misconfiguration": 2}
    if not findings:
        return None

    fig, ax = plt.subplots()
    # Sort findings by totals and weights where max items are first
    sorted_dict = dict(
        sorted(
            findings.items(),
            key=lambda x: (x[1][TOTAL_LABEL], x[1][WEIGHT_LABEL]),
            reverse=True,
        )
    )

    categories = list(sorted_dict.keys())
    # Color scheme came from
    # https://miro.medium.com/v2/resize:fit:500/format:webp/1*msOeUmFxdojyrur1kqxwaw.png
    color = {
        Severity.INFO.value.lower(): "#4E81BD",
        Severity.LOW.value.lower(): "#8BC53F",
        Severity.MED.value.lower(): "#F6941F",
        Severity.HIGH.value.lower(): "#F0582B",
        Severity.CRIT.value.lower(): "#DE0604",
    }

    num_of_categories = len(categories)
    bottom = [0] * num_of_categories
    # Makes sure the bars are ordered properly by severity where critical is on the right, etc...
    severity_order = [
        Severity.INFO,
        Severity.LOW,
        Severity.MED,
        Severity.HIGH,
        Severity.CRIT,
    ]

    # Need this to make sure the bar sizes are fine and the figure size is appropriate
    # For example, if only one finding is found the bar shouldn't be chunky and the
    # figure should be smaller in height
    # First tuple value is the bar height and the second tuple value is the figure height
    heights = (0.3, 2.9)
    if num_of_categories < 3:
        heights = (0.4, 0.5)
    elif num_of_categories == 3:
        heights = (0.4, 0.8)

    for s in severity_order:
        severity = s.value.lower()
        severity_counts = [
            # casing needs to match between the data coming in and the counts
            sorted_dict[cat][SEVERITY_LABEL].get(severity, 0)
            for cat in categories
        ]
        ax.barh(
            categories,
            severity_counts,
            left=bottom,
            color=color[severity],
            label=severity,
            height=heights[0],
        )
        bottom = [sum(x) for x in zip(bottom, severity_counts)]

    # Remove axes splines
    for s in ["top", "bottom", "left", "right"]:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position("none")
    ax.yaxis.set_ticks_position("none")

    # Add padding between axes and labels and set the font size
    label_size = 11
    ax.xaxis.set_tick_params(pad=5, labelsize=label_size)
    ax.yaxis.set_tick_params(pad=10, labelsize=label_size)

    # Set the font family for the x and y axis labels
    font = {"fontname": "Aptos"}
    for label in ax.get_xticklabels():
        label.set_fontname(font["fontname"])
    for label in ax.get_yticklabels():
        label.set_fontname(font["fontname"])

    # Add x gridlines
    ax.grid(
        visible=True,
        color="grey",
        linestyle="-",
        linewidth=0.2,
        axis="x",
        which="major",
    )
    ax.set_axisbelow(True)

    # Show top values
    ax.invert_yaxis()
    # Set range from 0, incrementing by 1 up to the max findings +1 was needed
    # for max finding count to be shown in chart
    first_max_count_item = next(iter(sorted_dict.items()))
    ax.set_xticks([*range(0, first_max_count_item[1][TOTAL_LABEL] + 1)])

    # Shrink figure to be close to current size in Word template
    # Current literals set make the figure fit on the page correctly
    fig.set_size_inches(10, heights[1])
    fig.set_dpi(200)
    return fig
