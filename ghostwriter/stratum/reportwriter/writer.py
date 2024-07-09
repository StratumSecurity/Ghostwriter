import os

from django.conf import settings
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from string import ascii_letters
from stratum.findings_chart import plt, build_bar_chart
from stratum.enums import Service


def _get_filepath(evidence_directory, filename):
    # Build the filepath to save the figure and add to report
    # Strip special chars except for - and _
    allowed = ascii_letters + "-" + "_"
    new_file_name = "".join(list(filter(allowed.__contains__, filename)))

    if not os.path.exists(evidence_directory):
        # Create a new directory because it does not exist
        os.makedirs(evidence_directory)
    return f"{evidence_directory}/{new_file_name}.png"


def _add_image(par, fig, filepath, pad=0.1, image_width=None, image_height=None):
    # Save the figure as a png to the file system under the report directory to be saved into the report
    fig.savefig(filepath, pad_inches=pad, bbox_inches="tight", dpi=fig.get_dpi())

    # Replace figure in report with saved image
    # Use the filename as a label for replacing the text with the image
    run = par.add_run()
    width = Inches(image_width) if image_width else None
    height = Inches(image_height) if image_height else None

    # The image_width and image_height are separate if we want to change the image
    # dimensions but not the figure
    # For example, we only care about setting the figure height to a specific value
    # but don't care about the width of the image
    run.add_picture(filepath, width=width, height=height)
    # Close the current figure window to clear up memory
    plt.close(fig)


def _build_report_bar_chart(par, keyword, project_id, chart_data):
    par.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fig = build_bar_chart(chart_data)

    # Only add image if we have data, None is returned when we don't have any findings
    if fig:
        # Subtracting from the width and the height to make it fit
        # perfectly on the page without the font looking squished together

        # Do not subtract if the figure height is less than 2
        # This is the case when there are only three categories
        fig_height = fig.get_figheight()
        if fig_height > 2:
            fig_height -= 0.8
        evidence_directory = f"{settings.MEDIA_ROOT}/evidence/${project_id}"
        filepath = _get_filepath(evidence_directory, keyword)
        _add_image(
            par,
            fig,
            filepath,
            image_width=fig.get_figwidth() - 3,
            image_height=fig_height,
        )


def _get_paragraph_of_variable(word_doc, variable_name):
    # Iterate through all paragraphs in the document
    for paragraph in word_doc.paragraphs:
        # Check if the variable is in the paragraph's text
        if variable_name in paragraph.text:
            return paragraph

    # If the variable is not found in any paragraph
    return None


def build_report_bar_chart(word_doc, docx_context):
    # Custom code needed to add bar chart and the data to the document
    # Project ID is needed to save the chart file as it's part of the filename
    project_id = docx_context["project"]["id"]

    chart_tag_mappings = [
        ("chart_bar_rt", "chart_data"),
        ("chart_bar_external_rt", "chart_data_external"),
        ("chart_bar_internal_rt", "chart_data_internal"),
    ]

    for chart_tag, chart_data_label in chart_tag_mappings:
        # Only generate the chart if there is chart data
        # This is needed as we only need to iterate once when it's not netsec reports
        chart_data = docx_context["totals"][chart_data_label]
        if chart_data and docx_context["project"][chart_tag]:
            # Get chart data from context
            # Build the report chart to add to the document
            keyword = chart_data_label.removesuffix("_rt")

            par = _get_paragraph_of_variable(word_doc, f"project.{chart_tag}")
            if par:
                _build_report_bar_chart(par, keyword, project_id, chart_data)


def get_grade_labels():
    grade_labels = []
    for label in ["report", "average"]:
        for service in [member.value for member in Service]:
            grade_labels.append(f"{label}_grade_{service}")
    return grade_labels
