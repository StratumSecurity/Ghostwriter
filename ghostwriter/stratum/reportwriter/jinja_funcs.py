from stratum.enums import Grade, GradeColor


# Define a function to create the custom Jinja tag for the grade cell color
def get_color_by_grade(grade):
    # Tried https://docxtpl.readthedocs.io/en/latest/#cell-color but can only
    # be called once even with if conditions
    # https://github.com/elapouya/python-docx-template/issues/373
    # Has to be {% cellbg ( totals.report_grade_appsec | color_by_grade) %}
    # cellbg doesn't like Jinja defined variables as the value such as cellbg jinja_var
    color_map = {i.name: i.value for i in GradeColor}
    # Return black if grade is None; this only happens during the linting
    # process for cloud templates as the hardcoded tag data isn't in the context
    # This prevents us from hardcoding the many finding types for cloud in the context
    return "000000" if not grade else color_map.get(grade)


def get_grade_comparison(grade, class_average_grade):
    # We have to convert the average grade back to a number so the comparison
    # between the current test and the average can be done properly
    # as the letters of both will equal the same when they match B==B in numeric 80==80
    my_grade = Grade.get_value(grade)
    average_grade = Grade.get_value(class_average_grade)
    # Default to "an average" when both are the same grade or both are None
    # None values only happen during the linting for cloud as mentioned
    # in the comments above in get_color_by_grade
    compare_label = "an average"

    if my_grade and average_grade:
        if my_grade > average_grade:
            compare_label = "an above average"
        elif my_grade < average_grade:
            compare_label = "a below average"
    return compare_label
