from bs4 import BeautifulSoup
from matplotlib import pyplot as plt


def format_chart_data(findings):
    # Returns the findings to a specific format to return to custom_serializer to put in the JSON
    # to properly build the bar chart from reportwriter
    counts = {}
    for finding in findings:
        soup = BeautifulSoup(finding["replication_steps"], "html.parser")
        category = soup.get_text()
        counts[category] = counts.get(category, 0) + 1
    return counts


def build_bar_chart(findings):
    # findings format is in the report JSON as {"Injection": 3, "Security Misconfiguration": 2}
    if not findings:
        return None

    fig, ax = plt.subplots()
    # Sort findings by totals where max items are first
    sorted_dict = dict(sorted(findings.items(), key=lambda x: x[1], reverse=True))

    labels = []
    counts = []
    for category, total in sorted_dict.items():
        labels.append(category)
        counts.append(total)

    # Horizontal Bar Plot
    ax.barh(labels, counts, height=0.3)

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
    ax.set_xticks([*range(0, max(counts) + 1)])

    # Shrink figure to be close to current size in Word template
    # Current literals set make the figure fit on the page correctly
    fig.set_size_inches(10, 2.9)
    fig.set_dpi(200)
    return fig
