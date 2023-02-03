# Django Imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

# Ghostwriter Libraries
from ghostwriter.reporting.models import ReportFindingLink

from .filters import ReportFindingFilter


@login_required
def report_findings_list(request):
    """
    Display a list of all report findings based on search criteria.

    **Template**

    :template:`stratum/report_findings_list.html`
    """
    findings = (
        ReportFindingLink.objects.select_related("severity", "finding_type", "report")
        .all()
        .order_by("severity__weight", "-cvss_score", "finding_type", "title")
    )
    findings_filter = ReportFindingFilter(request.GET, queryset=findings)
    return render(request, "report_findings_list.html", {"filter": findings_filter})


class ReportFindingListView(LoginRequiredMixin, generic.ListView):
    """
    Display a list of all :model:`reporting.ReportFindingLink`.

    **Template**

    :template:`reporting/report_template_list.html`
    """

    model = ReportFindingLink
    template_name = "report_findings_list.html"
