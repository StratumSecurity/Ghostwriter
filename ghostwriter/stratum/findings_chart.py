# Standard Libraries
from enum import Enum

# 3rd Party Libraries
import pandas as pd

# Custom code
from .enums import Severity


class CalcCol(Enum):
    TOTAL = "Total"
    WEIGHT = "Weight"


# https://stackoverflow.com/questions/42097053/matplotlib-cannot-find-basic-fonts
FONT_FAMILY = "Arial Narrow"
FONT_SIZE = 8
# BACKGROUND_COLOR = "#F6F5EE" <~ YUCK!
BACKGROUND_COLOR = "#FFFFFF"

# What we picked our new color scheme
# https://miro.medium.com/v2/resize:fit:500/format:webp/1*msOeUmFxdojyrur1kqxwaw.png
# https://medium.com/@alrieristivan/guide-to-colour-wheel-7ea66881a83a

# This app was used to get exact color codes from the image above
# https://redketchup.io/color-picker
CRITICAL = "#DE0604"
HIGH = "#F0582B"
MEDIUM = "#F6941F"
LOW = "#8BC53F"
BEST = "#4E81BD"

# This app was used to get exact color codes from the image above
# https://redketchup.io/color-picker
violet = "#662D91"
plum = "#262262"
blue = "#1075BD"
teal = "#10A89E"
green = "#0D9444"
lime = "#8BC53F"
yellow = "#FFF104"
orange = "#FCB040"
tangarine = "#F6941F"
redorange = "#F0582B"
red = "#BE1E2E"
pink = "#D91A5C"

colors = [
    violet,
    blue,
    red,
    green,
    orange,
    teal,
    lime,
    pink,
    tangarine,
    redorange,
    red,
    plum,
]

width = 0.8
fontsize = 7
barWidth = 1


def _build_axis_style(ax, max_y):
    ax.set_xlabel(
        "Findings Category",
        fontfamily=FONT_FAMILY,
        fontsize=FONT_SIZE,
        fontweight="bold",
        labelpad=20,
    )
    ax.set_ylabel(
        "Total Number of Findings",
        fontfamily=FONT_FAMILY,
        fontsize=FONT_SIZE,
        fontweight="bold",
    )
    ax.set_facecolor(BACKGROUND_COLOR)
    ax.set_yticks(range(0, max_y))

    # Hide the right and top spines
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    spine_color = "#868686"
    ax.spines.left.set_color(spine_color)
    ax.spines.bottom.set_color(spine_color)


def _build_legend_style(ax, fig):
    # Set the right font for the legend, remove frame, moves to the upper center, and stretches by 5 columns horizontally
    # https://matplotlib.org/3.1.1/api/legend_api.html
    h, l = ax.get_legend_handles_labels()
    legend = ax.legend(
        h,  # needs to be reversed(h), if using a vertical legend
        l,  # needs to be reversed(l), if using a vertical legend
        prop={"family": FONT_FAMILY, "size": FONT_SIZE},  # , weight": "bold"},
        columnspacing=1,
        handletextpad=-1.1,
        loc="upper center",
        ncol=5,
    )
    legend.set_frame_on(False)
    # Sets a smaller color swatch size for the legend
    for h in legend.legendHandles:
        h.set_width(5)

    # Moves the legend outside of all bars by archoring to the right edge
    # legend.set_bbox_to_anchor((1, 1), fig.transFigure)


def _label_bars(ax):
    # Loop through each category and do not display 0 labels in chart
    suppress_zero = 0
    for container in ax.containers:
        labels = [int(v) if v != suppress_zero else "" for v in container.datavalues]
        ax.bar_label(
            container,
            labels=labels,
            label_type="center",
            color="white",
            fontweight="bold",
            fontfamily=FONT_FAMILY,
            fontsize=FONT_SIZE + 1,
        )


def build_bar_chart(report_data):
    category_label = "Category"
    df = pd.DataFrame(
        report_data,
        columns=[
            category_label,
            Severity.BP.value,
            Severity.LOW.value,
            Severity.MED.value,
            Severity.HIGH.value,
            Severity.CRIT.value,
        ],
    )

    # Drops rows that have no findings
    df2 = df.loc[:, df.columns != category_label]
    df = df.loc[(df2 != 0).any(axis=1)]

    # Calculate the totals for each category and weight
    df[CalcCol.TOTAL.value] = df.sum(axis=1, numeric_only=True)
    df[CalcCol.WEIGHT.value] = (
        (df[Severity.BP.value] * 1)
        + (df[Severity.LOW.value] * 2)
        + (df[Severity.MED.value] * 3)
        + (df[Severity.HIGH.value] * 4)
        + (df[Severity.CRIT.value] * 5)
    )
    # Sorts the graph by weight
    df = df.sort_values([CalcCol.TOTAL.value, CalcCol.WEIGHT.value], ascending=False)

    # Get the max finding count and add spacing for the y axis
    max_y = int(df[CalcCol.TOTAL.value].max()) + 2

    # Drop the calc columns as they aren't used in the graph and the color field will throw an error if they are present
    df = df.drop(columns=[CalcCol.TOTAL.value, CalcCol.WEIGHT.value])

    if len(df.index) > 6:
        LABEL_FONT_SIZE = FONT_SIZE - 3
    else:
        LABEL_FONT_SIZE = FONT_SIZE - 1

    # font size - 3 is used to prevent overlapping x-axis labels
    ax = df.plot(
        x=category_label,
        legend="reverse",
        kind="bar",
        stacked=True,
        fontsize=LABEL_FONT_SIZE,
        # rot=45 to rotate the labels diagonally, but is centered by the middle of the text and not its ending - jnqpblc
        rot=0,
        color={
            Severity.BP.value: BEST,
            Severity.LOW.value: LOW,
            Severity.MED.value: MEDIUM,
            Severity.HIGH.value: HIGH,
            Severity.CRIT.value: CRITICAL,
        },
    )

    _build_axis_style(ax, max_y)
    fig = ax.get_figure()
    fig.set_facecolor(BACKGROUND_COLOR)

    # Shrink figure to be close to current size in Word template
    # Current literals set make the figure fit on the page correctly
    fig.set_size_inches(6.3, 3.8)

    # Think of DPI as zooming in on the image making it easier to see
    fig.set_dpi(200)

    _build_legend_style(ax, fig)
    _label_bars(ax)
    return fig


def build_pie_chart(report_data, total_findings):
    df = pd.DataFrame(report_data)
    # Make the category label the index and then the only column in the frame is the percentage
    df = df.set_index(0)
    df = round(df.sum(axis=1, numeric_only=True) / total_findings * 100, 0).astype(int)
    ax = df.plot(
        kind="pie",
        radius=1.5,
        y=1,
        legend=False,
        wedgeprops={"linewidth": 1, "edgecolor": "white", "antialiased": True},
        autopct="%1.0f%%",
        pctdistance=0.8,
        # Setting this with static values distorts the circle with differing values -- better to set only height in the reportwriter.py
        # figsize=(3.6, 3.2),
        startangle=145,
        labeldistance=1.3,
        colors=colors,
        # colors=mcolors.TABLEAU_COLORS,
        textprops={
            "size": FONT_SIZE + 9,
            "weight": "bold",
            "family": FONT_FAMILY,
            "horizontalalignment": "center",
        },
    )
    ax.set_ylabel(None)

    for text in ax.texts:
        if "%" in text.get_text():
            text.set_color("white")

    fig = ax.get_figure()
    fig.set_facecolor(BACKGROUND_COLOR)
    fig.set_dpi(200)
    return fig
